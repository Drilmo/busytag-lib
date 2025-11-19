"""LED event arguments"""

from dataclasses import dataclass


@dataclass
class LedArgs:
    """Arguments for LED-related events"""
    led_bits: int = 127
    color: str = ""
