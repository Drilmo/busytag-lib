# BusyTag Python DevContainer

This development container provides a secure, isolated environment for BusyTag Python development with network security.

## 🚀 Features

- **Python 3.12** with uv package manager
- **Claude Code** for AI-assisted development
- **Network Security**: Restricted network access to approved domains only
- **USB Device Support**: Access to serial ports for BusyTag devices
- **Streamlit**: Pre-configured for demo application (port 8501)
- **Development Tools**: git, zsh, fzf, and more
- **Python Extensions**: Black, Ruff, Pylance, Jupyter

## 📦 Pre-installed

- **uv**: Fast Python package manager
- **Claude Code**: AI coding assistant
- **Python tools**: black, ruff, mypy, pytest
- **USB tools**: usbutils, libusb
- **Git enhancements**: git-delta for better diffs

## 🔒 Network Security

The container implements strict network security with iptables:

### Allowed Domains

**Python/Package Management:**
- pypi.org
- files.pythonhosted.org
- astral.sh (for uv)

**Development:**
- github.com (via GitHub API meta)
- api.anthropic.com (Claude)

**Other:**
- registry.npmjs.org (for Node packages)
- sentry.io, statsig.com (telemetry)

### Network Features

- Firewall initialization on container start
- DNS resolution preserved
- SSH access maintained
- Local network access enabled
- All other outbound traffic blocked by default

## 🛠️ Usage

### 1. Open in VS Code

With the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed:

1. Open the `busy-tag-python` folder in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for the container to build and initialize

### 2. Manual Container Build

```bash
cd busy-tag-python/.devcontainer
docker build -t busytag-python-dev .
docker run -it --privileged --cap-add=NET_ADMIN --cap-add=NET_RAW busytag-python-dev
```

### 3. First Time Setup

The container automatically runs on creation:

```bash
# Firewall initialization
sudo /usr/local/bin/init-firewall.sh

# Install Python dependencies
cd /workspace
uv pip install -e '.[dev,demo]'
```

## 📱 Working with BusyTag Devices

### USB Access

The container has privileged access to USB devices:

```bash
# List USB devices
lsusb

# Check for serial ports
ls -la /dev/ttyUSB* /dev/ttyACM*
```

### Running the Demo

```bash
# Launch Streamlit demo (auto-forwards to port 8501)
cd demo
streamlit run app.py
```

### Running Examples

```bash
cd demo/examples

# Test connection
python basic_connection.py

# LED control
python led_control.py

# File management
python file_management.py
```

## 🔧 Development Commands

```bash
# Install dependencies with uv
uv pip install -e '.[dev]'

# Run tests
uv run pytest

# Format code
uv run black busytag/

# Lint code
uv run ruff check busytag/

# Type check
uv run mypy busytag/
```

## 🐛 Troubleshooting

### Firewall Issues

If you can't access required domains:

```bash
# Check firewall status
sudo iptables -L -n -v

# Check allowed domains
sudo ipset list allowed-domains

# Re-initialize firewall
sudo /usr/local/bin/init-firewall.sh
```

### USB Device Not Found

```bash
# Check if device is visible
lsusb

# Check device permissions
ls -la /dev/ttyUSB* /dev/ttyACM*

# Verify privileged mode
docker inspect <container-id> | grep Privileged
```

### Python Package Installation Fails

```bash
# Verify uv is installed
uv --version

# Check network access to PyPI
curl -I https://pypi.org

# Try manual installation
uv pip install --no-cache <package>
```

## 📝 Customization

### Adding Allowed Domains

Edit `.devcontainer/init-firewall.sh`:

```bash
for domain in \
    "pypi.org" \
    "your-custom-domain.com"; do  # Add here
    # ...
done
```

### Changing Python Version

Edit `.devcontainer/Dockerfile`:

```dockerfile
FROM python:3.11-slim-bookworm  # Change version
```

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json`:

```json
"extensions": [
  "ms-python.python",
  "your-extension-id"  // Add here
]
```

## 🔐 Security Notes

- Container runs with `--privileged` for USB and network control
- Network access is restricted by iptables
- Only approved domains are accessible
- Local network (host) access is allowed
- All outbound traffic is logged

## 📚 Additional Resources

- [Dev Containers Documentation](https://containers.dev/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [uv Documentation](https://github.com/astral-sh/uv)
- [BusyTag Python Library](../README.md)

## 🤝 Contributing

To modify the devcontainer setup:

1. Make changes to `.devcontainer/` files
2. Test by rebuilding the container
3. Commit and push changes
4. Document any new dependencies or domains

---

**Note**: This devcontainer is optimized for development with network security. For production use, consider additional security hardening.
