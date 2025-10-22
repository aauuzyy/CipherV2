"""Loading screen component for CipherV2"""
import tkinter as tk
from tkinter import ttk
import threading
import time

class LoadingScreen:
    def __init__(self, parent, theme, on_complete):
        self.parent = parent
        self.theme = theme
        self.on_complete = on_complete
        
        # Configure TTK style
        self.setup_styles()
        
        # Create UI
        self.setup_ui()
        
        # Start loading animation
        self.start_animation()
    
    def setup_styles(self):
        """Configure TTK styles"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Progress bar style
        style.configure("Loading.Horizontal.TProgressbar",
                       background=self.theme['accent_color'],
                       troughcolor=self.theme['secondary_bg'],
                       bordercolor=self.theme['bg_color'],
                       lightcolor=self.theme['accent_color'],
                       darkcolor=self.theme['accent_color'])
    
    def setup_ui(self):
        """Create the loading screen UI"""
        self.frame = tk.Frame(self.parent, bg=self.theme['bg_color'])
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Title
        self.title = tk.Label(self.frame,
                            text="CipherV2",
                            font=("Segoe UI", 24, "bold"),
                            bg=self.theme['bg_color'],
                            fg=self.theme['text_color'])
        self.title.place(relx=0.5, rely=0.4, anchor="center")
        
        # Loading text
        self.loading_text = tk.Label(self.frame,
                                   text="Loading...",
                                   font=("Segoe UI", 10),
                                   bg=self.theme['bg_color'],
                                   fg="#a0a0a0")
        self.loading_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Progress bar
        self.progress = ttk.Progressbar(self.frame,
                                      style="Loading.Horizontal.TProgressbar",
                                      length=300,
                                      mode='determinate')
        self.progress.place(relx=0.5, rely=0.55, anchor="center")
    
    def start_animation(self):
        """Start the loading animation"""
        self.loading_thread = threading.Thread(target=self.animate, daemon=True)
        self.loading_thread.start()
    
    def animate(self):
        """Animate the loading screen"""
        try:
            steps = [
                "Initializing...",
                "Loading modules...",
                "Setting up UI...",
                "Almost done..."
            ]
            
            for i, step in enumerate(steps):
                # Update UI in main thread
                self.parent.after(1, lambda s=step: self.loading_text.config(text=s))
                self.parent.after(1, lambda v=(i+1)*25: self.progress.config(value=v))
                
                # Delay between steps
                time.sleep(0.5)
            
            # Final delay
            time.sleep(0.3)
            
            # Complete loading
            self.parent.after(1, self.complete_loading)
            
        except Exception as e:
            print(f"Loading error: {str(e)}")
    
    def complete_loading(self):
        """Complete the loading process"""
        try:
            self.frame.destroy()
            if self.on_complete:
                self.on_complete()
        except Exception as e:
            print(f"Error completing loading: {str(e)}")
    
    def destroy(self):
        """Clean up the loading screen"""
        if hasattr(self, 'frame'):
            self.frame.destroy()