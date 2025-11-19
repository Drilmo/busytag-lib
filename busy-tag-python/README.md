# BusyTag Python Library

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/busy-tag/busytag-lib)

A powerful and intuitive Python library for seamless BusyTag device management via serial communication. Control LED patterns, manage files, and configure devices across Windows, macOS, and Linux platforms with ease.

This is the Python port of the .NET BusyTag.Lib library, providing the same functionality with a Pythonic interface.

## 🚀 Key Features

- **🔍 Cross-platform device discovery** - Automatic detection on Windows, macOS, and Linux
- **📡 Robust serial communication** - Reliable connection management with automatic reconnection
- **📁 Complete file management** - Upload, download, and delete files with real-time progress tracking
- **💡 Advanced LED control** - Solid colors, custom patterns, and predefined animations
- **⚙️ Device configuration** - Brightness, storage, Wi-Fi, and system settings management
- **📢 Real-time notifications** - Comprehensive event system for all device operations
- **🔄 Firmware update support** - Built-in firmware update capabilities with progress tracking
- **🎨 Rich pattern library** - 30+ predefined LED patterns including police, running lights, and pulses
- **☁️ Cloud support** - Remote device control via BusyTag Cloud API
- **🌐 HTTP API** - Control devices over Wi-Fi

## 📦 Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new project with busytag
uv init my-busytag-project
cd my-busytag-project

# Add busytag as a dependency
uv add busytag
```

### Using pip

```bash
pip install busytag
```

### From source

```bash
git clone https://github.com/busy-tag/busytag-lib.git
cd busytag-lib/busy-tag-python
uv sync
```

## 🖥️ Platform Support

### Windows
- **Device Discovery**: WMI-based VID/PID detection (303A:81DF)
- **Port Format**: `COM1`, `COM2`, `COM3`, etc.
- **Requirements**: `wmi` package (automatically installed)
- **Permissions**: Standard user permissions sufficient
- **Tested on**: Windows 10/11

### macOS
- **Device Discovery**: `ioreg` USB enumeration + AT command validation
- **Port Format**: `/dev/tty.usbmodem-xxx`
- **Requirements**: Xcode command line tools
- **Permissions**: May require accessibility permissions for serial access
- **Tested on**: macOS 10.15+ (Catalina and newer)

### Linux (Experimental)
- **Device Discovery**: `lsusb` command-line tool + AT command validation
- **Port Format**: `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
- **Requirements**: `usbutils` package
- **Permissions**: User must be in `dialout` group: `sudo usermod -a -G dialout $USER`
- **Status**: Experimental support - enable via `enable_experimental_linux_support` flag

## 🏃‍♂️ Quick Start

### Basic Usage

```python
import asyncio
from busytag import BusyTagManager, BusyTagDevice

async def main():
    # Create and configure the manager
    manager = BusyTagManager()

    # Subscribe to device events
    def on_device_connected(port):
        print(f"✅ Device connected on {port}")

    def on_device_disconnected(port):
        print(f"❌ Device disconnected from {port}")

    manager.on_device_connected = on_device_connected
    manager.on_device_disconnected = on_device_disconnected

    # Start automatic device scanning every 5 seconds
    manager.start_periodic_device_search(interval_ms=5000)

    # Manual device discovery
    devices = await manager.find_busytag_device()

    if devices:
        print(f"🎯 Found devices: {', '.join(devices)}")

        # Connect to first device
        device = BusyTagDevice(devices[0])
        await device.connect()

        if device.is_connected:
            print(f"🔗 Connected to {device.device_name}")
            print(f"📱 Firmware: {device.firmware_version}")
            print(f"💾 Free space: {device.free_storage_size:,} bytes")

            # Set LED color to red
            await device.set_solid_color_async("red", brightness=100)

            # Upload an image
            await device.send_new_file("path/to/image.png")

            # Display the image
            await device.show_picture_async("image.png")

            # Disconnect
            device.disconnect()

    # Stop periodic search
    manager.stop_periodic_device_search()

if __name__ == "__main__":
    asyncio.run(main())
```

### LED Control

