"""Header bar component for CipherV2"""
import tkinter as tk

class HeaderBar:
    def __init__(self, parent, theme, on_drag=None, on_minimize=None, on_close=None):
        self.parent = parent
        self.theme = theme
        self.on_drag = on_drag
        self.on_minimize = on_minimize or parent.iconify
        self.on_close = on_close or parent.quit
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the header bar UI"""
        self.frame = tk.Frame(self.parent,
                            bg=self.theme['secondary_bg'],
                            height=60)
        self.frame.pack(fill=tk.X, side=tk.TOP)
        self.frame.pack_propagate(False)
        
        # Bind drag events if callback provided
        if self.on_drag:
            self.frame.bind("<Button-1>", self.on_drag_start)
            self.frame.bind("<B1-Motion>", self.on_drag_motion)
        
        # Title and version
        self.create_title()
        
        # Window controls
        self.create_window_controls()
    
    def create_title(self):
        """Create title and version labels"""
        title = tk.Label(self.frame,
                        text="CipherV2",
                        font=("Segoe UI", 18, "bold"),
                        bg=self.theme['secondary_bg'],
                        fg=self.theme['text_color'])
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        if self.on_drag:
            title.bind("<Button-1>", self.on_drag_start)
            title.bind("<B1-Motion>", self.on_drag_motion)
        
        version = tk.Label(self.frame,
                          text="v2.0",
                          font=("Segoe UI", 8),
                          bg=self.theme['secondary_bg'],
                          fg="#a0a0a0")
        version.pack(side=tk.LEFT, pady=15)
    
    def create_window_controls(self):
        """Create window control buttons"""
        controls = tk.Frame(self.frame, bg=self.theme['secondary_bg'])
        controls.pack(side=tk.RIGHT, padx=5)
        
        # Minimize button
        min_btn = tk.Button(controls,
                           text="−",
                           font=("Segoe UI", 12),
                           bg=self.theme['secondary_bg'],
                           fg=self.theme['text_color'],
                           border=0,
                           command=self.on_minimize,
                           activebackground="#404040",
                           activeforeground="white",
                           cursor="hand2")
        min_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(controls,
                             text="×",
                             font=("Segoe UI", 12),
                             bg=self.theme['secondary_bg'],
                             fg=self.theme['text_color'],
                             border=0,
                             command=self.on_close,
                             activebackground="#d32f2f",
                             activeforeground="white",
                             cursor="hand2")
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Button hover effects
        min_btn.bind("<Enter>", lambda e: min_btn.config(bg="#404040"))
        min_btn.bind("<Leave>", lambda e: min_btn.config(bg=self.theme['secondary_bg']))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#d32f2f"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.theme['secondary_bg']))
    
    def on_drag_start(self, event):
        """Store initial drag position"""
        self._drag_data = (event.x, event.y)
    
    def on_drag_motion(self, event):
        """Handle drag motion"""
        if hasattr(self, '_drag_data'):
            start_x, start_y = self._drag_data
            # Call the provided drag callback
            self.on_drag(event.x - start_x, event.y - start_y)