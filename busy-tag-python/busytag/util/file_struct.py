"""File structure data class"""

from dataclasses import dataclass
from enum import Enum


class FileType(Enum):
    """File type enumeration"""
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class FileStruct:
    """Structure representing a file on the BusyTag device"""
    name: str
    size: int
    file_type: FileType = FileType.FILE

    def __str__(self) -> str:
        return f"name:{self.name},size:{self.size}"
