"""BusyTag device communication class"""

import asyncio
import json
import os
import platform
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List
import serial

from .util import (
    FileStruct,
    PatternLine,
    LedArgs,
    UploadProgressArgs,
    FileUploadFinishedArgs,
    UploadErrorType,
    WifiConfigArgs,
    DeviceConfig,
    SolidColor
)


class BusyTagDevice:
    """Represents a BusyTag device for serial communication"""

    MAX_FILENAME_LENGTH = 40

    def __init__(self, port_name: Optional[str]):
        self.port_name = port_name
        self._serial_port: Optional[serial.Serial] = None
        self._lock = asyncio.Lock()

        # Device information
        self.device_name = ""
        self.manufacture_name = ""
        self.id = ""
        self.firmware_version = ""
        self.hardware_version = ""
        self.firmware_version_float = 0.0

        self.current_image_name = ""
        self._cached_file_dir_path = ""
        self.file_list: List[FileStruct] = []
        self.local_host_address = ""

        self.free_storage_size = 0
        self.total_storage_size = 0
        self._busytag_drive: Optional[Path] = None

        self._current_upload_filename = ""
        self._pattern_list: List[PatternLine] = []
        self._async_command_active = False
        self._write_raw_data = False
        self._is_playing_pattern = False
        self._sending_file = False
        self._skip_checking = False

        # Centralized data buffer
        self._data_buffer = deque()
        self._data_available_event = asyncio.Event()

        # Cancellation tokens
        self._connection_task: Optional[asyncio.Task] = None
        self._file_sending_cancelled = False

        # Event callbacks
        self.on_connection_state_changed: Optional[Callable[[bool], None]] = None
        self.on_received_device_basic_information: Optional[Callable[[bool], None]] = None
        self.on_received_solid_color: Optional[Callable[[LedArgs], None]] = None
        self.on_received_pattern: Optional[Callable[[List[PatternLine]], None]] = None
        self.on_received_wifi_config: Optional[Callable[[WifiConfigArgs], None]] = None
        self.on_received_usb_mass_storage_active: Optional[Callable[[bool], None]] = None
        self.on_received_display_brightness: Optional[Callable[[int], None]] = None
        self.on_file_list_updated: Optional[Callable[[List[FileStruct]], None]] = None
        self.on_file_upload_finished: Optional[Callable[[FileUploadFinishedArgs], None]] = None
        self.on_file_upload_progress: Optional[Callable[[UploadProgressArgs], None]] = None
        self.on_received_showing_picture: Optional[Callable[[str], None]] = None
        self.on_firmware_update_status: Optional[Callable[[float], None]] = None
        self.on_play_pattern_status: Optional[Callable[[bool], None]] = None
        self.on_writing_in_storage: Optional[Callable[[bool], None]] = None

    @property
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._serial_port is not None and self._serial_port.is_open

    async def connect(self):
        """Connect to the device"""
        try:
            self._serial_port = serial.Serial(
                port=self.port_name,
                baudrate=460800,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                timeout=4,
                write_timeout=4
            )
            self._serial_port.dtr = False
            self._serial_port.rts = True

            if self.on_connection_state_changed:
                self.on_connection_state_changed(self.is_connected)

            if not self.is_connected:
                self.disconnect()
                return

            # Start data receiving task
            asyncio.create_task(self._data_receiver_task())

            # Get device information
            await self.get_device_name_async()

            self._cached_file_dir_path = str(
                Path.home() / ".local" / "share" / "BusyTagImages"
            )
            os.makedirs(self._cached_file_dir_path, exist_ok=True)

            await self.get_manufacture_name_async()
            await self.get_device_id_async()
            await self.get_firmware_version_async()
            await self.get_hardware_version_async()
            await self.get_current_image_name_async()
            await self.get_total_storage_size_async()
            await self.get_free_storage_size_async()
            await self.get_solid_color_async()
            await self.get_display_brightness_async()

            if self.firmware_version_float < 2.0:
                await self.set_usb_mass_storage_active_async(True)
                self._busytag_drive = self._find_busytag_drive()

            if self.firmware_version_float > 0.7:
                await self.set_allowed_auto_storage_scan_async(False)

            await self.get_file_list_async()

            if self.on_received_device_basic_information:
                self.on_received_device_basic_information(True)

            # Start connection monitoring task
            self._connection_task = asyncio.create_task(self._connection_monitor_task())

        except Exception as e:
            print(f"Error: {e}")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(self.is_connected)

    async def _data_receiver_task(self):
        """Continuously read data from serial port"""
        while self.is_connected:
            try:
                if self._serial_port and self._serial_port.in_waiting > 0:
                    data = self._serial_port.read(self._serial_port.in_waiting)
                    for byte in data:
                        self._data_buffer.append(byte)
                    self._data_available_event.set()

                    # Process async events
                    text = data.decode('utf-8', errors='ignore')
                    if not self._async_command_active or text.startswith("+evn:"):
                        self._filter_response(text)

                await asyncio.sleep(0.001)
            except Exception as e:
                print(f"[ERROR] Data receiver: {e}")
                break

    async def _connection_monitor_task(self):
        """Monitor connection status"""
        while self.is_connected:
            await asyncio.sleep(3)
            if not self.is_connected:
                self.disconnect()

    def disconnect(self):
        """Disconnect from the device"""
        try:
            if self._connection_task:
                self._connection_task.cancel()

            if self._serial_port:
                self._serial_port.close()

            self._clear_buffer()

        finally:
            if self.on_connection_state_changed:
                self.on_connection_state_changed(False)
            self._serial_port = None

    def _send_raw_data(self, data: bytes, offset: int, count: int):
        """Send raw bytes to device"""
        if not self.is_connected:
            self.disconnect()
            raise ConnectionError("Not connected to device")

        print(f"Sending raw data count: {count}")
        self._serial_port.write(data[offset:offset + count])

    async def _send_command_async(
        self,
        command: str,
        timeout_ms: int = 150,
        wait_for_first_response: bool = True,
        discard_in_buffer: bool = True
    ) -> str:
        """Send AT command and wait for response"""
        if self._async_command_active or self._write_raw_data:
            return ""

        if not self.is_connected:
            self.disconnect()
            return ""

        try:
            self._async_command_active = True

            async with self._lock:
                try:
                    if discard_in_buffer:
                        self._clear_buffer()

                    if command:
                        timestamp = datetime.now()
                        print(f"[{timestamp.strftime('%H:%M:%S.%f')[:-3]}]TX:{command}")
                        self._serial_port.write((command + "\r\n").encode())

                except Exception as ex:
                    self._async_command_active = False
                    raise ConnectionError(f"Command failed: {ex}")

            # Read response from buffer
            response = []
            start_time = time.time()

            while (time.time() - start_time) * 1000 < timeout_ms:
                if len(self._data_buffer) > 0:
                    print(f"Buffer has {len(self._data_buffer)} bytes")
                    data = await self._read_string_from_buffer_async(50)
                    response.append(data)

                    response_str = ''.join(response)
                    if "OK\r\n" in response_str or "ERROR:" in response_str or ">" in response_str:
                        timestamp = datetime.now()
                        print(f"[{timestamp.strftime('%H:%M:%S.%f')[:-3]}]RX:{response_str.strip()}")
                        self._async_command_active = False
                        return response_str.strip()

                    if wait_for_first_response:
                        break

                await asyncio.sleep(0.001)

            result = ''.join(response).strip()
            timestamp = datetime.now()
            print(f"[{timestamp.strftime('%H:%M:%S.%f')[:-3]}]RX:{result}")
            self._async_command_active = False
            return result

        finally:
            self._async_command_active = False

    async def _send_bytes_async(
        self,
        data: Optional[bytes],
        timeout_ms: int = 3000,
        discard_in_buffer: bool = True
    ) -> bytes:
        """Send bytes and read binary response"""
        if self._async_command_active or self._sending_file or self._write_raw_data:
            return b''

        if not self.is_connected:
            raise ConnectionError("Not connected to device")

        try:
            self._async_command_active = True

            async with self._lock:
                try:
                    is_read_only = data is None or len(data) == 0

                    if not is_read_only:
                        if discard_in_buffer and len(self._data_buffer) > 0:
                            self._clear_buffer()

                        if data:
                            self._serial_port.write(data)

                except Exception as ex:
                    self._async_command_active = False
                    raise ConnectionError(f"Binary operation failed: {ex}")

            # Read response
            response_buffer = bytearray()
            start_time = time.time()

            while (time.time() - start_time) * 1000 < timeout_ms:
                current_bytes_to_read = len(self._data_buffer)

                if current_bytes_to_read > 0:
                    buffer = await self._read_from_buffer_async(current_bytes_to_read, 100)
                    if len(buffer) > 0:
                        response_buffer.extend(buffer)
                else:
                    await asyncio.sleep(0.001)

            self._async_command_active = False
            return bytes(response_buffer)

        finally:
            self._async_command_active = False

    async def _read_from_buffer_async(self, max_bytes: int, timeout_ms: int) -> bytes:
        """Read data from centralized buffer"""
        result = bytearray()
        start_time = time.time()

        while len(result) < max_bytes and (time.time() - start_time) * 1000 < timeout_ms:
            if len(self._data_buffer) > 0:
                result.append(self._data_buffer.popleft())
            else:
                try:
                    await asyncio.wait_for(
                        self._data_available_event.wait(),
                        timeout=0.01
                    )
                    self._data_available_event.clear()
                except asyncio.TimeoutError:
                    pass

        return bytes(result)

    async def _read_string_from_buffer_async(self, timeout_ms: int) -> str:
        """Read string data from buffer"""
        data = await self._read_from_buffer_async(1024 * 8, timeout_ms)
        return data.decode('utf-8', errors='ignore')

    def _clear_buffer(self):
        """Clear the centralized buffer"""
        self._data_buffer.clear()
        self._data_available_event.clear()

    def _get_buffer_count(self) -> int:
        """Get number of bytes in buffer"""
        return len(self._data_buffer)

    def _filter_response(self, data: str):
        """Filter and process async responses"""
        timestamp = datetime.now()
        print(f"FilterResponse [{timestamp.strftime('%H:%M:%S.%f')[:-3]}]RX:{data}")

        lines = data.split('\r\n')
        for line in lines:
            if len(line) > 1 and line[0] == '+':
                parts = line.split(':', 1)
                if len(parts) > 1:
                    if parts[0] == "+evn":
                        self._skip_checking = True
                        args = parts[1].split(',')
                        if len(args) >= 2:
                            if args[0] == "SP":
                                self.current_image_name = args[1].strip()
                                if not self._file_exists_in_cache(self.current_image_name):
                                    asyncio.create_task(self.get_file_async(self.current_image_name))
                                if self.on_received_showing_picture:
                                    self.on_received_showing_picture(self.current_image_name)
                            elif args[0] == "FU":
                                progress = float(args[1].rstrip('%'))
                                if self.on_firmware_update_status:
                                    self.on_firmware_update_status(progress)
                            elif args[0] == "PP":
                                self._is_playing_pattern = int(args[1]) != 0
                                if self.on_play_pattern_status:
                                    self.on_play_pattern_status(self._is_playing_pattern)
                            elif args[0] == "WIS":
                                is_writing = args[1].strip() != "0"
                                if not is_writing:
                                    time.sleep(0.1)
                                if self.on_writing_in_storage:
                                    self.on_writing_in_storage(is_writing)
            elif line == "OK":
                pass
            elif "ERROR" in line:
                if self._sending_file:
                    error_message = line.split(':')[-1].strip() if ':' in line else "Unknown device error"
                    self._cancel_file_upload(
                        False,
                        UploadErrorType.DEVICE_ERROR,
                        f"Device reported error: {error_message}"
                    )

    # Device information commands
    async def get_device_name_async(self) -> str:
        """Get device name"""
        response = await self._send_command_async("AT+GDN")
        self.device_name = response.split(':')[-1] if "+DN:busytag-" in response else "busytag"
        self.local_host_address = f"http://{self.device_name}.local"
        return self.device_name

    async def get_manufacture_name_async(self) -> str:
        """Get manufacturer name"""
        response = await self._send_command_async("AT+GMN")
        self.manufacture_name = response.split(':')[-1] if "+MN:" in response else "BUSY TAG SIA"
        return self.manufacture_name

    async def get_device_id_async(self) -> str:
        """Get device ID"""
        response = await self._send_command_async("AT+GID")
        self.id = response.split(':')[-1] if "+ID:" in response else ""
        return self.id

    async def get_firmware_version_async(self) -> str:
        """Get firmware version"""
        response = await self._send_command_async("AT+GFV")
        self.firmware_version = response.split(':')[-1] if "+FV:" in response else ""
        try:
            self.firmware_version_float = float(self.firmware_version)
        except ValueError:
            self.firmware_version_float = 0.0
        return self.firmware_version

    async def get_hardware_version_async(self) -> str:
        """Get hardware version"""
        response = await self._send_command_async("AT+GHV")
        self.hardware_version = response.split(':')[-1] if "+HV:" in response else "1.0"
        return self.hardware_version

    async def get_current_image_name_async(self) -> str:
        """Get current displayed image name"""
        response = await self._send_command_async("AT+SP?")
        self.current_image_name = response.split(':')[-1] if "+SP:" in response else ""
        if self.current_image_name and not self._file_exists_in_cache(self.current_image_name):
            await self.get_file_async(self.current_image_name)
        if self.on_received_showing_picture:
            self.on_received_showing_picture(self.current_image_name)
        return self.current_image_name

    async def get_free_storage_size_async(self) -> int:
        """Get free storage size"""
        if self.firmware_version_float >= 2.0:
            response = await self._send_command_async("AT+GFSS", 200)
            size = response.split(':')[-1] if "+FSS:" in response else "0"
            self.free_storage_size = int(size)
        else:
            self.free_storage_size = self._busytag_drive.stat().st_blocks * 512 if self._busytag_drive else 0

        return self.free_storage_size

    async def get_total_storage_size_async(self) -> int:
        """Get total storage size"""
        if self.firmware_version_float >= 2.0:
            response = await self._send_command_async("AT+GTSS")
            size = response.split(':')[-1] if "+TSS:" in response else "0"
            self.total_storage_size = int(size)
        else:
            if self._busytag_drive:
                stat = self._busytag_drive.stat()
                self.total_storage_size = stat.st_blocks * 512

        return self.total_storage_size

    async def get_file_list_async(self) -> List[FileStruct]:
        """Get list of files on device"""
        self.file_list = []
        if self.firmware_version_float >= 2.0:
            response = await self._send_command_async("AT+GFL", 500, False)
            self.file_list = self._parse_file_list(response, "+FL:")
        else:
            if not self._busytag_drive:
                self._busytag_drive = self._find_busytag_drive()
            if self._busytag_drive:
                try:
                    for file_path in self._busytag_drive.iterdir():
                        if file_path.is_file():
                            self.file_list.append(FileStruct(file_path.name, file_path.stat().st_size))
                except Exception as e:
                    print(e)

        if self.on_file_list_updated:
            self.on_file_list_updated(self.file_list)

        return self.file_list

    async def get_solid_color_async(self) -> LedArgs:
        """Get current solid color"""
        response = await self._send_command_async("AT+SC?")
        solid_color = self._parse_solid_color(response)
        if self.on_received_solid_color:
            self.on_received_solid_color(solid_color)
        return solid_color

    async def get_display_brightness_async(self) -> int:
        """Get display brightness"""
        response = await self._send_command_async("AT+DB?")
        brightness_str = response.split(':')[-1] if "+DB:" in response else "100"
        brightness = int(brightness_str)
        if self.on_received_display_brightness:
            self.on_received_display_brightness(brightness)
        return brightness

    # Device control commands
    async def set_display_brightness_async(self, brightness: int) -> bool:
        """Set display brightness (0-100)"""
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be between 0 and 100")

        response = await self._send_command_async(f"AT+DB={brightness}")
        return "OK" in response

    async def set_usb_mass_storage_active_async(self, active: bool) -> bool:
        """Set USB mass storage active"""
        response = await self._send_command_async(f"AT+UMSA={1 if active else 0}")
        return "OK" in response

    async def set_allowed_auto_storage_scan_async(self, allowed: bool) -> bool:
        """Set allowed auto storage scan"""
        response = await self._send_command_async(f"AT+AASS={1 if allowed else 0}")
        return "OK" in response

    async def show_picture_async(self, file_name: str) -> bool:
        """Show a picture on the device"""
        response = await self._send_command_async(f"AT+SP={file_name}", 300)
        if "+evn:SP," in response:
            self.current_image_name = file_name
            if self.current_image_name and not self._file_exists_in_cache(self.current_image_name):
                await self.get_file_async(self.current_image_name)

            if self.on_received_showing_picture:
                self.on_received_showing_picture(self.current_image_name)
            return True

        return "OK" in response

    async def restart_device_async(self) -> bool:
        """Restart the device"""
        response = await self._send_command_async("AT+RST")
        return "OK" in response

    async def format_disk_async(self) -> bool:
        """Format the device disk"""
        response = await self._send_command_async("AT+FD", 2000)
        return "OK" in response

    async def play_pattern_async(self, allow: bool, repeat_count: int) -> bool:
        """Play LED pattern"""
        response = await self._send_command_async(f"AT+PP={1 if allow else 0},{repeat_count}", 60, False)
        if "+PP:" in response:
            value = response.split(':')[-1]
            if self.on_play_pattern_status:
                self.on_play_pattern_status(int(value) != 0)

        return "OK" in response

    async def set_solid_color_async(self, color: str, brightness: int = 100, led_bits: int = 127) -> bool:
        """Set solid LED color"""
        bright = int(brightness * 2.55)

        color_map = {
            "off": (0, 0, 0),
            "red": (bright, 0, 0),
            "green": (0, bright, 0),
            "blue": (0, 0, bright),
            "yellow": (bright, bright, 0),
            "cyan": (0, bright, bright),
            "magenta": (bright, 0, bright),
            "white": (bright, bright, bright),
        }

        rgb = color_map.get(color, (0, 0, 0))
        return await self.send_rgb_color_async(*rgb, led_bits)

    async def send_rgb_color_async(self, red: int = 0, green: int = 0, blue: int = 0, led_bits: int = 127) -> bool:
        """Send RGB color to device"""
        response = await self._send_command_async(
            f"AT+SC={led_bits},{red:02X}{green:02X}{blue:02X}",
            wait_for_first_response=False
        )
        if "OK" in response:
            if self.on_received_solid_color:
                self.on_received_solid_color(LedArgs(led_bits, f"{red:02X}{green:02X}{blue:02X}"))
            return True

        return False

    async def send_custom_command_async(
        self,
        command: str,
        timeout_ms: int = 150,
        wait_for_first_response: bool = True,
        discard_in_buffer: bool = True
    ) -> str:
        """Send custom AT command"""
        return await self._send_command_async(command, timeout_ms, wait_for_first_response, discard_in_buffer)

    # File operations
    async def send_new_file(self, source_path: str):
        """Upload a new file to the device"""
        file_name = os.path.basename(source_path)

        # Save in cache
        dest_file_path = os.path.join(self._cached_file_dir_path, file_name)
        import shutil
        shutil.copy(source_path, dest_file_path)

        self._sending_file = True

        args = UploadProgressArgs(file_name, 0.0)
        if self.on_file_upload_progress:
            self.on_file_upload_progress(args)

        if len(file_name) > self.MAX_FILENAME_LENGTH:
            self._cancel_file_upload(
                False,
                UploadErrorType.FILENAME_TOO_LONG,
                f"Filename '{file_name}' exceeds maximum length of {self.MAX_FILENAME_LENGTH}"
            )
            return

        self._file_sending_cancelled = False

        if self.firmware_version_float >= 2.0:
            try:
                success = await self._send_file_via_serial(source_path)
                self._sending_file = False

                if success:
                    self.file_list.append(FileStruct(file_name, os.path.getsize(source_path)))
                    self._cancel_file_upload(True)
            except Exception as ex:
                self._sending_file = False
                self._cancel_file_upload(
                    False,
                    UploadErrorType.UNKNOWN,
                    f"Unexpected error during file upload: {ex}"
                )
            return

        # Old firmware version - USB mass storage
        if not self._busytag_drive:
            self._busytag_drive = self._find_busytag_drive()

        if not self._busytag_drive:
            self._cancel_file_upload(
                False,
                UploadErrorType.DEVICE_ERROR,
                "Cannot find BusyTag drive for file transfer"
            )
            return

        # Implementation for older firmware...
        # (simplified for brevity)

    async def _send_file_via_serial(self, source_path: str) -> bool:
        """Send file via serial (firmware >= 2.0)"""
        file_name = os.path.basename(source_path)
        args = UploadProgressArgs(file_name, 0.0)

        try:
            file_size = os.path.getsize(source_path)
            is_free_space = await self._free_up_storage(file_size)

            if not is_free_space:
                self._cancel_file_upload(
                    False,
                    UploadErrorType.INSUFFICIENT_STORAGE,
                    "Insufficient storage space on device"
                )
                return False

            with open(source_path, 'rb') as f:
                data = f.read()

            chunk_size = 1024 * 8
            total_bytes_transferred = 0.0

            response = await self._send_command_async(f"AT+UF={file_name},{file_size}", 1000)
            if ">" not in response:
                self._cancel_file_upload(
                    False,
                    UploadErrorType.DEVICE_ERROR,
                    "Device did not respond properly to upload command"
                )
                return False

            self._write_raw_data = True

            for i in range(0, len(data), chunk_size):
                if self._file_sending_cancelled:
                    self._cancel_file_upload(
                        False,
                        UploadErrorType.CANCELLED,
                        "File upload was cancelled by user"
                    )
                    return False

                remaining_bytes = len(data) - i
                current_chunk_size = min(chunk_size, remaining_bytes)
                chunk_data = data[i:i + current_chunk_size]

                if not self.is_connected:
                    self.disconnect()
                    self._cancel_file_upload(
                        False,
                        UploadErrorType.CONNECTION_LOST,
                        "Connection to device was lost during upload"
                    )
                    return False

                try:
                    self._send_raw_data(chunk_data, 0, len(chunk_data))
                    total_bytes_transferred += len(chunk_data)

                    progress_level = (total_bytes_transferred / len(data)) * 100.0
                    args.progress_level = progress_level
                    if self.on_file_upload_progress:
                        self.on_file_upload_progress(args)

                except Exception as ex:
                    print(f"Error sending chunk: {ex}")
                    self._cancel_file_upload(
                        False,
                        UploadErrorType.TRANSFER_INTERRUPTED,
                        f"Data transfer failed: {ex}"
                    )
                    return False

            self._write_raw_data = False

            args.progress_level = 100.0
            if self.on_file_upload_progress:
                self.on_file_upload_progress(args)

            response = await self._send_command_async("", 1500, discard_in_buffer=False)
            if "OK" in response:
                return True
            else:
                self._cancel_file_upload(
                    False,
                    UploadErrorType.DEVICE_ERROR,
                    "Device did not confirm successful upload"
                )
                return False

        except Exception as ex:
            self._cancel_file_upload(
                False,
                UploadErrorType.UNKNOWN,
                f"Upload failed with exception: {ex}"
            )
            return False

    def _cancel_file_upload(
        self,
        successful: bool = True,
        error_type: UploadErrorType = UploadErrorType.NONE,
        error_message: Optional[str] = None
    ):
        """Cancel file upload"""
        self._file_sending_cancelled = True

        args = FileUploadFinishedArgs(
            success=successful,
            file_name=self._current_upload_filename,
            error_type=error_type,
            error_message=error_message
        )

        self._sending_file = False

        if self.on_file_upload_finished:
            self.on_file_upload_finished(args)

        self._current_upload_filename = ""

    async def delete_file(self, file_name: str) -> bool:
        """Delete a file from device"""
        if self.firmware_version_float >= 2.0:
            response = await self._send_command_async(f"AT+DF={file_name}", 300)
            if "OK" not in response:
                print(f"Error deleting file: {file_name}")
            await self.get_free_storage_size_async()
        else:
            if not self._busytag_drive:
                self._busytag_drive = self._find_busytag_drive()
            if not self._busytag_drive:
                return False

            path = self._busytag_drive / file_name
            try:
                path.unlink()
            except Exception:
                return False

        await self.get_file_list_async()
        return True

    async def get_file_async(self, file_name: str) -> str:
        """Download a file from device to cache"""
        dest_file_path = os.path.join(self._cached_file_dir_path, file_name)

        if self.firmware_version_float >= 2.0:
            # Implementation for downloading via serial
            # (simplified for brevity - see C# version for full implementation)
            pass
        else:
            if not self._busytag_drive:
                self._busytag_drive = self._find_busytag_drive()
            if not self._busytag_drive:
                return ""

            source_file_path = self._busytag_drive / file_name
            import shutil
            shutil.copy(source_file_path, dest_file_path)

        return dest_file_path

    def _file_exists_in_cache(self, file_name: str) -> bool:
        """Check if file exists in cache"""
        if not file_name:
            return False
        file_path = os.path.join(self._cached_file_dir_path, file_name)
        return os.path.exists(file_path)

    async def _free_up_storage(self, size: int) -> bool:
        """Free up storage space by deleting old files"""
        if self.firmware_version_float >= 2.0:
            counter = 0
            await self.get_free_storage_size_async()

            while self.free_storage_size < size:
                if not await self._auto_delete_file():
                    return False
                await self.get_free_storage_size_async()
                counter += 1
                if counter >= 20:
                    return False
        # Similar logic for older firmware...

        return True

    async def _auto_delete_file(self) -> bool:
        """Automatically delete old file"""
        for item in self.file_list:
            if self.current_image_name == item.name:
                continue
            if item.name.endswith(('.png', '.jpg', '.gif')):
                return await self.delete_file(item.name)
        return False

    def _find_busytag_drive(self) -> Optional[Path]:
        """Find BusyTag USB drive"""
        # Platform-specific implementation to find mounted drive
        # (simplified - see C# version for full implementation)
        return None

    @staticmethod
    def _parse_file_list(response: str, prefix: str) -> List[FileStruct]:
        """Parse file list response"""
        files = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith(prefix):
                data = line[len(prefix):]
                parts = data.split(',')

                if len(parts) >= 2:
                    name = parts[0]
                    try:
                        size = int(parts[-1])
                        files.append(FileStruct(name, size))
                    except ValueError:
                        pass

        return files

    @staticmethod
    def _parse_solid_color(response: str) -> LedArgs:
        """Parse solid color response"""
        value = response.split(':')[-1] if "+SC:" in response else ""
        parts = value.split(',')

        if len(parts) >= 2:
            try:
                led_bits = int(parts[0])
                color_hex = parts[1]
                return LedArgs(led_bits, color_hex)
            except ValueError:
                pass

        return LedArgs(127, "990000")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
