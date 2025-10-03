#!/bin/bash

# Fixed Pen-Deck Installation Script
# For Raspberry Pi Zero 2 W with Waveshare 1.44" Display HAT



echo "🔒 Pen-Deck Installation Script (Fixed)"
echo "======================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    build-essential \
    libjpeg-dev \
    libfreetype6-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    zlib1g-dev \
    libatlas-base-dev \
    wireless-tools \
    wpasupplicant \
    dhcpcd5 \
    hostapd \
    dnsmasq \
    python3-setuptools \
    python3-wheel

# Install penetration testing tools
echo "🔧 Installing penetration testing tools..."
sudo apt install -y \
    nmap \
    nikto \
    aircrack-ng \
    tcpdump \
    netcat-openbsd \
    dnsutils \
    whois \
    curl \
    wget

# Install Bettercap (optional)
echo "🔧 Installing Bettercap..."
if ! command -v bettercap &> /dev/null; then
    echo "Installing Bettercap dependencies..."
    sudo apt install -y libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev
    
    # Download and install Bettercap (correct URL for ARM)
    BETTERCAP_VERSION="2.32.0"
    BETTERCAP_URL="https://github.com/bettercap/bettercap/releases/download/v${BETTERCAP_VERSION}/bettercap-v${BETTERCAP_VERSION}-linux-arm.zip"
    
    echo "Downloading Bettercap from: $BETTERCAP_URL"
    if wget "$BETTERCAP_URL" -O bettercap.zip; then
        if unzip bettercap.zip; then
            sudo mv bettercap /usr/local/bin/
            rm bettercap.zip
            
            # Set capabilities
            sudo setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/bettercap
            
            echo "✅ Bettercap installed successfully"
        else
            echo "⚠️  Failed to extract Bettercap, continuing without it"
            rm -f bettercap.zip
        fi
    else
        echo "⚠️  Failed to download Bettercap, trying alternative method..."
        
        # Try installing via Go if available
        if command -v go &> /dev/null; then
            echo "Installing Bettercap via Go..."
            go install github.com/bettercap/bettercap@latest
            sudo mv ~/go/bin/bettercap /usr/local/bin/ 2>/dev/null || echo "Go installation failed"
        else
            echo "⚠️  Bettercap installation skipped - will continue without it"
        fi
    fi
else
    echo "✅ Bettercap already installed"
fi
    
    # Set capabilities
    sudo setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/bettercap
    
    echo "✅ Bettercap installed successfully"
else
    echo "✅ Bettercap already installed"
fi

# Enable SPI interface
echo "🔧 Configuring SPI interface..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "⚠️  SPI enabled - reboot required after installation"
fi

# Create Pen-Deck directory
INSTALL_DIR="/home/$USER/pen-deck"
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv pen-deck-env
source pen-deck-env/bin/activate

# Upgrade pip and setuptools
echo "📦 Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install dependencies one by one to avoid conflicts
echo "📦 Installing Python dependencies (this may take a while)..."

# Install core dependencies first
pip install RPi.GPIO==0.7.1
pip install gpiozero==1.6.2
pip install Pillow==9.5.0
pip install psutil==5.9.5
pip install netifaces==0.11.0
pip install requests==2.31.0

# Install Flask and related packages
pip install MarkupSafe==2.1.3
pip install Werkzeug==2.2.3
pip install Flask==2.2.5
pip install Flask-CORS==4.0.0

# Install display library
pip install luma.oled==3.8.1

# Install AI and other packages
pip install openai==0.28.1
pip install jsonschema==4.17.3

# Try to install wifi package (may fail on some systems)
pip install python-wifi==0.6.1 || echo "⚠️  python-wifi installation failed, WiFi features may be limited"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p results logs temp static templates

# Set up permissions
echo "🔒 Setting up permissions..."
# Add user to necessary groups
sudo usermod -a -G netdev,gpio,spi,i2c "$USER"

# Set capabilities for network tools
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/nmap || echo "⚠️  Could not set nmap capabilities"

# Create systemd service
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/pen-deck.service > /dev/null <<EOF
[Unit]
Description=Pen-Deck Cybersecurity Companion
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/pen-deck-env/bin
ExecStart=$INSTALL_DIR/pen-deck-env/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure WiFi country (required for some regions)
echo "🌍 Configuring WiFi country..."
sudo raspi-config nonint do_wifi_country US

# Create desktop shortcut (if desktop environment is available)
if [ -d "/home/$USER/Desktop" ]; then
    echo "🖥️  Creating desktop shortcut..."
    tee "/home/$USER/Desktop/pen-deck.desktop" > /dev/null <<EOF
[Desktop Entry]
Name=Pen-Deck
Comment=Cybersecurity Companion
Exec=$INSTALL_DIR/pen-deck-env/bin/python $INSTALL_DIR/main.py
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;Security;
EOF
    chmod +x "/home/$USER/Desktop/pen-deck.desktop"
fi

# Create configuration backup
echo "💾 Creating configuration backup..."
cp config.json config.json.backup

# Final setup steps
echo "✅ Installation completed successfully!"
echo
echo "📋 Next Steps:"
echo "1. Edit config.json to add your WiFi networks and API keys:"
echo "   nano $INSTALL_DIR/config.json"
echo
echo "2. Test the installation:"
echo "   cd $INSTALL_DIR"
echo "   source pen-deck-env/bin/activate"
echo "   python main.py"
echo
echo "3. Enable auto-start (optional):"
echo "   sudo systemctl enable pen-deck.service"
echo
echo "4. If SPI was enabled, reboot the system:"
echo "   sudo reboot"
echo
echo "🌐 Web UI will be available at: http://[PI_IP]:8080"
echo "🔧 Hardware: Connect Waveshare 1.44\" Display HAT before first run"
echo
echo "📖 For detailed usage instructions, see README.md"
echo
echo "⚠️  Important:"
echo "- Add your OpenAI API key to config.json for AI assistant"
echo "- Configure WiFi networks in config.json"
echo "- Only use penetration testing tools on networks you own or have permission to test"

# Check if reboot is needed
if grep -q "dtparam=spi=on" /boot/config.txt && [ ! -e /dev/spidev0.0 ]; then
    echo
    echo "🔄 Reboot required to enable SPI interface"
    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
fi

echo "🎉 Pen-Deck installation complete!"
