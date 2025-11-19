"""Upload progress event arguments"""

from dataclasses import dataclass


@dataclass
class UploadProgressArgs:
    """Arguments for file upload progress events"""
    file_name: str = ""
    progress_level: float = 0.0
