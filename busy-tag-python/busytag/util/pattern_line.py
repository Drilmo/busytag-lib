"""Pattern line data class for LED patterns"""

from dataclasses import dataclass


@dataclass
class PatternLine:
    """Represents a single line in an LED pattern"""
    led_bits: int
    color: str
    speed: int
    delay: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "led_bits": self.led_bits,
            "color": self.color,
            "speed": self.speed,
            "delay": self.delay
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PatternLine":
        """Create from dictionary"""
        return cls(
            led_bits=data.get("led_bits", 127),
            color=data.get("color", "000000"),
            speed=data.get("speed", 100),
            delay=data.get("delay", 0)
        )
