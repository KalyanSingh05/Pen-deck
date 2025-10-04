"""
Menu System for Pen-Deck
Handles menu navigation and user interaction
"""

import time
import threading
import logging
from src.tools.tool_manager import ToolManager
from src.ai_assistant import AIAssistant
from src.utils.system_info import SystemInfo
from src.input_handler import InputHandler

class MenuSystem:
    def __init__(self, display_manager, config_manager, network_manager):
        self.logger = logging.getLogger(__name__)
        self.display = display_manager
        self.config = config_manager
        self.network = network_manager
        self.tool_manager = ToolManager(config_manager)
        self.ai_assistant = AIAssistant(config_manager)
        self.system_info = SystemInfo()
        self.input_handler = InputHandler(display_manager)
        
        self.current_menu = "main"
        self.selected_index = 0
        self.scroll_offset = 0
        self.menu_stack = []
        self.running = True
        
        # Menu definitions
        self.menus = {
            "main": {
                "title": "Pen-Deck",
                "items": ["Pentest Tools", "AI Assistant", "Network Settings", "System Info", "Power Off"]
            },
            "pentest_tools": {
                "title": "Pentest Tools",
                "items": ["Nmap", "Nikto", "Bettercap", "Aircrack-ng", "Custom Command", "View Results"]
            },
            "nmap": {
                "title": "Nmap",
                "items": ["Quick Scan", "Aggressive Scan", "Version Scan", "Stealth Scan", "Custom"]
            },
            "nikto": {
                "title": "Nikto",
                "items": ["Basic Scan", "SSL Scan", "Custom"]
            },
            "bettercap": {
                "title": "Bettercap",
                "items": ["Network Discovery", "ARP Spoof", "Custom"]
            },
            "aircrack": {
                "title": "Aircrack-ng",
                "items": ["Monitor Mode", "Capture", "Custom"]
            },
            "network_settings": {
                "title": "Network",
                "items": ["View Status", "Saved Networks", "Add Network", "Auto Connect"]
            },
            "system_info": {
                "title": "System",
                "items": ["Hardware Info", "Network Info", "Disk Usage", "Processes"]
            }
        }
        
        self.setup_button_callbacks()
        
    def setup_button_callbacks(self):
        """Setup button callbacks for navigation"""
        try:
            self.display.set_button_callback(self.display.PIN_UP, self.move_up)
            self.display.set_button_callback(self.display.PIN_DOWN, self.move_down)
            self.display.set_button_callback(self.display.PIN_LEFT, self.go_back)
            self.display.set_button_callback(self.display.PIN_RIGHT, self.select_item)
            self.display.set_button_callback(self.display.PIN_CENTER, self.select_item)
            self.display.set_button_callback(self.display.PIN_KEY1, self.key1_pressed)
            self.display.set_button_callback(self.display.PIN_KEY2, self.key2_pressed)
            self.display.set_button_callback(self.display.PIN_KEY3, self.key3_pressed)
        except Exception as e:
            self.logger.error(f"Setup button callbacks error: {e}")
        
    def move_up(self):
        """Move selection up"""
        try:
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
            self.update_display()
        except Exception as e:
            self.logger.error(f"Move up error: {e}")
        
    def move_down(self):
        """Move selection down"""
        try:
            current_menu_items = len(self.menus[self.current_menu]["items"])
            if self.selected_index < current_menu_items - 1:
                self.selected_index += 1
                if self.selected_index >= self.scroll_offset + 6:
                    self.scroll_offset = self.selected_index - 5
            self.update_display()
        except Exception as e:
            self.logger.error(f"Move down error: {e}")
        
    def go_back(self):
        """Go back to previous menu"""
        try:
            if self.menu_stack:
                previous_menu, previous_index, previous_scroll = self.menu_stack.pop()
                self.current_menu = previous_menu
                self.selected_index = previous_index
                self.scroll_offset = previous_scroll
                self.update_display()
            else:
                # Already at main menu, do nothing
                self.logger.debug("Already at main menu, cannot go back")
        except Exception as e:
            self.logger.error(f"Go back error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def select_item(self):
        """Select current menu item"""
        try:
            current_menu_data = self.menus[self.current_menu]
            selected_item = current_menu_data["items"][self.selected_index]
            
            # Handle menu navigation
            if self.current_menu == "main":
                self.handle_main_menu(selected_item)
            elif self.current_menu == "pentest_tools":
                self.handle_pentest_menu(selected_item)
            elif self.current_menu in ["nmap", "nikto", "bettercap", "aircrack"]:
                self.handle_tool_selection(self.current_menu, selected_item)
            elif self.current_menu == "network_settings":
                self.handle_network_menu(selected_item)
            elif self.current_menu == "system_info":
                self.handle_system_menu(selected_item)
        except Exception as e:
            self.logger.error(f"Select item error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def handle_main_menu(self, item):
        """Handle main menu selections"""
        try:
            if item == "Pentest Tools":
                self.navigate_to_menu("pentest_tools")
            elif item == "AI Assistant":
                self.start_ai_assistant()
            elif item == "Network Settings":
                self.navigate_to_menu("network_settings")
            elif item == "System Info":
                self.navigate_to_menu("system_info")
            elif item == "Power Off":
                self.power_off()
        except Exception as e:
            self.logger.error(f"Handle main menu error: {e}")
            
    def handle_pentest_menu(self, item):
        """Handle pentest tools menu"""
        try:
            if item in ["Nmap", "Nikto", "Bettercap", "Aircrack-ng"]:
                menu_name = item.lower().replace("-", "")
                self.navigate_to_menu(menu_name)
            elif item == "Custom Command":
                self.custom_command()
            elif item == "View Results":
                self.view_results()
        except Exception as e:
            self.logger.error(f"Handle pentest menu error: {e}")
            
    def handle_tool_selection(self, tool, command):
        """Handle tool command selection"""
        try:
            if command == "Custom":
                target = self.input_handler.get_text_input("Custom Command", f"Enter {tool} command:")
                if target:
                    self.tool_manager.run_custom_command(tool, target)
            else:
                target = self.input_handler.get_text_input("Target", "Enter target IP/URL:")
                if target:
                    self.tool_manager.run_tool_command(tool, command, target)
            # Return to menu after command
            self.update_display()
        except Exception as e:
            self.logger.error(f"Handle tool selection error: {e}")
            self.update_display()
                
    def handle_network_menu(self, item):
        """Handle network settings menu"""
        try:
            if item == "View Status":
                self.show_network_status()
            elif item == "Saved Networks":
                self.show_saved_networks()
            elif item == "Add Network":
                self.add_network()
            elif item == "Auto Connect":
                self.network.auto_connect()
            # Return to menu
            self.update_display()
        except Exception as e:
            self.logger.error(f"Handle network menu error: {e}")
            self.update_display()
            
    def handle_system_menu(self, item):
        """Handle system info menu"""
        try:
            if item == "Hardware Info":
                info = self.system_info.get_hardware_info()
                self.display.show_system_info(info)
                time.sleep(3)
            elif item == "Network Info":
                info = self.system_info.get_network_info()
                self.display.show_system_info(info)
                time.sleep(3)
            elif item == "Disk Usage":
                info = self.system_info.get_disk_info()
                self.display.show_system_info(info)
                time.sleep(3)
            elif item == "Processes":
                info = self.system_info.get_process_info()
                self.display.show_text_screen("Processes", str(info))
                time.sleep(5)
            # Return to menu
            self.update_display()
        except Exception as e:
            self.logger.error(f"Handle system menu error: {e}")
            self.update_display()
            
    def navigate_to_menu(self, menu_name):
        """Navigate to a specific menu"""
        try:
            self.menu_stack.append((self.current_menu, self.selected_index, self.scroll_offset))
            self.current_menu = menu_name
            self.selected_index = 0
            self.scroll_offset = 0
            self.update_display()
        except Exception as e:
            self.logger.error(f"Navigate to menu error: {e}")
        
    def start_ai_assistant(self):
        """Start AI assistant interface"""
        try:
            query = self.input_handler.get_text_input("AI Assistant", "Enter your question:")
            if query:
                response = self.ai_assistant.get_response(query)
                self.display.show_text_screen("AI Response", response, 0)
                time.sleep(10)
            # Return to menu
            self.update_display()
        except Exception as e:
            self.logger.error(f"AI assistant error: {e}")
            self.update_display()
            
    def custom_command(self):
        """Run custom command"""
        try:
            command = self.input_handler.get_text_input("Custom Command", "Enter command:")
            if command:
                result = self.tool_manager.run_custom_command("custom", command)
                self.display.show_text_screen("Command Output", result)
                time.sleep(5)
            # Return to menu
            self.update_display()
        except Exception as e:
            self.logger.error(f"Custom command error: {e}")
            self.update_display()
            
    def view_results(self):
        """View saved results"""
        try:
            results = self.tool_manager.get_recent_results()
            if results:
                result_text = "\n".join(results)
                self.display.show_text_screen("Recent Results", result_text)
                time.sleep(10)
            else:
                self.display.show_text_screen("Results", "No results found")
                time.sleep(2)
            # Return to menu
            self.update_display()
        except Exception as e:
            self.logger.error(f"View results error: {e}")
            self.update_display()
            
    def show_network_status(self):
        """Show network connection status"""
        try:
            status = self.network.get_status()
            self.display.show_system_info(status)
            time.sleep(3)
        except Exception as e:
            self.logger.error(f"Show network status error: {e}")
        
    def show_saved_networks(self):
        """Show saved WiFi networks"""
        try:
            networks = self.network.get_saved_networks()
            if networks:
                network_list = "\n".join([net["ssid"] for net in networks])
            else:
                network_list = "No saved networks"
            self.display.show_text_screen("Saved Networks", network_list)
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"Show saved networks error: {e}")
        
    def add_network(self):
        """Add new WiFi network"""
        try:
            ssid = self.input_handler.get_text_input("Add Network", "Enter SSID:")
            if ssid:
                password = self.input_handler.get_text_input("Network Password", "Enter password:")
                if password:
                    self.network.add_network(ssid, password)
                    self.display.show_text_screen("Network Added", f"Added: {ssid}")
                    time.sleep(2)
        except Exception as e:
            self.logger.error(f"Add network error: {e}")
                
    def power_off(self):
        """Safely power off the system"""
        try:
            self.display.show_text_screen("Power Off", "Shutting down...")
            time.sleep(2)
            import os
            os.system("sudo shutdown -h now")
        except Exception as e:
            self.logger.error(f"Power off error: {e}")
        
    def key1_pressed(self):
        """Handle KEY1 press - Quick Select"""
        try:
            self.logger.debug("KEY1 pressed - Quick select")
            self.select_item()
        except Exception as e:
            self.logger.error(f"KEY1 press error: {e}")
        
    def key2_pressed(self):
        """Handle KEY2 press - Go Back"""
        try:
            self.logger.debug("KEY2 pressed - Go back")
            self.go_back()
        except Exception as e:
            self.logger.error(f"KEY2 press error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
    def key3_pressed(self):
        """Handle KEY3 press - Refresh Display"""
        try:
            self.logger.debug("KEY3 pressed - Refresh")
            self.update_display()
        except Exception as e:
            self.logger.error(f"KEY3 press error: {e}")
        
    def update_display(self):
        """Update the current display"""
        try:
            if self.current_menu in self.menus:
                current_menu_data = self.menus[self.current_menu]
                self.display.show_menu(
                    current_menu_data["title"],
                    current_menu_data["items"],
                    self.selected_index,
                    self.scroll_offset
                )
                self.logger.debug(f"Display updated: {self.current_menu}")
            else:
                self.logger.error(f"Invalid menu: {self.current_menu}")
        except Exception as e:
            self.logger.error(f"Display update error: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
    def run(self):
        """Main menu loop"""
        self.logger.info("Menu system starting...")
        
        # Check if display is actually available
        if not self.display.display_enabled:
            self.logger.warning("Display not enabled, menu system cannot run")
            return False
            
        try:
            # Show initial menu
            self.logger.info("Showing initial menu...")
            self.update_display()
            self.logger.info("Menu displayed, entering event loop")
        except Exception as e:
            self.logger.error(f"Failed to update initial display: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        
        while self.running:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.logger.info("Menu system interrupted")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Menu loop error: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(1)
            
        self.logger.info("Menu system stopped")
        return True
