"""Cloud client for BusyTag device communication"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import httpx


@dataclass
class CloudCommandResponse:
    """Response from cloud command"""
    success: bool = False
    command_id: str = ""
    status: str = ""
    error_message: Optional[str] = None


@dataclass
class CloudCommandStatus:
    """Status of a cloud command"""
    command_id: str = ""
    device_id: str = ""
    command: str = ""
    status: str = ""
    response: Optional[str] = None
    success: Optional[bool] = None
    created_at: str = ""
    sent_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class CloudTestResult:
    """Result from cloud connection test"""
    success: bool = False
    message: str = ""
    details: Optional[str] = None
    command_id: Optional[str] = None
    response: Optional[str] = None


@dataclass
class DeviceStatus:
    """Device status from cloud"""
    id: Optional[int] = None
    device_id: str = ""
    device_name: Optional[str] = None
    firmware_version: Optional[str] = None
    last_seen: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[str] = None
    online: bool = False
    wifi_connected: Optional[bool] = None
    image_count: Optional[int] = None
    active_image: Optional[str] = None
    active_image_url: Optional[str] = None
    pending_commands: Optional[int] = None
    completed_commands: Optional[int] = None
    event_count: Optional[int] = None


@dataclass
class LatestImageInfo:
    """Latest image information"""
    filename: str = ""
    url: str = ""
    hash: str = ""
    timestamp: int = 0
    size: int = 0


@dataclass
class CloudImageUploadResponse:
    """Response from image upload"""
    success: bool = False
    file_name: Optional[str] = None
    hash: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None


class BusyTagCloudClient:
    """Client for communicating with BusyTag Cloud Server API"""

    def __init__(self, base_url: str, device_id: str):
        self._base_url = base_url.rstrip('/')
        self._device_id = device_id
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"X-Device-Key": device_id}
        )

    async def queue_command_async(self, command: str, priority: int = 1) -> CloudCommandResponse:
        """Queue a command for the device to execute"""
        try:
            print(f"[Cloud] Queuing command: {command} (priority: {priority})")
            print(f"[Cloud] URL: {self._base_url}/device/{self._device_id}/commands")

            request_body = {
                "command": command,
                "priority": priority
            }

            response = await self._client.post(
                f"{self._base_url}/device/{self._device_id}/commands",
                json=request_body
            )

            print(f"[Cloud] Queue command response: {response.status_code}")

            if response.status_code != 200:
                error_content = response.text
                print(f"[Cloud] Queue command failed: {error_content}")

                return CloudCommandResponse(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {error_content}"
                )

            result = response.json()
            print(f"[Cloud] Command queued successfully: {result.get('command_id')}")

            return CloudCommandResponse(
                success=True,
                command_id=result.get("command_id", ""),
                status=result.get("status", "unknown")
            )

        except Exception as ex:
            print(f"[Cloud] Queue command exception: {type(ex).__name__}: {ex}")
            return CloudCommandResponse(
                success=False,
                error_message=f"Failed to queue command: {ex}"
            )

    async def get_command_status_async(self, command_id: str) -> Optional[CloudCommandStatus]:
        """Get the status of a queued command"""
        try:
            url = f"{self._base_url}/commands/{command_id}"
            print(f"[Cloud] GET {url}")

            response = await self._client.get(url)

            print(f"[Cloud] Response: {response.status_code}")

            if response.status_code != 200:
                error_content = response.text
                print(f"[Cloud] Error: {error_content}")
                return None

            content = response.json()
            print(f"[Cloud] Response body: {content}")

            # Handle bool/int conversion for success field
            success_value = content.get("success")
            if isinstance(success_value, int):
                success_value = success_value != 0
            elif isinstance(success_value, str):
                success_value = success_value == "1" or success_value.lower() == "true"

            status = CloudCommandStatus(
                command_id=content.get("command_id", ""),
                device_id=content.get("device_id", ""),
                command=content.get("command", ""),
                status=content.get("status", ""),
                response=content.get("response"),
                success=success_value,
                created_at=content.get("created_at", ""),
                sent_at=content.get("sent_at"),
                completed_at=content.get("completed_at")
            )

            print(f"[Cloud] Parsed: Status={status.status}, Success={status.success}")

            return status

        except Exception as ex:
            print(f"[Cloud] GetCommandStatus exception: {ex}")
            return None

    async def wait_for_command_completion_async(
        self,
        command_id: str,
        timeout_seconds: float,
        poll_interval_seconds: float = 2.0
    ) -> Optional[CloudCommandStatus]:
        """Wait for a command to complete and return its response"""
        end_time = datetime.now().timestamp() + timeout_seconds
        check_count = 0

        print(f"[Cloud] Waiting for command completion: {command_id}")
        print(f"[Cloud] Timeout: {timeout_seconds}s, Poll interval: {poll_interval_seconds}s")

        while datetime.now().timestamp() < end_time:
            check_count += 1
            status = await self.get_command_status_async(command_id)

            if status:
                print(f"[Cloud] Check #{check_count}: Status={status.status}, Success={status.success}")

                if status.status in ("completed", "failed"):
                    print(f"[Cloud] Command finished: {status.status}")
                    return status
            else:
                print(f"[Cloud] Check #{check_count}: No status returned")

            await asyncio.sleep(poll_interval_seconds)

        print(f"[Cloud] Command timed out after {check_count} checks")
        return None

    async def wait_for_device_online_async(
        self,
        timeout_seconds: float,
        poll_interval_seconds: float = 3.0
    ) -> bool:
        """Check if device is online by querying device status"""
        end_time = datetime.now().timestamp() + timeout_seconds

        while datetime.now().timestamp() < end_time:
            try:
                status = await self.get_device_status_async()

                if status and status.online:
                    return True
            except:
                pass

            await asyncio.sleep(poll_interval_seconds)

        return False

    async def test_cloud_connection_async(
        self,
        timeout_seconds: float = 45,
        wait_for_online: bool = True
    ) -> CloudTestResult:
        """Test cloud connectivity by sending a simple command and waiting for response"""
        try:
            # First, wait for device to come online if requested
            if wait_for_online:
                online_timeout = min(30, timeout_seconds / 2)
                is_online = await self.wait_for_device_online_async(online_timeout)

                if not is_online:
                    return CloudTestResult(
                        success=False,
                        message="Device did not connect to cloud",
                        details=f"Device not online after {online_timeout} seconds"
                    )

            # Queue a simple test command
            queue_result = await self.queue_command_async("AT+GDN", priority=10)

            if not queue_result.success:
                return CloudTestResult(
                    success=False,
                    message="Failed to queue test command",
                    details=queue_result.error_message
                )

            # Wait for the device to execute the command
            remaining_timeout = timeout_seconds - (30 if wait_for_online else 0)
            if remaining_timeout < 30:
                remaining_timeout = 30

            print(f"[Cloud] Waiting up to {remaining_timeout}s for device to execute command")

            command_status = await self.wait_for_command_completion_async(
                queue_result.command_id,
                remaining_timeout,
                3.0
            )

            if not command_status:
                return CloudTestResult(
                    success=False,
                    message="Device did not respond within timeout period",
                    details="Command queued but not executed. Device might not be polling for commands.",
                    command_id=queue_result.command_id
                )

            if command_status.status == "completed" and command_status.success:
                return CloudTestResult(
                    success=True,
                    message="Cloud connection successful!",
                    details=f"Device responded: {command_status.response}",
                    command_id=queue_result.command_id,
                    response=command_status.response
                )
            else:
                return CloudTestResult(
                    success=False,
                    message="Device responded but command failed",
                    details=command_status.response or "No response",
                    command_id=queue_result.command_id
                )

        except Exception as ex:
            return CloudTestResult(
                success=False,
                message="Cloud connection test failed",
                details=str(ex)
            )

    async def register_device_async(
        self,
        device_name: str = "",
        firmware_version: str = ""
    ) -> bool:
        """Register device with cloud server"""
        try:
            print(f"[Cloud] Registering device: {self._device_id}")
            print(f"[Cloud] URL: {self._base_url}/device/{self._device_id}/register")
            print(f"[Cloud] Device Name: {device_name}, Firmware: {firmware_version}")

            request_body = {
                "device_name": device_name,
                "firmware_version": firmware_version
            }

            response = await self._client.post(
                f"{self._base_url}/device/{self._device_id}/register",
                json=request_body
            )

            print(f"[Cloud] Registration response: {response.status_code}")

            if response.status_code == 200:
                response_content = response.text
                print(f"[Cloud] Registration success: {response_content}")
            else:
                error_content = response.text
                print(f"[Cloud] Registration failed: {error_content}")

            return response.status_code == 200

        except Exception as ex:
            print(f"[Cloud] Registration exception: {type(ex).__name__}: {ex}")
            return False

    async def get_device_status_async(self) -> Optional[DeviceStatus]:
        """Check device status on cloud"""
        try:
            response = await self._client.get(f"{self._base_url}/device/{self._device_id}/status")

            if response.status_code != 200:
                return None

            data = response.json()

            # Handle bool/int conversions
            online_value = data.get("online")
            if isinstance(online_value, int):
                online_value = online_value != 0

            wifi_connected_value = data.get("wifi_connected")
            if isinstance(wifi_connected_value, int):
                wifi_connected_value = wifi_connected_value != 0

            status = DeviceStatus(
                id=data.get("id"),
                device_id=data.get("device_id", ""),
                device_name=data.get("device_name"),
                firmware_version=data.get("firmware_version"),
                last_seen=data.get("last_seen"),
                ip_address=data.get("ip_address"),
                created_at=data.get("created_at"),
                online=online_value or False,
                wifi_connected=wifi_connected_value,
                image_count=data.get("image_count"),
                active_image=data.get("active_image"),
                pending_commands=data.get("pending_commands"),
                completed_commands=data.get("completed_commands"),
                event_count=data.get("event_count")
            )

            # Add full image URL if active_image exists
            if status.active_image:
                status.active_image_url = f"{self._base_url}/uploads/{self._device_id}/{status.active_image}"

            return status

        except:
            return None

    async def get_latest_image_async(self) -> Optional[LatestImageInfo]:
        """Get latest image info for the device"""
        try:
            response = await self._client.get(f"{self._base_url}/device/{self._device_id}/image/latest")

            if response.status_code == 204:
                # No image available
                return None

            if response.status_code != 200:
                return None

            data = response.json()

            return LatestImageInfo(
                filename=data.get("filename", ""),
                url=data.get("url", ""),
                hash=data.get("hash", ""),
                timestamp=data.get("timestamp", 0),
                size=data.get("size", 0)
            )

        except:
            return None

    async def upload_image_async(self, image_data: bytes, file_name: str) -> CloudImageUploadResponse:
        """Upload an image to the device via cloud"""
        try:
            # Determine MIME type
            extension = Path(file_name).suffix.lower()
            mime_type = {
                ".png": "image/png",
                ".gif": "image/gif",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
            }.get(extension, "application/octet-stream")

            files = {
                "image": (file_name, image_data, mime_type)
            }

            response = await self._client.post(
                f"{self._base_url}/device/{self._device_id}/image/upload",
                files=files
            )

            if response.status_code != 200:
                error_content = response.text
                return CloudImageUploadResponse(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {error_content}"
                )

            result = response.json()

            return CloudImageUploadResponse(
                success=True,
                file_name=result.get("filename", file_name),
                hash=result.get("hash"),
                message=result.get("message")
            )

        except Exception as ex:
            return CloudImageUploadResponse(
                success=False,
                error_message=f"Failed to upload image: {ex}"
            )

    async def download_image_async(self, image_url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            # Convert HTTP to HTTPS if needed
            if image_url.startswith("http://"):
                image_url = image_url.replace("http://", "https://")

            response = await self._client.get(image_url)

            if response.status_code != 200:
                return None

            return response.content

        except:
            return None

    async def download_active_image_async(self) -> Optional[bytes]:
        """Download the active image for the device"""
        try:
            image_info = await self.get_latest_image_async()
            if not image_info or not image_info.url:
                return None

            return await self.download_image_async(image_info.url)

        except:
            return None

    async def set_solid_color_async(
        self,
        color_hex: str,
        led_bits: int = 127,
        timeout_seconds: int = 30
    ) -> CloudCommandResponse:
        """Set LED solid color via cloud"""
        command = f"AT+SC={led_bits},{color_hex}"
        queue_result = await self.queue_command_async(command, priority=5)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        # Wait for completion
        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def show_picture_async(self, file_name: str, timeout_seconds: int = 30) -> CloudCommandResponse:
        """Display an image via cloud"""
        command = f"AT+SP={file_name}"
        queue_result = await self.queue_command_async(command, priority=5)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def set_display_brightness_async(
        self,
        brightness: int,
        timeout_seconds: int = 30
    ) -> CloudCommandResponse:
        """Set display brightness via cloud"""
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be between 0 and 100")

        command = f"AT+DB={brightness}"
        queue_result = await self.queue_command_async(command, priority=5)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def restart_device_async(self) -> CloudCommandResponse:
        """Restart device via cloud"""
        return await self.queue_command_async("AT+RST", priority=10)

    async def get_device_name_async(self, timeout_seconds: int = 30) -> CloudCommandResponse:
        """Get device name via cloud"""
        queue_result = await self.queue_command_async("AT+GDN", priority=5)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def get_firmware_version_async(self, timeout_seconds: int = 30) -> CloudCommandResponse:
        """Get firmware version via cloud"""
        queue_result = await self.queue_command_async("AT+GFV", priority=5)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def send_custom_command_async(
        self,
        command: str,
        priority: int = 5,
        timeout_seconds: int = 30
    ) -> CloudCommandResponse:
        """Send a custom AT command via cloud"""
        queue_result = await self.queue_command_async(command, priority)

        if not queue_result.success or timeout_seconds <= 0:
            return queue_result

        status = await self.wait_for_command_completion_async(
            queue_result.command_id,
            timeout_seconds,
            1.0
        )

        if status:
            queue_result.status = status.status
            queue_result.error_message = status.response

        return queue_result

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
