import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import json
import re
from io import StringIO
from collections import deque

from utils.settings import Settings
from utils.constants import (
    SYNTAX_COLORS,
    PYTHON_KEYWORDS,
    CODE_SNIPPETS,
    DARK_THEME,
    LIGHT_THEME
)

class ModernUI:
    """Main UI class for CipherV2"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        
        # Initialize instance variables
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.tabs = {"Tab 1": ""}
        self.current_tab = "Tab 1"
        self.tab_counter = 1
        
        self.undo_stacks = {"Tab 1": deque(maxlen=50)}
        self.redo_stacks = {"Tab 1": deque(maxlen=50)}
        
        self.command_history = deque(maxlen=100)
        self.history_index = 0
        
        # Initialize settings
        self.settings = Settings()
        
        # Set up scripts directory
        self.scripts_dir = os.path.join(os.path.expanduser("~"), "Desktop", "BotModMenuSystem", "Saved Scripts")
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        # Initialize theme
        self.apply_theme()
        
        # Create UI
        self.show_loading_screen()
        
        # Set up auto-reload
        self.script_path = __file__
        self.last_modified = os.path.getmtime(self.script_path)
        self.watch_file()
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.save_script_dialog())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self.show_find_replace())
        self.root.bind('<Control-b>', lambda e: self.beautify_code())
    
    def apply_theme(self):
        """Apply current theme based on dark/light mode setting"""
        theme = DARK_THEME if self.settings.darkmode.get() else LIGHT_THEME
        
        for key, value in theme.items():
            setattr(self, key, value)
            
        self.root.configure(bg=self.bg_color)
    
    def show_loading_screen(self):
        """Show the initial loading screen animation"""
        self.loading_frame = tk.Frame(self.root, bg=self.bg_color)
        self.loading_frame.place(x=0, y=0, width=800, height=600)
        
        title = tk.Label(self.loading_frame, text="CipherV2", 
                        font=("Segoe UI", 24, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.place(relx=0.5, rely=0.4, anchor="center")
        
        self.loading_text = tk.Label(self.loading_frame, text="Loading...", 
                                   font=("Segoe UI", 10),
                                   bg=self.bg_color, fg="#a0a0a0")
        self.loading_text.place(relx=0.5, rely=0.5, anchor="center")
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Loading.Horizontal.TProgressbar",
                       background=self.accent_color,
                       troughcolor=self.secondary_bg,
                       bordercolor=self.bg_color,
                       lightcolor=self.accent_color,
                       darkcolor=self.accent_color)
        
        self.loading_progress = ttk.Progressbar(self.loading_frame, 
                                             style="Loading.Horizontal.TProgressbar",
                                             length=300, mode='determinate')
        self.loading_progress.place(relx=0.5, rely=0.55, anchor="center")
        
        threading.Thread(target=self.animate_loading, daemon=True).start()
    
    def animate_loading(self):
        """Animate the loading progress bar"""
        steps = ["Initializing...", "Loading modules...", "Setting up UI...", "Almost done..."]
        for i, step in enumerate(steps):
            time.sleep(0.5)
            self.loading_text.config(text=step)
            self.loading_progress['value'] = (i + 1) * 25
            self.root.update()
        
        time.sleep(0.3)
        self.loading_frame.destroy()
        self.create_main_ui()

    def create_main_ui(self):
        """Create the main UI components"""
        self.root.attributes('-alpha', 1.0)
        self.create_header_bar()
        self.create_footer()
        self.create_sidebar()
        self.create_main_content()

    def create_header_bar(self):
        """Create the custom window header bar"""
        self.header = tk.Frame(self.root, bg=self.secondary_bg, height=60)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)
        
        # Add window drag functionality
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)
        
        # Title and version label
        title = tk.Label(self.header, text="CipherV2", 
                        font=("Segoe UI", 18, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        title.bind("<Button-1>", self.start_drag)
        title.bind("<B1-Motion>", self.do_drag)
        
        version = tk.Label(self.header, text="v2.0", 
                          font=("Segoe UI", 8),
                          bg=self.secondary_bg, fg="#a0a0a0")
        version.pack(side=tk.LEFT, pady=15)
        
        # Window control buttons
        close_btn = tk.Button(self.header, text="✕", font=("Segoe UI", 14),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, command=self.root.quit,
                             activebackground="#d32f2f",
                             activeforeground="white", cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        reload_btn = tk.Button(self.header, text="↻", font=("Segoe UI", 16),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, command=self.manual_reload,
                              cursor="hand2", width=2)
        reload_btn.pack(side=tk.RIGHT, padx=5)
        
        # Button hover effects
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#d32f2f"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.secondary_bg))
        reload_btn.bind("<Enter>", lambda e: reload_btn.config(bg=self.button_hover))
        reload_btn.bind("<Leave>", lambda e: reload_btn.config(bg=self.secondary_bg))

    def start_drag(self, event):
        """Begin window drag operation"""
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y
    
    def do_drag(self, event):
        """Perform window drag operation"""
        x = self.root.winfo_x() + event.x - self.drag_offset_x
        y = self.root.winfo_y() + event.y - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")
    
    def watch_file(self):
        """Watch script file for changes and auto-reload"""
        try:
            current_modified = os.path.getmtime(self.script_path)
            if current_modified != self.last_modified:
                self.last_modified = current_modified
                print("\n[AUTO-RELOAD] Script file changed! Reloading UI...")
                
                current_page = self.current_page
                current_tab = self.current_tab
                tabs_backup = self.tabs.copy()
                settings_backup = self.settings.get_all()
                
                self.root.after(100, lambda: self.perform_reload(
                    current_page, current_tab, tabs_backup, settings_backup))
                return
        except Exception as e:
            print(f"[AUTO-RELOAD] Error checking file: {e}")
            pass
        
        self.root.after(1000, self.watch_file)
    
    def perform_reload(self, page, tab, tabs, settings_vals):
        """Perform UI reload while preserving state"""
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            
            self.settings.update_from_dict(settings_vals)
            self.tabs = tabs
            self.current_tab = tab
            
            self.apply_theme()
            self.create_header_bar()
            self.create_footer()
            self.create_sidebar()
            self.create_main_content()
            
            self.switch_page(page)
            
            self.update_status("UI reloaded successfully")
            print("[AUTO-RELOAD] UI reloaded successfully!\n")
        except Exception as e:
            print(f"[AUTO-RELOAD] Error during reload: {e}")
            self.watch_file()
    
    def manual_reload(self):
        """Manual reload triggered by button"""
        print("\n[MANUAL RELOAD] Reloading UI...")
        current_page = self.current_page
        current_tab = self.current_tab
        tabs_backup = self.tabs.copy()
        settings_backup = self.settings.get_all()
        
        self.perform_reload(current_page, current_tab, tabs_backup, settings_backup)

# ... Rest of the code follows same pattern of organization and improvement ...