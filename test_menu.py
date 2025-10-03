#!/usr/bin/env python3
"""
Quick test to verify menu display is working
"""

import sys
import time
sys.path.insert(0, '/home/pi/pen-deck')

from src.display_manager import DisplayManager
from PIL import Image, ImageDraw

def test_menu():
    print("Initializing display...")
    display = DisplayManager()
    
    if not display.initialize():
        print("Display init failed")
        return
    
    print("Display initialized!")
    time.sleep(2)
    
    print("Testing menu display...")
    
    # Test 1: Simple menu
    menu_items = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]
    
    for selected in range(5):
        print(f"Showing menu with item {selected} selected...")
        display.show_menu("Test Menu", menu_items, selected, 0)
        time.sleep(1.5)
    
    print("Menu test complete!")
    
    # Test 2: Text screen
    print("Testing text screen...")
    display.show_text_screen("Test Text", "This is a test message\nLine 2\nLine 3\nLine 4", 0)
    time.sleep(2)
    
    # Test 3: System info
    print("Testing system info...")
    info = {
        "CPU": "50%",
        "Memory": "256MB",
        "Disk": "5GB",
        "Network": "Connected"
    }
    display.show_system_info(info)
    time.sleep(2)
    
    print("All tests passed!")
    display.cleanup()

if __name__ == "__main__":
    test_menu()
