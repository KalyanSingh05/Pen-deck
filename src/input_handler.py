"""
Input Handler for Pen-Deck
Handles on-screen keyboard and text input
"""

import time
import logging
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

class InputHandler:
    def __init__(self, display_manager):
        self.display = display_manager
        self.logger = logging.getLogger(__name__)
        
        self.keyboard_layout = [
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
            ['k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't'],
            ['u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3'],
            ['4', '5', '6', '7', '8', '9', '.', '-', '_', '@'],
            ['SPC', 'DEL', 'OK', 'CAN', '', '', '', '', '', '']
        ]
        
        self.current_row = 0
        self.current_col = 0
        self.input_active = False
        self.current_input = ""
        
    def get_text_input(self, title, prompt, initial_text=""):
        """Get text input from user using on-screen keyboard"""
        if not self.display.display_enabled:
            self.logger.warning("Text input in headless mode")
            return None
            
        self.current_input = initial_text
        self.input_active = True
        self.current_row = 0
        self.current_col = 0
        
        # Remove GPIO event detection, use polling
        pins = [self.display.PIN_UP, self.display.PIN_DOWN, self.display.PIN_LEFT, 
                self.display.PIN_RIGHT, self.display.PIN_CENTER, self.display.PIN_KEY1, 
                self.display.PIN_KEY2, self.display.PIN_KEY3]
        
        for pin in pins:
            try:
                GPIO.remove_event_detect(pin)
            except:
                pass
        
        # Track button states
        last_states = {pin: GPIO.input(pin) for pin in pins}
        
        try:
            while self.input_active:
                self._show_keyboard_screen(title, prompt)
                
                # Poll buttons manually
                for pin in pins:
                    current_state = GPIO.input(pin)
                    if current_state == GPIO.LOW and last_states[pin] == GPIO.HIGH:
                        self._handle_button_press(pin)
                        time.sleep(0.2)
                    last_states[pin] = current_state
                
                time.sleep(0.05)
                
            result = self.current_input if self.current_input else None
            
        except Exception as e:
            self.logger.error(f"Input error: {e}")
            result = None
        finally:
            self._restore_menu_callbacks()
            
        return result
    
    def _handle_button_press(self, pin):
        """Handle button press during text input"""
        if pin == self.display.PIN_UP:
            self._move_cursor_up()
        elif pin == self.display.PIN_DOWN:
            self._move_cursor_down()
        elif pin == self.display.PIN_LEFT:
            self._move_cursor_left()
        elif pin == self.display.PIN_RIGHT:
            self._move_cursor_right()
        elif pin == self.display.PIN_CENTER:
            self._select_key()
        elif pin == self.display.PIN_KEY1:
            self._confirm_input()
        elif pin == self.display.PIN_KEY2:
            self._cancel_input()
        elif pin == self.display.PIN_KEY3:
            self._backspace()
    
    def _restore_menu_callbacks(self):
        """Restore menu event detection after input"""
        pins = [self.display.PIN_UP, self.display.PIN_DOWN, self.display.PIN_LEFT, 
                self.display.PIN_RIGHT, self.display.PIN_CENTER, self.display.PIN_KEY1, 
                self.display.PIN_KEY2, self.display.PIN_KEY3]
        
        for pin in pins:
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.FALLING, 
                                    callback=self.display._button_callback, 
                                    bouncetime=300)
            except Exception as e:
                self.logger.warning(f"Failed to restore event for pin {pin}: {e}")
        
    def _move_cursor_up(self):
        """Move keyboard cursor up"""
        if self.current_row > 0:
            self.current_row -= 1
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
            while self.keyboard_layout[self.current_row][self.current_col] == '':
                if self.current_col > 0:
                    self.current_col -= 1
                else:
                    break
        else:
            self.current_col = len(self.keyboard_layout[self.current_row]) - 1
            while self.keyboard_layout[self.current_row][self.current_col] == '':
                self.current_col -= 1
            
    def _move_cursor_right(self):
        """Move keyboard cursor right"""
        max_col = len(self.keyboard_layout[self.current_row]) - 1
        if self.current_col < max_col:
            self.current_col += 1
            while self.current_col < max_col and \
                  self.keyboard_layout[self.current_row][self.current_col] == '':
                self.current_col += 1
        else:
            self.current_col = 0
            
    def _select_key(self):
        """Select current key"""
        if self.current_row < len(self.keyboard_layout):
            row = self.keyboard_layout[self.current_row]
            if self.current_col < len(row):
                key = row[self.current_col]
                if key:
                    self._process_key(key)
                
    def _process_key(self, key):
        """Process selected key"""
        if key == 'OK':
            self._confirm_input()
        elif key == 'CAN':
            self._cancel_input()
        elif key == 'DEL':
            self._backspace()
        elif key == 'SPC':
            self.current_input += ' '
        else:
            self.current_input += key
            
    def _confirm_input(self):
        """Confirm input and exit"""
        self.logger.info(f"Input confirmed: {self.current_input}")
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
            
            # Title
            draw.rectangle([(0, 0), (127, 12)], fill=(0, 100, 200))
            draw.text((2, 1), title[:15], font=self.display.font_small, fill=(255, 255, 255))
            
            # Input display
            draw.rectangle([(0, 14), (127, 28)], outline=(255, 255, 255))
            input_display = self.current_input
            if len(input_display) > 20:
                input_display = "..." + input_display[-17:]
            draw.text((2, 16), input_display + "_", font=self.display.font_small, fill=(0, 255, 0))
            
            # Keyboard
            start_y = 32
            key_width = 12
            key_height = 10
            gap = 1
            
            for row_idx, row in enumerate(self.keyboard_layout):
                y = start_y + (row_idx * (key_height + gap))
                
                for col_idx, key in enumerate(row):
                    if col_idx >= 10 or not key:
                        continue
                        
                    x = 2 + (col_idx * (key_width + gap))
                    
                    if row_idx == self.current_row and col_idx == self.current_col:
                        draw.rectangle([(x, y), (x+key_width-1, y+key_height-1)], fill=(255, 255, 255))
                        text_color = (0, 0, 0)
                    else:
                        draw.rectangle([(x, y), (x+key_width-1, y+key_height-1)], outline=(100, 100, 100))
                        text_color = (255, 255, 255)
                    
                    key_display = key[:3] if len(key) > 3 else key
                    draw.text((x + 2, y + 1), key_display, font=self.display.font_small, fill=text_color)
            
            # Instructions
            draw.rectangle([(0, 110), (127, 127)], fill=(50, 50, 50))
            draw.text((2, 112), "Joy:Move Ctr:Sel", font=self.display.font_small, fill=(255, 255, 255))
            draw.text((2, 120), "K1:OK K2:Can K3:Del", font=self.display.font_small, fill=(255, 255, 255))
            
            if self.display.st7735s:
                self.display.st7735s.display_image(image)
                
        except Exception as e:
            self.logger.error(f"Keyboard display error: {e}")
