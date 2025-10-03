# Hardware Setup Guide

## Required Hardware

- Raspberry Pi Zero 2 W
- Waveshare 1.44-inch 128x128 Display HAT
- 32 GB microSD card (Class 10 recommended)
- Power supply (5V 2.5A recommended)

## Display HAT Connection

The Waveshare 1.44-inch Display HAT connects directly to the Raspberry Pi GPIO pins:

### Pin Connections
- VCC → 3.3V (Pin 1)
- GND → Ground (Pin 6)
- DIN → GPIO 10 (MOSI)
- CLK → GPIO 11 (SCLK)
- CS → GPIO 8 (CE0)
- DC → GPIO 24
- RST → GPIO 25
- BL → GPIO 18 (PWM)

### Joystick and Buttons
- UP → GPIO 6
- DOWN → GPIO 19
- LEFT → GPIO 5
- RIGHT → GPIO 26
- CENTER → GPIO 13
- KEY1 → GPIO 21
- KEY2 → GPIO 20
- KEY3 → GPIO 16

## Raspberry Pi Configuration

### Enable SPI Interface
```bash
sudo raspi-config
```
Navigate to: Interface Options → SPI → Enable

### Enable GPIO
```bash
sudo raspi-config
```
Navigate to: Interface Options → GPIO → Enable

### Memory Split (Optional)
For better performance with the display:
```bash
sudo raspi-config
```
Navigate to: Advanced Options → Memory Split → Set to 64

## Testing the Display

After installation, test the display with:
```bash
cd /home/pi/pen-deck
source pen-deck-env/bin/activate
python -c "
from src.display_manager import DisplayManager
dm = DisplayManager()
if dm.initialize():
    print('Display initialized successfully!')
    dm.show_splash_screen()
    import time
    time.sleep(3)
    dm.cleanup()
else:
    print('Display initialization failed!')
"
```

## Troubleshooting

### Display Not Working
1. Check SPI is enabled: `lsmod | grep spi`
2. Verify connections are secure
3. Check for GPIO conflicts: `gpio readall`

### Button Input Issues
1. Test GPIO pins: `gpio read <pin_number>`
2. Check for pull-up resistors
3. Verify pin assignments in code

### Performance Issues
1. Increase GPU memory split
2. Disable unnecessary services
3. Use faster SD card (Class 10 or better)

## Power Considerations

The Raspberry Pi Zero 2 W with display typically consumes:
- Idle: ~200mA
- Active scanning: ~400-600mA
- Peak usage: ~800mA

Use a quality power supply rated for at least 2.5A to ensure stable operation.