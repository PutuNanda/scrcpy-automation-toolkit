# scrcpy Automation Toolkit

Streamline your Android device mirroring experience with automated connection management and seamless reconnection capabilities.

![scrcpy](https://img.shields.io/badge/scrcpy-automated-blue) ![Python](https://img.shields.io/badge/python-3.6%2B-green) ![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

## ✨ Features

-   **🔌 Multi-Connection Support**: Automatically connect via USB, Local WiFi, or Tailscale.
-   **🎯 Priority-Based Connection**: Configure your preferred connection method order.
-   **🔄 Auto-Reconnect**: Automatically reconnects when the connection is lost.
-   **📱 Device Detection**: Smart device discovery and selection.
-   **🎨 Beautiful Interface**: Colorful, user-friendly terminal interface.
-   **⚡ Quick Setup**: Easy configuration and desktop shortcuts.

## 🚀 Quick Start

### Prerequisites

-   **Python 3.6 or higher** - [Download here](https://www.python.org/downloads/)
-   **Android Device** with USB Debugging enabled.
-   **scrcpy** (included in the package).

### Step-by-Step Setup

1.  **Enable Developer Options on Your Android Device:**
    -   Go to `Settings` → `About Phone`.
    -   Tap `Build Number` 7 times until "You are now a developer!" appears.

2.  **Enable USB Debugging:**
    -   Go to `Settings` → `Developer Options`.
    -   Enable `USB Debugging`.
    -   Allow USB debugging when prompted.

3.  **Initial Device Detection:**
    ```bash
    # Connect your device via USB and run:
    python what-is-my-device.py
    ```

4.  **Configure Your Device:**
    -   Select your device from the list.
    -   Copy the device information to `config.json`.
    -   Customize connection preferences if needed.

5.  **Run Automated Mirroring:**
    ```bash
    python run-scrcpy.py
    ```

## ⚙️ Configuration

Edit `config.json` to customize your setup:

```json
{
    "device_id": "08990372CO005820",
    "device_name": "TECNO_LG7n",
    "local_ip": "192.168.1.30",
    "tailscale_ip": "100.73.249.128",
    "port": "5555",
    "scrcpy_folder": "scrcpy-win64-v3.2",
    "timeout_delay": "3",
    "auto_reconnect_delay": "3",
    "priority": ["tailscale", "local-ip", "usb"]
}
```

### Configuration Options

-   **`device_id`**: Your device's unique identifier.
-   **`device_name`**: Your device's model name.
-   **`local_ip`**: Local network IP (requires static IP for reliability).
-   **`tailscale_ip`**: Tailscale VPN IP (optional).
-   **`priority`**: Connection method preference order.

## 🖥️ Desktop Shortcut

Create a desktop shortcut for quick access:

**Windows:**
-   Right-click `run-scrcpy.py`.
-   Select `Send to` → `Desktop (create shortcut)`.

**Linux:**
```bash
cp run-scrcpy.py ~/Desktop/
```

**macOS:**
-   Drag `run-scrcpy.py` to the Dock.

## 🌐 Network Setup Tips

### Local WiFi Connection
-   Ensure your device has a **static IP address**.
-   Dynamic IPs may cause connection failures due to IP changes.
-   Set static IP in your router settings or device network configuration.

### Tailscale VPN
-   Install Tailscale on both computer and mobile device.
-   Join the same Tailscale network.
-   Use the Tailscale IP provided in the app.

## 🛠️ Troubleshooting

### Common Issues

1.  **"No devices detected"**
    -   Check USB cable connection.
    -   Verify USB Debugging is enabled.
    -   Allow USB Debugging permission on device.

2.  **"Device offline"**
    -   Unlock your device screen.
    -   Check if USB Debugging is still enabled.
    -   Restart ADB: `adb kill-server && adb start-server`.

3.  **Wireless connection fails**
    -   Verify device and computer are on the same network.
    -   Check firewall settings.
    -   Ensure static IP configuration.

## 📁 Project Structure

```
scrcpy-automation-toolkit/
├── config.json              # Configuration file
├── what-is-my-device.py     # Device detection tool
├── run-scrcpy.py           # Main automation script
└── scrcpy-win64-v3.2/      # scrcpy binaries
    ├── scrcpy.exe
    ├── adb.exe
    └── ...
```

## 🤝 Contributing

We welcome contributions! Feel free to submit issues and enhancement requests.

## 📄 Licensing

This project uses **scrcpy** as a dependency. scrcpy is developed by Genymobile and includes contributions from its authors.

**Copyright (C) 2018 Genymobile**
**Copyright (C) 2018–2025 Romain Vimont**

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
http://www.apache.org/licenses/LICENSE-2.0

The full original scrcpy license is included in:
`third_party/scrcpy/LICENSE`

---

**Enjoy seamless Android mirroring!** 🚀📱

*For more information about scrcpy, visit: https://github.com/Genymobile/scrcpy*