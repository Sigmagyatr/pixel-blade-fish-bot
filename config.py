"""
Configuration file for Pixel Blade Fishing Bot
Adjust these settings to optimize performance for your setup
"""

# Fishing controls
FISHING_KEY = 'e'  # Key to press for fishing
FISHING_KEY_MODIFIERS = []  # Modifiers: ['alt', 'shift', 'ctrl'] or combinations like ['alt+shift']

# Examples of different key combinations:
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = []  # Just 'e'
# 
# FISHING_KEY = 'e'  
# FISHING_KEY_MODIFIERS = ['alt']  # Alt+E
#
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = ['shift']  # Shift+E
#
# FISHING_KEY = 'e' 
# FISHING_KEY_MODIFIERS = ['ctrl']  # Ctrl+E
#
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = ['alt+shift']  # Alt+Shift+E
#
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = ['ctrl+shift']  # Ctrl+Shift+E
#
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = ['alt+ctrl']  # Alt+Ctrl+E
#
# FISHING_KEY = 'e'
# FISHING_KEY_MODIFIERS = ['alt+shift+ctrl']  # Alt+Shift+Ctrl+E

# Timing settings (in seconds)
CHECK_INTERVAL = 0.1  # How often to check for UI changes
FISHING_UI_TIMEOUT = 5.0  # Max time to wait for fishing UI
CIRCLE_OVERLAP_TIMEOUT = 10.0  # Max time to wait for circle overlap
SPAM_DURATION = 2.0  # How long to spam E after catching
CYCLE_PAUSE = 0.5  # Pause between successful fishing cycles

# Circle detection parameters
CIRCLE_DETECTION_THRESHOLD = 0.3  # Minimum circularity score (0.0-1.0)
# Multiple radius ranges for different circle sizes
RADIUS_RANGES = [
    (10, 40),    # Small circles
    (30, 80),    # Medium circles  
    (60, 150),   # Large circles
    (100, 250)   # Extra large circles
]

# Green color detection (for when inner circle turns green)
GREEN_HSV_MIN = [40, 40, 40]    # Lower bound for green in HSV
GREEN_HSV_MAX = [80, 255, 255]  # Upper bound for green in HSV
MIN_GREEN_AREA = 200            # Minimum green area to detect
GREEN_CIRCULARITY_THRESHOLD = 0.3  # Minimum circularity for green regions

# Screen capture settings
# Set to None to capture full screen, or specify (x, y, width, height)
SCREEN_REGION = None  # Example: (100, 100, 800, 600)

# OpenCV Hough Circle parameters
HOUGH_DP = 1  # Inverse ratio of resolution
HOUGH_MINDIST = 50  # Minimum distance between detected circles
HOUGH_PARAM1 = 50  # Upper threshold for the internal Canny edge detector
HOUGH_PARAM2 = 30  # Threshold for circle center detection

# Safety settings
FAILSAFE_ENABLED = True  # Move mouse to corner to stop bot
AUTO_PAUSE = 0.1  # Pause between pyautogui actions

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# Advanced settings
CONCENTRIC_DISTANCE_THRESHOLD = 10  # Max distance for circles to be considered concentric
RADIUS_RATIO_MIN = 0.5  # Minimum ratio between inner/outer circle radii
RADIUS_RATIO_MAX = 0.8  # Maximum ratio between inner/outer circle radii
OVERLAP_TOLERANCE = 5  # Tolerance for detecting circle overlap (pixels)
