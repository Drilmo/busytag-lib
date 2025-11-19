# 🏷️ BusyTag Demo Application

Interactive demo application for the BusyTag Python library with a beautiful web-based interface.

![BusyTag Demo](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)

## 🌟 Features

This demo application showcases all the features of the BusyTag Python library:

- **💡 LED Control**: Change colors with preset buttons or custom RGB values
- **📁 File Management**: Upload, view, and manage images on your device
- **⚙️ Configuration**: Adjust brightness, view storage, send custom AT commands
- **🎨 Patterns**: Control LED patterns with repeat options
- **🌐 HTTP API**: Test WiFi connectivity and HTTP commands
- **☁️ Cloud API**: Test cloud integration and remote control
- **📋 Activity Logs**: Real-time activity logging

## 📦 Installation

### Using uv (Recommended)

```bash
# Navigate to the demo directory
cd busy-tag-python/demo

# Install demo dependencies
uv pip install -r requirements.txt

# Or install in the project environment
cd ..
uv sync
uv pip install streamlit pillow
```

### Using pip

```bash
cd busy-tag-python/demo
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Connect Your BusyTag Device

Make sure your BusyTag device is connected to your Mac via USB.

### 2. Launch the Demo

From the `demo` directory:

```bash
streamlit run app.py
```

Or if using uv:

```bash
uv run streamlit run app.py
```

### 3. Open Your Browser

The demo will automatically open in your default browser at `http://localhost:8501`

If it doesn't open automatically, navigate to that URL manually.

### 4. Start Using the Demo

1. Click **"🔍 Scan for Devices"** in the sidebar
2. Select your device from the dropdown
3. Click **"🔌 Connect"**
4. Explore the different tabs!

## 🖥️ Mac-Specific Notes

### Serial Port Permissions

On macOS, you may need to grant permissions for serial port access:

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Add your terminal application or Python to the allowed applications

### Device Detection

BusyTag devices on Mac appear as `/dev/tty.usbmodem*` or `/dev/cu.usbmodem*` devices.

### Port Format

Example: `/dev/tty.usbmodem14101`

## 📱 Demo Tabs

### 💡 LED Control

- **Preset Colors**: Quick buttons for common colors (Red, Green, Blue, etc.)
- **Custom RGB**: Sliders for precise RGB color control
- **Brightness Control**: Adjust overall brightness (0-100%)
- **LED Bits Selection**: Control which LEDs are affected

### 📁 File Management

- **Upload Images**: Drag and drop or browse to upload PNG, JPG, GIF files
- **Preview**: See images before uploading
- **Progress Tracking**: Real-time upload progress bar
- **File List**: View all files on the device with size information
- **Quick Actions**: Show or delete files with one click

### ⚙️ Configuration

- **Display Brightness**: Adjust screen brightness
- **Storage Info**: View free and used space with visual progress bar
- **Device Commands**: Restart device and other system commands
- **Custom AT Commands**: Send any AT command and see the response

### 🎨 Patterns

- **Pattern Control**: Play and stop LED patterns
- **Repeat Count**: Configure how many times the pattern repeats
- **Pattern Upload**: (Coming soon) Upload custom LED patterns

### 🌐 HTTP API

- **WiFi Connection**: Connect to device over WiFi
- **Token Authentication**: Automatic token fetching
- **AT Commands**: Send commands via HTTP
- **Connection Testing**: Verify HTTP API functionality

### ☁️ Cloud API

- **Cloud Connection**: Test connection to BusyTag Cloud
- **Device Registration**: Register device with cloud server
- **Remote Commands**: Send commands through the cloud
- **Status Monitoring**: Check device online status

### 📋 Activity Logs

- **Real-time Logging**: See all actions and responses
- **Color-coded Messages**: Info, success, warning, and error messages
- **Log History**: Keep track of up to 50 recent actions
- **Clear Logs**: Reset the log display

## 🎨 Interface Features

- **Responsive Design**: Works on different screen sizes
- **Dark Mode Support**: Follows your system theme (Streamlit auto-detects)
- **Live Updates**: Real-time feedback for all operations
- **Error Handling**: Clear error messages with troubleshooting hints
- **Progress Indicators**: Visual feedback for long operations

## 🔧 Troubleshooting

### Device Not Found

**Problem**: Scanner doesn't find your device

**Solutions**:
- Ensure the device is properly connected via USB
- Try unplugging and reconnecting the device
- Check USB cable (try a different cable if possible)
- Verify device is powered on
- Try a different USB port

### Connection Failed

**Problem**: Can't connect to the device

**Solutions**:
- Close any other applications using the serial port
- Check device permissions on macOS
- Restart the demo application
- Restart your device

### Upload Fails

**Problem**: File upload doesn't complete

**Solutions**:
- Check available storage space on the device
- Ensure file size is reasonable (< 1MB recommended)
- Try a smaller or different image file
- Verify stable connection

### Slow Performance

**Problem**: Demo is slow or unresponsive

**Solutions**:
- Close other browser tabs
- Restart the Streamlit server
- Check system resources (Activity Monitor)
- Reduce image file sizes

## 🛠️ Development

### Running in Development Mode

```bash
# With auto-reload on file changes
streamlit run app.py --server.runOnSave true
```

### Debug Mode

Enable verbose logging by setting the environment variable:

```bash
export BUSYTAG_DEBUG=1
streamlit run app.py
```

### Custom Port

Run on a different port:

```bash
streamlit run app.py --server.port 8502
```

## 📚 Additional Examples

Check out the standalone examples in the parent directory for more specific use cases:

- `examples/basic_connection.py` - Simple connection example
- `examples/led_control.py` - LED control examples
- `examples/file_management.py` - File operations
- `examples/cloud_demo.py` - Cloud API usage

## 🔗 Links

- [BusyTag Python Library](../)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [BusyTag Website](https://www.busy-tag.com)

## 📝 License

This demo application is part of the BusyTag Python library and is licensed under the MIT License.

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

---

<div align="center">

**Made with ❤️ by [BUSY TAG SIA](https://www.busy-tag.com)**

*Happy BusyTagging! 🏷️*

</div>
