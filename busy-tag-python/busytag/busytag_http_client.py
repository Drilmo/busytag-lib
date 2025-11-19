"""HTTP client for BusyTag device communication"""

import re
from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class AtCommandResponse:
    """Response from AT command via HTTP"""
    status: str = ""
    message: str = ""
    data: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if response was successful"""
        return self.status.lower() == "success"


class BusyTagHttpClient:
    """HTTP client for communicating with BusyTag device over WiFi"""

    def __init__(self, device_host: str = "192.168.4.1", port: int = 80, auth_token: Optional[str] = None):
        self._base_url = f"http://{device_host}:{port}"
        self._auth_token = auth_token
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=10.0)

        print(f"BusyTagHttpClient initialized with base URL: {self._base_url}")

    async def fetch_auth_token_async(self) -> Optional[str]:
        """Fetch authentication token from device homepage"""
        try:
            print(f"[HTTP] Fetching auth token from {self._base_url}/")

            response = await self._client.get("/")

            if response.status_code != 200:
                print(f"[HTTP] Failed to fetch homepage: {response.status_code}")
                return None

            html = response.text

            # Parse the token from the HTML
            # Example: -H "Authorization: Bearer <span class='token'>abc123def456</span>"
            match = re.search(
                r"Bearer\s+<span class='token'>([^<]+)</span>",
                html
            )

            if match:
                token = match.group(1)
                print(f"[HTTP] Extracted auth token: {token}")
                self._auth_token = token
                return token

            print("[HTTP] Could not find auth token in homepage")
            return None

        except Exception as ex:
            print(f"[HTTP] Exception fetching auth token: {ex}")
            return None

    async def send_at_command_async(self, command: str) -> AtCommandResponse:
        """Send AT command via HTTP"""
        try:
            print(f"[HTTP] Sending AT command: {command}")

            headers = {}
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"

            command_data = {"command": command}

            print(f"[HTTP] Request URL: {self._base_url}/at")
            print(f"[HTTP] Request body: {command_data}")

            response = await self._client.post(
                "/at",
                json=command_data,
                headers=headers
            )

            print(f"[HTTP] Response status: {response.status_code}")
            print(f"[HTTP] Response body: {response.text}")

            if response.status_code != 200:
                print(f"[HTTP] Error: {response.status_code} - {response.text}")
                return AtCommandResponse(
                    status="error",
                    message=f"HTTP {response.status_code}: {response.text}",
                    data=None
                )

            result = response.json()

            print(f"[HTTP] Parsed response - Status: {result.get('status')}, "
                  f"Message: {result.get('message')}, Data: {result.get('data')}")

            return AtCommandResponse(
                status=result.get("status", "error"),
                message=result.get("message", ""),
                data=result.get("data")
            )

        except httpx.TimeoutException as ex:
            print(f"[HTTP] Request timeout: {ex}")
            return AtCommandResponse(
                status="error",
                message="Request timeout - device did not respond",
                data=None
            )
        except httpx.HTTPError as ex:
            print(f"[HTTP] Connection error: {ex}")
            return AtCommandResponse(
                status="error",
                message=f"Cannot connect to device: {ex}",
                data=None
            )
        except Exception as ex:
            print(f"[HTTP] Unexpected error: {ex}")
            return AtCommandResponse(
                status="error",
                message=f"Error: {ex}",
                data=None
            )

    async def set_wifi_station_credentials_async(self, ssid: str, password: str) -> bool:
        """Set WiFi station credentials"""
        response = await self.send_at_command_async(f"AT+STA={ssid},{password}")
        return response.is_success and (response.data and "OK" in response.data)

    async def set_wifi_mode_async(self, mode: int) -> bool:
        """Set WiFi mode (0=OFF, 1=STA, 2=AP, 3=STA+AP)"""
        if not 0 <= mode <= 3:
            raise ValueError("WiFi mode must be between 0 and 3")

        response = await self.send_at_command_async(f"AT+WM={mode}")
        return response.is_success and (response.data and "OK" in response.data)

    async def get_device_info_async(self) -> AtCommandResponse:
        """Get device information"""
        return await self.send_at_command_async("AT+GDN")

    async def get_station_status_async(self) -> AtCommandResponse:
        """Get station status"""
        return await self.send_at_command_async("AT+STA?")

    async def get_wifi_mode_async(self) -> AtCommandResponse:
        """Get WiFi mode"""
        return await self.send_at_command_async("AT+WM?")

    async def get_hardware_version_async(self) -> AtCommandResponse:
        """Get hardware version"""
        return await self.send_at_command_async("AT+GHV")

    async def test_connection_async(self) -> bool:
        """Test connection to device"""
        try:
            response = await self.send_at_command_async("AT")
            return response.is_success
        except:
            return False

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
