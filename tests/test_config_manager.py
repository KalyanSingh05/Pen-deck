#!/usr/bin/env python3
"""
Unit tests for ConfigManager
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.config_file.exists():
            self.config_file.unlink()
        os.rmdir(self.temp_dir)
        
    def test_default_config_creation(self):
        """Test that default config is created when file doesn't exist"""
        config = ConfigManager(str(self.config_file))
        
        # Check that config file was created
        self.assertTrue(self.config_file.exists())
        
        # Check default values
        self.assertIn('wifi_networks', config.config)
        self.assertIn('ai_assistant', config.config)
        self.assertIn('tools', config.config)
        self.assertEqual(config.get('system.log_level'), 'INFO')
        
    def test_config_loading(self):
        """Test loading existing config file"""
        # Create test config
        test_config = {
            "wifi_networks": [{"ssid": "test", "password": "pass", "priority": 1}],
            "ai_assistant": {"api_key": "test_key"},
            "system": {"log_level": "DEBUG"}
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        config = ConfigManager(str(self.config_file))
        
        # Check loaded values
        self.assertEqual(config.get('system.log_level'), 'DEBUG')
        self.assertEqual(config.get('ai_assistant.api_key'), 'test_key')
        
    def test_get_set_operations(self):
        """Test get and set operations with dot notation"""
        config = ConfigManager(str(self.config_file))
        
        # Test setting values
        config.set('ai_assistant.model', 'gpt-4')
        self.assertEqual(config.get('ai_assistant.model'), 'gpt-4')
        
        # Test nested setting
        config.set('new_section.nested.value', 'test')
        self.assertEqual(config.get('new_section.nested.value'), 'test')
        
    def test_wifi_network_management(self):
        """Test WiFi network management functions"""
        config = ConfigManager(str(self.config_file))
        
        # Add network
        config.add_wifi_network('TestSSID', 'TestPassword', 2)
        networks = config.get_wifi_networks()
        
        self.assertEqual(len(networks), 1)
        self.assertEqual(networks[0]['ssid'], 'TestSSID')
        self.assertEqual(networks[0]['priority'], 2)
        
        # Update existing network
        config.add_wifi_network('TestSSID', 'NewPassword', 3)
        networks = config.get_wifi_networks()
        
        self.assertEqual(len(networks), 1)
        self.assertEqual(networks[0]['password'], 'NewPassword')
        self.assertEqual(networks[0]['priority'], 3)
        
        # Remove network
        config.remove_wifi_network('TestSSID')
        networks = config.get_wifi_networks()
        
        self.assertEqual(len(networks), 0)
        
    def test_tool_command_management(self):
        """Test tool command management"""
        config = ConfigManager(str(self.config_file))
        
        # Set tool command
        config.set_tool_command('test_tool', 'test_command', 'echo {target}')
        
        commands = config.get_tool_commands('test_tool')
        self.assertEqual(commands['test_command'], 'echo {target}')
        
    def test_ai_config_management(self):
        """Test AI configuration management"""
        config = ConfigManager(str(self.config_file))
        
        # Update AI config
        config.set_ai_config(api_key='new_key', model='gpt-4', max_tokens=1000)
        
        ai_config = config.get_ai_config()
        self.assertEqual(ai_config['api_key'], 'new_key')
        self.assertEqual(ai_config['model'], 'gpt-4')
        self.assertEqual(ai_config['max_tokens'], 1000)

if __name__ == '__main__':
    unittest.main()