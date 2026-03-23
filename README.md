# Pixel Blade Fishing Bot

An automated fishing bot for the game Pixel Blade that uses computer vision to detect fishing UI elements and automate the fishing process.

Everything is open source! Feel free to fork and modify as you see fit if you want to customize it for your needs or if its not good enough for you.
For non programmers, there are instructions on how to edit the bot in the code in the green text.

## Features

- **Computer Vision Detection**: Uses OpenCV to detect fishing UI circles and timing
- **Automated Fishing**: Presses 'E' to start fishing and automatically times the catch
- **Circle Overlap Detection**: Detects when the inner circle touches the outer circle for optimal timing
- **Configurable Settings**: Easy to adjust timing, detection parameters, and screen regions
- **Safe Operation**: Includes failsafe mechanisms and logging

## How It Works                                          bnm

1. **Start Fishing**: Press Alt/custom keybind to initiate fishing
2. **UI Detection**: Waits for the fishing UI to appear (detects circular patterns)
3. **Timing Detection**: Monitors the inner and outer circles
4. **Optimal Catch**: Presses 'E' when the inner circle touches the outer circle
5. **Cleanup**: Spams 'E' to clear any remaining UI elements
6. **Repeat**: Continues the cycle until no more fishing opportunities are found

## Installation

1. Clone or download this repository

2. Navigate to the project directory

3. Download python from https://www.python.org/downloads/

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```


## Usage

1. Make sure Pixel Blade is running and visible on your screen
2. Run the bot:
```bash
python fishing_bot.py
```
3. The bot will ask for confirmation before starting
4. Press `Ctrl+C` at any time to stop the bot

## Configuration

Edit `config.py` to adjust the following settings:

### Keybind Settings
- **FISHING_KEY**: Main key to press (default: 'e')
- **FISHING_KEY_MODIFIERS**: List of modifiers like ['alt'], ['shift'], ['ctrl'], or combinations like ['alt+shift']

#### Keybind Examples:
```python
# Simple key
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = []  # Just 'e'

# Alt + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['alt']

# Shift + E  
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['shift']

# Ctrl + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['ctrl']

# Alt + Shift + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['alt+shift']

# Ctrl + Shift + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['ctrl+shift']

# Alt + Ctrl + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['alt+ctrl']

# Alt + Shift + Ctrl + E
FISHING_KEY = 'e'
FISHING_KEY_MODIFIERS = ['alt+shift+ctrl']
```

### Other Settings
- **Timing settings**: Adjust timeouts and intervals
- **Circle detection**: Modify detection thresholds and radius ranges
- **Screen region**: Specify a particular screen region to monitor
- **Safety settings**: Enable/disable failsafe features

## Requirements

- Python 3.7+
- Windows OS (tested on Windows 10/11)
- Pixel Blade game running in windowed or fullscreen mode
- Administrative privileges may be required for screen capture

## Dependencies

- `opencv-python`: Computer vision and image processing
- `numpy`: Numerical operations
- `pyautogui`: Mouse and keyboard automation
- `Pillow`: Image handling
- `mss`: Fast screen capture

## Safety Features

- **Failsafe**: Move mouse to screen corner to immediately stop the bot
- **Logging**: Detailed logging of all bot actions
- **Configurable timeouts**: Prevents infinite waiting
- **Error handling**: Graceful handling of detection failures

## Troubleshooting

**Bot doesn't detect fishing UI:**
- Adjust `MIN_CIRCLE_RADIUS` and `MAX_CIRCLE_RADIUS` in config.py
- Try different `CIRCLE_DETECTION_THRESHOLD` values
- Ensure the game window is visible and not obscured

**Timing is off:**
- Adjust `CIRCLE_OVERLAP_TIMEOUT` for longer/shorter wait times
- Modify `OVERLAP_TOLERANCE` for more/less sensitive overlap detection

**Performance issues:**
- Increase `CHECK_INTERVAL` to reduce CPU usage
- Specify a smaller `SCREEN_REGION` to monitor less area

## Disclaimer

This bot is for educational purposes only. Use at your own risk and make sure to comply with the game's terms of service.

## License

MIT License - see LICENSE file for details

This is a bot for the game Pixel Blade.
It uses computer vision to detect the fishing UI and automatically clicks the fishing key when the fishing ui's inner circle touches the outer circle, maximizing catch efficiency. Then it spam clicks the 'e' key to clear any remaining UI.