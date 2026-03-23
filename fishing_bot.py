import cv2
import numpy as np
import pyautogui
import time
import mss
import sys
from typing import Tuple, Optional, List
import logging
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PixelBladeFishingBot:
    def __init__(self):
        # Configuration from config.py
        self.fishing_key = config.FISHING_KEY
        self.fishing_key_modifiers = config.FISHING_KEY_MODIFIERS
        self.check_interval = config.CHECK_INTERVAL
        self.circle_detection_threshold = config.CIRCLE_DETECTION_THRESHOLD
        
        # Circle detection parameters
        self.radius_ranges = config.RADIUS_RANGES
        
        # Green detection parameters
        self.green_hsv_min = np.array(config.GREEN_HSV_MIN)
        self.green_hsv_max = np.array(config.GREEN_HSV_MAX)
        self.min_green_area = config.MIN_GREEN_AREA
        self.green_circularity_threshold = config.GREEN_CIRCULARITY_THRESHOLD
        
        # Screen capture setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
        
        # State management
        self.is_fishing = False
        self.last_fishing_time = 0
        
        # Safety settings
        pyautogui.FAILSAFE = config.FAILSAFE_ENABLED
        pyautogui.PAUSE = config.AUTO_PAUSE
        
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen region or full screen"""
        if region:
            monitor = {
                "top": region[1],
                "left": region[0], 
                "width": region[2],
                "height": region[3]
            }
        else:
            monitor = self.monitor
            
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def detect_fishing_ui(self, image: np.ndarray) -> bool:
        """Detect if fishing UI is present by looking for circular patterns and colors"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles with multiple parameter sets for different sizes
        all_circles = []
        
        # Use radius ranges from config
        for min_r, max_r in self.radius_ranges:
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=30,
                param1=50,
                param2=25,  # Lower threshold for more sensitive detection
                minRadius=min_r,
                maxRadius=max_r
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                all_circles.extend(circles)
        
        if len(all_circles) == 0:
            return False
            
        # Check if we found circles that look like fishing UI
        for (x, y, r) in all_circles:
            if self.validate_fishing_circle(image, x, y, r):
                return True
                
        return False
    
    def validate_fishing_circle(self, image: np.ndarray, x: int, y: int, r: int) -> bool:
        """Validate if detected circle is likely a fishing UI element"""
        # Extract region around circle
        margin = 10
        x1, y1 = max(0, x - r - margin), max(0, y - r - margin)
        x2, y2 = min(image.shape[1], x + r + margin), min(image.shape[0], y + r + margin)
        
        circle_region = image[y1:y2, x1:x2]
        if circle_region.size == 0:
            return False
            
        # Check for typical fishing UI characteristics
        gray_circle = cv2.cvtColor(circle_region, cv2.COLOR_BGR2GRAY)
        
        # Look for concentric circles (inner and outer)
        edges = cv2.Canny(gray_circle, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter for circular contours
        circular_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > self.circle_detection_threshold:
                        circular_contours.append(contour)
        
        # If we found multiple circular contours, likely concentric circles
        return len(circular_contours) >= 2
    
    def detect_circle_overlap(self, image: np.ndarray) -> bool:
        """Detect when inner circle touches outer circle OR when inner circle turns green"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Method 1: Check for green color indication (inner circle turning green)
        green_detected = self.detect_green_indicator(hsv)
        if green_detected:
            logger.info("Green indicator detected - optimal fishing time!")
            return True
        
        # Method 2: Traditional circle overlap detection
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        all_circles = []
        
        # Detect circles of various sizes using config
        for min_r, max_r in self.radius_ranges:
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=30,
                param1=50,
                param2=25,
                minRadius=min_r,
                maxRadius=max_r
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                all_circles.extend(circles)
        
        if len(all_circles) < 2:
            return False
            
        # Look for concentric circles with overlap conditions
        for i, (x1, y1, r1) in enumerate(all_circles):
            for j, (x2, y2, r2) in enumerate(all_circles):
                if i != j:
                    # Check if circles are concentric (same center)
                    distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                    if distance < 15:  # Nearly concentric
                        # Check if circles are touching or overlapping
                        # This happens when distance ≈ |r1 - r2| (touching) or distance < |r1 - r2| (overlapping)
                        radius_diff = abs(r1 - r2)
                        
                        # Touching condition
                        if abs(distance - radius_diff) < 8:
                            # Additional validation: check if this looks like fishing UI
                            if self.validate_fishing_overlap(image, x1, y1, r1, r2):
                                logger.info("Circle overlap detected - optimal fishing time!")
                                return True
                        
                        # Overlapping condition (inner circle has expanded beyond touching point)
                        elif distance < radius_diff:
                            if self.validate_fishing_overlap(image, x1, y1, r1, r2):
                                logger.info("Circle overlap detected - optimal fishing time!")
                                return True
        
        return False
    
    def detect_green_indicator(self, hsv_image: np.ndarray) -> bool:
        """Detect green color indication when inner circle turns green"""
        # Use config parameters for green detection
        lower_green = self.green_hsv_min
        upper_green = self.green_hsv_max
        
        # Create mask for green colors
        green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
        
        # Find contours of green areas
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for circular green regions
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_green_area:  # Minimum green area threshold from config
                # Check if contour is circular
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > self.green_circularity_threshold:  # Use config threshold
                        return True
        
        return False
    
    def validate_fishing_overlap(self, image: np.ndarray, x: int, y: int, r1: int, r2: int) -> bool:
        """Additional validation for fishing circle overlap"""
        # Extract region around the circles
        max_r = max(r1, r2)
        margin = 20
        x1, y1 = max(0, x - max_r - margin), max(0, y - max_r - margin)
        x2, y2 = min(image.shape[1], x + max_r + margin), min(image.shape[0], y + max_r + margin)
        
        if x2 <= x1 or y2 <= y1:
            return False
            
        overlap_region = image[y1:y2, x1:x2]
        if overlap_region.size == 0:
            return False
        
        # Check for typical fishing UI characteristics in the overlap region
        gray = cv2.cvtColor(overlap_region, cv2.COLOR_BGR2GRAY)
        
        # Look for high contrast between circles
        contrast = np.std(gray)
        if contrast > 30:  # Good contrast indicates distinct circles
            return True
            
        return False
    
    def press_fishing_key(self):
        """Press the fishing key with modifiers"""
        try:
            # Parse modifiers
            modifiers = []
            if self.fishing_key_modifiers:
                for modifier_group in self.fishing_key_modifiers:
                    # Split combined modifiers like 'alt+shift'
                    modifiers.extend(modifier_group.split('+'))
            
            # Press modifier keys first
            for modifier in modifiers:
                modifier = modifier.lower()
                if modifier == 'alt':
                    pyautogui.keyDown('alt')
                elif modifier == 'shift':
                    pyautogui.keyDown('shift')
                elif modifier == 'ctrl':
                    pyautogui.keyDown('ctrl')
            
            # Press the main key
            pyautogui.press(self.fishing_key)
            
            # Release modifier keys in reverse order
            for modifier in reversed(modifiers):
                modifier = modifier.lower()
                if modifier == 'alt':
                    pyautogui.keyUp('alt')
                elif modifier == 'shift':
                    pyautogui.keyUp('shift')
                elif modifier == 'ctrl':
                    pyautogui.keyUp('ctrl')
            
            # Format log message
            if modifiers:
                modifier_str = '+'.join(modifiers).upper()
                logger.info(f"Pressed {modifier_str}+{self.fishing_key.upper()}")
            else:
                logger.info(f"Pressed {self.fishing_key.upper()}")
                
        except Exception as e:
            logger.error(f"Error pressing fishing key: {e}")
        
        time.sleep(0.2)
    
    def wait_for_fishing_ui(self, timeout: float = None) -> bool:
        """Wait for fishing UI to appear"""
        if timeout is None:
            timeout = config.FISHING_UI_TIMEOUT
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            image = self.capture_screen()
            if self.detect_fishing_ui(image):
                logger.info("Fishing UI detected")
                return True
            time.sleep(self.check_interval)
        return False
    
    def wait_for_circle_overlap(self, timeout: float = None) -> bool:
        """Wait for inner circle to touch outer circle"""
        if timeout is None:
            timeout = config.CIRCLE_OVERLAP_TIMEOUT
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            image = self.capture_screen()
            if self.detect_circle_overlap(image):
                logger.info("Circle overlap detected - time to click!")
                return True
            time.sleep(self.check_interval)
        return False
    
    def spam_fishing_key(self, duration: float = None):
        """Spam fishing key to clear remaining UI"""
        if duration is None:
            duration = config.SPAM_DURATION
            
        end_time = time.time() + duration
        while time.time() < end_time:
            self.press_fishing_key()
            time.sleep(0.1)
    
    def fishing_cycle(self):
        """Complete one fishing cycle"""
        logger.info("Starting fishing cycle")
        
        # Press configured key to start fishing
        self.press_fishing_key()
        
        # Wait for fishing UI
        if not self.wait_for_fishing_ui():
            logger.warning("Fishing UI not detected, trying next cycle")
            return False
        
        # Wait for circle overlap
        if not self.wait_for_circle_overlap():
            logger.warning("Circle overlap not detected, trying next cycle")
            return False
        
        # Press configured key at the right moment
        self.press_fishing_key()
        
        # Wait a bit for the catch
        time.sleep(1.0)
        
        # Spam configured key to clear any remaining UI
        self.spam_fishing_key()
        
        logger.info("Fishing cycle completed")
        return True
    
    def run(self):
        """Main bot loop"""
        logger.info("Starting Pixel Blade Fishing Bot")
        
        # Log current keybind configuration
        if self.fishing_key_modifiers:
            modifier_str = '+'.join([m.split('+') for m in self.fishing_key_modifiers])
            logger.info(f"Using keybind: {modifier_str}+{self.fishing_key.upper()}")
        else:
            logger.info(f"Using keybind: {self.fishing_key.upper()}")
        
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                # Try to find fishing opportunities
                success = self.fishing_cycle()
                
                if not success:
                    # If fishing failed, wait a bit and try again
                    logger.info("No fishing detected, waiting...")
                    time.sleep(1.0)
                else:
                    # Brief pause between successful catches
                    time.sleep(config.CYCLE_PAUSE)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            logger.info("Bot shutdown complete")

def main():
    """Main entry point"""
    print("Pixel Blade Fishing Bot")
    print("=" * 30)
    print("This bot will automatically fish in Pixel Blade game")
    print("Make sure the game window is visible and active")
    print("Press Ctrl+C to stop the bot")
    print()
    
    # Safety check
    response = input("Do you want to start the fishing bot? (y/n): ")
    if response.lower() != 'y':
        print("Bot not started")
        return
    
    bot = PixelBladeFishingBot()
    bot.run()

if __name__ == "__main__":
    main()
