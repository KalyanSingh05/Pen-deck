#!/bin/bash

# Install pygame for framebuffer display
echo "Installing pygame for display..."

# Install system dependencies
sudo apt update
sudo apt install -y python3-pygame

# Install in virtual environment
cd /home/pi/pen-deck
source pen-deck-env/bin/activate

# Remove problematic luma libraries
pip uninstall -y luma.oled luma.lcd luma.core

# Install pygame
pip install pygame==2.1.0

echo "✅ Pygame installed successfully"
echo "Now run: python main.py"
