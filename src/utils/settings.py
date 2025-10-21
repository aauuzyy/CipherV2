import tkinter as tk
from dataclasses import dataclass

@dataclass
class Settings:
    """Container for application settings"""
    
    # Constructor-initialized variables
    def __init__(self):
        self.notifications = tk.BooleanVar(value=True)
        self.autostart = tk.BooleanVar(value=False) 
        self.darkmode = tk.BooleanVar(value=True)
        self.savelogs = tk.BooleanVar(value=True)
        self.syntax_highlight = tk.BooleanVar(value=True)
        self.line_numbers = tk.BooleanVar(value=True)
        self.autocomplete = tk.BooleanVar(value=True)

    # Method to get all settings as a dict
    def get_all(self):
        return {
            'notifications': self.notifications.get(),
            'autostart': self.autostart.get(),
            'darkmode': self.darkmode.get(),
            'savelogs': self.savelogs.get(),
            'syntax_highlight': self.syntax_highlight.get(),
            'line_numbers': self.line_numbers.get(),
            'autocomplete': self.autocomplete.get()
        }

    # Method to update all settings from a dict
    def update_from_dict(self, settings_dict):
        for key, value in settings_dict.items():
            if hasattr(self, key):
                getattr(self, key).set(value)