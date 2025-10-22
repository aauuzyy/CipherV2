"""Login screen for CipherV2"""
import tkinter as tk
from tkinter import messagebox
import uuid

from .license import LicenseManager

class LoginScreen:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.license_manager = LicenseManager()
        
        # Check existing license first
        valid, message = self.license_manager.check_existing_license()
        if valid:
            self.on_success()
            return

        self.setup_login_window()

    def setup_login_window(self):
        """Create login window UI"""
        # Main window setup
        self.root.title("CipherV2 Login")
        self.root.geometry("400x500")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 500) // 2
        self.root.geometry(f"400x500+{x}+{y}")

        # Create diagonal pattern canvas
        canvas = tk.Canvas(self.root, width=400, height=500, 
                         bg="#1e1e1e", highlightthickness=0)
        canvas.place(x=0, y=0)

        # Draw diagonal lines
        for i in range(-500, 900, 20):
            canvas.create_line(i, 0, i+500, 500, 
                             fill="#2d2d2d", width=1)

        # Title
        title = tk.Label(self.root, text="CipherV2",
                        font=("Segoe UI", 24, "bold"),
                        bg="#1e1e1e", fg="#e0e0e0")
        title.place(relx=0.5, rely=0.2, anchor="center")

        # Subtitle
        subtitle = tk.Label(self.root, 
                          text="Enter your license key to continue",
                          font=("Segoe UI", 10),
                          bg="#1e1e1e", fg="#a0a0a0")
        subtitle.place(relx=0.5, rely=0.3, anchor="center")

        # License key entry
        self.license_entry = tk.Entry(self.root,
                                    font=("Segoe UI", 12),
                                    bg="#2d2d2d", fg="#e0e0e0",
                                    insertbackground="#e0e0e0",
                                    relief=tk.FLAT,
                                    justify="center",
                                    width=32)
        self.license_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Activate button
        activate_btn = tk.Button(self.root,
                               text="Activate License",
                               font=("Segoe UI", 11, "bold"),
                               bg="#0d7377", fg="white",
                               activebackground="#14a0a6",
                               activeforeground="white",
                               relief=tk.FLAT,
                               command=self.validate_license,
                               cursor="hand2",
                               width=20, height=2)
        activate_btn.place(relx=0.5, rely=0.5, anchor="center")

        # Generate trial button
        trial_btn = tk.Button(self.root,
                            text="Generate Trial License",
                            font=("Segoe UI", 9),
                            bg="#2d2d2d", fg="#e0e0e0",
                            activebackground="#3d3d3d",
                            activeforeground="#e0e0e0",
                            relief=tk.FLAT,
                            command=self.generate_trial,
                            cursor="hand2",
                            width=20)
        trial_btn.place(relx=0.5, rely=0.6, anchor="center")

        # Status label
        self.status_label = tk.Label(self.root,
                                   text="",
                                   font=("Segoe UI", 9),
                                   bg="#1e1e1e", fg="#a0a0a0",
                                   wraplength=300)
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")

    def validate_license(self):
        """Validate entered license key"""
        license_key = self.license_entry.get().strip()
        if not license_key:
            self.show_status("Please enter a license key", "error")
            return

        valid, message = self.license_manager.validate_license(license_key)
        if valid:
            self.show_status("License validated successfully!", "success")
            self.root.after(1000, self.on_success)
        else:
            self.show_status(message, "error")

    def generate_trial(self):
        """Generate trial license key"""
        trial_key = str(uuid.uuid4())
        self.license_entry.delete(0, tk.END)
        self.license_entry.insert(0, trial_key)
        self.show_status("Trial license generated! Click Activate to use.", "info")

    def show_status(self, message, status_type="info"):
        """Show status message with color"""
        colors = {
            "error": "#ff4444",
            "success": "#00ff00",
            "info": "#00aaff"
        }
        self.status_label.config(text=message, fg=colors.get(status_type, "#a0a0a0"))