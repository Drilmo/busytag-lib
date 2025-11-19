"""
BusyTag Demo Application

Interactive demo application for BusyTag Python library using Streamlit.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import busytag
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from busytag import BusyTagManager, BusyTagDevice, BusyTagHttpClient, BusyTagCloudClient
from busytag.util import UploadProgressArgs, FileUploadFinishedArgs


# Page configuration
st.set_page_config(
    page_title="BusyTag Demo",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = None
if 'device' not in st.session_state:
    st.session_state.device = None
if 'connected_port' not in st.session_state:
    st.session_state.connected_port = None
if 'device_info' not in st.session_state:
    st.session_state.device_info = {}
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []


def add_log(message: str, level: str = "info"):
    """Add a log message"""
    icon = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(level, "ℹ️")
    st.session_state.log_messages.append(f"{icon} {message}")
    # Keep only last 50 messages
    if len(st.session_state.log_messages) > 50:
        st.session_state.log_messages = st.session_state.log_messages[-50:]


# Header
st.markdown('<div class="main-header">🏷️ BusyTag Demo Application</div>', unsafe_allow_html=True)

st.markdown("""
Welcome to the **BusyTag Python Library Demo**! This interactive application demonstrates all the features
of the BusyTag library for managing BusyTag devices.
""")

# Sidebar
with st.sidebar:
    st.header("📱 Device Connection")

    # Device discovery
    if st.button("🔍 Scan for Devices", use_container_width=True):
        with st.spinner("Scanning for devices..."):
            try:
                if st.session_state.manager is None:
                    st.session_state.manager = BusyTagManager()
                    st.session_state.manager.enable_verbose_logging = True

                devices = asyncio.run(st.session_state.manager.find_busytag_device())

                if devices:
                    add_log(f"Found {len(devices)} device(s): {', '.join(devices)}", "success")
                    st.success(f"✅ Found {len(devices)} device(s)")
                    st.session_state.available_devices = devices
                else:
                    add_log("No devices found", "warning")
                    st.warning("⚠️ No devices found")
                    st.session_state.available_devices = []
            except Exception as e:
                add_log(f"Error scanning: {e}", "error")
                st.error(f"❌ Error: {e}")

    # Device selection
    if 'available_devices' in st.session_state and st.session_state.available_devices:
        selected_port = st.selectbox(
            "Select Device Port",
            st.session_state.available_devices
        )

        # Connect button
        if st.session_state.device is None or not st.session_state.device.is_connected:
            if st.button("🔌 Connect", use_container_width=True):
                with st.spinner("Connecting..."):
                    try:
                        st.session_state.device = BusyTagDevice(selected_port)
                        asyncio.run(st.session_state.device.connect())

                        if st.session_state.device.is_connected:
                            st.session_state.connected_port = selected_port

                            # Get device info
                            info = {
                                "Device Name": st.session_state.device.device_name,
                                "Manufacturer": st.session_state.device.manufacture_name,
                                "Device ID": st.session_state.device.id,
                                "Firmware": st.session_state.device.firmware_version,
                                "Hardware": st.session_state.device.hardware_version,
                                "Free Space": f"{st.session_state.device.free_storage_size:,} bytes",
                                "Total Space": f"{st.session_state.device.total_storage_size:,} bytes",
                            }
                            st.session_state.device_info = info

                            add_log(f"Connected to {st.session_state.device.device_name}", "success")
                            st.success("✅ Connected!")
                            st.rerun()
                        else:
                            add_log("Failed to connect", "error")
                            st.error("❌ Failed to connect")
                    except Exception as e:
                        add_log(f"Connection error: {e}", "error")
                        st.error(f"❌ Error: {e}")
        else:
            # Disconnect button
            if st.button("🔌 Disconnect", use_container_width=True):
                try:
                    st.session_state.device.disconnect()
                    st.session_state.device = None
                    st.session_state.connected_port = None
                    st.session_state.device_info = {}
                    add_log("Disconnected from device", "info")
                    st.success("✅ Disconnected")
                    st.rerun()
                except Exception as e:
                    add_log(f"Disconnect error: {e}", "error")
                    st.error(f"❌ Error: {e}")

    # Device info display
    if st.session_state.connected_port:
        st.success(f"🔗 Connected to: {st.session_state.connected_port}")

        if st.session_state.device_info:
            st.subheader("Device Information")
            for key, value in st.session_state.device_info.items():
                st.text(f"{key}: {value}")


# Main content tabs
if st.session_state.device and st.session_state.device.is_connected:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💡 LED Control",
        "📁 File Management",
        "⚙️ Configuration",
        "🎨 Patterns",
        "🌐 HTTP API",
        "☁️ Cloud API",
        "📋 Logs"
    ])

    # LED Control Tab
    with tab1:
        st.header("💡 LED Control")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Preset Colors")

            colors = {
                "🔴 Red": "red",
                "🟢 Green": "green",
                "🔵 Blue": "blue",
                "🟡 Yellow": "yellow",
                "🔵 Cyan": "cyan",
                "🟣 Magenta": "magenta",
                "⚪ White": "white",
                "⚫ Off": "off"
            }

            brightness = st.slider("Brightness (%)", 0, 100, 100)

            cols = st.columns(4)
            for idx, (label, color) in enumerate(colors.items()):
                with cols[idx % 4]:
                    if st.button(label, use_container_width=True):
                        try:
                            asyncio.run(
                                st.session_state.device.set_solid_color_async(
                                    color, brightness
                                )
                            )
                            add_log(f"Set LED to {color} at {brightness}%", "success")
                            st.success(f"✅ Set to {color}")
                        except Exception as e:
                            add_log(f"LED error: {e}", "error")
                            st.error(f"❌ Error: {e}")

        with col2:
            st.subheader("Custom RGB Color")

            red = st.slider("Red", 0, 255, 255)
            green = st.slider("Green", 0, 255, 0)
            blue = st.slider("Blue", 0, 255, 0)

            # Color preview
            color_hex = f"#{red:02X}{green:02X}{blue:02X}"
            st.markdown(
                f'<div style="width: 100%; height: 50px; background-color: {color_hex}; '
                f'border-radius: 5px; border: 2px solid #ccc;"></div>',
                unsafe_allow_html=True
            )

            led_bits = st.selectbox("LED Bits", [127, 63, 31, 15, 7, 3, 1], index=0)

            if st.button("🎨 Set Custom Color", use_container_width=True):
                try:
                    asyncio.run(
                        st.session_state.device.send_rgb_color_async(
                            red, green, blue, led_bits
                        )
                    )
                    add_log(f"Set RGB to ({red}, {green}, {blue})", "success")
                    st.success("✅ Custom color set!")
                except Exception as e:
                    add_log(f"RGB error: {e}", "error")
                    st.error(f"❌ Error: {e}")

    # File Management Tab
    with tab2:
        st.header("📁 File Management")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Upload File")

            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'gif']
            )

            if uploaded_file:
                st.image(uploaded_file, caption="Preview", use_container_width=True)

                if st.button("⬆️ Upload to Device", use_container_width=True):
                    try:
                        # Save temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                        # Upload with progress
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def on_progress(args: UploadProgressArgs):
                            progress_bar.progress(int(args.progress_level) / 100)
                            status_text.text(f"Uploading: {args.progress_level:.1f}%")

                        st.session_state.device.on_file_upload_progress = on_progress

                        asyncio.run(st.session_state.device.send_new_file(temp_path))

                        add_log(f"Uploaded {uploaded_file.name}", "success")
                        st.success(f"✅ Uploaded {uploaded_file.name}")

                    except Exception as e:
                        add_log(f"Upload error: {e}", "error")
                        st.error(f"❌ Error: {e}")

        with col2:
            st.subheader("Device Files")

            if st.button("🔄 Refresh File List", use_container_width=True):
                try:
                    files = asyncio.run(st.session_state.device.get_file_list_async())
                    st.session_state.device_files = files
                    add_log(f"Found {len(files)} files", "info")
                except Exception as e:
                    add_log(f"File list error: {e}", "error")
                    st.error(f"❌ Error: {e}")

            if 'device_files' in st.session_state:
                for file in st.session_state.device_files:
                    col_a, col_b, col_c = st.columns([3, 1, 1])

                    with col_a:
                        st.text(f"📄 {file.name} ({file.size:,} bytes)")

                    with col_b:
                        if st.button("👁️", key=f"show_{file.name}"):
                            try:
                                asyncio.run(
                                    st.session_state.device.show_picture_async(file.name)
                                )
                                add_log(f"Showing {file.name}", "success")
                                st.success(f"✅ Showing {file.name}")
                            except Exception as e:
                                add_log(f"Show error: {e}", "error")
                                st.error(f"❌ Error: {e}")

                    with col_c:
                        if st.button("🗑️", key=f"del_{file.name}"):
                            try:
                                asyncio.run(
                                    st.session_state.device.delete_file(file.name)
                                )
                                add_log(f"Deleted {file.name}", "success")
                                st.success(f"✅ Deleted {file.name}")
                                st.rerun()
                            except Exception as e:
                                add_log(f"Delete error: {e}", "error")
                                st.error(f"❌ Error: {e}")

    # Configuration Tab
    with tab3:
        st.header("⚙️ Device Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Display Settings")

            brightness_val = st.slider("Display Brightness", 0, 100, 100, key="disp_brightness")

            if st.button("💡 Set Brightness", use_container_width=True):
                try:
                    asyncio.run(
                        st.session_state.device.set_display_brightness_async(brightness_val)
                    )
                    add_log(f"Set brightness to {brightness_val}%", "success")
                    st.success(f"✅ Brightness set to {brightness_val}%")
                except Exception as e:
                    add_log(f"Brightness error: {e}", "error")
                    st.error(f"❌ Error: {e}")

            st.subheader("Storage Information")
            if st.button("📊 Update Storage Info", use_container_width=True):
                try:
                    free = asyncio.run(st.session_state.device.get_free_storage_size_async())
                    total = asyncio.run(st.session_state.device.get_total_storage_size_async())

                    used = total - free
                    percent_used = (used / total * 100) if total > 0 else 0

                    st.metric("Free Space", f"{free:,} bytes")
                    st.metric("Total Space", f"{total:,} bytes")
                    st.progress(percent_used / 100)
                    st.text(f"Used: {percent_used:.1f}%")

                    add_log("Updated storage info", "info")
                except Exception as e:
                    add_log(f"Storage info error: {e}", "error")
                    st.error(f"❌ Error: {e}")

        with col2:
            st.subheader("Device Commands")

            if st.button("🔄 Restart Device", use_container_width=True):
                if st.checkbox("Confirm restart"):
                    try:
                        asyncio.run(st.session_state.device.restart_device_async())
                        add_log("Device restarting...", "warning")
                        st.warning("⚠️ Device is restarting...")
                    except Exception as e:
                        add_log(f"Restart error: {e}", "error")
                        st.error(f"❌ Error: {e}")

            st.subheader("Custom AT Command")

            custom_command = st.text_input("Enter AT command", "AT+GDN")

            if st.button("📤 Send Command", use_container_width=True):
                try:
                    response = asyncio.run(
                        st.session_state.device.send_custom_command_async(custom_command)
                    )
                    st.code(response, language="text")
                    add_log(f"Sent: {custom_command}", "info")
                    add_log(f"Response: {response}", "success")
                except Exception as e:
                    add_log(f"Command error: {e}", "error")
                    st.error(f"❌ Error: {e}")

    # Patterns Tab
    with tab4:
        st.header("🎨 LED Patterns")

        st.info("⚠️ Pattern functionality requires pattern upload. Coming soon in this demo!")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Pattern Control")

            repeat_count = st.number_input("Repeat Count", 1, 255, 5)

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("▶️ Play Pattern", use_container_width=True):
                    try:
                        asyncio.run(
                            st.session_state.device.play_pattern_async(True, repeat_count)
                        )
                        add_log(f"Playing pattern ({repeat_count} repeats)", "success")
                        st.success("✅ Pattern started")
                    except Exception as e:
                        add_log(f"Pattern error: {e}", "error")
                        st.error(f"❌ Error: {e}")

            with col_b:
                if st.button("⏹️ Stop Pattern", use_container_width=True):
                    try:
                        asyncio.run(
                            st.session_state.device.play_pattern_async(False, 0)
                        )
                        add_log("Stopped pattern", "info")
                        st.success("✅ Pattern stopped")
                    except Exception as e:
                        add_log(f"Pattern error: {e}", "error")
                        st.error(f"❌ Error: {e}")

    # HTTP API Tab
    with tab5:
        st.header("🌐 HTTP API")

        st.info("⚠️ HTTP API requires device to be connected to WiFi network")

        device_host = st.text_input("Device IP Address", "192.168.4.1")
        port = st.number_input("Port", 1, 65535, 80)

        if st.button("🔌 Test HTTP Connection"):
            try:
                async def test_http():
                    async with BusyTagHttpClient(device_host, port) as http:
                        token = await http.fetch_auth_token_async()
                        if token:
                            st.success(f"✅ Connected! Token: {token}")
                            add_log(f"HTTP connected, token: {token}", "success")
                        else:
                            st.warning("⚠️ Connected but no token found")
                            add_log("HTTP connected, no token", "warning")

                        response = await http.test_connection_async()
                        if response:
                            st.success("✅ HTTP API is working!")
                        else:
                            st.error("❌ HTTP API test failed")

                asyncio.run(test_http())
            except Exception as e:
                add_log(f"HTTP error: {e}", "error")
                st.error(f"❌ Error: {e}")

    # Cloud API Tab
    with tab6:
        st.header("☁️ Cloud API")

        st.info("⚠️ Cloud API requires device to be registered with BusyTag Cloud")

        cloud_url = st.text_input("Cloud URL", "https://cloud.busy-tag.com/api")
        device_id = st.text_input("Device ID", st.session_state.device_info.get("Device ID", ""))

        if st.button("☁️ Test Cloud Connection"):
            if device_id:
                try:
                    async def test_cloud():
                        async with BusyTagCloudClient(cloud_url, device_id) as cloud:
                            result = await cloud.test_cloud_connection_async(
                                timeout_seconds=30,
                                wait_for_online=True
                            )

                            if result.success:
                                st.success(f"✅ {result.message}")
                                st.info(f"Details: {result.details}")
                                add_log(f"Cloud test: {result.message}", "success")
                            else:
                                st.error(f"❌ {result.message}")
                                st.warning(f"Details: {result.details}")
                                add_log(f"Cloud test failed: {result.message}", "error")

                    asyncio.run(test_cloud())
                except Exception as e:
                    add_log(f"Cloud error: {e}", "error")
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please enter a Device ID")

    # Logs Tab
    with tab7:
        st.header("📋 Activity Logs")

        col1, col2 = st.columns([3, 1])

        with col2:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                st.session_state.log_messages = []
                st.rerun()

        # Display logs in reverse order (newest first)
        log_container = st.container()
        with log_container:
            for message in reversed(st.session_state.log_messages):
                st.text(message)

else:
    # No device connected
    st.info("👈 Please scan for and connect to a device using the sidebar to get started!")

    st.markdown("### 🚀 Quick Start Guide")

    st.markdown("""
    1. **Scan for Devices**: Click the "🔍 Scan for Devices" button in the sidebar
    2. **Select Device**: Choose your BusyTag device from the dropdown
    3. **Connect**: Click the "🔌 Connect" button
    4. **Explore**: Use the tabs above to explore different features!

    ### 📚 Features Available

    - **💡 LED Control**: Change colors, brightness, and RGB values
    - **📁 File Management**: Upload, view, and delete images
    - **⚙️ Configuration**: Adjust display settings and device parameters
    - **🎨 Patterns**: Control LED patterns
    - **🌐 HTTP API**: Test WiFi connectivity
    - **☁️ Cloud API**: Test cloud integration
    - **📋 Logs**: View activity logs
    """)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">'
    '🏷️ BusyTag Python Library Demo | Made with ❤️ by BUSY TAG SIA'
    '</div>',
    unsafe_allow_html=True
)
