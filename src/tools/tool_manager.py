"""
Tool Manager for Pen-Deck
Handles execution of penetration testing tools
"""

import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime
import threading

class ToolManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.current_process = None
        self.running = False
        
    def run_tool_command(self, tool_name, command_name, target):
        """
        Run a specific tool command with target
        
        Args:
            tool_name: Name of the tool (nmap, nikto, etc.)
            command_name: Command name (quick_scan, basic_scan, etc.)
            target: Target IP/URL/hostname
        
        Returns:
            Command output or error message
        """
        try:
            # Get command template from config
            commands = self.config.get_tool_commands(tool_name)
            
            if not commands or command_name not in commands:
                return f"Error: Command '{command_name}' not found for tool '{tool_name}'"
            
            command_template = commands[command_name]
            
            # Replace placeholders
            command = command_template.replace('{target}', target)
            command = command.replace('{port}', '80')  # Default port
            
            self.logger.info(f"Executing: {command}")
            
            # Execute command
            result = self._execute_command(command, tool_name, command_name)
            
            # Save results
            if self.config.get('system.auto_save_results', True):
                self._save_result(tool_name, command_name, target, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running tool command: {e}")
            return f"Error: {str(e)}"
            
    def run_custom_command(self, tool_name, command):
        """
        Run a custom command
        
        Args:
            tool_name: Tool identifier
            command: Full command to execute
        
        Returns:
            Command output or error message
        """
        try:
            self.logger.info(f"Executing custom command: {command}")
            
            result = self._execute_command(command, tool_name, "custom")
            
            # Save results
            if self.config.get('system.auto_save_results', True):
                self._save_result(tool_name, "custom", "N/A", result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running custom command: {e}")
            return f"Error: {str(e)}"
            
    def _execute_command(self, command, tool_name, command_name):
        """
        Execute shell command with timeout
        
        Args:
            command: Command to execute
            tool_name: Tool name for logging
            command_name: Command type for logging
        
        Returns:
            Command output string
        """
        try:
            self.running = True
            timeout = self.config.get('advanced.scan_timeout_seconds', 300)
            
            # Execute command
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = self.current_process.communicate(timeout=timeout)
                
                # Combine output
                output = ""
                if stdout:
                    output += stdout
                if stderr:
                    output += f"\n--- STDERR ---\n{stderr}"
                
                if not output.strip():
                    output = "Command completed with no output"
                
                return output
                
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                return f"Error: Command timed out after {timeout} seconds"
                
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return f"Error executing command: {str(e)}"
            
        finally:
            self.running = False
            self.current_process = None
            
    def _save_result(self, tool_name, command_name, target, output):
        """
        Save command results to file
        
        Args:
            tool_name: Tool name
            command_name: Command type
            target: Target address
            output: Command output
        """
        try:
            results_dir = Path(self.config.get('system.results_directory', 'results'))
            results_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{tool_name}_{command_name}_{timestamp}.txt"
            filepath = results_dir / filename
            
            # Write results
            with open(filepath, 'w') as f:
                f.write(f"Tool: {tool_name}\n")
                f.write(f"Command: {command_name}\n")
                f.write(f"Target: {target}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(output)
            
            self.logger.info(f"Results saved to: {filepath}")
            
            # Clean up old results if needed
            self._cleanup_old_results(results_dir)
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            
    def _cleanup_old_results(self, results_dir):
        """
        Clean up old result files based on config
        
        Args:
            results_dir: Path to results directory
        """
        try:
            max_files = self.config.get('system.max_results_files', 100)
            
            # Get all result files sorted by modification time
            result_files = sorted(
                results_dir.glob('*.txt'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Delete oldest files if over limit
            if len(result_files) > max_files:
                for old_file in result_files[max_files:]:
                    old_file.unlink()
                    self.logger.info(f"Deleted old result file: {old_file}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old results: {e}")
            
    def get_recent_results(self, limit=10):
        """
        Get list of recent result files
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of result filenames
        """
        try:
            results_dir = Path(self.config.get('system.results_directory', 'results'))
            
            if not results_dir.exists():
                return []
            
            result_files = sorted(
                results_dir.glob('*.txt'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            return [f.name for f in result_files[:limit]]
            
        except Exception as e:
            self.logger.error(f"Error getting recent results: {e}")
            return []
            
    def get_result_content(self, filename):
        """
        Get content of a specific result file
        
        Args:
            filename: Result filename
        
        Returns:
            File content or None
        """
        try:
            results_dir = Path(self.config.get('system.results_directory', 'results'))
            filepath = results_dir / filename
            
            if filepath.exists() and filepath.is_file():
                with open(filepath, 'r') as f:
                    return f.read()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error reading result file: {e}")
            return None
            
    def stop_current_command(self):
        """Stop currently running command"""
        try:
            if self.current_process and self.running:
                self.current_process.kill()
                self.running = False
                self.logger.info("Command stopped by user")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping command: {e}")
            return False
            
    def is_tool_available(self, tool_name):
        """
        Check if a tool is installed and available
        
        Args:
            tool_name: Tool name to check
        
        Returns:
            Boolean indicating availability
        """
        try:
            result = subprocess.run(
                ['which', tool_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking tool availability: {e}")
            return False
            
    def get_available_tools(self):
        """
        Get list of available tools
        
        Returns:
            Dictionary of tool names and their availability
        """
        tools = {
            'nmap': self.is_tool_available('nmap'),
            'nikto': self.is_tool_available('nikto'),
            'bettercap': self.is_tool_available('bettercap'),
            'aircrack-ng': self.is_tool_available('aircrack-ng'),
            'netcat': self.is_tool_available('nc'),
            'dig': self.is_tool_available('dig'),
            'nslookup': self.is_tool_available('nslookup'),
            'tcpdump': self.is_tool_available('tcpdump')
        }
        return tools
