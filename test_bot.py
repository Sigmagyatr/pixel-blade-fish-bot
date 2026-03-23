"""
Test script for Pixel Blade Fishing Bot
Use this to test individual components and debug issues
"""

import cv2
import numpy as np
import time
from fishing_bot import PixelBladeFishingBot
import config

def test_screen_capture():
    """Test screen capture functionality"""
    print("Testing screen capture...")
    bot = PixelBladeFishingBot()
    
    # Capture full screen
    image = bot.capture_screen()
    print(f"Captured image shape: {image.shape}")
    
    # Save a sample capture for inspection
    cv2.imwrite("test_capture.png", image)
    print("Saved test capture as 'test_capture.png'")
    
    return image

def test_circle_detection():
    """Test circle detection on captured image"""
    print("Testing circle detection...")
    bot = PixelBladeFishingBot()
    
    # Capture screen
    image = bot.capture_screen()
    
    # Test fishing UI detection
    has_fishing_ui = bot.detect_fishing_ui(image)
    print(f"Fishing UI detected: {has_fishing_ui}")
    
    # Test circle overlap detection
    has_overlap = bot.detect_circle_overlap(image)
    print(f"Circle overlap detected: {has_overlap}")
    
    # Draw detected circles for visualization
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=config.MIN_CIRCLE_RADIUS,
        maxRadius=config.MAX_CIRCLE_RADIUS
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    cv2.imwrite("test_circles.png", image)
    print("Saved circle detection result as 'test_circles.png'")
    
    return has_fishing_ui, has_overlap

def test_key_press():
    """Test key press functionality"""
    print("Testing key press functionality...")
    print("Will press 'e' key in 3 seconds...")
    time.sleep(3)
    
    bot = PixelBladeFishingBot()
    bot.press_fishing_key()
    print("Key press test completed")

def interactive_test():
    """Interactive testing mode"""
    print("Interactive Testing Mode")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Test screen capture")
        print("2. Test circle detection")
        print("3. Test key press")
        print("4. Continuous monitoring (press Ctrl+C to stop)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_screen_capture()
        elif choice == "2":
            test_circle_detection()
        elif choice == "3":
            test_key_press()
        elif choice == "4":
            print("Starting continuous monitoring...")
            bot = PixelBladeFishingBot()
            try:
                while True:
                    image = bot.capture_screen()
                    has_ui = bot.detect_fishing_ui(image)
                    has_overlap = bot.detect_circle_overlap(image)
                    
                    print(f"\rFishing UI: {'YES' if has_ui else 'NO'} | Overlap: {'YES' if has_overlap else 'NO'}", end="", flush=True)
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
        elif choice == "5":
            print("Exiting test mode")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main test entry point"""
    print("Pixel Blade Fishing Bot - Test Suite")
    print("=" * 40)
    print("Use this script to test and debug the bot components")
    print()
    
    # Check if Pixel Blade might be running
    response = input("Is Pixel Blade currently running? (y/n): ").strip().lower()
    if response != 'y':
        print("Please start Pixel Blade before running tests")
        print("Some tests may not work without the game running")
        print()
    
    interactive_test()

if __name__ == "__main__":
    main()
