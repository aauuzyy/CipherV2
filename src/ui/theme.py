"""UI theme and visual enhancement utilities"""
import tkinter as tk

class ThemeManager:
    """Manage application themes and visual effects"""
    
    DARK_THEME = {
        'bg_color': "#1e1e1e",
        'secondary_bg': "#2d2d2d",
        'accent_color': "#0d7377",
        'text_color': "#e0e0e0",
        'button_hover': "#14a0a6",
        'scrollbar_bg': "#2d2d2d",
        'scrollbar_fg': "#404040"
    }
    
    LIGHT_THEME = {
        'bg_color': "#f5f5f5",
        'secondary_bg': "#ffffff",
        'accent_color': "#0d7377",
        'text_color': "#000000",
        'button_hover': "#14a0a6",
        'scrollbar_bg': "#f0f0f0",
        'scrollbar_fg': "#c0c0c0"
    }

    @staticmethod
    def create_diagonal_pattern(canvas, color="#2d2d2d", spacing=20):
        """Create diagonal line pattern on canvas"""
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        
        # Clear existing lines
        canvas.delete("pattern")
        
        # Draw new diagonal lines
        for i in range(-height, width + height, spacing):
            canvas.create_line(i, 0, i + height, height,
                             fill=color, width=1, tags="pattern")

    @staticmethod
    def create_custom_scrollbar(parent, **kwargs):
        """Create a custom styled scrollbar"""
        style = kwargs.get('style', 'dark')
        width = kwargs.get('width', 12)
        
        colors = ThemeManager.DARK_THEME if style == 'dark' else ThemeManager.LIGHT_THEME
        
        scrollbar = tk.Scrollbar(parent,
                               width=width,
                               bg=colors['scrollbar_bg'],
                               troughcolor=colors['bg_color'],
                               activebackground=colors['scrollbar_fg'])
        return scrollbar

    @staticmethod
    def apply_fade_transition(widget, start_alpha=1.0, end_alpha=0.3, 
                            step=0.05, interval=10, callback=None):
        """Apply fade transition effect to widget"""
        def fade_out(alpha):
            if alpha > end_alpha:
                widget.attributes('-alpha', alpha)
                widget.after(interval, lambda: fade_out(alpha - step))
            else:
                if callback:
                    callback()
                fade_in(end_alpha)
        
        def fade_in(alpha):
            if alpha < start_alpha:
                widget.attributes('-alpha', alpha)
                widget.after(interval, lambda: fade_in(alpha + step))
            else:
                widget.attributes('-alpha', start_alpha)
        
        fade_out(start_alpha)

    @staticmethod
    def create_hover_effect(widget, enter_color, leave_color):
        """Create hover effect for widget"""
        widget.bind("<Enter>", lambda e: widget.config(bg=enter_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=leave_color))

    @staticmethod
    def create_card_layout(parent, title, description, callback=None, **kwargs):
        """Create a modern card-based layout element"""
        colors = ThemeManager.DARK_THEME if kwargs.get('style', 'dark') == 'dark' else ThemeManager.LIGHT_THEME
        
        card = tk.Frame(parent,
                       bg=colors['secondary_bg'],
                       highlightbackground=colors['accent_color'],
                       highlightthickness=0)
        
        title_label = tk.Label(card,
                             text=title,
                             font=("Segoe UI", 12, "bold"),
                             bg=colors['secondary_bg'],
                             fg=colors['text_color'])
        title_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        desc_label = tk.Label(card,
                            text=description,
                            font=("Segoe UI", 9),
                            bg=colors['secondary_bg'],
                            fg="#a0a0a0",
                            wraplength=200)
        desc_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        if callback:
            action_btn = tk.Button(card,
                                 text="Execute",
                                 font=("Segoe UI", 9, "bold"),
                                 bg=colors['accent_color'],
                                 fg="white",
                                 border=0,
                                 cursor="hand2",
                                 command=callback)
            action_btn.pack(anchor="w", padx=15, pady=(0, 15))
            
            ThemeManager.create_hover_effect(action_btn,
                                          colors['button_hover'],
                                          colors['accent_color'])
        
        def on_card_enter(e):
            card.config(highlightthickness=1)
        
        def on_card_leave(e):
            card.config(highlightthickness=0)
        
        card.bind("<Enter>", on_card_enter)
        card.bind("<Leave>", on_card_leave)
        
        return card