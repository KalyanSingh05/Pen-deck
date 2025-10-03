#!/usr/bin/env python3
"""
Unit tests for ToolManager
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.tool_manager import ToolManager
from config_manager import ConfigManager

class TestToolManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
        # Create mock config manager
        self.config_manager = ConfigManager(str(self.config_file))
        
        # Change to temp directory for results
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.tool_manager = ToolManager(self.config_manager)
        
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @patch('subprocess.run')
    def test_successful_command_execution(self, mock_run):
        """Test successful command execution"""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.tool_manager.run_tool_command('nmap', 'quick_scan', '127.0.0.1')
        
        self.assertIn("Success!", result)
        self.assertIn("Test output", result)
        
        # Check that results file was created
        results_files = list(Path('results').glob('*.txt'))
        self.assertEqual(len(results_files), 1)
        
    @patch('subprocess.run')
    def test_failed_command_execution(self, mock_run):
        """Test failed command execution"""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result
        
        result = self.tool_manager.run_tool_command('nmap', 'quick_scan', '127.0.0.1')
        
        self.assertIn("Error", result)
        self.assertIn("Command failed", result)
        
    @patch('subprocess.run')
    def test_command_timeout(self, mock_run):
        """Test command timeout handling"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired('test', 300)
        
        result = self.tool_manager.run_tool_command('nmap', 'quick_scan', '127.0.0.1')
        
        self.assertIn("timed out", result)
        
    def test_get_recent_results(self):
        """Test getting recent results"""
        # Create some test result files
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        
        test_files = [
            'nmap_test1_20231201_120000.txt',
            'nikto_test2_20231201_130000.txt'
        ]
        
        for filename in test_files:
            (results_dir / filename).write_text("Test content")
            
        recent = self.tool_manager.get_recent_results()
        
        self.assertEqual(len(recent), 2)
        self.assertTrue(any('nmap_test1' in item for item in recent))
        self.assertTrue(any('nikto_test2' in item for item in recent))
        
    def test_get_result_content(self):
        """Test getting result file content"""
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        
        test_content = "Test result content"
        test_file = results_dir / "test_result.txt"
        test_file.write_text(test_content)
        
        content = self.tool_manager.get_result_content("test_result.txt")
        
        self.assertEqual(content, test_content)
        
    def test_delete_result(self):
        """Test deleting result file"""
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        
        test_file = results_dir / "test_result.txt"
        test_file.write_text("Test content")
        
        # Verify file exists
        self.assertTrue(test_file.exists())
        
        # Delete file
        success = self.tool_manager.delete_result("test_result.txt")
        
        self.assertTrue(success)
        self.assertFalse(test_file.exists())

if __name__ == '__main__':
    unittest.main()