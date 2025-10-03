#!/usr/bin/env python3
"""
Test script for Waveshare 1.44" LCD HAT with official library
Run this on your Raspberry Pi to verify the display works correctly
"""

import time
from PIL import Image, ImageDraw, ImageFont
from src.drivers.LCD_1in44 import LCD, SCAN_DIR_DFT

def main():
    print("=" * 50)
    print("Waveshare 1.44\" LCD HAT Test")
    print("Using Official Waveshare Library")
    print("=" * 50)

    try:
        print("\n1. Initializing display...")
        lcd = LCD()

        if lcd.LCD_Init(SCAN_DIR_DFT) != 0:
            print("❌ LCD initialization failed!")
            return

        print("✅ LCD initialized successfully!")

        print("\n2. Clearing display to white...")
        lcd.LCD_Clear()
        time.sleep(1)

        print("\n3. Testing solid colors...")
        colors = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
            ("Cyan", (0, 255, 255)),
            ("Magenta", (255, 0, 255)),
            ("White", (255, 255, 255)),
            ("Black", (0, 0, 0))
        ]

        for name, color in colors:
            print(f"   - {name}: {color}")
            image = Image.new('RGB', (128, 128), color)
            lcd.LCD_ShowImage(image, 0, 0)
            time.sleep(0.5)

        print("\n4. Testing pattern with text...")
        image = Image.new('RGB', (128, 128), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()

        draw.rectangle([0, 0, 127, 127], outline=(255, 255, 255))
        draw.rectangle([10, 10, 50, 50], fill=(255, 0, 0))
        draw.rectangle([60, 10, 100, 50], fill=(0, 255, 0))
        draw.rectangle([10, 60, 50, 100], fill=(0, 0, 255))
        draw.rectangle([60, 60, 100, 100], fill=(255, 255, 0))

        draw.text((20, 54), "TEST", font=font, fill=(255, 255, 255))
        draw.text((15, 105), "SUCCESS", font=font, fill=(0, 255, 0))

        lcd.LCD_ShowImage(image, 0, 0)
        print("✅ Pattern displayed!")

        print("\n5. Testing button input...")
        print("   Press buttons to test (Ctrl+C to exit)")

        button_names = {
            lcd.GPIO_KEY_UP_PIN: "UP",
            lcd.GPIO_KEY_DOWN_PIN: "DOWN",
            lcd.GPIO_KEY_LEFT_PIN: "LEFT",
            lcd.GPIO_KEY_RIGHT_PIN: "RIGHT",
            lcd.GPIO_KEY_PRESS_PIN: "CENTER",
            lcd.GPIO_KEY1_PIN: "KEY1",
            lcd.GPIO_KEY2_PIN: "KEY2",
            lcd.GPIO_KEY3_PIN: "KEY3"
        }

        while True:
            for pin, name in button_names.items():
                if lcd.digital_read(pin) == 0:
                    print(f"   Button pressed: {name}")
                    time.sleep(0.2)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n✅ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n6. Cleaning up...")
        try:
            lcd.module_exit()
            print("✅ Cleanup complete")
        except:
            pass
        print("\n" + "=" * 50)
        print("Test completed!")
        print("=" * 50)

if __name__ == "__main__":
    main()
