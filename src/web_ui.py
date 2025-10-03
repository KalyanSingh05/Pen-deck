"""
Web UI for Pen-Deck
Flask-based web interface for remote configuration and management
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import logging
from pathlib import Path
import threading
import time

class WebUI:
    def __init__(self, config_manager):
        self.config = config_manager
        self.app = Flask(__name__, 
                        template_folder='../templates',
                        static_folder='static')
        CORS(self.app)
        self.setup_routes()
        self.logger = logging.getLogger(__name__)
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard"""
            return render_template('index.html')
            
        @self.app.route('/api/config')
        def get_config():
            """Get current configuration"""
            return jsonify(self.config.config)
            
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update configuration"""
            try:
                config_data = request.json
                
                # Update specific sections
                if 'wifi_networks' in config_data:
                    self.config.config['wifi_networks'] = config_data['wifi_networks']
                    
                if 'ai_assistant' in config_data:
                    self.config.config['ai_assistant'].update(config_data['ai_assistant'])
                    
                if 'tools' in config_data:
                    self.config.config['tools'].update(config_data['tools'])
                    
                if 'display' in config_data:
                    self.config.config['display'].update(config_data['display'])
                    
                if 'system' in config_data:
                    self.config.config['system'].update(config_data['system'])
                    
                # Save configuration
                success = self.config.save_config()
                
                return jsonify({'success': success})
                
            except Exception as e:
                self.logger.error(f"Config update error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/wifi/scan')
        def scan_wifi():
            """Scan for WiFi networks"""
            try:
                # This would integrate with network_manager
                # For now, return mock data
                networks = [
                    {'ssid': 'Network1', 'signal': -45, 'encrypted': True},
                    {'ssid': 'Network2', 'signal': -67, 'encrypted': False}
                ]
                return jsonify(networks)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/wifi/connect', methods=['POST'])
        def connect_wifi():
            """Connect to WiFi network"""
            try:
                data = request.json
                ssid = data.get('ssid')
                password = data.get('password')
                
                # Add to saved networks
                success = self.config.add_wifi_network(ssid, password)
                
                return jsonify({'success': success})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/tools')
        def get_tools():
            """Get available tools and commands"""
            tools = self.config.get('tools', {})
            return jsonify(tools)
            
        @self.app.route('/api/tools', methods=['POST'])
        def update_tools():
            """Update tool commands"""
            try:
                tools_data = request.json
                self.config.config['tools'].update(tools_data)
                success = self.config.save_config()
                return jsonify({'success': success})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/results')
        def get_results():
            """Get recent results"""
            try:
                results_dir = Path('results')
                results = []
                
                if results_dir.exists():
                    for result_file in sorted(results_dir.glob('*.txt'), 
                                            key=lambda x: x.stat().st_mtime, 
                                            reverse=True)[:20]:
                        results.append({
                            'filename': result_file.name,
                            'size': result_file.stat().st_size,
                            'modified': result_file.stat().st_mtime
                        })
                        
                return jsonify(results)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/results/<filename>')
        def get_result_content(filename):
            """Get content of specific result file"""
            try:
                result_path = Path('results') / filename
                if result_path.exists() and result_path.is_file():
                    with open(result_path, 'r') as f:
                        content = f.read()
                    return jsonify({'content': content})
                else:
                    return jsonify({'error': 'File not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/system/info')
        def get_system_info():
            """Get system information"""
            try:
                import psutil
                import platform
                
                info = {
                    'platform': platform.platform(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory()._asdict(),
                    'disk': psutil.disk_usage('/')._asdict(),
                    'uptime': time.time() - psutil.boot_time()
                }
                
                return jsonify(info)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/system/shutdown', methods=['POST'])
        def shutdown_system():
            """Shutdown the system"""
            try:
                import os
                threading.Timer(2.0, lambda: os.system('sudo shutdown -h now')).start()
                return jsonify({'success': True, 'message': 'Shutting down in 2 seconds'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
                
    def run(self):
        """Run the web server"""
        try:
            port = self.config.get('system.web_ui_port', 8080)
            self.app.run(
                host='0.0.0.0',
                port=port,
                debug=False,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"Web UI start failed: {e}")
