# BusyTag Libraries

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A monorepo containing BusyTag device management libraries for multiple platforms.

## 📦 Packages

### [busy-tag-dotnet](./busy-tag-dotnet)

[![NuGet Version](https://img.shields.io/nuget/v/BusyTag.Lib.svg)](https://www.nuget.org/packages/BusyTag.Lib/)
[![.NET](https://img.shields.io/badge/.NET-8.0%20%7C%209.0-blue)](https://dotnet.microsoft.com/)

A powerful .NET library for BusyTag device management via serial communication. Supports Windows and macOS platforms.

**Features:**
- Cross-platform device discovery
- Robust serial communication
- Complete file management
- Advanced LED control
- Device configuration
- Real-time notifications
- Firmware update support

[📚 Documentation](./busy-tag-dotnet/README.md)

### [busy-tag-python](./busy-tag-python)

🚧 **Coming Soon** - Python implementation based on the .NET library

A Python library for BusyTag device management, providing the same powerful features in a Pythonic API.

**Planned Features:**
- Cross-platform device discovery
- Serial communication
- File management
- LED control
- Device configuration
- Async/await support

## 🚀 Quick Start

Choose your preferred platform:

### .NET
```bash
cd busy-tag-dotnet
dotnet build
```

### Python
```bash
cd busy-tag-python
# Coming soon
```

## 🏗️ Repository Structure

```
busytag-lib/
├── busy-tag-dotnet/     # .NET implementation
│   ├── BusyTag.Lib.csproj
│   ├── BusyTag.Lib.sln
│   └── README.md
├── busy-tag-python/     # Python implementation (coming soon)
│   └── README.md
├── .github/             # GitHub workflows and configuration
├── LICENSE              # MIT License
└── README.md           # This file
```

## 📋 System Requirements

### .NET Library
- .NET Runtime: 8.0 or 9.0
- OS: Windows 10+, macOS 10.15+
- Hardware: BusyTag device with compatible firmware (v0.7+)

### Python Library
- Python: 3.8+ (planned)
- OS: Windows, macOS, Linux (planned)
- Hardware: BusyTag device with compatible firmware (v0.7+)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [BusyTag Website](https://www.busy-tag.com)
- [NuGet Package](https://www.nuget.org/packages/BusyTag.Lib/)
- [Documentation](./busy-tag-dotnet/README.md)

---

<div align="center">

**Made with ❤️ by [BUSY TAG SIA](https://www.busy-tag.com)**

*Empowering developers to create amazing IoT experiences*

</div>
