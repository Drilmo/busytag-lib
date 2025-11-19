# 🪟 BusyTag for Windows - Quick Start Guide

Complete guide for using BusyTag Python library on Windows.

## ✅ Prerequisites

- **Windows 10** version 1903 or later / **Windows 11**
- **Python 3.10** or higher
- **USB Cable** for connecting BusyTag device

## 📦 Installation

### Step 1: Install uv (Recommended)

Open PowerShell and run:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or download from: https://github.com/astral-sh/uv

### Step 2: Install BusyTag Library

**Option A: Using uv (Recommended)**

```powershell
# Clone the repository
git clone https://github.com/busy-tag/busytag-lib.git
cd busytag-lib\busy-tag-python

# Install with demo extras
uv pip install -e ".[demo]"
```

**Option B: Using pip**

```powershell
pip install "busytag[demo]"
```

## 🚀 Launch the Demo

### Method 1: Using the Launcher (Easiest)

```powershell
cd busytag-lib\busy-tag-python\demo
run.bat
```

The demo will automatically open in your browser at http://localhost:8501

### Method 2: Manual Launch

```powershell
cd busytag-lib\busy-tag-python
uv run streamlit run demo\app.py
```

## 🔌 Connecting Your Device

### 1. Plug in Your BusyTag Device

Connect your BusyTag device to a USB port.

### 2. Identify the COM Port

**Method A: Using Device Manager**
1. Press `Win + X` and select "Device Manager"
2. Expand "Ports (COM & LPT)"
3. Look for "USB Serial Device" or similar
4. Note the COM port number (e.g., COM3, COM4)

**Method B: Using PowerShell**

```powershell
Get-WmiObject Win32_SerialPort | Select-Object DeviceID, Description
```

**Method C: Let the App Find It**
- In the demo app, click "Scan for Devices"
- The app will automatically detect your BusyTag device

### 3. Connect in the Demo App

1. Click "🔍 Scan for Devices" in the sidebar
2. Select your device (e.g., COM3) from the dropdown
3. Click "🔌 Connect"
4. Start exploring!

## 🛠️ Troubleshooting

### Device Not Detected

**Problem**: Scanner doesn't find the device

**Solutions**:
1. Check if device is powered on and connected
2. Try a different USB port
3. Try a different USB cable
4. Check Device Manager for driver issues
5. Restart the computer

### Driver Issues

**Problem**: Device shows as "Unknown Device" in Device Manager

**Solutions**:
1. Windows usually auto-installs USB CDC drivers
2. If not, you may need to install USB Serial (CDC) drivers
3. Try unplugging and reconnecting the device
4. Update Windows to the latest version

### Permission Errors

**Problem**: Access denied when trying to connect

**Solutions**:
1. Close any other programs using the COM port
2. Run PowerShell/Command Prompt as Administrator
3. Check if antivirus is blocking access

### Port Already in Use

**Problem**: "Port is already open" error

**Solutions**:
1. Close all other programs that might use serial ports
2. Close Arduino IDE, PuTTY, or similar applications
3. Restart the demo application
4. Check Task Manager for Python processes and end them

### Slow Performance

**Problem**: Demo is slow or laggy

**Solutions**:
1. Close unnecessary browser tabs
2. Restart the Streamlit server
3. Check Task Manager for high CPU/memory usage
4. Try using Microsoft Edge or Chrome

## 💻 Command Line Examples

### Basic Connection Test

Create a file `test.py`:

```python
import asyncio
from busytag import BusyTagManager, BusyTagDevice

async def main():
    manager = BusyTagManager()
    devices = await manager.find_busytag_device()

    if devices:
        print(f"Found device on: {devices[0]}")

        device = BusyTagDevice(devices[0])
        await device.connect()

        if device.is_connected:
            print(f"Connected to: {device.device_name}")
            print(f"Firmware: {device.firmware_version}")

            # Set LED to red
            await device.set_solid_color_async("red", brightness=100)
            await asyncio.sleep(2)

            # Turn off
            await device.set_solid_color_async("off")

            device.disconnect()
        else:
            print("Failed to connect")
    else:
        print("No devices found")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```powershell
python test.py
```

### LED Control Example

```python
import asyncio
from busytag import BusyTagDevice

async def main():
    # Replace COM3 with your actual port
    device = BusyTagDevice("COM3")
    await device.connect()

    if device.is_connected:
        # Cycle through colors
        colors = ["red", "green", "blue", "yellow"]

        for color in colors:
            print(f"Setting LED to {color}")
            await device.set_solid_color_async(color, brightness=100)
            await asyncio.sleep(1)

        # Turn off
        await device.set_solid_color_async("off")
        device.disconnect()

asyncio.run(main())
```

## 🎯 Running Standalone Examples

The demo includes several standalone Python examples:

```powershell
cd busytag-lib\busy-tag-python\demo\examples

# Basic connection
python basic_connection.py

# LED control
python led_control.py

# File management
python file_management.py

# Cloud API (requires internet connection)
python cloud_demo.py
```

## 🔍 Debugging

### Enable Verbose Logging

```python
manager = BusyTagManager()
manager.enable_verbose_logging = True
```

### Check Python Version

```powershell
python --version
```

Should be 3.10 or higher.

### Verify Installation

```powershell
python -c "import busytag; print('BusyTag installed successfully!')"
```

### List Installed Packages

```powershell
uv pip list
# or
pip list
```

## 📱 Windows-Specific Features

### COM Port Auto-Detection

The library uses WMI (Windows Management Instrumentation) for automatic device discovery on Windows. This provides reliable detection without needing to test each COM port individually.

### Windows Terminal

For the best experience, use Windows Terminal (available from Microsoft Store):
- Better Unicode support
- Emoji rendering
- Color support
- Multiple tabs

### Firewall Settings

If using HTTP or Cloud features, you may need to allow Python through Windows Firewall:

1. Go to Windows Security → Firewall & network protection
2. Click "Allow an app through firewall"
3. Find Python or add it if not listed

## 🎨 Windows-Optimized Demo Theme

The demo automatically adapts to Windows:
- Light theme by default
- Windows-friendly fonts
- Responsive layout
- Touch-friendly buttons (for Windows tablets)

## 📚 Additional Resources

- [Main README](README.md) - Complete library documentation
- [Demo README](demo/README.md) - Demo application guide
- [API Documentation](README.md#api-documentation) - API reference

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review the main [README](README.md)
3. Check GitHub Issues: https://github.com/busy-tag/busytag-lib/issues
4. Create a new issue with:
   - Windows version
   - Python version
   - Error messages
   - Steps to reproduce

## 📝 Quick Commands Reference

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install BusyTag with demo
uv pip install -e ".[demo]"

# Launch demo
cd demo
run.bat

# Run example
python examples\basic_connection.py

# List COM ports
Get-WmiObject Win32_SerialPort | Select-Object DeviceID, Description

# Check Python version
python --version

# Verify installation
python -c "import busytag; print('OK')"
```

---

<div align="center">

**Made with ❤️ for Windows users**

🏷️ BusyTag - BUSY TAG SIA

</div>
