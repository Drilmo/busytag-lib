"""
LED Control Example

This example demonstrates various LED control features including
preset colors, custom RGB colors, and brightness control.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from busytag import BusyTagManager, BusyTagDevice


async def demo_preset_colors(device: BusyTagDevice):
    """Demo preset color functions"""
    print("\n🎨 Preset Colors Demo")
    print("-" * 30)

    colors = [
        ("Red", "red"),
        ("Green", "green"),
        ("Blue", "blue"),
        ("Yellow", "yellow"),
        ("Cyan", "cyan"),
        ("Magenta", "magenta"),
        ("White", "white"),
    ]

    for name, color in colors:
        print(f"Setting color to {name}...")
        await device.set_solid_color_async(color, brightness=100)
        await asyncio.sleep(1)

    # Turn off
    print("Turning off LEDs...")
    await device.set_solid_color_async("off")


async def demo_brightness_control(device: BusyTagDevice):
    """Demo brightness control"""
    print("\n💡 Brightness Control Demo")
    print("-" * 30)

    # Set to red
    await device.set_solid_color_async("red", brightness=100)
    print("Set to red at 100% brightness")

    # Fade down
    for brightness in range(100, 0, -10):
        print(f"Brightness: {brightness}%")
        await device.set_solid_color_async("red", brightness=brightness)
        await asyncio.sleep(0.3)

    # Fade up
    for brightness in range(0, 101, 10):
        print(f"Brightness: {brightness}%")
        await device.set_solid_color_async("red", brightness=brightness)
        await asyncio.sleep(0.3)


async def demo_custom_rgb(device: BusyTagDevice):
    """Demo custom RGB colors"""
    print("\n🌈 Custom RGB Colors Demo")
    print("-" * 30)

    colors = [
        (255, 0, 0, "Pure Red"),
        (0, 255, 0, "Pure Green"),
        (0, 0, 255, "Pure Blue"),
        (255, 128, 0, "Orange"),
        (128, 0, 128, "Purple"),
        (0, 255, 255, "Aqua"),
        (255, 192, 203, "Pink"),
    ]

    for red, green, blue, name in colors:
        print(f"Setting color to {name} (R:{red}, G:{green}, B:{blue})")
        await device.send_rgb_color_async(red, green, blue)
        await asyncio.sleep(1.5)


async def demo_rainbow_effect(device: BusyTagDevice):
    """Demo rainbow color cycling"""
    print("\n🌈 Rainbow Effect Demo")
    print("-" * 30)
    print("Cycling through rainbow colors...")

    # HSV to RGB conversion for rainbow
    import colorsys

    for hue in range(0, 360, 10):
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
        red = int(r * 255)
        green = int(g * 255)
        blue = int(b * 255)

        await device.send_rgb_color_async(red, green, blue)
        await asyncio.sleep(0.1)


async def main():
    print("🏷️  BusyTag LED Control Example")
    print("=" * 50)

    # Find and connect to device
    print("\n🔍 Scanning for devices...")
    manager = BusyTagManager()
    devices = await manager.find_busytag_device()

    if not devices:
        print("❌ No devices found!")
        return

    print(f"✅ Found device: {devices[0]}")

    # Connect
    print(f"\n🔌 Connecting to {devices[0]}...")
    device = BusyTagDevice(devices[0])
    await device.connect()

    if not device.is_connected:
        print("❌ Failed to connect!")
        return

    print("✅ Connected!")

    try:
        # Run demos
        await demo_preset_colors(device)
        await asyncio.sleep(1)

        await demo_brightness_control(device)
        await asyncio.sleep(1)

        await demo_custom_rgb(device)
        await asyncio.sleep(1)

        await demo_rainbow_effect(device)

        # Turn off
        print("\n🔌 Turning off LEDs...")
        await device.set_solid_color_async("off")

    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        device.disconnect()
        print("✅ Disconnected")

    print("\n✨ Example completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
