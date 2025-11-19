"""
Cloud API Example

This example demonstrates using the BusyTag Cloud API for remote device control.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from busytag import BusyTagCloudClient


async def demo_device_status(cloud: BusyTagCloudClient):
    """Demo getting device status"""
    print("\n📊 Device Status")
    print("-" * 30)

    status = await cloud.get_device_status_async()

    if status:
        print(f"Device ID: {status.device_id}")
        print(f"Device Name: {status.device_name or 'N/A'}")
        print(f"Firmware: {status.firmware_version or 'N/A'}")
        print(f"Online: {'✅ Yes' if status.online else '❌ No'}")
        print(f"Last Seen: {status.last_seen or 'Never'}")
        print(f"IP Address: {status.ip_address or 'N/A'}")
        print(f"Image Count: {status.image_count or 0}")
        print(f"Active Image: {status.active_image or 'None'}")
        print(f"Pending Commands: {status.pending_commands or 0}")
        print(f"Completed Commands: {status.completed_commands or 0}")
    else:
        print("❌ Failed to get device status")


async def demo_test_connection(cloud: BusyTagCloudClient):
    """Demo testing cloud connection"""
    print("\n🔌 Testing Cloud Connection")
    print("-" * 30)

    print("Waiting for device to come online...")
    result = await cloud.test_cloud_connection_async(
        timeout_seconds=45,
        wait_for_online=True
    )

    if result.success:
        print(f"✅ {result.message}")
        print(f"Details: {result.details}")
        if result.response:
            print(f"Response: {result.response}")
    else:
        print(f"❌ {result.message}")
        print(f"Details: {result.details}")


async def demo_send_command(cloud: BusyTagCloudClient):
    """Demo sending a command via cloud"""
    print("\n📤 Sending Command")
    print("-" * 30)

    # Get device name
    print("Sending AT+GDN command...")
    result = await cloud.get_device_name_async(timeout_seconds=30)

    if result.success:
        print(f"✅ Command executed successfully")
        print(f"Status: {result.status}")
        if result.error_message:
            print(f"Response: {result.error_message}")
    else:
        print(f"❌ Command failed: {result.error_message}")


async def demo_led_control(cloud: BusyTagCloudClient):
    """Demo LED control via cloud"""
    print("\n💡 LED Control via Cloud")
    print("-" * 30)

    colors = [
        ("Red", "FF0000"),
        ("Green", "00FF00"),
        ("Blue", "0000FF"),
        ("Off", "000000"),
    ]

    for name, hex_color in colors:
        print(f"Setting color to {name} ({hex_color})...")

        result = await cloud.set_solid_color_async(
            hex_color,
            timeout_seconds=30
        )

        if result.success:
            print(f"  ✅ Success!")
        else:
            print(f"  ❌ Failed: {result.error_message}")

        await asyncio.sleep(2)


async def demo_image_operations(cloud: BusyTagCloudClient):
    """Demo image operations via cloud"""
    print("\n🖼️  Image Operations")
    print("-" * 30)

    # Get latest image
    print("Fetching latest image info...")
    image_info = await cloud.get_latest_image_async()

    if image_info:
        print(f"✅ Latest Image:")
        print(f"  Filename: {image_info.filename}")
        print(f"  Size: {image_info.size:,} bytes")
        print(f"  Hash: {image_info.hash}")
        print(f"  URL: {image_info.url}")
    else:
        print("❌ No images found")


async def main():
    print("🏷️  BusyTag Cloud API Example")
    print("=" * 50)

    # Configuration
    cloud_url = input("\n🌐 Enter Cloud URL (default: https://cloud.busy-tag.com/api): ").strip()
    if not cloud_url:
        cloud_url = "https://cloud.busy-tag.com/api"

    device_id = input("🆔 Enter Device ID: ").strip()

    if not device_id:
        print("❌ Device ID is required!")
        return

    print(f"\n📡 Connecting to cloud: {cloud_url}")
    print(f"🆔 Device ID: {device_id}")

    async with BusyTagCloudClient(cloud_url, device_id) as cloud:
        try:
            # Get device status
            await demo_device_status(cloud)
            await asyncio.sleep(1)

            # Ask if device is online
            print("\n" + "=" * 50)
            response = input("\nIs your device online and connected to WiFi? (y/n): ").lower()

            if response != 'y':
                print("\n⚠️  Please ensure your device is:")
                print("  1. Powered on")
                print("  2. Connected to WiFi")
                print("  3. Has internet access")
                print("  4. Is registered with the cloud")
                return

            # Test connection
            await demo_test_connection(cloud)
            await asyncio.sleep(1)

            # Send command
            await demo_send_command(cloud)
            await asyncio.sleep(1)

            # LED control
            await demo_led_control(cloud)
            await asyncio.sleep(1)

            # Image operations
            await demo_image_operations(cloud)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

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
