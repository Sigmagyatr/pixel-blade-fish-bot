#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import time
import cv2
import numpy as np
import pyautogui
import mss
import logging
import requests
import base64
from typing import Tuple, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PixelBladeFishingBot:
    def __init__(self):
        # Default settings
        self.fishing_key = 'e'
        self.fishing_key_modifiers = []
        self.check_interval = 0.1
        self.circle_detection_threshold = 0.3
        self.radius_ranges = [(10, 40), (30, 80), (60, 150), (100, 250)]
        self.green_hsv_min = np.array([40, 40, 40])
        self.green_hsv_max = np.array([80, 255, 255])
        self.min_green_area = 200
        self.green_circularity_threshold = 0.3
        
        # Screen capture setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
        # Safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen region or full screen"""
        if region:
            monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
        else:
            monitor = self.monitor
        
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def detect_fishing_ui(self, image: np.ndarray) -> bool:
        """Enhanced detection for Pixel Blade fishing circles"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Enhanced light blue outer circle detection
        blue_ranges = [
            ([80, 80, 180], [120, 255, 255]),
            ([90, 100, 200], [110, 255, 255]),
            ([70, 60, 160], [100, 240, 240])
        ]
        
        for lower_blue, upper_blue in blue_ranges:
            lower = np.array(lower_blue)
            upper = np.array(upper_blue)
            blue_mask = cv2.inRange(hsv, lower, upper)
            
            blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in blue_contours:
                area = cv2.contourArea(contour)
                if area > 300:
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.3:
                            return True
        
        return False
    
    def detect_circle_overlap(self, image: np.ndarray) -> bool:
        """Detect when inner circle touches outer circle OR when inner circle turns green"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Method 1: Check for green color indication
        lower_green = self.green_hsv_min
        upper_green = self.green_hsv_max
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_green_area:
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > self.green_circularity_threshold:
                        return True
        
        return False
    
    def detect_loot(self, image: np.ndarray) -> tuple:
        """Detect loot text and return (found, rarity, position)"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        loot_colors = {
            'Vaulted(Red)': ([0, 150, 100], [10, 255, 255]),
            'Legendary(Yellow)': ([20, 150, 100], [30, 255, 255]), 
            'Rare(Blue)': ([100, 150, 100], [130, 255, 255]),
            'Epic(Purple)': ([130, 150, 100], [170, 255, 255]),
            'Common(Grey)': ([0, 0, 150], [180, 30, 255])
        }
        
        for rarity_name, (lower, upper) in loot_colors.items():
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(hsv, lower, upper)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 200:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 5:
                        return True, rarity_name, (x, y, w, h)
        
        return False, None, None
    
    def press_fishing_key(self):
        """Press the fishing key with modifiers"""
        try:
            modifiers = []
            if self.fishing_key_modifiers:
                for modifier_group in self.fishing_key_modifiers:
                    modifiers.extend(modifier_group.split('+'))
            
            for modifier in modifiers:
                modifier = modifier.lower()
                if modifier == 'alt':
                    pyautogui.keyDown('alt')
                elif modifier == 'shift':
                    pyautogui.keyDown('shift')
                elif modifier == 'ctrl':
                    pyautogui.keyDown('ctrl')
            
            pyautogui.press(self.fishing_key)
            
            for modifier in reversed(modifiers):
                modifier = modifier.lower()
                if modifier == 'alt':
                    pyautogui.keyUp('alt')
                elif modifier == 'shift':
                    pyautogui.keyUp('shift')
                elif modifier == 'ctrl':
                    pyautogui.keyUp('ctrl')
            
        except Exception as e:
            logger.error(f"Error pressing fishing key: {e}")
        
        time.sleep(0.2)
    
    def anti_stuck_check(self, timeout=5.0):
        """Anti-stuck mechanism - spam E if no fishing UI found"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            image = self.capture_screen()
            if self.detect_fishing_ui(image):
                return True
            
            time.sleep(0.5)
        
        logger.info("Anti-stuck activated: No fishing UI detected, spamming E key")
        for _ in range(10):
            self.press_fishing_key()
            time.sleep(0.1)
        
        return False
    
    def wait_for_circle_overlap(self, timeout: float = 10.0) -> bool:
        """Wait for inner circle to touch outer circle"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            image = self.capture_screen()
            if self.detect_circle_overlap(image):
                return True
            time.sleep(self.check_interval)
        return False
    
    def spam_fishing_key(self, duration: float = 2.0):
        """Spam fishing key to clear remaining UI"""
        end_time = time.time() + duration
        while time.time() < end_time:
            self.press_fishing_key()
            time.sleep(0.1)

class StatusUI:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.root = tk.Toplevel()
        self.setup_window()
        self.setup_widgets()
        
        # Position at top-right by default
        self.position_window(50, 50)
        
        # Make draggable
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def setup_window(self):
        """Setup status window properties"""
        self.root.title("Bot Status")
        self.root.geometry("300x200")
        self.root.configure(bg='#404040')  # Light grey background
        
        # Remove window decorations
        self.root.overrideredirect(True)
        self.root.attributes('-toolwindow', True)
        
        # Always on top
        if self.main_gui.settings.get('always_on_top', True):
            self.root.attributes('-topmost', True)
    
    def setup_widgets(self):
        """Setup status display widgets"""
        main_frame = tk.Frame(self.root, bg='#404040')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Status: Ready",
            bg='#404040',
            fg='#00ff00',
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack(pady=5)
        
        # Fish counter
        self.fish_label = tk.Label(
            main_frame,
            text="Fish: 0",
            bg='#404040',
            fg='white',
            font=('Arial', 10)
        )
        self.fish_label.pack(pady=5)
        
        # Rarity counters
        self.rarity_frame = tk.Frame(main_frame, bg='#404040')
        self.rarity_labels = {}
        
        rarities = ['Vaulted(Red)', 'Legendary(Yellow)', 'Rare(Blue)', 'Epic(Purple)', 'Common(Grey)']
        for rarity in rarities:
            label = tk.Label(
                self.rarity_frame,
                text=f"{rarity}: 0",
                bg='#404040',
                fg=self.get_rarity_color(rarity),
                font=('Arial', 8)
            )
            label.pack(anchor='w')
            self.rarity_labels[rarity] = label
        
        # Only show rarity frame if UI is enabled
        if not self.main_gui.settings.get('ui_enabled', False):
            self.rarity_frame.pack_forget()
        else:
            self.rarity_frame.pack(pady=5)
        
        # Bind mouse events for dragging
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
    
    def get_rarity_color(self, rarity):
        """Get color for rarity display"""
        colors = {
            'Vaulted(Red)': '#ff4444',
            'Legendary(Yellow)': '#ffaa00',
            'Rare(Blue)': '#4444ff',
            'Epic(Purple)': '#ff44ff',
            'Common(Grey)': '#888888'
        }
        return colors.get(rarity, 'white')
    
    def position_window(self, right_offset=50, top_offset=50):
        """Position window at top-right of screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        
        x = screen_width - self.root.winfo_width() - right_offset
        y = top_offset
        
        self.root.geometry(f"+{x}+{y}")
    
    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def drag(self, event):
        """Handle window dragging"""
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Stop dragging the window"""
        pass
    
    def update_status(self, status):
        """Update status label"""
        def update():
            self.status_label.config(text=f"Status: {status}")
        
        if hasattr(self, 'root'):
            self.root.after(0, update)
    
    def update_fish_count(self, count):
        """Update fish counter"""
        def update():
            self.fish_label.config(text=f"Fish: {count}")
        
        if hasattr(self, 'root'):
            self.root.after(0, update)
    
    def update_rarity_count(self, rarity, count):
        """Update specific rarity counter"""
        if rarity in self.rarity_labels:
            def update():
                self.rarity_labels[rarity].config(text=f"{rarity}: {count}")
            
            if hasattr(self, 'root'):
                self.root.after(0, update)
    
    def show(self):
        """Show the status window"""
        self.root.deiconify()
        self.root.lift()
    
    def hide(self):
        """Hide the status window"""
        self.root.withdraw()
    
    def close(self):
        """Close the status window"""
        self.root.destroy()

class SquircleGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.bot = None
        self.bot_thread = None
        self.is_running = False
        self.status_ui = None
        
        # Settings
        self.settings = {
            'fishing_key': 'e',
            'key_modifiers': [],
            'discord_webhook': '',
            'send_loot_colors': {'Vaulted(Red)': True, 'Legendary(Yellow)': True, 'Rare(Blue)': True, 'Epic(Purple)': True, 'Common(Grey)': False},
            'always_on_top': True,
            'anti_stuck': True,
            'total_fishes': 0,
            'ui_enabled': False,
            'ui_position': {'x': 50, 'y': 50},
            'rarity_counters': {'Vaulted(Red)': 0, 'Legendary(Yellow)': 0, 'Rare(Blue)': 0, 'Epic(Purple)': 0, 'Common(Grey)': 0}
        }
        
        self.load_settings()
        self.setup_gui()
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('bot_settings.json'):
                with open('bot_settings.json', 'r') as f:
                    self.settings.update(json.load(f))
        except:
            pass
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open('bot_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root.title("Pixel Blade Fishing Bot")
        self.root.geometry("500x600")
        self.root.configure(bg='#2d2d2d')
        
        if self.settings['always_on_top']:
            self.root.attributes('-topmost', True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2d2d2d')
        style.configure('TNotebook.Tab', background='#404040', foreground='white')
        style.map('TNotebook.Tab', background=[('selected', '#505050')])
        
        # Create tabs
        self.create_main_tab()
        self.create_settings_tab()
        self.create_discord_tab()
        self.create_stats_tab()
    
    def create_main_tab(self):
        """Create main control tab"""
        main_frame = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(main_frame, text='Main')
        
        # Start/Stop button
        self.start_button = tk.Button(
            main_frame, 
            text="START BOT", 
            command=self.toggle_bot,
            bg='#4CAF50', 
            fg='white', 
            font=('Arial', 14, 'bold'),
            width=20, 
            height=2
        )
        self.start_button.pack(pady=20)
        
        # Status display
        self.status_label = tk.Label(
            main_frame, 
            text="Status: Ready", 
            bg='#2d2d2d', 
            fg='#00ff00',
            font=('Arial', 12)
        )
        self.status_label.pack(pady=10)
        
        # Quick settings
        quick_frame = tk.Frame(main_frame, bg='#2d2d2d')
        quick_frame.pack(pady=20)
        
        # Anti-stuck toggle
        self.anti_stuck_var = tk.BooleanVar(value=self.settings['anti_stuck'])
        anti_stuck_cb = tk.Checkbutton(
            quick_frame, 
            text="Anti-Stuck (spam E if no circle found)",
            variable=self.anti_stuck_var,
            bg='#2d2d2d', 
            fg='white',
            selectcolor='#404040',
            command=self.update_anti_stuck
        )
        anti_stuck_cb.pack(pady=5)
        
        # Always on top toggle
        self.always_on_top_var = tk.BooleanVar(value=self.settings['always_on_top'])
        top_cb = tk.Checkbutton(
            quick_frame, 
            text="Always on Top",
            variable=self.always_on_top_var,
            bg='#2d2d2d', 
            fg='white',
            selectcolor='#404040',
            command=self.update_always_on_top
        )
        top_cb.pack(pady=5)
        
        # UI toggle
        self.ui_enabled_var = tk.BooleanVar(value=self.settings['ui_enabled'])
        ui_cb = tk.Checkbutton(
            quick_frame, 
            text="Status UI (draggable window)",
            variable=self.ui_enabled_var,
            bg='#2d2d2d', 
            fg='white',
            selectcolor='#404040',
            command=self.toggle_ui
        )
        ui_cb.pack(pady=5)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(settings_frame, text='Settings')
        
        # Keybind section
        keybind_frame = tk.LabelFrame(settings_frame, text="Keybind Settings", bg='#2d2d2d', fg='white')
        keybind_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(keybind_frame, text="Fishing Key:", bg='#2d2d2d', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.key_entry = tk.Entry(keybind_frame, bg='#404040', fg='white')
        self.key_entry.insert(0, self.settings['fishing_key'])
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Modifiers
        modifiers_frame = tk.Frame(keybind_frame, bg='#2d2d2d')
        modifiers_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.alt_var = tk.BooleanVar()
        self.shift_var = tk.BooleanVar()
        self.ctrl_var = tk.BooleanVar()
        
        tk.Checkbutton(modifiers_frame, text="Alt", variable=self.alt_var, bg='#2d2d2d', fg='white', selectcolor='#404040').pack(side='left', padx=5)
        tk.Checkbutton(modifiers_frame, text="Shift", variable=self.shift_var, bg='#2d2d2d', fg='white', selectcolor='#404040').pack(side='left', padx=5)
        tk.Checkbutton(modifiers_frame, text="Ctrl", variable=self.ctrl_var, bg='#2d2d2d', fg='white', selectcolor='#404040').pack(side='left', padx=5)
        
        # Save button
        tk.Button(settings_frame, text="Save Settings", command=self.save_settings, bg='#4CAF50', fg='white').pack(pady=20)
    
    def create_discord_tab(self):
        """Create Discord webhook tab"""
        discord_frame = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(discord_frame, text='Discord')
        
        # Webhook URL
        tk.Label(discord_frame, text="Discord Webhook URL:", bg='#2d2d2d', fg='white').pack(anchor='w', padx=10, pady=5)
        
        self.webhook_entry = tk.Text(discord_frame, height=3, bg='#404040', fg='white')
        self.webhook_entry.insert('1.0', self.settings['discord_webhook'])
        self.webhook_entry.pack(fill='x', padx=10, pady=5)
        
        # Loot color selection
        tk.Label(discord_frame, text="Send loot for these rarities:", bg='#2d2d2d', fg='white').pack(anchor='w', padx=10, pady=10)
        
        colors_frame = tk.Frame(discord_frame, bg='#2d2d2d')
        colors_frame.pack(padx=10, pady=5)
        
        self.loot_vars = {}
        for rarity in ['Vaulted(Red)', 'Legendary(Yellow)', 'Rare(Blue)', 'Epic(Purple)', 'Common(Grey)']:
            var = tk.BooleanVar(value=self.settings['send_loot_colors'].get(rarity, True))
            self.loot_vars[rarity] = var
            tk.Checkbutton(
                colors_frame, 
                text=rarity, 
                variable=var,
                bg='#2d2d2d', 
                fg='white',
                selectcolor='#404040'
            ).pack(anchor='w', pady=2)
        
        # Send image option
        self.send_image_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            discord_frame, 
            text="Send screenshot with loot", 
            variable=self.send_image_var,
            bg='#2d2d2d', 
            fg='white',
            selectcolor='#404040'
        ).pack(anchor='w', padx=10, pady=10)
    
    def create_stats_tab(self):
        """Create statistics tab"""
        stats_frame = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(stats_frame, text='Stats')
        
        # Total fishes counter
        tk.Label(stats_frame, text="Total Fishes Caught:", bg='#2d2d2d', fg='white', font=('Arial', 12)).pack(pady=10)
        
        self.fishes_label = tk.Label(stats_frame, text=str(self.settings['total_fishes']), bg='#2d2d2d', fg='#00ff00', font=('Arial', 24, 'bold'))
        self.fishes_label.pack(pady=10)
        
        # Reset counter button
        tk.Button(stats_frame, text="Reset Counter", command=self.reset_counter, bg='#f44336', fg='white').pack(pady=20)
    
    def toggle_bot(self):
        """Start or stop the bot"""
        if not self.is_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        """Start the fishing bot"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="STOP BOT", bg='#f44336')
            self.status_label.config(text="Status: Running", fg='#ffff00')
            
            # Update settings from GUI
            self.update_settings_from_gui()
            
            # Show status UI if enabled
            if self.settings['ui_enabled']:
                if self.status_ui is None:
                    self.status_ui = StatusUI(self)
                self.status_ui.show()
            
            # Start bot in separate thread
            self.bot_thread = threading.Thread(target=self.run_bot)
            self.bot_thread.daemon = True
            self.bot_thread.start()
    
    def stop_bot(self):
        """Stop the fishing bot"""
        self.is_running = False
        self.start_button.config(text="START BOT", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='#ff0000')
    
    def run_bot(self):
        """Run the bot logic with enhanced detection"""
        try:
            # Initialize bot with current settings
            self.bot = PixelBladeFishingBot()
            self.bot.fishing_key = self.settings['fishing_key']
            self.bot.fishing_key_modifiers = self.settings['key_modifiers']
            
            logger.info("Bot started with enhanced detection")
            
            while self.is_running:
                # Anti-stuck check if enabled
                if self.settings['anti_stuck']:
                    if not self.bot.anti_stuck_check():
                        continue
                
                # Look for fishing UI
                image = self.bot.capture_screen()
                if self.bot.detect_fishing_ui(image):
                    self.update_status("Fishing UI detected - starting cycle")
                    
                    # Start fishing
                    self.bot.press_fishing_key()
                    time.sleep(0.5)
                    
                    # Wait for optimal timing
                    if self.bot.wait_for_circle_overlap():
                        self.bot.press_fishing_key()
                        time.sleep(1.0)
                        
                        # Check for loot
                        image = self.bot.capture_screen()
                        found_loot, loot_rarity, position = self.bot.detect_loot(image)
                        
                        if found_loot and self.settings['send_loot_colors'].get(loot_rarity, False):
                            self.handle_loot_found(loot_rarity, position, image)
                        
                        # Update counter
                        self.settings['total_fishes'] += 1
                        self.update_fish_counter()
                        
                        # Update status UI
                        if self.status_ui:
                            self.status_ui.update_fish_count(self.settings['total_fishes'])
                            if found_loot:
                                self.settings['rarity_counters'][loot_rarity] += 1
                                self.status_ui.update_rarity_count(loot_rarity, 
                                    self.settings['rarity_counters'][loot_rarity])
                        
                        # Clean up
                        self.bot.spam_fishing_key()
                    
                    self.update_status("Ready")
                    time.sleep(1.0)
                else:
                    self.update_status("Searching...")
                    time.sleep(0.5)
                    
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.update_status(f"Error: {str(e)}")
    
    def handle_loot_found(self, color, position, image):
        """Handle loot detection and Discord notification"""
        self.update_status(f"Loot found: {color}!")
        
        # Send Discord notification if webhook is configured
        if self.settings['discord_webhook']:
            try:
                # Prepare Discord message
                embed = {
                    "title": f"🎣 {color} Loot Found!",
                    "description": f"Pixel Blade fishing bot found {color} loot!",
                    "color": self.get_discord_color(color)
                }
                
                # Send to Discord
                requests.post(self.settings['discord_webhook'], json={"embeds": [embed]})
                
            except Exception as e:
                logger.error(f"Failed to send Discord notification: {e}")
    
    def get_discord_color(self, loot_color):
        """Get Discord color code for loot color"""
        colors = {
            'Vaulted(Red)': 0xFF0000,
            'Legendary(Yellow)': 0xFFFF00,
            'Rare(Blue)': 0x0000FF,
            'Epic(Purple)': 0xFF00FF,
            'Common(Grey)': 0x808080
        }
        return colors.get(loot_color, 0xFFFFFF)
    
    def update_status(self, status):
        """Update status label in main thread"""
        def update():
            self.status_label.config(text=f"Status: {status}")
        
        if hasattr(self, 'root'):
            self.root.after(0, update)
    
    def update_fish_counter(self):
        """Update fish counter display"""
        def update():
            self.fishes_label.config(text=str(self.settings['total_fishes']))
            self.save_settings()
        
        if hasattr(self, 'root'):
            self.root.after(0, update)
    
    def update_settings_from_gui(self):
        """Update settings from GUI inputs"""
        self.settings['fishing_key'] = self.key_entry.get()
        self.settings['anti_stuck'] = self.anti_stuck_var.get()
        self.settings['always_on_top'] = self.always_on_top_var.get()
        self.settings['discord_webhook'] = self.webhook_entry.get('1.0', tk.END).strip()
        
        # Update modifiers
        modifiers = []
        if self.alt_var.get():
            modifiers.append('alt')
        if self.shift_var.get():
            modifiers.append('shift')
        if self.ctrl_var.get():
            modifiers.append('ctrl')
        self.settings['key_modifiers'] = modifiers
        
        # Update loot colors
        for color, var in self.loot_vars.items():
            self.settings['send_loot_colors'][color] = var.get()
        
        self.save_settings()
    
    def update_anti_stuck(self):
        """Update anti-stuck setting"""
        self.settings['anti_stuck'] = self.anti_stuck_var.get()
        self.save_settings()
    
    def toggle_ui(self):
        """Toggle status UI window"""
        self.settings['ui_enabled'] = self.ui_enabled_var.get()
        self.save_settings()
        
        if self.settings['ui_enabled']:
            if self.status_ui is None:
                self.status_ui = StatusUI(self)
            self.status_ui.show()
        else:
            if self.status_ui:
                self.status_ui.hide()
    
    def update_always_on_top(self):
        """Update always on top setting"""
        self.settings['always_on_top'] = self.always_on_top_var.get()
        self.root.attributes('-topmost', self.settings['always_on_top'])
        
        # Update status UI if it exists
        if self.status_ui:
            self.status_ui.root.attributes('-topmost', self.settings['always_on_top'])
        
        self.save_settings()
    
    def reset_counter(self):
        """Reset the fish counter"""
        self.settings['total_fishes'] = 0
        self.fishes_label.config(text="0")
        self.save_settings()
    
    def run(self):
        """Start the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            self.stop_bot()
        self.save_settings()
        self.root.destroy()

def main():
    """Main entry point"""
    gui = SquircleGUI()
    gui.run()

if __name__ == "__main__":
    main()

# Continue in next part...
