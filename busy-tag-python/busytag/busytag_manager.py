"""BusyTag device manager for discovering and managing devices"""

import asyncio
import platform
import subprocess
import re
from typing import List, Optional, Callable
import serial.tools.list_ports
from threading import Lock, Timer


class BusyTagManager:
    """Manager for discovering and tracking BusyTag devices"""

    # VID:PID for BusyTag devices
    TARGET_VID = "303A"
    TARGET_PID = "81DF"

    def __init__(self):
        self._busytag_serial_devices: List[str] = []
        self._previous_busytag_serial_devices: List[str] = []
        self._is_scanning_for_devices = False
        self._periodic_search_timer: Optional[Timer] = None
        self._is_periodic_search_enabled = False
        self._lock = Lock()
        self._disposed = False

        # Callbacks
        self.on_found_devices: Optional[Callable[[List[str]], None]] = None
        self.on_device_connected: Optional[Callable[[str], None]] = None
        self.on_device_disconnected: Optional[Callable[[str], None]] = None

        # Configuration
        self.enable_verbose_logging = False
        self.enable_experimental_linux_support = False

    def all_serial_ports(self) -> List[str]:
        """Get all available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start_periodic_device_search(self, interval_ms: int = 5000):
        """Start periodic device searching"""
        with self._lock:
            if self._is_periodic_search_enabled:
                return

            self._is_periodic_search_enabled = True
            self._schedule_periodic_search(interval_ms)

    def stop_periodic_device_search(self):
        """Stop periodic device searching"""
        with self._lock:
            self._is_periodic_search_enabled = False
            if self._periodic_search_timer:
                self._periodic_search_timer.cancel()
                self._periodic_search_timer = None

    def _schedule_periodic_search(self, interval_ms: int):
        """Schedule the next periodic search"""
        if not self._is_periodic_search_enabled:
            return

        async def search_task():
            try:
                await self.find_busytag_device()
            except Exception as e:
                if self.enable_verbose_logging:
                    print(f"[DEBUG] Periodic search error: {e}")
            finally:
                if self._is_periodic_search_enabled:
                    self._periodic_search_timer = Timer(
                        interval_ms / 1000.0,
                        lambda: asyncio.run(search_task())
                    )
                    self._periodic_search_timer.start()

        asyncio.run(search_task())

    async def find_busytag_device(self) -> Optional[List[str]]:
        """Find BusyTag devices based on the current platform"""
        if self._is_scanning_for_devices:
            return None

        self._is_scanning_for_devices = True

        try:
            system = platform.system()

            if system == "Windows":
                return await self._discover_by_vid_pid_windows()
            elif system == "Darwin":  # macOS
                return await self._discover_by_vid_pid_macos()
            elif system == "Linux":
                if self.enable_experimental_linux_support:
                    if self.enable_verbose_logging:
                        print("[WARNING] Linux support is experimental and not fully tested")
                    return await self._discover_by_vid_pid_linux()
                else:
                    if self.enable_verbose_logging:
                        print("[INFO] Linux platform detected but support is disabled. "
                              "Set enable_experimental_linux_support = True to enable.")
        except Exception as e:
            if self.enable_verbose_logging:
                print(f"[DEBUG] Device discovery error: {e}")
        finally:
            self._is_scanning_for_devices = False

        return None

    def _check_for_device_changes(self):
        """Check for newly connected or disconnected devices"""
        with self._lock:
            if self._busytag_serial_devices is None or self._previous_busytag_serial_devices is None:
                self._previous_busytag_serial_devices = self._busytag_serial_devices.copy() if self._busytag_serial_devices else []
                return

            # Check for newly connected devices
            new_devices = set(self._busytag_serial_devices) - set(self._previous_busytag_serial_devices)
            for device in new_devices:
                if self.on_device_connected:
                    self.on_device_connected(device)

            # Check for disconnected devices
            disconnected_devices = set(self._previous_busytag_serial_devices) - set(self._busytag_serial_devices)
            for device in disconnected_devices:
                if self.on_device_disconnected:
                    self.on_device_disconnected(device)

            self._previous_busytag_serial_devices = self._busytag_serial_devices.copy()

    async def _discover_by_vid_pid_windows(self) -> Optional[List[str]]:
        """Discover devices on Windows using WMI"""
        try:
            import wmi

            device_id = f"VID_{self.TARGET_VID}&PID_{self.TARGET_PID}"
            found_devices = []

            c = wmi.WMI()
            for device in c.Win32_PnPEntity():
                device_id_str = device.DeviceID
                if device_id_str and device_id in device_id_str:
                    name = device.Name
                    if name and "COM" in name:
                        match = re.search(r'COM(\d+)', name)
                        if match:
                            port = f"COM{match.group(1)}"
                            found_devices.append(port)

            with self._lock:
                self._busytag_serial_devices = found_devices
                self._check_for_device_changes()

            self._is_scanning_for_devices = False
            if self.on_found_devices:
                self.on_found_devices(self._busytag_serial_devices)

            return self._busytag_serial_devices

        except ImportError:
            if self.enable_verbose_logging:
                print("[DEBUG] WMI not available, falling back to AT command testing")
            return await self._find_device_by_at_command()
        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] Windows VID/PID discovery failed: {ex}")
            self._is_scanning_for_devices = False
            return None

    async def _discover_by_vid_pid_macos(self) -> Optional[List[str]]:
        """Discover devices on macOS using ioreg"""
        try:
            # Get USB device information using ioreg
            usb_devices = await self._get_macos_usb_devices()

            key = f"{self.TARGET_VID}:{self.TARGET_PID}"
            if key in usb_devices:
                # Found the device, now find associated serial port
                return await self._find_macos_serial_port()
            else:
                # Device not found, clear the list
                with self._lock:
                    self._busytag_serial_devices = []
                    self._check_for_device_changes()

                self._is_scanning_for_devices = False
                if self.on_found_devices:
                    self.on_found_devices(self._busytag_serial_devices)

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] macOS VID/PID discovery failed: {ex}")
            self._is_scanning_for_devices = False

        return None

    async def _get_macos_usb_devices(self) -> dict:
        """Get USB devices on macOS using ioreg"""
        devices = {}

        try:
            process = await asyncio.create_subprocess_exec(
                "ioreg", "-c", "IOUSBHostDevice", "-r",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            output = stdout.decode()

            lines = output.split('\n')
            current_device = {}

            for line in lines:
                # Start of a new device block
                if "class IOUSBHostDevice" in line:
                    if current_device:
                        devices[f"{current_device.get('vid', '')}:{current_device.get('pid', '')}"] = current_device
                    current_device = {}
                elif '"idVendor"' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        vendor_id_str = parts[1].strip()
                        try:
                            vendor_id = int(vendor_id_str)
                            current_device['vid'] = f"{vendor_id:04X}"
                        except ValueError:
                            pass
                elif '"idProduct"' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        product_id_str = parts[1].strip()
                        try:
                            product_id = int(product_id_str)
                            current_device['pid'] = f"{product_id:04X}"
                        except ValueError:
                            pass

            # Don't forget the last device
            if current_device:
                devices[f"{current_device.get('vid', '')}:{current_device.get('pid', '')}"] = current_device

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] Failed to get macOS USB devices: {ex}")

        return devices

    async def _find_macos_serial_port(self) -> Optional[List[str]]:
        """Find serial ports on macOS"""
        found_devices = []

        try:
            # Since we've already confirmed the USB device exists via VID/PID,
            # just return the USB modem ports that match our device pattern
            ports = serial.tools.list_ports.comports()

            usb_ports = [port.device for port in ports if port.device.startswith("/dev/cu.usbmodem")]
            found_devices.extend(usb_ports)

            with self._lock:
                self._busytag_serial_devices = found_devices
                self._check_for_device_changes()

            self._is_scanning_for_devices = False
            if self.on_found_devices:
                self.on_found_devices(self._busytag_serial_devices)

            return self._busytag_serial_devices

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] macOS serial port discovery failed: {ex}")
            self._is_scanning_for_devices = False

        return None

    async def _discover_by_vid_pid_linux(self) -> Optional[List[str]]:
        """Discover devices on Linux using lsusb (experimental)"""
        try:
            process = await asyncio.create_subprocess_exec(
                "lsusb",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            output = stdout.decode()

            if f"{self.TARGET_VID}:{self.TARGET_PID}" in output:
                # Device found, look for an associated tty device
                return await self._find_linux_serial_port()
            else:
                # Device not found, clear the list
                with self._lock:
                    self._busytag_serial_devices = []
                    self._check_for_device_changes()

                self._is_scanning_for_devices = False
                if self.on_found_devices:
                    self.on_found_devices(self._busytag_serial_devices)

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] Linux VID/PID discovery failed: {ex}")
            self._is_scanning_for_devices = False

        return None

    async def _find_linux_serial_port(self) -> Optional[List[str]]:
        """Find serial ports on Linux"""
        found_devices = []

        try:
            ports = serial.tools.list_ports.comports()

            # Filter for USB serial devices
            usb_ports = [port.device for port in ports
                        if port.device.startswith("/dev/ttyUSB") or port.device.startswith("/dev/ttyACM")]

            for port_name in usb_ports:
                try:
                    import serial
                    test_port = serial.Serial(port_name, 460800, timeout=2, write_timeout=2)
                    test_port.write(b"AT+GDN\r\n")
                    await asyncio.sleep(0.1)

                    if test_port.in_waiting > 0:
                        response = test_port.read(test_port.in_waiting).decode('utf-8', errors='ignore')
                        if "+DN:busytag-" in response:
                            if self.enable_verbose_logging:
                                print(f"[INFO] Found BusyTag device on {port_name} via Linux discovery")
                            found_devices.append(port_name)

                    test_port.close()
                except:
                    continue

            with self._lock:
                self._busytag_serial_devices = found_devices
                self._check_for_device_changes()

            self._is_scanning_for_devices = False
            if self.on_found_devices:
                self.on_found_devices(self._busytag_serial_devices)

            return self._busytag_serial_devices

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] Linux serial port discovery failed: {ex}")
            self._is_scanning_for_devices = False

        return None

    async def _find_device_by_at_command(self) -> Optional[List[str]]:
        """Fallback method: find devices by sending AT commands to all ports"""
        found_devices = []

        try:
            import serial
            ports = serial.tools.list_ports.comports()

            for port_info in ports:
                port_name = port_info.device
                try:
                    test_port = serial.Serial(port_name, 460800, timeout=2, write_timeout=2)
                    test_port.write(b"AT+GDN\r\n")
                    await asyncio.sleep(0.1)

                    if test_port.in_waiting > 0:
                        response = test_port.read(test_port.in_waiting).decode('utf-8', errors='ignore')
                        if "+DN:busytag-" in response:
                            if self.enable_verbose_logging:
                                print(f"[INFO] Found BusyTag device on {port_name} via AT command")
                            found_devices.append(port_name)

                    test_port.close()
                except:
                    continue

            with self._lock:
                self._busytag_serial_devices = found_devices
                self._check_for_device_changes()

            self._is_scanning_for_devices = False
            if self.on_found_devices:
                self.on_found_devices(self._busytag_serial_devices)

            return self._busytag_serial_devices

        except Exception as ex:
            if self.enable_verbose_logging:
                print(f"[DEBUG] AT command discovery failed: {ex}")
            self._is_scanning_for_devices = False

        return None

    def dispose(self):
        """Clean up resources"""
        if self._disposed:
            return

        self.stop_periodic_device_search()
        self._disposed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    def __del__(self):
        self.dispose()
