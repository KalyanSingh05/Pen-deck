"""
Input Handler for Pen-Deck
Handles on-screen keyboard and text input
"""

import time
import logging
from PIL import Image, ImageDraw

class InputHandler:
    def __init__(self, display_manager):
        self.display = display_manager
        self.logger = logging.getLogger(__name__)
        
        # Simplified keyboard layout for 128x128 screen
        self.keyboard_layout = [
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
            ['k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't'],
            ['u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3'],
            ['4', '5', '6', '7', '8', '9', '.', '-', '_', '@'],
            ['SPC', 'DEL', 'OK', 'CANCEL', '', '', '', '', '', '']
        ]
        
        self.current_row = 0
        self.current_col = 0
        self.input_active = False
        self.current_input = ""
        self.original_callbacks = {}
        
    def get_text_input(self, title, prompt, initial_text=""):
        """Get text input from user using on-screen keyboard"""
        if not self.display.display_enabled:
            # Headless mode - just return empty or ask via console
            self.logger.warning("Text input requested in headless mode")
            return None
            
        self.current_input = initial_text
        self.input_active = True
        self.current_row = 0
        self.current_col = 0
        
        # Save original callbacks
        self.original_callbacks = self.display.button_callbacks.copy()
        
        # Set up input callbacks
        self._setup_input_callbacks()
        
        try:
            # Show keyboard and wait for input
            while self.input_active:
                self._show_keyboard_screen(title, prompt)
                time.sleep(0.05)  # Faster refresh for better responsiveness
                
            # Restore original callbacks
            self.display.button_callbacks = self.original_callbacks.copy()
            
            result = self.current_input if self.current_input else None
            self.logger.info(f"Text input completed: '{result}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Input error: {e}")
            # Restore callbacks on error
            self.display.button_callbacks = self.original_callbacks.copy()
            return None
            
    def _setup_input_callbacks(self):
        """Setup button callbacks for input mode"""
        self.display.button_callbacks = {
            self.display.PIN_UP: self._move_cursor_up,
            self.display.PIN_DOWN: self._move_cursor_down,
            self.display.PIN_LEFT: self._move_cursor_left,
            self.display.PIN_RIGHT: self._move_cursor_right,
            self.display.PIN_CENTER: self._select_key,
            self.display.PIN_KEY1: self._confirm_input,  # OK
            self.display.PIN_KEY2: self._cancel_input,   # Cancel
            self.display.PIN_KEY3: self._backspace       # Backspace
        }
        
    def _move_cursor_up(self):
        """Move keyboard cursor up"""
        if self.current_row > 0:
            self.current_row -= 1
            # Skip empty cells
            while self.current_col < len(self.keyboard_layout[self.current_row]) and \
                  self.keyboard_layout[self.current_row][self.current_col] == '':
                if self.current_col > 0:
                    self.current_col -= 1
                else:
                    break
            
    def _move_cursor_down(self):
        """Move keyboard cursor down"""
        if self.current_row < len(self.keyboard_layout) - 1:
            self.current_row += 1
            # Skip empty cells
            while self.current_col < len(self.keyboard_layout[self.current_row]) and \
                  self.keyboard_layout[self.current_row][self.current_col] == '':
                if self.current_col > 0:
                    self.current_col -= 1
                else:
                    break
            
    def _move_cursor_left(self):
        """Move keyboard cursor left"""
        if self.current_col > 0:
            self.current_col -= 1
            # Skip empty cells
            while self.keyboard_layout[self.current_row][self.current_col] == '':
                if self.current_col > 0:
                    self.current_col -= 1
                else:
                    break
        else:
            # Wrap to end of row
            self.current_col = len(self.keyboard_layout[self.current_row]) - 1
            while self.keyboard_layout[self.current_row][self.current_col] == '':
                self.current_col -= 1
            
    def _move_cursor_right(self):
        """Move keyboard cursor right"""
        max_col = len(self.keyboard_layout[self.current_row]) - 1
        if self.current_col < max_col:
            self.current_col += 1
            # Skip empty cells
            while self.current_col < max_col and \
                  self.keyboard_layout[self.current_row][self.current_col] == '':
                self.current_col += 1
        else:
            # Wrap to start of row
            self.current_col = 0
            
    def _select_key(self):
        """Select current key"""
        if self.current_row < len(self.keyboard_layout):
            row = self.keyboard_layout[self.current_row]
            if self.current_col < len(row):
                key = row[self.current_col]
                if key:  # Not empty
                    self._process_key(key)
                
    def _process_key(self, key):
        """Process selected key"""
        if key == 'OK':
            self._confirm_input()
        elif key == 'CANCEL':
            self._cancel_input()
        elif key == 'DEL':
            self._backspace()
        elif key == 'SPC':
            self.current_input += ' '
        else:
            self.current_input += key
            
    def _confirm_input(self):
        """Confirm input and exit"""
        self.logger.info("Input confirmed")
        self.input_active = False
        
    def _cancel_input(self):
        """Cancel input and exit"""
        self.logger.info("Input cancelled")
        self.current_input = ""
        self.input_active = False
        
    def _backspace(self):
        """Remove last character"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            
    def _show_keyboard_screen(self, title, prompt):
        """Display on-screen keyboard"""
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Title bar
            draw.rectangle([(0, 0), (127, 12)], fill=(0, 100, 200))
            draw.text((2, 1), title[:15], font=self.display.font_small, fill=(255, 255, 255))
            
            # Input display area
            draw.rectangle([(0, 14), (127, 28)], outline=(255, 255, 255))
            input_display = self.current_input
            if len(input_display) > 20:
                input_display = "..." + input_display[-17:]
            draw.text((2, 16), input_display + "_", font=self.display.font_small, fill=(0, 255, 0))
            
            # Keyboard grid
            start_y = 32
            key_width = 12
            key_height = 10
            gap = 1
            
            for row_idx, row in enumerate(self.keyboard_layout):
                y = start_y + (row_idx * (key_height + gap))
                
                for col_idx, key in enumerate(row):
                    if col_idx >= 10 or not key:  # Only show first 10 keys per row
                        continue
                        
                    x = 2 + (col_idx * (key_width + gap))
                    
                    # Highlight current key
                    if row_idx == self.current_row and col_idx == self.current_col:
                        draw.rectangle([(x, y), (x+key_width-1, y+key_height-1)], 
                                     fill=(255, 255, 255))
                        text_color = (0, 0, 0)
                    else:
                        draw.rectangle([(x, y), (x+key_width-1, y+key_height-1)], 
                                     outline=(100, 100, 100))
                        text_color = (255, 255, 255)
                    
                    # Display key
                    key_display = key
                    if len(key) > 3:
                        key_display = key[:2]  # Truncate long keys
                        
                    # Center text in key
                    text_x = x + 2
                    text_y = y + 1
                    draw.text((text_x, text_y), key_display, 
                            font=self.display.font_small, fill=text_color)
            
            # Instructions at bottom
            draw.rectangle([(0, 110), (127, 127)], fill=(50, 50, 50))
            draw.text((2, 112), "Arrows:Move Ctr:Sel", font=self.display.font_small, fill=(255, 255, 255))
            draw.text((2, 120), "K1:OK K2:Can K3:Del", font=self.display.font_small, fill=(255, 255, 255))
            
            # Display the keyboard
            if self.display.st7735s:
                self.display.st7735s.display_image(image)
                
        except Exception as e:
            self.logger.error(f"Keyboard display error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def get_numeric_input(self, title, prompt, min_val=None, max_val=None):
        """Get numeric input with validation"""
        while True:
            text_input = self.get_text_input(title, prompt)
            
            if text_input is None:  # User cancelled
                return None
                
            try:
                value = float(text_input)
                
                if min_val is not None and value < min_val:
                    self._show_error(f"Min: {min_val}")
                    continue
                    
                if max_val is not None and value > max_val:
                    self._show_error(f"Max: {max_val}")
                    continue
                    
                return value
                
            except ValueError:
                self._show_error("Invalid number")
                continue
                
    def get_choice_input(self, title, choices):
        """Get user choice from a list of options"""
        selected_index = 0
        choice_active = True
        
        # Save original callbacks
        original_callbacks = self.display.button_callbacks.copy()
        
        def move_up():
            nonlocal selected_index
            if selected_index > 0:
                selected_index -= 1
                
        def move_down():
            nonlocal selected_index
            if selected_index < len(choices) - 1:
                selected_index += 1
                
        def select_choice():
            nonlocal choice_active
            choice_active = False
            
        def cancel_choice():
            nonlocal choice_active, selected_index
            choice_active = False
            selected_index = -1
            
        self.display.button_callbacks = {
            self.display.PIN_UP: move_up,
            self.display.PIN_DOWN: move_down,
            self.display.PIN_CENTER: select_choice,
            self.display.PIN_KEY1: select_choice,
            self.display.PIN_KEY2: cancel_choice
        }
        
        try:
            while choice_active:
                self.display.show_menu(title, choices, selected_index, 0)
                time.sleep(0.1)
                
            # Restore callbacks
            self.display.button_callbacks = original_callbacks.copy()
            
            return choices[selected_index] if selected_index >= 0 else None
            
        except Exception as e:
            self.logger.error(f"Choice input error: {e}")
            self.display.button_callbacks = original_callbacks.copy()
            return None
            
    def _show_error(self, message):
        """Show error message briefly"""
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            draw.rectangle([(0, 0), (127, 127)], outline=(255, 0, 0), width=2)
            draw.text((10, 50), "ERROR", font=self.display.font_large, fill=(255, 0, 0))
            draw.text((10, 70), message[:18], font=self.display.font_small, fill=(255, 255, 255))
            
            if self.display.st7735s:
                self.display.st7735s.display_image(image)
            time.sleep(2)
        except:
            pass
