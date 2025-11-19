"""Device configuration data class"""

from dataclasses import dataclass
from typing import List


@dataclass
class SolidColor:
    """Solid color configuration"""
    led_bits: int
    color: str

    def to_dict(self) -> dict:
        return {
            "led_bits": self.led_bits,
            "color": self.color
        }


@dataclass
class DeviceConfig:
    """Complete device configuration"""
    version: int = 3
    image: str = "def.png"
    show_after_drop: bool = False
    allow_usb_msc: bool = True
    allow_file_server: bool = False
    disp_brightness: int = 100
    solid_color: SolidColor | None = None
    activate_pattern: bool = False
    pattern_repeat: int = 3
    custom_pattern_arr: List = None

    def __post_init__(self):
        if self.solid_color is None:
            self.solid_color = SolidColor(127, "990000")
        if self.custom_pattern_arr is None:
            self.custom_pattern_arr = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "version": self.version,
            "image": self.image,
            "show_after_drop": self.show_after_drop,
            "allow_usb_msc": self.allow_usb_msc,
            "allow_file_server": self.allow_file_server,
            "disp_brightness": self.disp_brightness,
            "solidColor": self.solid_color.to_dict() if self.solid_color else None,
            "activate_pattern": self.activate_pattern,
            "pattern_repeat": self.pattern_repeat,
            "custom_pattern_arr": [p.to_dict() if hasattr(p, 'to_dict') else p
                                   for p in self.custom_pattern_arr]
        }
