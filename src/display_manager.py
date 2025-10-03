"""
Display Manager for Waveshare 1.44-inch HAT
Based on official Waveshare code with correct pin assignments
"""

import time
from PIL import Image, ImageDraw, ImageFont
import logging
import numpy as np

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False

class ST7735S_Waveshare:
    """ST7735S driver for Waveshare 1.44" HAT - Using official pin assignments"""
    
    def __init__(self):
        # CORRECT GPIO PINS FOR WAVESHARE 1.44" HAT
        self.rst_pin = 27  # Changed from 25
        self.dc_pin = 25   # Changed from 24
        self.cs_pin = 8    # CE0
        self.bl_pin = 24   # Changed from 18
        
        self.width = 128
        self.height = 128
        self.x_offset = 2
        self.y_offset = 1
        
        self.spi = None
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
    def initialize(self):
        """Initialize display with Waveshare settings"""
        if not GPIO_AVAILABLE or not SPI_AVAILABLE:
            self.logger.error("GPIO or SPI not available")
            return False
            
        try:
            print("=== Waveshare 1.44\" HAT Initialization ===")
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            GPIO.setup(self.dc_pin, GPIO.OUT)
            GPIO.setup(self.cs_pin, GPIO.OUT)
            GPIO.setup(self.bl_pin, GPIO.OUT)
            print("✓ GPIO configured (RST:27, DC:25, CS:8, BL:24)")
            
            # Turn on backlight
            GPIO.output(self.bl_pin, GPIO.HIGH)
            print("✓ Backlight ON")
            
            # Setup SPI - Use Waveshare speed
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 9000000  # 9MHz like Waveshare
            self.spi.mode = 0b00
            print("✓ SPI configured (9MHz)")
            
            # Hardware reset
            self._reset()
            print("✓ Hardware reset complete")
            
            # Initialize registers (Waveshare sequence)
            self._init_registers()
            print("✓ Registers initialized")
            
            # Set scan direction (Waveshare uses U2D_R2L)
            self._set_scan_direction()
            print("✓ Scan direction set")
            
            # Sleep out
            self._write_cmd(0x11)
            time.sleep(0.12)
            print("✓ Sleep out")
            
            # Display on
            self._write_cmd(0x29)
            time.sleep(0.01)
            print("✓ Display ON")
            
            self.initialized = True
            
            # Clear to white (like Waveshare demo)
            print("Clearing to white...")
            self.clear((255, 255, 255))
            
            print("🎉 Waveshare display initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _reset(self):
        """Hardware reset - Waveshare timing"""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.1)
        
    def _write_cmd(self, cmd):
        """Write command"""
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        
    def _write_data(self, data):
        """Write data"""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
            
    def _init_registers(self):
        """Initialize registers - EXACT Waveshare sequence"""
        # Frame Rate
        self._write_cmd(0xB1)
        self._write_data([0x01, 0x2C, 0x2D])
        
        self._write_cmd(0xB2)
        self._write_data([0x01, 0x2C, 0x2D])
        
        self._write_cmd(0xB3)
        self._write_data([0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D])
        
        # Column inversion
        self._write_cmd(0xB4)
        self._write_data(0x07)
        
        # Power Sequence
        self._write_cmd(0xC0)
        self._write_data([0xA2, 0x02, 0x84])
        
        self._write_cmd(0xC1)
        self._write_data(0xC5)
        
        self._write_cmd(0xC2)
        self._write_data([0x0A, 0x00])
        
        self._write_cmd(0xC3)
        self._write_data([0x8A, 0x2A])
        
        self._write_cmd(0xC4)
        self._write_data([0x8A, 0xEE])
        
        # VCOM
        self._write_cmd(0xC5)
        self._write_data(0x0E)
        
        # Gamma - EXACT Waveshare values
        self._write_cmd(0xE0)
        self._write_data([0x0f, 0x1a, 0x0f, 0x18, 0x2f, 0x28, 0x20, 0x22,
                         0x1f, 0x1b, 0x23, 0x37, 0x00, 0x07, 0x02, 0x10])
        
        self._write_cmd(0xE1)
        self._write_data([0x0f, 0x1b, 0x0f, 0x17, 0x33, 0x2c, 0x29, 0x2e,
                         0x30, 0x30, 0x39, 0x3f, 0x00, 0x07, 0x03, 0x10])
        
        # Enable test command
        self._write_cmd(0xF0)
        self._write_data(0x01)
        
        # Disable ram power save mode
        self._write_cmd(0xF6)
        self._write_data(0x00)
        
        # 65k mode (16-bit color)
        self._write_cmd(0x3A)
        self._write_data(0x05)
        
    def _set_scan_direction(self):
        """Set scan direction - U2D_R2L (Waveshare default)"""
        # U2D_R2L = Up to Down, Right to Left
        memory_access_reg = 0x00 | 0x40 | 0x20  # = 0x60
        memory_access_reg |= 0x08  # RGB mode for 1.44 inch
        
        self._write_cmd(0x36)  # MADCTL
        self._write_data(memory_access_reg)
        
    def set_window(self, x_start, y_start, x_end, y_end):
        """Set display window - Waveshare method"""
        # Set X coordinates
        self._write_cmd(0x2A)
        self._write_data([0x00, (x_start & 0xFF) + self.x_offset,
                         0x00, ((x_end - 1) & 0xFF) + self.x_offset])
        
        # Set Y coordinates
        self._write_cmd(0x2B)
        self._write_data([0x00, (y_start & 0xFF) + self.y_offset,
                         0x00, ((y_end - 1) & 0xFF) + self.y_offset])
        
        # Memory write
        self._write_cmd(0x2C)
        
    def clear(self, color=(255, 255, 255)):
        """Clear screen - Waveshare method"""
        if not self.initialized:
            return False
            
        try:
            # Create buffer
            buffer = [0xFF] * (self.width * self.height * 2)
            
            # Set window
            self.set_window(0, 0, self.width, self.height)
            
            # Send data
            GPIO.output(self.dc_pin, GPIO.HIGH)
            for i in range(0, len(buffer), 4096):
                self.spi.writebytes(buffer[i:i+4096])
                
            return True
        except Exception as e:
            self.logger.error(f"Clear failed: {e}")
            return False
            
    def display_image(self, image):
        """Display image - Using Waveshare's numpy method"""
        if not self.initialized:
            return False
            
        try:
            # Ensure correct size
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height), Image.LANCZOS)
            
            # Convert to numpy array (Waveshare method)
            img = np.asarray(image)
            pix = np.zeros((self.width, self.height, 2), dtype=np.uint8)
            
            # RGB565 conversion (Waveshare formula)
            pix[..., [0]] = np.add(np.bitwise_and(img[..., [0]], 0xF8), 
                                   np.right_shift(img[..., [1]], 5))
            pix[..., [1]] = np.add(np.bitwise_and(np.left_shift(img[..., [1]], 3), 0xE0), 
                                   np.right_shift(img[..., [2]], 3))
            
            pix = pix.flatten().tolist()
            
            # Set window and send
            self.set_window(0, 0, self.width, self.height)
            GPIO.output(self.dc_pin, GPIO.HIGH)
            
            for i in range(0, len(pix), 4096):
                self.spi.writebytes(pix[i:i+4096])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Display image failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def cleanup(self):
        """Cleanup"""
        try:
            if self.spi:
                self.spi.close()
            # Don't cleanup GPIO here
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

