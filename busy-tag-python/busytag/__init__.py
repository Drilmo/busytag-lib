"""
BusyTag Python Library

A Python library for managing BusyTag devices via serial communication.
Supports device discovery, file management, LED control, and pattern configuration.
"""

from .busytag_manager import BusyTagManager
from .busytag_device import BusyTagDevice
from .busytag_http_client import BusyTagHttpClient, AtCommandResponse
from .busytag_cloud_client import (
    BusyTagCloudClient,
    CloudCommandResponse,
    CloudTestResult,
    DeviceStatus,
    LatestImageInfo,
    CloudImageUploadResponse
)

__version__ = "0.1.0"
__author__ = "BUSY TAG SIA"
__all__ = [
    "BusyTagManager",
    "BusyTagDevice",
    "BusyTagHttpClient",
    "BusyTagCloudClient",
    "AtCommandResponse",
    "CloudCommandResponse",
    "CloudTestResult",
    "DeviceStatus",
    "LatestImageInfo",
    "CloudImageUploadResponse",
]
