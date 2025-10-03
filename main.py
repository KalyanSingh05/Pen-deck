#!/usr/bin/env python3
"""
Pen-Deck - Cybersecurity Companion
Main application entry point
"""

import sys
import time
import threading
import logging
import signal
from pathlib import Path

# Local imports
from src.display_manager import DisplayManager
from src.menu_system import MenuSystem
from src.config_manager import ConfigManager
from src.network_manager import NetworkManager
from src.web_ui import WebUI
from src.utils.logger import setup_logger

class PenDeck:
    def __init__(self):
        """Initialize Pen-Deck application"""
        self.setup_directories()
        self.logger = setup_logger()
        self.logger.info("Initializing Pen-Deck components...")
        
        self.config_manager = ConfigManager()
        self.logger.info("Config manager initialized")
        
        self.display_manager = DisplayManager()
        self.logger.info("Display manager initialized")
        
        self.network_manager = NetworkManager(self.config_manager)
        self.logger.info("Network manager initialized")
        
        self.menu_system = MenuSystem(
            self.display_manager, 
            self.config_manager, 
            self.network_manager
        )
        self.logger.info("Menu system initialized")
        
        self.web_ui = WebUI(self.config_manager)
        self.logger.info("Web UI initialized")
        
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['results', 'logs', 'temp']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
    def start_web_ui(self):
        """Start web UI in separate thread"""
        try:
            self.logger.info("Starting Web UI thread...")
            web_thread = threading.Thread(target=self.web_ui.run, daemon=True)
            web_thread.start()
            self.logger.info("Web UI started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Web UI: {e}")
            return False
            
    def auto_connect_wifi(self):
        """Auto-connect to strongest available network"""
        try:
            self.logger.info("Attempting WiFi auto-connect...")
            self.network_manager.auto_connect()
        except Exception as e:
            self.logger.error(f"Auto WiFi connection failed: {e}")
            
    def run(self):
        """Main application loop"""
        self.logger.info("Starting Pen-Deck...")
        
        # Initialize display
        self.logger.info("Initializing display...")
        self.display_manager.initialize()
        
        # Check if display actually initialized successfully
        if self.display_manager.display_enabled and self.display_manager.st7735s and self.display_manager.st7735s.initialized:
            self.logger.info("Display enabled, showing splash screen...")
            try:
                self.display_manager.show_splash_screen()
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Splash screen failed: {e}")
                self.display_manager.display_enabled = False
        else:
            self.logger.warning("Display initialization failed - running in headless mode")
            self.display_manager.display_enabled = False
            print("Pen-Deck running in headless mode (no display)")
            print("Access web UI at: http://[PI_IP]:8080")
        
        # Auto-connect to WiFi
        self.logger.info("Starting WiFi auto-connect...")
        try:
            self.auto_connect_wifi()
        except Exception as e:
            self.logger.error(f"WiFi auto-connect failed: {e}")
        
        # Start web UI
        self.logger.info("Starting Web UI...")
        web_started = self.start_web_ui()
        if not web_started:
            self.logger.warning("Web UI failed to start")
        
        # Give web UI time to start
        time.sleep(2)
        
        # Start main menu loop
        self.logger.info("Starting menu system...")
        try:
            if self.display_manager.display_enabled and self.display_manager.st7735s and self.display_manager.st7735s.initialized:
                # Run menu system in main thread
                try:
                    self.logger.info("Starting display-based menu system...")
                    self.menu_system.run()
                except KeyboardInterrupt:
                    self.logger.info("Menu system interrupted by user")
                except Exception as e:
                    self.logger.error(f"Menu system error: {e}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't exit, continue to headless mode
                    self.logger.info("Falling back to headless mode...")
                    self.display_manager.display_enabled = False
                    # Continue to headless mode below
            
            # If we reach here, either display failed or we're in headless mode
            if not (self.display_manager.display_enabled and self.display_manager.st7735s and self.display_manager.st7735s.initialized):
                # Headless mode - just keep running
                self.logger.info("Running in headless mode - Web UI available")
                print("Pen-Deck is running in headless mode")
                print("Access the web interface at: http://[PI_IP]:8080")
                print("Press Ctrl+C to stop")
                
                while self.running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Shutting down Pen-Deck...")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("Cleaning up resources...")
            self.running = False
            self.display_manager.cleanup()
            self.logger.info("Pen-Deck shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        app = PenDeck()
        app.run()
    except Exception as e:
        print(f"Failed to start Pen-Deck: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
