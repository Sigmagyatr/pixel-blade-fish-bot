"""
Debug visualization tool for Pixel Blade Fishing Bot
Shows what the bot sees in real-time with detection overlays
"""

import cv2
import numpy as np
import mss
import time
from fishing_bot import PixelBladeFishingBot
import config

class DebugVisualizer:
    def __init__(self):
        self.bot = PixelBladeFishingBot()
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
    def draw_detections(self, image, all_circles, green_mask=None):
        """Draw detection overlays on image"""
        result = image.copy()
        
        # Draw all detected circles
        if all_circles:
            for (x, y, r) in all_circles:
                cv2.circle(result, (x, y), r, (0, 255, 0), 2)
                cv2.circle(result, (x, y), 2, (0, 0, 255), -1)
                cv2.putText(result, f"r={r}", (x-20, y-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Overlay green detection mask
        if green_mask is not None:
            # Resize mask to match image if needed
            if green_mask.shape[:2] != result.shape[:2]:
                green_mask = cv2.resize(green_mask, (result.shape[1], result.shape[0]))
            
            # Create green overlay
            green_overlay = np.zeros_like(result)
            green_overlay[green_mask > 0] = [0, 255, 0]
            
            # Blend with original image
            result = cv2.addWeighted(result, 0.7, green_overlay, 0.3, 0)
        
        return result
    
    def detect_all_circles(self, image):
        """Detect circles of all sizes"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        all_circles = []
        
        # Detect circles with multiple radius ranges
        radius_ranges = config.RADIUS_RANGES
        
        for min_r, max_r in radius_ranges:
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
        
        return all_circles
    
    def detect_green_mask(self, image):
        """Create green detection mask"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        lower_green = np.array(config.GREEN_HSV_MIN)
        upper_green = np.array(config.GREEN_HSV_MAX)
        
        return cv2.inRange(hsv, lower_green, upper_green)
    
    def run_debug_mode(self):
        """Run debug visualization"""
        print("Debug Visualization Mode")
        print("=" * 30)
        print("Press 'q' to quit, 's' to save screenshot")
        print("Green circles = detected fishing UI")
        print("Green overlay = green color detection")
        print()
        
        try:
            while True:
                # Capture screen
                screenshot = self.sct.grab(self.monitor)
                image = np.array(screenshot)
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                
                # Run detections
                all_circles = self.detect_all_circles(image)
                green_mask = self.detect_green_mask(image)
                
                # Check bot logic
                has_fishing_ui = self.bot.detect_fishing_ui(image)
                has_overlap = self.bot.detect_circle_overlap(image)
                
                # Create visualization
                viz_image = self.draw_detections(image, all_circles, green_mask)
                
                # Add status text
                status_text = f"Fishing UI: {'YES' if has_fishing_ui else 'NO'} | Overlap: {'YES' if has_overlap else 'NO'}"
                cv2.putText(viz_image, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Add circle count
                circle_text = f"Circles detected: {len(all_circles)}"
                cv2.putText(viz_image, circle_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Show visualization
                cv2.imshow('Pixel Blade Fishing Bot - Debug View', viz_image)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = int(time.time())
                    cv2.imwrite(f'debug_screenshot_{timestamp}.png', viz_image)
                    print(f"Screenshot saved: debug_screenshot_{timestamp}.png")
                
                time.sleep(0.1)  # Control frame rate
                
        except KeyboardInterrupt:
            print("\nDebug mode stopped")
        finally:
            cv2.destroyAllWindows()

def main():
    """Main entry point"""
    print("Pixel Blade Fishing Bot - Debug Visualizer")
    print("This tool shows what the bot sees in real-time")
    print()
    
    viz = DebugVisualizer()
    viz.run_debug_mode()

if __name__ == "__main__":
    main()
