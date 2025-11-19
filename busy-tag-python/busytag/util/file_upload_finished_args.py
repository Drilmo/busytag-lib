"""File upload finished event arguments"""

from dataclasses import dataclass
from enum import Enum


class UploadErrorType(Enum):
    """Types of upload errors"""
    NONE = "none"
    FILENAME_TOO_LONG = "filename_too_long"
    INSUFFICIENT_STORAGE = "insufficient_storage"
    TRANSFER_INTERRUPTED = "transfer_interrupted"
    CONNECTION_LOST = "connection_lost"
    DEVICE_ERROR = "device_error"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class FileUploadFinishedArgs:
    """Arguments for file upload finished events"""
    success: bool = False
    file_name: str = ""
    error_type: UploadErrorType = UploadErrorType.NONE
    error_message: str | None = None
