"""
Configuration Manager for Pen-Deck
Handles loading and saving configuration from config.json
"""

import json
import os
from pathlib import Path
import logging

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self.default_config = {
            "wifi_networks": [],
            "ai_assistant": {
                "api_key": "",
                "model": "gpt-3.5-turbo",
                "max_tokens": 500,
                "temperature": 0.7,
                "provider": "openai"
            },
            "tools": {
                "nmap": {
                    "quick_scan": "nmap -T4 -F {target}",
                    "aggressive_scan": "nmap -A -T4 {target}",
                    "version_scan": "nmap -sV {target}",
                    "stealth_scan": "nmap -sS -T2 {target}"
                },
                "nikto": {
                    "basic_scan": "nikto -h {target}",
                    "ssl_scan": "nikto -h {target} -ssl"
                },
                "bettercap": {
                    "network_discovery": "bettercap -eval 'net.probe on; net.show'",
                    "arp_spoof": "bettercap -T {target}"
                },
                "aircrack": {
                    "monitor_mode": "airmon-ng start wlan0",
                    "capture": "airodump-ng wlan0mon"
                }
            },
            "display": {
                "brightness": 128,
                "contrast": 128,
                "scroll_speed": 2
            },
            "system": {
                "log_level": "INFO",
                "auto_save_results": True,
                "web_ui_port": 8080
            }
        }
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.config = self._merge_configs(self.default_config, self.config)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self.config = self.default_config.copy()
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            return False
            
    def get(self, key_path, default=None):
        """Get configuration value using dot notation (e.g., 'ai_assistant.api_key')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
            
        # Set the final value
        config_ref[keys[-1]] = value
        
        # Save the configuration
        return self.save_config()
        
    def get_wifi_networks(self):
        """Get WiFi networks configuration"""
        return self.config.get('wifi_networks', [])
        
    def add_wifi_network(self, ssid, password, priority=1):
        """Add WiFi network to configuration"""
        networks = self.get_wifi_networks()
        
        # Check if network already exists
        for network in networks:
            if network['ssid'] == ssid:
                network['password'] = password
                network['priority'] = priority
                return self.save_config()
                
        # Add new network
        networks.append({
            'ssid': ssid,
            'password': password,
            'priority': priority
        })
        
        self.config['wifi_networks'] = networks
        return self.save_config()
        
    def remove_wifi_network(self, ssid):
        """Remove WiFi network from configuration"""
        networks = self.get_wifi_networks()
        self.config['wifi_networks'] = [n for n in networks if n['ssid'] != ssid]
        return self.save_config()
        
    def get_tool_commands(self, tool_name):
        """Get commands for a specific tool"""
        return self.config.get('tools', {}).get(tool_name, {})
        
    def set_tool_command(self, tool_name, command_name, command_template):
        """Set command template for a tool"""
        if 'tools' not in self.config:
            self.config['tools'] = {}
        if tool_name not in self.config['tools']:
            self.config['tools'][tool_name] = {}
            
        self.config['tools'][tool_name][command_name] = command_template
        return self.save_config()
        
    def get_ai_config(self):
        """Get AI assistant configuration"""
        return self.config.get('ai_assistant', {})
        
    def set_ai_config(self, **kwargs):
        """Update AI assistant configuration"""
        if 'ai_assistant' not in self.config:
            self.config['ai_assistant'] = {}
            
        self.config['ai_assistant'].update(kwargs)
        return self.save_config()
        
    def _merge_configs(self, default, user):
        """Recursively merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        return self.save_config()
        
    def export_config(self, export_path):
        """Export current configuration to a file"""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error exporting config: {e}")
            return False
            
    def import_config(self, import_path):
        """Import configuration from a file"""
        try:
            with open(import_path, 'r') as f:
                imported_config = json.load(f)
            
            # Validate and merge with defaults
            self.config = self._merge_configs(self.default_config, imported_config)
            return self.save_config()
        except Exception as e:
            logging.error(f"Error importing config: {e}")
            return False