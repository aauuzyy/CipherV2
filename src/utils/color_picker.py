"""
Color Picker Widget - Visual color selector
"""
import tkinter as tk
from tkinter import ttk

class ColorPicker:
    """Color picker with visual selector and hex/rgb conversion"""
    
    def __init__(self, parent, initial_color="#0078d4", callback=None):
        self.parent = parent
        self.current_color = initial_color
        self.callback = callback
        
    def show(self):
        """Show color picker dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Color Picker")
        dialog.geometry("400x500")
        dialog.configure(bg="#1e1e1e")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Preview
        preview_frame = tk.Frame(dialog, bg="#1e1e1e")
        preview_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(preview_frame, text="Preview:", font=("Segoe UI", 10, "bold"),
                bg="#1e1e1e", fg="white").pack(anchor="w", pady=(0, 10))
        
        self.preview = tk.Frame(preview_frame, bg=self.current_color,
                               height=80, highlightbackground="white",
                               highlightthickness=2)
        self.preview.pack(fill=tk.X)
        
        # RGB Sliders
        sliders_frame = tk.Frame(dialog, bg="#1e1e1e")
        sliders_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Parse initial color
        r, g, b = self.hex_to_rgb(self.current_color)
        
        self.r_var = tk.IntVar(value=r)
        self.g_var = tk.IntVar(value=g)
        self.b_var = tk.IntVar(value=b)
        
        def update_color(*args):
            r = self.r_var.get()
            g = self.g_var.get()
            b = self.b_var.get()
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.current_color = hex_color
            self.preview.config(bg=hex_color)
            hex_entry.delete(0, tk.END)
            hex_entry.insert(0, hex_color.upper())
            rgb_label.config(text=f"RGB({r}, {g}, {b})")
        
        # Red slider
        tk.Label(sliders_frame, text="Red:", font=("Segoe UI", 10),
                bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky="w", pady=5)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                variable=self.r_var, command=update_color,
                bg="#cc0000", fg="white", highlightthickness=0,
                length=250).grid(row=0, column=1, padx=10)
        tk.Label(sliders_frame, textvariable=self.r_var, font=("Consolas", 10),
                bg="#1e1e1e", fg="white", width=3).grid(row=0, column=2)
        
        # Green slider
        tk.Label(sliders_frame, text="Green:", font=("Segoe UI", 10),
                bg="#1e1e1e", fg="white").grid(row=1, column=0, sticky="w", pady=5)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                variable=self.g_var, command=update_color,
                bg="#00cc00", fg="white", highlightthickness=0,
                length=250).grid(row=1, column=1, padx=10)
        tk.Label(sliders_frame, textvariable=self.g_var, font=("Consolas", 10),
                bg="#1e1e1e", fg="white", width=3).grid(row=1, column=2)
        
        # Blue slider
        tk.Label(sliders_frame, text="Blue:", font=("Segoe UI", 10),
                bg="#1e1e1e", fg="white").grid(row=2, column=0, sticky="w", pady=5)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                variable=self.b_var, command=update_color,
                bg="#0066cc", fg="white", highlightthickness=0,
                length=250).grid(row=2, column=1, padx=10)
        tk.Label(sliders_frame, textvariable=self.b_var, font=("Consolas", 10),
                bg="#1e1e1e", fg="white", width=3).grid(row=2, column=2)
        
        # Color values
        values_frame = tk.Frame(dialog, bg="#2d2d2d")
        values_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # HEX input
        hex_frame = tk.Frame(values_frame, bg="#2d2d2d")
        hex_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(hex_frame, text="HEX:", font=("Segoe UI", 10, "bold"),
                bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        
        hex_entry = tk.Entry(hex_frame, font=("Consolas", 11), width=10,
                            bg="#1e1e1e", fg="white", insertbackground="white")
        hex_entry.pack(side=tk.LEFT, padx=5)
        hex_entry.insert(0, self.current_color.upper())
        
        def apply_hex(*args):
            try:
                hex_color = hex_entry.get()
                if not hex_color.startswith('#'):
                    hex_color = '#' + hex_color
                r, g, b = self.hex_to_rgb(hex_color)
                self.r_var.set(r)
                self.g_var.set(g)
                self.b_var.set(b)
            except:
                pass
        
        hex_entry.bind('<Return>', apply_hex)
        
        tk.Button(hex_frame, text="Apply", font=("Segoe UI", 9),
                 bg="#0078d4", fg="white", relief=tk.FLAT, padx=10, pady=5,
                 cursor="hand2", command=apply_hex).pack(side=tk.LEFT, padx=5)
        
        # RGB display
        rgb_label = tk.Label(values_frame, text=f"RGB({r}, {g}, {b})",
                            font=("Consolas", 10),
                            bg="#2d2d2d", fg="white")
        rgb_label.pack(pady=5)
        
        # Common colors
        common_frame = tk.LabelFrame(dialog, text="Common Colors",
                                     font=("Segoe UI", 10, "bold"),
                                     bg="#1e1e1e", fg="white")
        common_frame.pack(fill=tk.X, padx=20, pady=10)
        
        common_colors = [
            "#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff",
            "#ffff00", "#ff00ff", "#00ffff", "#808080", "#c0c0c0",
            "#800000", "#808000", "#008000", "#800080", "#008080",
            "#000080", "#ff8000", "#0078d4", "#00aa00", "#cc3333"
        ]
        
        colors_grid = tk.Frame(common_frame, bg="#1e1e1e")
        colors_grid.pack(padx=10, pady=10)
        
        def select_common(color):
            r, g, b = self.hex_to_rgb(color)
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
        
        for i, color in enumerate(common_colors):
            btn = tk.Button(colors_grid, bg=color, width=3, height=1,
                           relief=tk.FLAT, cursor="hand2",
                           command=lambda c=color: select_common(c))
            btn.grid(row=i // 10, column=i % 10, padx=2, pady=2)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#1e1e1e")
        btn_frame.pack(pady=20)
        
        def ok_clicked():
            if self.callback:
                self.callback(self.current_color)
            dialog.destroy()
        
        def copy_hex():
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.current_color)
        
        tk.Button(btn_frame, text="OK", font=("Segoe UI", 10, "bold"),
                 bg="#0078d4", fg="white", relief=tk.FLAT, padx=30, pady=10,
                 cursor="hand2", command=ok_clicked).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Copy HEX", font=("Segoe UI", 10),
                 bg="#2d2d2d", fg="white", relief=tk.FLAT, padx=20, pady=10,
                 cursor="hand2", command=copy_hex).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10),
                 bg="#2d2d2d", fg="white", relief=tk.FLAT, padx=20, pady=10,
                 cursor="hand2", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert HEX to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