```python
import asyncio
from busytag import BusyTagDevice

async def control_leds():
    device = BusyTagDevice("COM3")  # or "/dev/tty.usbmodem1234" on macOS
    await device.connect()

    # Set solid colors
    await device.set_solid_color_async("red", brightness=100)
    await asyncio.sleep(1)

    await device.set_solid_color_async("green", brightness=50)
    await asyncio.sleep(1)

    # Custom RGB color
    await device.send_rgb_color_async(red=255, green=128, blue=0, led_bits=127)

    # Turn off
    await device.set_solid_color_async("off")

    device.disconnect()

asyncio.run(control_leds())
```

### File Management

```python
import asyncio
from busytag import BusyTagDevice

async def manage_files():
    device = BusyTagDevice("COM3")
    await device.connect()

    # Get file list
    files = await device.get_file_list_async()
    for file in files:
        print(f"📄 {file.name} - {file.size:,} bytes")

    # Upload progress callback
    def on_progress(args):
        print(f"⬆️ Uploading {args.file_name}: {args.progress_level:.1f}%")

    device.on_file_upload_progress = on_progress

    # Upload new file
    await device.send_new_file("my_image.png")

    # Show the uploaded file
    await device.show_picture_async("my_image.png")

    # Delete a file
    await device.delete_file("old_image.png")

    device.disconnect()

asyncio.run(manage_files())
```

### Cloud Control

```python
import asyncio
from busytag import BusyTagCloudClient

async def cloud_control():
    # Initialize cloud client
    cloud = BusyTagCloudClient(
        base_url="https://cloud.busy-tag.com/api",
        device_id="your-device-id"
    )

    # Register device
    await cloud.register_device_async("My BusyTag", "2.0")

    # Check device status
    status = await cloud.get_device_status_async()
    if status and status.online:
        print(f"✅ Device is online!")

        # Send command via cloud
        result = await cloud.set_solid_color_async("FF0000", timeout_seconds=30)
        if result.success:
            print("🎨 Color changed successfully!")

    await cloud.close()

asyncio.run(cloud_control())
```

### HTTP API

```python
import asyncio
from busytag import BusyTagHttpClient

async def http_control():
    # Connect to device via WiFi
    http = BusyTagHttpClient(device_host="192.168.4.1", port=80)

    # Fetch auth token from device
    token = await http.fetch_auth_token_async()
    print(f"🔑 Auth token: {token}")

    # Send AT command
    response = await http.send_at_command_async("AT+GDN")
    print(f"📱 Device name: {response.data}")

    # Test connection
    is_connected = await http.test_connection_async()
    print(f"🔗 Connected: {is_connected}")

    await http.close()

asyncio.run(http_control())
```

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Operating Systems**:
  - Windows 10 version 1903 or later
  - macOS 10.15 (Catalina) or later
  - Linux (experimental support)
- **Hardware**: BusyTag device with compatible firmware (v0.7+)
- **Permissions**: Serial port access rights

## 🔧 Development

### Setup with uv

```bash
# Clone the repository
git clone https://github.com/busy-tag/busytag-lib.git
cd busytag-lib/busy-tag-python

# Install dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run black busytag/

# Lint code
uv run ruff check busytag/
```

### Building

```bash
# Build package
uv build

# Publish to PyPI
uv publish
```

## 📚 API Documentation

For detailed API documentation, please refer to the inline docstrings in the source code. The API closely mirrors the .NET version for consistency.

### Main Classes

- **`BusyTagManager`**: Device discovery and management
- **`BusyTagDevice`**: Serial communication with device
- **`BusyTagHttpClient`**: HTTP API for WiFi-connected devices
- **`BusyTagCloudClient`**: Cloud API for remote control

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/busy-tag/busytag-lib)
- [.NET Library](https://github.com/busy-tag/busytag-lib/tree/main/busy-tag-dotnet)
- [BusyTag Website](https://www.busy-tag.com)

---

<div align="center">

**Made with ❤️ by [BUSY TAG SIA](https://www.busy-tag.com)**

*Empowering developers to create amazing IoT experiences*

</div>
