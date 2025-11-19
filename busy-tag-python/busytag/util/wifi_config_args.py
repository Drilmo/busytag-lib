"""WiFi configuration event arguments"""

from dataclasses import dataclass


@dataclass
class WifiConfigArgs:
    """Arguments for WiFi configuration events"""
    ssid: str = ""
    password: str = ""
