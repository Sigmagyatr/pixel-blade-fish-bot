import tkinter as tk
from tkinter import ttk
import threading
import time

class StatusUI:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.root = tk.Toplevel()
        self.setup_window()
        self.setup_widgets()
        
        # Position at top-right by default
        self.position_window(50, 50)  # 50px from right, 50px from top
        
        # Make draggable
        self.drag_start_x = 0
        self.drag_start_y = 0
        
    def setup_window(self):
        """Setup the status window properties"""
        self.root.title("Bot Status")
        self.root.geometry("300x200")
        self.root.configure(bg='#2d2d2d')
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Always on top if main GUI has it enabled
        if self.main_gui.settings.get('always_on_top', True):
            self.root.attributes('-topmost', True)
        
        # Make transparent background
        self.root.attributes('-transparentcolor', '#2d2d2d')
        
    def setup_widgets(self):
        """Setup status display widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Status: Ready",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack(pady=5)
        
        # Fish counter
        self.fish_label = tk.Label(
            main_frame,
            text="Fish: 0",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 10)
        )
        self.fish_label.pack(pady=5)
        
        # Rarity counters (if enabled)
        self.rarity_frame = tk.Frame(main_frame, bg='#2d2d2d')
        self.rarity_labels = {}
        
        rarities = ['Vaulted(Red)', 'Legendary(Yellow)', 'Rare(Blue)', 'Epic(Purple)', 'Common(Grey)']
        for rarity in rarities:
            label = tk.Label(
                self.rarity_frame,
                text=f"{rarity}: 0",
                bg='#2d2d2d',
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
        screen_height = self.root.winfo_screenheight()
        
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
