# Pen-Deck - Cybersecurity Companion

A comprehensive penetration testing companion designed for Raspberry Pi Zero 2 W with Waveshare 1.44-inch display HAT.

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Waveshare 1.44-inch 128x128 Display HAT (with joystick and 3 buttons)
- 32 GB memory card
- WiFi connectivity

## Features

### 🎯 Core Functionality
- **Menu System**: Navigate through tools and settings using joystick/buttons
- **Pentest Tools Integration**: Pre-configured tools (Nmap, Nikto, Bettercap, Aircrack-ng)
- **AI Assistant**: OpenAI-powered cybersecurity guidance
- **Network Management**: Auto-connect WiFi with saved networks
- **Results Management**: Automatically save and view scan results
- **Web UI**: Remote configuration and management interface

### 🔧 Supported Tools
- **Nmap**: Quick scan, aggressive scan, version detection, stealth scan
- **Nikto**: Basic web vulnerability scanning, SSL scanning
- **Bettercap**: Network discovery, ARP spoofing
- **Aircrack-ng**: Monitor mode, packet capture
- **Custom Commands**: Run any command-line tool

### 🤖 AI Assistant Features
- Cybersecurity guidance and explanations
- Tool usage help and parameter suggestions
- Vulnerability analysis and next-step recommendations
- Configurable API settings (OpenAI GPT-3.5/GPT-4)

### 📱 Interface Options
- **Local Display**: 128x128 pixel menu system with joystick navigation
- **Web UI**: Full-featured web interface accessible via WiFi
- **On-screen Keyboard**: Text input for IPs, URLs, and AI queries

## Installation

### 1. System Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-venv git
sudo apt install -y nmap nikto aircrack-ng
sudo apt install -y wireless-tools wpasupplicant dhcpcd5

# Install Bettercap (if desired)
# Follow official Bettercap installation guide
```

### 2. Install Pen-Deck
```bash
# Clone or copy the project files to your Pi
cd /home/pi
# (Copy all project files to this directory)

# Create virtual environment
python3 -m venv pen-deck-env
source pen-deck-env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Hardware Setup
- Connect the Waveshare 1.44-inch display HAT to your Raspberry Pi Zero 2 W
- Enable SPI interface: `sudo raspi-config` → Interface Options → SPI → Enable

### 4. Configuration
1. Edit `config.json` to add your WiFi networks and AI API key
2. Adjust tool commands as needed for your specific use case
3. Set appropriate permissions for network tools if needed

## Usage

### Starting Pen-Deck
```bash
cd /home/pi/pen-deck
source pen-deck-env/bin/activate
python main.py
```

### Navigation Controls
- **Joystick**: Navigate menus (Up/Down/Left/Right/Center)
- **KEY1**: Confirm/OK
- **KEY2**: Cancel/Back  
- **KEY3**: Backspace/Delete

### Menu Structure
```
Pen-Deck
├── Pentest Tools
│   ├── Nmap (Quick, Aggressive, Version, Stealth scans)
│   ├── Nikto (Basic, SSL scans)
│   ├── Bettercap (Discovery, ARP spoof)
│   ├── Aircrack-ng (Monitor, Capture)
│   ├── Custom Command
│   └── View Results
├── AI Assistant
├── Network Settings
│   ├── View Status
│   ├── Saved Networks
│   ├── Add Network
│   └── Auto Connect
├── System Info
│   ├── Hardware Info
│   ├── Network Info
│   ├── Disk Usage
│   └── Processes
└── Power Off
```

### Web Interface
1. Connect to WiFi network
2. Find the Pi's IP address (shown in System Info)
3. Open browser to `http://[PI_IP]:8080`
4. Configure tools, manage networks, view results remotely

## Configuration

### WiFi Networks (`config.json`)
```json
{
  "wifi_networks": [
    {
      "ssid": "YourNetwork",
      "password": "YourPassword", 
      "priority": 1
    }
  ]
}
```

### AI Assistant Setup
1. Get OpenAI API key from https://platform.openai.com/
2. Add to config.json or via Web UI:
```json
{
  "ai_assistant": {
    "api_key": "your-openai-api-key",
    "model": "gpt-3.5-turbo",
    "max_tokens": 500
  }
}
```

### Custom Tool Commands
Add your own tool commands in `config.json`:
```json
{
  "tools": {
    "custom_tool": {
      "scan_command": "your-tool -options {target}"
    }
  }
}
```

## File Structure
```
pen-deck/
├── main.py                 # Main application entry point
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── src/
│   ├── display_manager.py  # Display and GPIO handling
│   ├── menu_system.py      # Menu navigation logic
│   ├── config_manager.py   # Configuration management
│   ├── network_manager.py  # WiFi connectivity
│   ├── ai_assistant.py     # AI integration
│   ├── input_handler.py    # On-screen keyboard
│   ├── web_ui.py          # Flask web interface
│   ├── tools/
│   │   └── tool_manager.py # Tool execution
│   └── utils/
│       ├── logger.py       # Logging setup
│       └── system_info.py  # System information
├── templates/
│   └── index.html         # Web UI template
├── results/               # Scan results storage
└── logs/                  # Application logs
```

## Results Storage

All scan results are automatically saved to the `results/` directory with timestamps:
- Format: `{tool}_{target}_{timestamp}.txt`
- Viewable via display menu or web interface
- Results include command, output, timestamps, and execution details

## Troubleshooting

### Display Issues
- Verify SPI is enabled: `sudo raspi-config`
- Check GPIO connections
- Ensure display HAT is properly seated

### Network Issues
- Check `sudo iwconfig` for interface status
- Verify WiFi credentials in config.json
- Try manual connection: `sudo wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf`

### Tool Issues
- Install missing tools: `sudo apt install [tool-name]`
- Check tool paths: `which nmap`
- Verify permissions for network tools

### Permission Issues
```bash
# Add user to required groups
sudo usermod -a -G netdev pi

# Set capabilities for network tools (if needed)
sudo setcap cap_net_admin,cap_net_raw+eip /usr/bin/nmap
```

## Auto-Start Setup

To run Pen-Deck automatically on boot:

1. Create systemd service:
```bash
sudo nano /etc/systemd/system/pen-deck.service
```

2. Add service configuration:
```ini
[Unit]
Description=Pen-Deck Cybersecurity Companion
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pen-deck
Environment=PATH=/home/pi/pen-deck/pen-deck-env/bin
ExecStart=/home/pi/pen-deck/pen-deck-env/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable service:
```bash
sudo systemctl enable pen-deck.service
sudo systemctl start pen-deck.service
```

## Security Notes

- Keep your API keys secure and never commit them to version control
- Regularly update the system and dependencies
- Use strong WiFi passwords
- Be responsible with penetration testing tools - only test systems you own or have permission to test
- Consider network isolation when running potentially disruptive tools

## Contributing

This is a modular system designed for easy expansion:
- Add new tools in `src/tools/tool_manager.py`
- Extend the menu system in `src/menu_system.py`
- Add new web interface features in `src/web_ui.py`
- Customize display layouts in `src/display_manager.py`

## License

This project is for educational and authorized security testing purposes only. Users are responsible for complying with all applicable laws and regulations.