class DisplayManager:
    def __init__(self):
        self.device = None
        self.width = 128
        self.height = 128
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        self.logger = logging.getLogger(__name__)
        self.display_enabled = False
        self.st7735s = None
        
        # Button GPIO pins (from your original joystick setup)
        self.PIN_UP = 6
        self.PIN_DOWN = 19
        self.PIN_LEFT = 5
        self.PIN_RIGHT = 26
        self.PIN_CENTER = 13
        self.PIN_KEY1 = 21
        self.PIN_KEY2 = 20
        self.PIN_KEY3 = 16
        
        self.button_callbacks = {}
        self.last_button_time = {}
        self.debounce_time = 0.2
        
    def initialize(self):
        """Initialize display manager"""
        try:
            print("=== DISPLAY MANAGER INITIALIZATION ===")
            
            if not GPIO_AVAILABLE or not SPI_AVAILABLE:
                print("Hardware not available - headless mode")
                self.display_enabled = False
                self._load_fonts()
                return True
            
            # Initialize Waveshare display
            self.st7735s = ST7735S_Waveshare()
            
            if self.st7735s.initialize():
                print("Display initialized successfully!")
                self.display_enabled = True
                
                # Test with colors
                print("\nTesting colors...")
                test_colors = [
                    ((255, 0, 0), "Red"),
                    ((0, 255, 0), "Green"),
                    ((0, 0, 255), "Blue")
                ]
                
                for color, name in test_colors:
                    print(f"  {name}...")
                    img = Image.new('RGB', (128, 128), color)
                    self.st7735s.display_image(img)
                    time.sleep(1)
                    
            else:
                print("Display initialization failed")
                self.display_enabled = False
            
            # Load fonts
            self._load_fonts()
            
            # Setup buttons
            if GPIO_AVAILABLE:
                self._setup_buttons()
                
            return True
            
        except Exception as e:
            print(f"Display manager init failed: {e}")
            import traceback
            traceback.print_exc()
            self.display_enabled = False
            return False
            
    def _load_fonts(self):
        """Load fonts"""
        try:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
            
            for font_path in font_paths:
                try:
                    self.font_small = ImageFont.truetype(font_path, 10)
                    self.font_medium = ImageFont.truetype(font_path, 12)
                    self.font_large = ImageFont.truetype(font_path, 14)
                    break
                except:
                    continue
                    
            if not self.font_small:
                self.font_small = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_large = ImageFont.load_default()
                
        except Exception as e:
            self.logger.warning(f"Font loading failed: {e}")
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            
    def _setup_buttons(self):
        """Setup button GPIO"""
        try:
            pins = [self.PIN_UP, self.PIN_DOWN, self.PIN_LEFT, self.PIN_RIGHT,
                   self.PIN_CENTER, self.PIN_KEY1, self.PIN_KEY2, self.PIN_KEY3]
            
            for pin in pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.FALLING, 
                                    callback=self._button_callback, bouncetime=300)
                self.last_button_time[pin] = 0
                
            self.logger.info("Buttons initialized")
        except Exception as e:
            self.logger.error(f"Button setup failed: {e}")
            
    def _button_callback(self, pin):
        """Button callback"""
        try:
            current_time = time.time()
            if current_time - self.last_button_time.get(pin, 0) < self.debounce_time:
                return
                
            self.last_button_time[pin] = current_time
            
            if pin in self.button_callbacks:
                self.button_callbacks[pin]()
        except Exception as e:
            self.logger.error(f"Button callback error: {e}")
            
    def set_button_callback(self, pin, callback):
        """Set button callback"""
        self.button_callbacks[pin] = callback
        
    def show_splash_screen(self):
        """Show splash screen"""
        if not self.display_enabled:
            print("PEN-DECK - Loading...")
            return
            
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            draw.rectangle([0, 0, 127, 127], outline=(0, 100, 200), width=2)
            draw.text((25, 35), "PEN-DECK", font=self.font_large, fill=(255, 255, 255))
            draw.text((15, 55), "Cybersecurity", font=self.font_medium, fill=(0, 255, 0))
            draw.text((25, 70), "Companion", font=self.font_medium, fill=(0, 255, 0))
            draw.text((30, 95), "Loading...", font=self.font_small, fill=(255, 255, 0))
            
            self.st7735s.display_image(image)
        except Exception as e:
            self.logger.error(f"Splash screen error: {e}")
            
    def show_menu(self, title, items, selected_index=0, scroll_offset=0):
        """Show menu"""
        if not self.display_enabled:
            print(f"\n=== {title} ===")
            for i, item in enumerate(items):
                print(f"{'>' if i == selected_index else ' '} {item}")
            return
            
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Title
            draw.rectangle([0, 0, 127, 18], fill=(0, 100, 200))
            draw.text((4, 3), title[:15], font=self.font_medium, fill=(255, 255, 255))
            
            # Menu items
            visible_items = 6
            for i in range(visible_items):
                idx = i + scroll_offset
                if idx >= len(items):
                    break
                    
                y = 22 + (i * 16)
                if idx == selected_index:
                    draw.rectangle([2, y-1, 125, y+14], fill=(255, 255, 255))
                    draw.text((6, y), ">" + items[idx][:13], font=self.font_small, fill=(0, 0, 0))
                else:
                    draw.text((6, y), items[idx][:14], font=self.font_small, fill=(255, 255, 255))
            
            self.st7735s.display_image(image)
        except Exception as e:
            self.logger.error(f"Menu display error: {e}")
            
    def show_text_screen(self, title, content, scroll_position=0):
        """Show text screen"""
        if not self.display_enabled:
            print(f"\n=== {title} ===\n{content[:200]}")
            return
            
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            draw.rectangle([0, 0, 127, 18], fill=(0, 100, 200))
            draw.text((4, 3), title[:15], font=self.font_medium, fill=(255, 255, 255))
            
            lines = str(content).split('\n')
            for i in range(8):
                if i + scroll_position < len(lines):
                    draw.text((4, 22 + i*12), lines[i + scroll_position][:20], 
                            font=self.font_small, fill=(255, 255, 255))
            
            self.st7735s.display_image(image)
        except Exception as e:
            self.logger.error(f"Text screen error: {e}")
            
    def show_system_info(self, info_data):
        """Show system info"""
        if not self.display_enabled:
            print("\n=== System Info ===")
            for k, v in info_data.items():
                print(f"{k}: {v}")
            return
            
        try:
            image = Image.new('RGB', (128, 128), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            draw.rectangle([0, 0, 127, 18], fill=(0, 100, 200))
            draw.text((4, 3), "System Info", font=self.font_medium, fill=(255, 255, 255))
            
            y = 22
            for key, value in list(info_data.items())[:8]:
                text = f"{key}: {value}"[:18]
                draw.text((4, y), text, font=self.font_small, fill=(255, 255, 255))
                y += 12
            
            self.st7735s.display_image(image)
        except Exception as e:
            self.logger.error(f"System info error: {e}")
            
    def cleanup(self):
        """Cleanup"""
        try:
            if self.st7735s:
                self.st7735s.cleanup()
            if GPIO_AVAILABLE:
                pins = [self.PIN_UP, self.PIN_DOWN, self.PIN_LEFT, self.PIN_RIGHT,
                       self.PIN_CENTER, self.PIN_KEY1, self.PIN_KEY2, self.PIN_KEY3]
                GPIO.cleanup(pins)
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
