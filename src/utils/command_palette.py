"""
Command Palette - Fuzzy search for all commands and features
"""
import tkinter as tk
from tkinter import ttk

class CommandPalette:
    """Command palette with fuzzy search"""
    
    def __init__(self, parent, commands_dict, theme, callback):
        """
        Initialize command palette
        commands_dict: {command_name: callback_function}
        """
        self.parent = parent
        self.commands = commands_dict
        self.theme = theme
        self.callback = callback
        self.dialog = None
        
    def show(self):
        """Show command palette dialog"""
        if self.dialog:
            self.dialog.destroy()
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Command Palette")
        self.dialog.geometry("600x400")
        self.dialog.configure(bg=self.theme['bg_color'])
        self.dialog.overrideredirect(True)
        
        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Make it topmost
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Search frame
        search_frame = tk.Frame(self.dialog, bg=self.theme['secondary_bg'])
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="❯",
                font=("Segoe UI", 14, "bold"),
                bg=self.theme['secondary_bg'],
                fg=self.theme['accent_color']).pack(side=tk.LEFT, padx=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_commands)
        
        self.search_entry = tk.Entry(search_frame,
                                     textvariable=self.search_var,
                                     font=("Segoe UI", 12),
                                     bg=self.theme['bg_color'],
                                     fg=self.theme['text_color'],
                                     insertbackground=self.theme['accent_color'],
                                     relief=tk.FLAT,
                                     bd=0)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=10)
        self.search_entry.focus()
        
        # Results list
        results_frame = tk.Frame(self.dialog, bg=self.theme['bg_color'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_list = tk.Listbox(results_frame,
                                       font=("Segoe UI", 11),
                                       bg=self.theme['secondary_bg'],
                                       fg=self.theme['text_color'],
                                       selectbackground=self.theme['accent_color'],
                                       selectforeground="white",
                                       relief=tk.FLAT,
                                       bd=0,
                                       highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_list.yview)
        
        # Populate initial list
        self.populate_list(list(self.commands.keys()))
        
        # Key bindings
        self.search_entry.bind('<Return>', self.execute_selected)
        self.search_entry.bind('<Escape>', lambda e: self.dialog.destroy())
        self.search_entry.bind('<Down>', self.move_selection_down)
        self.search_entry.bind('<Up>', self.move_selection_up)
        self.results_list.bind('<Return>', self.execute_selected)
        self.results_list.bind('<Double-Button-1>', self.execute_selected)
    
    def populate_list(self, commands):
        """Populate results list with commands"""
        self.results_list.delete(0, tk.END)
        for cmd in commands[:20]:  # Limit to 20 results
            self.results_list.insert(tk.END, f"  {cmd}")
        if commands:
            self.results_list.selection_set(0)
    
    def filter_commands(self, *args):
        """Filter commands based on search query"""
        query = self.search_var.get().lower()
        if not query:
            self.populate_list(list(self.commands.keys()))
            return
        
        # Fuzzy search
        matches = []
        for cmd in self.commands.keys():
            if self.fuzzy_match(query, cmd.lower()):
                matches.append(cmd)
        
        self.populate_list(matches)
    
    def fuzzy_match(self, query, text):
        """Simple fuzzy matching"""
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)
    
    def move_selection_down(self, event):
        """Move selection down"""
        current = self.results_list.curselection()
        if current:
            next_idx = min(current[0] + 1, self.results_list.size() - 1)
            self.results_list.selection_clear(0, tk.END)
            self.results_list.selection_set(next_idx)
            self.results_list.see(next_idx)
        return "break"
    
    def move_selection_up(self, event):
        """Move selection up"""
        current = self.results_list.curselection()
        if current:
            prev_idx = max(current[0] - 1, 0)
            self.results_list.selection_clear(0, tk.END)
            self.results_list.selection_set(prev_idx)
            self.results_list.see(prev_idx)
        return "break"
    
    def execute_selected(self, event=None):
        """Execute selected command"""
        selection = self.results_list.curselection()
        if selection:
            cmd_text = self.results_list.get(selection[0]).strip()
            if cmd_text in self.commands:
                self.dialog.destroy()
                self.callback(self.commands[cmd_text])
