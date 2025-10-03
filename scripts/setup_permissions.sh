#!/bin/bash

# Setup permissions for Pen-Deck tools
echo "Setting up permissions for penetration testing tools..."

# Add user to necessary groups
sudo usermod -a -G netdev,gpio,spi,i2c pi

# Set capabilities for network tools (allows running without sudo)
echo "Setting capabilities for network tools..."

# Nmap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/nmap 2>/dev/null || echo "Warning: Could not set nmap capabilities"

# Tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump 2>/dev/null || echo "Warning: Could not set tcpdump capabilities"

# Bettercap (if installed)
if command -v bettercap &> /dev/null; then
    sudo setcap cap_net_raw,cap_net_admin=eip $(which bettercap) 2>/dev/null || echo "Warning: Could not set bettercap capabilities"
fi

# Create udev rules for GPIO access
echo "Creating udev rules for GPIO access..."
sudo tee /etc/udev/rules.d/99-gpio.rules > /dev/null <<EOF
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Permissions setup complete!"
echo "Note: You may need to log out and back in for group changes to take effect."