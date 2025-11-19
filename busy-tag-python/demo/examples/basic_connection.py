"""
Basic Connection Example

This example demonstrates how to discover and connect to a BusyTag device.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from busytag import BusyTagManager, BusyTagDevice


async def main():
    print("🏷️  BusyTag Basic Connection Example")
    print("=" * 50)

    # Create manager
    manager = BusyTagManager()
    manager.enable_verbose_logging = True

    # Find devices
    print("\n🔍 Scanning for devices...")
    devices = await manager.find_busytag_device()

    if not devices:
        print("❌ No devices found!")
        print("\nTroubleshooting:")
        print("  - Ensure device is connected via USB")
        print("  - Try unplugging and reconnecting")
        print("  - Check USB cable")
        return

    print(f"✅ Found {len(devices)} device(s):")
    for i, port in enumerate(devices, 1):
        print(f"  {i}. {port}")

    # Connect to first device
    print(f"\n🔌 Connecting to {devices[0]}...")
    device = BusyTagDevice(devices[0])

    # Setup event handlers
    def on_connection_changed(connected: bool):
        if connected:
            print("✅ Connection established!")
        else:
            print("❌ Connection lost!")

    def on_device_info(received: bool):
        if received:
            print("\n📱 Device Information:")
            print(f"  Name: {device.device_name}")
            print(f"  Manufacturer: {device.manufacture_name}")
            print(f"  ID: {device.id}")
            print(f"  Firmware: {device.firmware_version}")
            print(f"  Hardware: {device.hardware_version}")
            print(f"  Free Space: {device.free_storage_size:,} bytes")
            print(f"  Total Space: {device.total_storage_size:,} bytes")
            print(f"  Local Address: {device.local_host_address}")

    device.on_connection_state_changed = on_connection_changed
    device.on_received_device_basic_information = on_device_info

    # Connect
    await device.connect()

    if device.is_connected:
        print("\n🎉 Successfully connected to BusyTag device!")

        # Wait a bit
        print("\n⏳ Keeping connection for 5 seconds...")
        await asyncio.sleep(5)

        # Disconnect
        print("\n🔌 Disconnecting...")
        device.disconnect()
        print("✅ Disconnected successfully")
    else:
        print("❌ Failed to connect to device")

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
