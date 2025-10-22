"""Status bar component for CipherV2"""
import tkinter as tk
import time

class StatusBar:
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.setup_ui()
        self.start_time_update()
    
    def setup_ui(self):
        """Create the status bar UI"""
        self.frame = tk.Frame(self.parent, 
                            bg=self.theme['secondary_bg'],
                            height=25)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.frame.pack_propagate(False)
        
        # Status message
        self.status_text = tk.Label(self.frame, 
                                  text="Ready",
                                  font=("Segoe UI", 8),
                                  bg=self.theme['secondary_bg'],
                                  fg="#a0a0a0")
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # Time display
        self.time_display = tk.Label(self.frame,
                                   text="",
                                   font=("Segoe UI", 8),
                                   bg=self.theme['secondary_bg'],
                                   fg="#a0a0a0")
        self.time_display.pack(side=tk.RIGHT, padx=10)
    
    def update_status(self, message):
        """Update status message"""
        if hasattr(self, 'status_text'):
            self.status_text.config(text=message)
    
    def update_time(self):
        """Update time display"""
        if hasattr(self, 'time_display'):
            current_time = time.strftime("%I:%M:%S %p")
            self.time_display.config(text=current_time)
            self.parent.after(1000, self.update_time)
    
    def start_time_update(self):
        """Start the time update cycle"""
        self.update_time()