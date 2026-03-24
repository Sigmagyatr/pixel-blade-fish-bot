import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
from fishing_bot import PixelBladeFishingBot
from status_ui import StatusUI

class SquircleGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.bot = None
        self.bot_thread = None
        self.is_running = False
        self.status_ui = None  # Status window instance
        
        # Settings
        self.settings = {
            'fishing_key': 'e',
            'key_modifiers': [],
            'discord_webhook': '',
            'send_loot_colors': {'Vaulted(Red)': True, 'Legendary(Yellow)': True, 'Rare(Blue)': True, 'Epic(Purple)': True, 'Common(Grey)': False},
            'always_on_top': True,
            'anti_stuck': True,
            'total_fishes': 0,
            'ui_enabled': False,  # Status UI disabled by default
            'ui_position': {'x': 50, 'y': 50},  # Default top-right position
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
            
            # Hide Python console window
            self.hide_console()
            
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
    
    def hide_console(self):
        """Hide the Python console window"""
        try:
            import ctypes
            import os
            
            # Get console window handle
            console_hwnd = ctypes.windll.user32.FindWindowW(None, "python.exe", None)
            if console_hwnd:
                # Hide the console
                ctypes.windll.user32.ShowWindow(console_hwnd, 0)  # SW_HIDE
        except:
            pass
    
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
                        continue  # Anti-stuck handled, continue loop
                
                # Look for fishing UI
                image = self.bot.capture_screen()
                if self.bot.detect_fishing_ui(image):
                    self.update_status("Fishing UI detected - starting cycle")
                    
                    # Start fishing
                    self.bot.press_fishing_key()
                    time.sleep(0.5)
                    
                    # Wait for optimal timing (green indicator or overlap)
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
                                # Update rarity counter
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
                import requests
                import base64
                
                # Prepare Discord message
                embed = {
                    "title": f"🎣 {color.capitalize()} Loot Found!",
                    "description": f"Pixel Blade fishing bot found {color} loot!",
                    "color": self.get_discord_color(color)
                }
                
                # Send image if option is enabled
                if self.send_image_var.get():
                    # Convert image to base64
                    _, buffer = cv2.imencode('.png', image)
                    img_base64 = base64.b64encode(buffer).decode()
                    
                    # Note: Discord webhook with images requires more complex handling
                    # This is a simplified version
                    embed["image"] = {"url": f"data:image/png;base64,{img_base64}"}
                
                # Send to Discord
                requests.post(self.settings['discord_webhook'], json={"embeds": [embed]})
                
            except Exception as e:
                logger.error(f"Failed to send Discord notification: {e}")
    
    def get_discord_color(self, loot_color):
        """Get Discord color code for loot color"""
        colors = {
            'red': 0xFF0000,
            'yellow': 0xFFFF00,
            'blue': 0x0000FF,
            'purple': 0xFF00FF,
            'grey': 0x808080
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

if __name__ == "__main__":
    gui = SquircleGUI()
    gui.run()
