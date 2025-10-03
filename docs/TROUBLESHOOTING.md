# Troubleshooting Guide

## Common Issues and Solutions

### Display Issues

#### Display Not Initializing
**Symptoms**: Black screen, no display output
**Solutions**:
1. Check SPI is enabled:
   ```bash
   sudo raspi-config
   # Interface Options → SPI → Enable
   ```
2. Verify display connections
3. Check for conflicting processes:
   ```bash
   sudo lsof /dev/spidev0.0
   ```
4. Test with simple display script

#### Display Flickering or Artifacts
**Symptoms**: Screen flickers, corrupted display
**Solutions**:
1. Check power supply (use 2.5A minimum)
2. Reduce SPI bus speed in display_manager.py
3. Add ferrite cores to cables if available
4. Check for loose connections

#### Buttons Not Responding
**Symptoms**: Joystick/buttons don't work
**Solutions**:
1. Test GPIO pins:
   ```bash
   gpio readall
   gpio read 6  # Test UP button
   ```
2. Check for GPIO conflicts
3. Verify pull-up resistors are working
4. Test with simple GPIO script

### Network Issues

#### WiFi Not Connecting
**Symptoms**: Cannot connect to saved networks
**Solutions**:
1. Check WiFi credentials in config.json
2. Test manual connection:
   ```bash
   sudo wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
   ```
3. Check network signal strength
4. Restart network interface:
   ```bash
   sudo ifdown wlan0 && sudo ifup wlan0
   ```

#### Web UI Not Accessible
**Symptoms**: Cannot access web interface
**Solutions**:
1. Check if Flask is running:
   ```bash
   ps aux | grep python
   ```
2. Verify IP address:
   ```bash
   ip addr show wlan0
   ```
3. Check firewall settings
4. Test with curl:
   ```bash
   curl http://localhost:8080
   ```

### Tool Execution Issues

#### Tools Not Found
**Symptoms**: "Tool not found" errors
**Solutions**:
1. Install missing tools:
   ```bash
   sudo apt install nmap nikto aircrack-ng
   ```
2. Check PATH environment:
   ```bash
   which nmap
   echo $PATH
   ```
3. Verify tool permissions

#### Permission Denied Errors
**Symptoms**: Tools fail with permission errors
**Solutions**:
1. Run permission setup script:
   ```bash
   ./scripts/setup_permissions.sh
   ```
2. Add capabilities manually:
   ```bash
   sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/nmap
   ```
3. Check user groups:
   ```bash
   groups pi
   ```

### AI Assistant Issues

#### API Key Errors
**Symptoms**: "Invalid API key" or authentication errors
**Solutions**:
1. Verify API key in config.json
2. Check OpenAI account status
3. Test API key manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
   ```

#### Timeout Errors
**Symptoms**: AI requests timeout
**Solutions**:
1. Check internet connection
2. Increase timeout in ai_assistant.py
3. Try different model (gpt-3.5-turbo vs gpt-4)
4. Reduce max_tokens setting

### System Performance Issues

#### High CPU Usage
**Symptoms**: System slow, high load average
**Solutions**:
1. Check running processes:
   ```bash
   top
   htop
   ```
2. Reduce display refresh rate
3. Optimize tool commands
4. Add swap file if needed:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

#### Memory Issues
**Symptoms**: Out of memory errors, system freezing
**Solutions**:
1. Check memory usage:
   ```bash
   free -h
   ```
2. Increase GPU memory split:
   ```bash
   sudo raspi-config
   # Advanced Options → Memory Split → 64
   ```
3. Clean up old results:
   ```bash
   find results/ -name "*.txt" -mtime +30 -delete
   ```

### File System Issues

#### SD Card Corruption
**Symptoms**: File system errors, boot failures
**Solutions**:
1. Check file system:
   ```bash
   sudo fsck /dev/mmcblk0p2
   ```
2. Use high-quality SD card (Class 10+)
3. Enable regular backups
4. Consider read-only root filesystem

#### Permission Issues
**Symptoms**: Cannot write files, access denied
**Solutions**:
1. Check file permissions:
   ```bash
   ls -la /home/pi/pen-deck/
   ```
2. Fix ownership:
   ```bash
   sudo chown -R pi:pi /home/pi/pen-deck/
   ```
3. Set correct permissions:
   ```bash
   chmod 755 /home/pi/pen-deck/
   chmod 644 /home/pi/pen-deck/config.json
   ```

## Diagnostic Commands

### System Health Check
```bash
# Check system status
systemctl status pen-deck.service

# Check logs
journalctl -u pen-deck.service -f

# Check disk space
df -h

# Check memory
free -h

# Check temperature
vcgencmd measure_temp

# Check GPIO
gpio readall
```

### Network Diagnostics
```bash
# Check WiFi status
iwconfig wlan0

# Check network interfaces
ip addr show

# Test connectivity
ping -c 4 8.8.8.8

# Check DNS
nslookup google.com
```

### Application Logs
```bash
# View application logs
tail -f /home/pi/pen-deck/logs/pen-deck.log

# View error logs
tail -f /home/pi/pen-deck/logs/pen-deck-errors.log

# Check web UI logs
sudo journalctl -u pen-deck.service | grep Flask
```

## Getting Help

If you continue to experience issues:

1. Check the logs for detailed error messages
2. Run the diagnostic commands above
3. Create a backup of your configuration
4. Try the installation script again
5. Check the GitHub issues page for similar problems

For hardware-specific issues, consult the Waveshare documentation for your display HAT model.