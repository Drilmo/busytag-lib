"""
File Management Example

This example demonstrates file upload, download, listing, and deletion.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from busytag import BusyTagManager, BusyTagDevice
from busytag.util import UploadProgressArgs, FileUploadFinishedArgs


def create_sample_image():
    """Create a sample image for testing"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠️  PIL not installed. Using placeholder.")
        return None

    # Create a simple test image
    img = Image.new('RGB', (296, 128), color='blue')
    draw = ImageDraw.Draw(img)

    # Draw text
    try:
        draw.text((10, 50), "BusyTag Demo", fill='white')
    except:
        pass

    # Save
    path = Path("/tmp/busytag_demo.png")
    img.save(path)
    print(f"✅ Created sample image: {path}")
    return str(path)


async def demo_file_list(device: BusyTagDevice):
    """Demo listing files on device"""
    print("\n📁 File List Demo")
    print("-" * 30)

    files = await device.get_file_list_async()

    if files:
        print(f"Found {len(files)} file(s) on device:")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name} ({file.size:,} bytes)")
    else:
        print("No files found on device")

    return files


async def demo_file_upload(device: BusyTagDevice, file_path: str):
    """Demo file upload with progress"""
    print("\n⬆️  File Upload Demo")
    print("-" * 30)

    # Setup progress callback
    def on_progress(args: UploadProgressArgs):
        bar_length = 30
        filled = int(bar_length * args.progress_level / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r  [{bar}] {args.progress_level:.1f}%", end="", flush=True)

    def on_finished(args: FileUploadFinishedArgs):
        print()  # New line after progress
        if args.success:
            print(f"✅ Upload completed: {args.file_name}")
        else:
            print(f"❌ Upload failed: {args.error_message}")

    device.on_file_upload_progress = on_progress
    device.on_file_upload_finished = on_finished

    # Upload
    print(f"Uploading {Path(file_path).name}...")
    await device.send_new_file(file_path)


async def demo_show_picture(device: BusyTagDevice, filename: str):
    """Demo showing a picture"""
    print("\n👁️  Show Picture Demo")
    print("-" * 30)

    print(f"Displaying {filename} on device...")
    success = await device.show_picture_async(filename)

    if success:
        print("✅ Picture displayed successfully")
    else:
        print("❌ Failed to display picture")


async def demo_file_delete(device: BusyTagDevice, filename: str):
    """Demo file deletion"""
    print("\n🗑️  File Delete Demo")
    print("-" * 30)

    print(f"Deleting {filename}...")
    success = await device.delete_file(filename)

    if success:
        print("✅ File deleted successfully")
    else:
        print("❌ Failed to delete file")


async def demo_storage_info(device: BusyTagDevice):
    """Demo storage information"""
    print("\n💾 Storage Info Demo")
    print("-" * 30)

    free = await device.get_free_storage_size_async()
    total = await device.get_total_storage_size_async()

    used = total - free
    percent_used = (used / total * 100) if total > 0 else 0

    print(f"Total Space: {total:,} bytes ({total / 1024 / 1024:.2f} MB)")
    print(f"Used Space:  {used:,} bytes ({used / 1024 / 1024:.2f} MB)")
    print(f"Free Space:  {free:,} bytes ({free / 1024 / 1024:.2f} MB)")
    print(f"Usage:       {percent_used:.1f}%")

    # Visual bar
    bar_length = 40
    filled = int(bar_length * percent_used / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"[{bar}]")


async def main():
    print("🏷️  BusyTag File Management Example")
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
        # Show storage info
        await demo_storage_info(device)
        await asyncio.sleep(1)

        # List files
        files = await demo_file_list(device)
        await asyncio.sleep(1)

        # Create and upload a sample image
        sample_image = create_sample_image()
        if sample_image:
            await demo_file_upload(device, sample_image)
            await asyncio.sleep(1)

            # Show the uploaded image
            await demo_show_picture(device, "busytag_demo.png")
            await asyncio.sleep(2)

            # Optional: Delete the uploaded file
            # print("\n⏳ Waiting 5 seconds before deletion...")
            # await asyncio.sleep(5)
            # await demo_file_delete(device, "busytag_demo.png")

        # Show updated file list
        await demo_file_list(device)

        # Show updated storage info
        await demo_storage_info(device)

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
