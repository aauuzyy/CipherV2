"""
Toast Notification System - Non-intrusive notifications
"""
import tkinter as tk

class ToastNotification:
    """Toast-style notification that appears in bottom-right corner"""
    
    def __init__(self, parent, message, notification_type="info", duration=3000):
        """
        Create toast notification
        notification_type: "info", "success", "warning", "error"
        duration: milliseconds to show notification
        """
        self.parent = parent
        self.duration = duration
        
        # Colors for different types
        colors = {
            "info": ("#0078d4", "#ffffff"),
            "success": ("#00aa00", "#ffffff"),
            "warning": ("#ff8c00", "#ffffff"),
            "error": ("#cc0000", "#ffffff")
        }
        
        bg_color, fg_color = colors.get(notification_type, colors["info"])
        
        # Create notification window
        self.notification = tk.Toplevel(parent)
        self.notification.overrideredirect(True)
        self.notification.attributes('-topmost', True)
        self.notification.configure(bg=bg_color)
        
        # Get icons for notification types
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }
        
        icon = icons.get(notification_type, "ℹ️")
        
        # Content frame
        content_frame = tk.Frame(self.notification, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Icon
        icon_label = tk.Label(content_frame, text=icon,
                             font=("Segoe UI", 16),
                             bg=bg_color, fg=fg_color)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Message
        msg_label = tk.Label(content_frame, text=message,
                           font=("Segoe UI", 10),
                           bg=bg_color, fg=fg_color,
                           wraplength=250)
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Position in bottom-right corner
        self.notification.update_idletasks()
        width = self.notification.winfo_width()
        height = self.notification.winfo_height()
        
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        x = screen_width - width - 20
        y = screen_height - height - 60
        
        # Start off-screen (below)
        self.notification.geometry(f"+{x}+{screen_height}")
        
        # Animate in
        self.animate_in(y)
        
        # Schedule close
        parent.after(duration, self.animate_out)
    
    def animate_in(self, target_y):
        """Slide in animation"""
        current_y = int(self.notification.geometry().split('+')[-1])
        
        if current_y > target_y:
            new_y = max(current_y - 20, target_y)
            x = int(self.notification.geometry().split('+')[1])
            self.notification.geometry(f"+{x}+{new_y}")
            self.parent.after(10, lambda: self.animate_in(target_y))
    
    def animate_out(self):
        """Slide out animation"""
        try:
            current_y = int(self.notification.geometry().split('+')[-1])
            screen_height = self.parent.winfo_screenheight()
            
            if current_y < screen_height:
                new_y = current_y + 20
                x = int(self.notification.geometry().split('+')[1])
                self.notification.geometry(f"+{x}+{new_y}")
                self.parent.after(10, self.animate_out)
            else:
                self.notification.destroy()
        except:
            pass
