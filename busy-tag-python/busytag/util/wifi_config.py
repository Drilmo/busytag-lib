"""WiFi configuration data class"""

from dataclasses import dataclass


@dataclass
class WiFiConfig:
    """WiFi configuration for the device"""
    ssid: str = ""
    password: str = ""
