# BusyTag Python Library

🚧 **Work in Progress** - Python implementation of BusyTag device management library

## 📋 Overview

This is a Python port of the [BusyTag.Lib .NET library](../busy-tag-dotnet), providing the same powerful features for managing BusyTag devices via serial communication.

## 🚀 Planned Features

- **🔍 Cross-platform device discovery** - Automatic detection on Windows, macOS, and Linux
- **📡 Robust serial communication** - Reliable connection management with automatic reconnection
- **📁 Complete file management** - Upload, download, and delete files with real-time progress tracking
- **💡 Advanced LED control** - Solid colors, custom patterns, and predefined animations
- **⚙️ Device configuration** - Brightness, storage, Wi-Fi, and system settings management
- **📢 Real-time notifications** - Event system for all device operations
- **🔄 Firmware update support** - Built-in firmware update capabilities
- **🎨 Rich pattern library** - 30+ predefined LED patterns
- **⚡ Async/await support** - Modern asynchronous Python API

## 📦 Installation (Coming Soon)

```bash
pip install busytag
```

## 🏃‍♂️ Quick Start (Preview)

```python
import asyncio
from busytag import BusyTagManager, BusyTagDevice

async def main():
    # Create manager
    manager = BusyTagManager()

    # Subscribe to device events
    manager.on_device_connected(lambda port: print(f"✅ Device connected on {port}"))
    manager.on_device_disconnected(lambda port: print(f"❌ Device disconnected from {port}"))

    # Find devices
    devices = await manager.find_busytag_devices()

    if devices:
        # Connect to first device
        device = BusyTagDevice(devices[0])
        await device.connect()

        if device.is_connected:
            print(f"🔗 Connected to {device.device_name}")
            print(f"📱 Firmware: {device.firmware_version}")
            print(f"💾 Free space: {device.free_storage_size} bytes")

            # Set LED color
            await device.set_led_color(255, 0, 0)  # Red

            # Upload a file
            await device.upload_file("image.jpg", progress_callback=lambda p: print(f"Progress: {p}%"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 🖥️ Platform Support

- **Windows**: COM port detection and management
- **macOS**: USB device enumeration via system_profiler
- **Linux**: USB device detection via lsusb

## 🏗️ Development Status

This library is currently under development. The initial implementation will be based on the .NET library architecture with Python best practices.

### Roadmap

- [ ] Core serial communication
- [ ] Device discovery (Windows/macOS/Linux)
- [ ] AT command protocol implementation
- [ ] File transfer capabilities
- [ ] LED control
- [ ] Pattern management
- [ ] Event system
- [ ] Async API
- [ ] Unit tests
- [ ] Documentation
- [ ] PyPI package

## 🤝 Contributing

Contributions are welcome! This is a great opportunity to help build a Python library from scratch based on a proven .NET implementation.

## 📋 Requirements (Planned)

- Python 3.8+
- pyserial >= 3.5
- Additional dependencies TBD

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Related Projects

- [BusyTag .NET Library](../busy-tag-dotnet) - Original .NET implementation

---

<div align="center">

**Made with ❤️ by [BUSY TAG SIA](https://www.busy-tag.com)**

</div>
