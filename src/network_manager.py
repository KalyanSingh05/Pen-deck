"""
Network Manager for WiFi connectivity
Handles WiFi connection, auto-connect, and network management
"""

import subprocess
import time
import re
import netifaces
import logging
from pathlib import Path

class NetworkManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.current_connection = None
        
    def scan_networks(self):
        """Scan for available WiFi networks"""
        try:
            result = subprocess.run(['sudo', 'iwlist', 'wlan0', 'scan'], 
                                  capture_output=True, text=True, timeout=30)
            
            networks = []
            if result.returncode == 0:
                # Parse scan results
                scan_output = result.stdout
                network_blocks = re.split(r'Cell \d+', scan_output)[1:]
                
                for block in network_blocks:
                    ssid_match = re.search(r'ESSID:"([^"]+)"', block)
                    signal_match = re.search(r'Signal level=(-?\d+)', block)
                    encryption_match = re.search(r'Encryption key:(on|off)', block)
                    
                    if ssid_match:
                        ssid = ssid_match.group(1)
                        signal = int(signal_match.group(1)) if signal_match else -100
                        encrypted = encryption_match.group(1) == 'on' if encryption_match else True
                        
                        networks.append({
                            'ssid': ssid,
                            'signal': signal,
                            'encrypted': encrypted
                        })
                        
            return sorted(networks, key=lambda x: x['signal'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            return []
            
    def connect_to_network(self, ssid, password=None):
        """Connect to a specific WiFi network"""
        try:
            # Kill any existing wpa_supplicant processes
            subprocess.run(['sudo', 'pkill', 'wpa_supplicant'], 
                         capture_output=True)
            time.sleep(2)
            
            # Create wpa_supplicant configuration
            wpa_config = self._create_wpa_config(ssid, password)
            config_path = '/tmp/wpa_supplicant.conf'
            
            with open(config_path, 'w') as f:
                f.write(wpa_config)
                
            # Start wpa_supplicant
            wpa_cmd = [
                'sudo', 'wpa_supplicant',
                '-B', '-i', 'wlan0',
                '-c', config_path,
                '-D', 'nl80211,wext'
            ]
            
            result = subprocess.run(wpa_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get IP address via DHCP
                dhcp_result = subprocess.run(['sudo', 'dhclient', 'wlan0'], 
                                           capture_output=True, text=True, timeout=30)
                
                if dhcp_result.returncode == 0:
                    self.current_connection = ssid
                    self.logger.info(f"Successfully connected to {ssid}")
                    return True
                else:
                    self.logger.error(f"DHCP failed for {ssid}")
                    return False
            else:
                self.logger.error(f"wpa_supplicant failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
            
    def _create_wpa_config(self, ssid, password):
        """Create wpa_supplicant configuration"""
        config = f"""ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=US

network={{
    ssid="{ssid}"
"""
        
        if password:
            config += f'    psk="{password}"\n'
        else:
            config += '    key_mgmt=NONE\n'
            
        config += "}\n"
        return config
        
    def auto_connect(self):
        """Auto-connect to the strongest available saved network"""
        try:
            saved_networks = self.config.get_wifi_networks()
            available_networks = self.scan_networks()
            
            if not saved_networks or not available_networks:
                return False
                
            # Sort saved networks by priority
            saved_networks.sort(key=lambda x: x.get('priority', 1), reverse=True)
            
            # Find the best available saved network
            for saved_net in saved_networks:
                for available_net in available_networks:
                    if saved_net['ssid'] == available_net['ssid']:
                        self.logger.info(f"Attempting to connect to {saved_net['ssid']}")
                        if self.connect_to_network(saved_net['ssid'], saved_net['password']):
                            return True
                        break
                        
            return False
            
        except Exception as e:
            self.logger.error(f"Auto-connect failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from current network"""
        try:
            subprocess.run(['sudo', 'pkill', 'wpa_supplicant'], capture_output=True)
            subprocess.run(['sudo', 'dhclient', '-r', 'wlan0'], capture_output=True)
            self.current_connection = None
            return True
        except Exception as e:
            self.logger.error(f"Disconnect failed: {e}")
            return False
            
    def get_status(self):
        """Get current network status"""
        try:
            status = {
                'connected': False,
                'ssid': None,
                'ip_address': None,
                'signal_strength': None
            }
            
            # Check if wlan0 is up and has an IP
            try:
                addresses = netifaces.ifaddresses('wlan0')
                if netifaces.AF_INET in addresses:
                    status['ip_address'] = addresses[netifaces.AF_INET][0]['addr']
                    status['connected'] = True
            except ValueError:
                pass
                
            # Get SSID if connected
            if status['connected']:
                try:
                    result = subprocess.run(['iwgetid', 'wlan0', '--raw'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        status['ssid'] = result.stdout.strip()
                except:
                    pass
                    
            # Get signal strength
            if status['ssid']:
                try:
                    result = subprocess.run(['iwconfig', 'wlan0'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        signal_match = re.search(r'Signal level=(-?\d+)', result.stdout)
                        if signal_match:
                            status['signal_strength'] = int(signal_match.group(1))
                except:
                    pass
                    
            return status
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {'connected': False, 'ssid': None, 'ip_address': None, 'signal_strength': None}
            
    def get_saved_networks(self):
        """Get list of saved networks"""
        return self.config.get_wifi_networks()
        
    def add_network(self, ssid, password, priority=1):
        """Add network to saved networks"""
        return self.config.add_wifi_network(ssid, password, priority)
        
    def remove_network(self, ssid):
        """Remove network from saved networks"""
        return self.config.remove_wifi_network(ssid)
        
    def is_connected(self):
        """Check if currently connected to any network"""
        status = self.get_status()
        return status['connected']
        
    def get_ip_address(self):
        """Get current IP address"""
        status = self.get_status()
        return status.get('ip_address')
        
    def restart_interface(self):
        """Restart the WiFi interface"""
        try:
            subprocess.run(['sudo', 'ifdown', 'wlan0'], capture_output=True)
            time.sleep(2)
            subprocess.run(['sudo', 'ifup', 'wlan0'], capture_output=True)
            time.sleep(5)
            return True
        except Exception as e:
            self.logger.error(f"Interface restart failed: {e}")
            return False