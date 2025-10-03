"""
Input Handler for Pen-Deck
Handles on-screen keyboard and text input
"""

import time
from src.display_manager import DisplayManager

class InputHandler:
    def __init__(self, display_manager):
        self.display = display_manager
        self.keyboard_layout = [
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
            ['k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't'],
            ['u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4'],
            ['5', '6', '7', '8', '9', '0', '.', '-', '_', ' '],
            ['@', '/', ':', '?', '=', '&', '#', '[SPACE]', '[DEL]', '[OK]']
        ]
        
        self.current_row = 0
        self.current_col = 0
        self.input_active = False
        self.current_input = ""
        self.input_callbacks = {}
        
    def get_text_input(self, title, prompt, initial_text=""):
        """Get text input from user using on-screen keyboard"""
        self.current_input = initial_text
        self.input_active = True
        self.current_row = 0
        self.current_col = 0
        
        # Set up input callbacks
        original_callbacks = self.display.button_callbacks.copy()
        self._setup_input_callbacks()
        
        try:
            while self.input_active:
                self._show_keyboard_screen(title, prompt)
                time.sleep(0.1)
                
            # Restore original callbacks
            self.display.button_callbacks = original_callbacks
            
            return self.current_input if self.current_input else None
            
        except Exception as e:
            print(f"Input error: {e}")
            self.display.button_callbacks = original_callbacks
            return None
            
    def _setup_input_callbacks(self):
        """Setup button callbacks for input mode"""
        self.display.button_callbacks = {
            self.display.PIN_UP: self._move_cursor_up,
            self.display.PIN_DOWN: self._move_cursor_down,
            self.display.PIN_LEFT: self._move_cursor_left,
            self.display.PIN_RIGHT: self._move_cursor_right,
            self.display.PIN_CENTER: self._select_key,
            self.display.PIN_KEY1: self._confirm_input,
            self.display.PIN_KEY2: self._cancel_input,
            self.display.PIN_KEY3: self._backspace
        }
        
    def _move_cursor_up(self):
        """Move keyboard cursor up"""
        if self.current_row > 0:
            self.current_row -= 1
            
    def _move_cursor_down(self):
        """Move keyboard cursor down"""
        if self.current_row < len(self.keyboard_layout) - 1:
            self.current_row += 1
            
    def _move_cursor_left(self):
        """Move keyboard cursor left"""
        if self.current_col > 0:
            self.current_col -= 1
        else:
            self.current_col = len(self.keyboard_layout[self.current_row]) - 1
            
    def _move_cursor_right(self):
        """Move keyboard cursor right"""
        if self.current_col < len(self.keyboard_layout[self.current_row]) - 1:
            self.current_col += 1
        else:
            self.current_col = 0
            
    def _select_key(self):
        """Select current key"""
        if self.current_row < len(self.keyboard_layout):
            row = self.keyboard_layout[self.current_row]
            if self.current_col < len(row):
                key = row[self.current_col]
                self._process_key(key)
                
    def _process_key(self, key):
        """Process selected key"""
        if key == '[OK]':
            self._confirm_input()
        elif key == '[DEL]':
            self._backspace()
        elif key == '[SPACE]':
            self.current_input += ' '
        else:
            self.current_input += key
            
    def _confirm_input(self):
        """Confirm input and exit"""
        self.input_active = False
        
    def _cancel_input(self):
        """Cancel input and exit"""
        self.current_input = ""
        self.input_active = False
        
    def _backspace(self):
        """Remove last character"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            
    def _show_keyboard_screen(self, title, prompt):
        """Display on-screen keyboard"""
        try:
            if not self.display.display_enabled:
                # Fallback to simple text input
                print(f"\n{title}: {prompt}")
                print(f"Current input: {self.current_input}")
                print("Use buttons to navigate virtual keyboard")
                return
                
            from PIL import Image, ImageDraw
            
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Title
            draw.text((2, 2), title[:15], font=self.display.font_small, fill=(255, 255, 255))
            
            # Prompt
            draw.text((2, 15), prompt[:18], font=self.display.font_small, fill=(255, 255, 255))
            
            # Current input display
            input_display = self.current_input if len(self.current_input) <= 18 else "..." + self.current_input[-15:]
            draw.rectangle([(0, 28), (127, 42)], outline=(255, 255, 255))
            draw.text((2, 31), input_display, font=self.display.font_small, fill=(255, 255, 255))
            
            # Keyboard
            start_y = 45
            key_width = 12
            key_height = 10
            
            for row_idx, row in enumerate(self.keyboard_layout):
                y = start_y + (row_idx * (key_height + 2))
                
                for col_idx, key in enumerate(row):
                    if col_idx >= 10:  # Only show first 10 keys per row to fit screen
                        break
                        
                    x = 2 + (col_idx * (key_width + 1))
                    
                    # Highlight current key
                    if row_idx == self.current_row and col_idx == self.current_col:
                        draw.rectangle([(x-1, y-1), (x+key_width, y+key_height)], fill=(255, 255, 255))
                        text_color = (0, 0, 0)
                    else:
                        draw.rectangle([(x-1, y-1), (x+key_width, y+key_height)], outline=(255, 255, 255))
                        text_color = (255, 255, 255)
                        
                    # Display key (truncated for special keys)
                    key_display = key
                    if key.startswith('[') and key.endswith(']'):
                        key_display = key[1:3]  # Show first 2 chars of special keys
                        
                    draw.text((x, y), key_display[:2], font=self.display.font_small, fill=text_color)
                    
            # Instructions
            draw.text((2, 110), "K1:OK K2:Cancel K3:Del", font=self.display.font_small, fill=(255, 255, 255))
            
            # Display the keyboard
            if self.display.st7735s:
                self.display.st7735s.display_image(image)
                
        except Exception as e:
            print(f"Keyboard display error: {e}")
            
    def get_numeric_input(self, title, prompt, min_val=None, max_val=None):
        """Get numeric input with validation"""
        while True:
            text_input = self.get_text_input(title, prompt)
            
            if text_input is None:  # User cancelled
                return None
                
            try:
                value = float(text_input)
                
                if min_val is not None and value < min_val:
                    self.show_error(f"Value must be >= {min_val}")
                    continue
                    
                if max_val is not None and value > max_val:
                    self.show_error(f"Value must be <= {max_val}")
                    continue
                    
                return value
                
            except ValueError:
                self.show_error("Please enter a valid number")
                continue
                
    def get_choice_input(self, title, choices):
        """Get user choice from a list of options"""
        selected_index = 0
        choice_active = True
        
        # Setup choice callbacks
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
                self.display.show_menu(title, choices, selected_index)
                time.sleep(0.1)
                
            # Restore callbacks
            self.display.button_callbacks = original_callbacks
            
            return choices[selected_index] if selected_index >= 0 else None
            
        except Exception as e:
            print(f"Choice input error: {e}")
            self.display.button_callbacks = original_callbacks
            return None
            
    def show_error(self, message):
        """Show error message"""
        self.display.show_text_screen("Error", message)
        time.sleep(2)
