import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
import json
import re
from io import StringIO
from collections import deque

class ModernUI:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.tabs = {"Tab 1": ""}
        self.current_tab = "Tab 1"
        self.tab_counter = 1
        
        self.undo_stacks = {"Tab 1": deque(maxlen=50)}
        self.redo_stacks = {"Tab 1": deque(maxlen=50)}
        
        self.command_history = deque(maxlen=100)
        self.history_index = 0
        
        self.scripts_dir = r"C:\Users\gavin\OneDrive\Desktop\BotModMenuSystem\Saved Scripts"
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        self.settings = {
            'notifications': tk.BooleanVar(value=True),
            'autostart': tk.BooleanVar(value=False),
            'darkmode': tk.BooleanVar(value=True),
            'savelogs': tk.BooleanVar(value=True),
            'syntax_highlight': tk.BooleanVar(value=True),
            'line_numbers': tk.BooleanVar(value=True),
            'autocomplete': tk.BooleanVar(value=True)
        }
        
        self.syntax_colors = {
            'keyword': '#569cd6',
            'string': '#ce9178',
            'comment': '#6a9955',
            'function': '#dcdcaa',
            'number': '#b5cea8',
            'error': '#ff4444'
        }
        
        self.keywords = ['def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for', 
                        'while', 'return', 'try', 'except', 'finally', 'with', 'as',
                        'lambda', 'yield', 'pass', 'break', 'continue', 'True', 'False',
                        'None', 'and', 'or', 'not', 'in', 'is', 'async', 'await']
        
        self.snippets = {
            "for_loop": "for i in range(10):\n    print(i)",
            "function": "def function_name(param):\n    return param",
            "class": "class ClassName:\n    def __init__(self):\n        pass",
            "try_except": "try:\n    # code\n    pass\nexcept Exception as e:\n    print(e)",
            "file_read": "with open('file.txt', 'r') as f:\n    content = f.read()",
            "list_comp": "[x for x in range(10) if x % 2 == 0]",
            "dict_comp": "{k: v for k, v in enumerate(range(10))}",
            "requests": "import requests\nresponse = requests.get('url')\nprint(response.json())"
        }
        
        self.apply_theme()
        self.show_loading_screen()
        
        self.script_path = __file__
        self.last_modified = os.path.getmtime(self.script_path)
        self.watch_file()
        
        self.setup_keyboard_shortcuts()
        
    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.save_script_dialog())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self.show_find_replace())
        self.root.bind('<Control-b>', lambda e: self.beautify_code())
        
    def undo(self):
        """Undo last change in current tab"""
        if hasattr(self, 'code_input') and self.current_tab in self.undo_stacks:
            if self.undo_stacks[self.current_tab]:
                current_content = self.code_input.get('1.0', tk.END)
                self.redo_stacks[self.current_tab].append(current_content)
                
                previous_content = self.undo_stacks[self.current_tab].pop()
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', previous_content)
                self.update_status("Undo")
                
    def redo(self):
        """Redo last undone change"""
        if hasattr(self, 'code_input') and self.current_tab in self.redo_stacks:
            if self.redo_stacks[self.current_tab]:
                current_content = self.code_input.get('1.0', tk.END)
                self.undo_stacks[self.current_tab].append(current_content)
                
                next_content = self.redo_stacks[self.current_tab].pop()
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', next_content)
                self.update_status("Redo")
                
    def track_change(self, event=None):
        """Track changes for undo/redo"""
        if hasattr(self, 'code_input'):
            if self.current_tab not in self.undo_stacks:
                self.undo_stacks[self.current_tab] = deque(maxlen=50)
            if self.current_tab not in self.redo_stacks:
                self.redo_stacks[self.current_tab] = deque(maxlen=50)
            
            content = self.code_input.get('1.0', tk.END)
            if not self.undo_stacks[self.current_tab] or self.undo_stacks[self.current_tab][-1] != content:
                self.undo_stacks[self.current_tab].append(content)
                self.redo_stacks[self.current_tab].clear()
        
    def apply_theme(self):
        """Apply color theme based on dark mode setting"""
        if self.settings['darkmode'].get():
            self.bg_color = "#1e1e1e"
            self.secondary_bg = "#2d2d2d"
            self.accent_color = "#0d7377"
            self.text_color = "#e0e0e0"
            self.button_hover = "#14a0a6"
        else:
            self.bg_color = "#f5f5f5"
            self.secondary_bg = "#ffffff"
            self.accent_color = "#0d7377"
            self.text_color = "#000000"
            self.button_hover = "#14a0a6"
        
        self.root.configure(bg=self.bg_color)
        
    def show_loading_screen(self):
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
        self.root.attributes('-alpha', 1.0)
        self.create_header_bar()
        self.create_footer()
        self.create_sidebar()
        self.create_main_content()
    
    def create_header_bar(self):
        """Create the header bar with title and control buttons"""
        self.header = tk.Frame(self.root, bg=self.secondary_bg, height=60)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)
        
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)
        
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
        version.bind("<Button-1>", self.start_drag)
        version.bind("<B1-Motion>", self.do_drag)
        
        close_btn = tk.Button(self.header, text="✕", font=("Segoe UI", 14),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, command=self.root.quit,
                             activebackground="#d32f2f",
                             activeforeground="white", cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#d32f2f"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.secondary_bg))
        
        reload_btn = tk.Button(self.header, text="↻", font=("Segoe UI", 16),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, command=self.manual_reload,
                              cursor="hand2", width=2)
        reload_btn.pack(side=tk.RIGHT, padx=5)
        reload_btn.bind("<Enter>", lambda e: reload_btn.config(bg="#14a0a6"))
        reload_btn.bind("<Leave>", lambda e: reload_btn.config(bg=self.secondary_bg))
    
    def start_drag(self, event):
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y
    
    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_offset_x
        y = self.root.winfo_y() + event.y - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")
    
    def watch_file(self):
        """Watch the script file for changes and auto-reload"""
        try:
            current_modified = os.path.getmtime(self.script_path)
            if current_modified != self.last_modified:
                self.last_modified = current_modified
                print("\n[AUTO-RELOAD] Script file changed! Reloading UI...")
                
                current_page = self.current_page
                current_tab = self.current_tab
                tabs_backup = self.tabs.copy()
                settings_backup = {k: v.get() for k, v in self.settings.items()}
                
                self.root.after(100, lambda: self.perform_reload(current_page, current_tab, tabs_backup, settings_backup))
                return
        except:
            pass
        
        self.root.after(1000, self.watch_file)
    
    def perform_reload(self, page, tab, tabs, settings_vals):
        """Actually perform the reload with state preservation"""
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            
            for key, val in settings_vals.items():
                if key in self.settings:
                    self.settings[key].set(val)
            
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
        """Manual reload via button click"""
        print("\n[MANUAL RELOAD] Reloading UI...")
        current_page = self.current_page
        current_tab = self.current_tab
        tabs_backup = self.tabs.copy()
        settings_backup = {k: v.get() for k, v in self.settings.items()}
        
        self.perform_reload(current_page, current_tab, tabs_backup, settings_backup)
        
    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=self.secondary_bg, width=200)
        self.sidebar.pack(fill=tk.Y, side=tk.LEFT)
        self.sidebar.pack_propagate(False)
        
        self.menu_items = {
            "Dashboard": "Dashboard",
            "Console": "Console",
            "History": "History",
            "Snippets": "Snippets",
            "Progress": "Progress",
            "Settings": "Settings",
            "About": "About"
        }
        
        self.menu_buttons = {}
        for item, display_name in self.menu_items.items():
            btn_container = tk.Frame(self.sidebar, bg=self.secondary_bg)
            btn_container.pack(fill=tk.X)
            
            border_indicator = tk.Frame(btn_container, bg=self.secondary_bg, width=4)
            border_indicator.pack(side=tk.LEFT, fill=tk.Y)
            
            btn = tk.Button(btn_container, text=display_name, font=("Segoe UI", 11),
                          bg=self.secondary_bg, fg=self.text_color,
                          border=0, pady=15, cursor="hand2",
                          activebackground=self.secondary_bg,
                          activeforeground=self.text_color, anchor="w", padx=16,
                          relief=tk.FLAT)
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            btn.border_indicator = border_indicator
            
            def on_enter(e, b=btn, ind=border_indicator):
                if b.cget('bg') != self.accent_color:
                    ind.config(bg=self.accent_color)
                    b.config(bg="#363636" if self.settings['darkmode'].get() else "#e8e8e8")
            
            def on_leave(e, b=btn, ind=border_indicator):
                if b.cget('bg') != self.accent_color:
                    ind.config(bg=self.secondary_bg)
                    b.config(bg=self.secondary_bg)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.config(command=lambda i=item: self.switch_page(i))
            self.menu_buttons[item] = btn
    
    def create_main_content(self):
        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        self.current_page = None
        self.switch_page("Dashboard")
    
    def switch_page(self, page):
        if self.current_page == page:
            return
            
        self.current_page = page
        
        self.content_frame.update()
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        loading_frame.pack(fill=tk.BOTH, expand=True)
        
        loading_label = tk.Label(loading_frame, text="Loading...", 
                                font=("Segoe UI", 12),
                                bg=self.bg_color, fg="#a0a0a0")
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
        def animate_dots(count=0):
            dots = "." * (count % 4)
            loading_label.config(text=f"Loading{dots}")
            if count < 3:
                self.root.after(80, lambda: animate_dots(count + 1))
            else:
                loading_frame.destroy()
                self.load_page_content(page)
        
        for name, btn in self.menu_buttons.items():
            if name == page:
                btn.config(bg=self.accent_color, fg="white")
                btn.border_indicator.config(bg=self.accent_color)
            else:
                btn.config(bg=self.secondary_bg, fg=self.text_color)
                btn.border_indicator.config(bg=self.secondary_bg)
        
        self.update_status(f"Loading {page}...")
        animate_dots()
    
    def load_page_content(self, page):
        """Load the actual page content after loading animation"""
        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Console":
            self.show_console()
        elif page == "History":
            self.show_history()
        elif page == "Snippets":
            self.show_snippets()
        elif page == "Progress":
            self.show_progress_page()
        elif page == "Settings":
            self.show_settings()
        elif page == "About":
            self.show_about()
        self.update_status("Ready")
    
    def show_dashboard(self):
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome = tk.Label(container, text="Dashboard",
                          font=("Segoe UI", 16, "bold"),
                          bg=self.bg_color, fg=self.text_color)
        welcome.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Welcome! Manage your tasks and monitor progress.",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        cards_frame = tk.Frame(container, bg=self.bg_color)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_card(cards_frame, "Quick Action", "Execute a fast task", 0, 0)
        self.create_card(cards_frame, "Batch Process", "Process multiple items", 0, 1)
        self.create_card(cards_frame, "Analysis", "Analyze your data", 1, 0)
        self.create_card(cards_frame, "Export", "Export results", 1, 1)
    
    def create_card(self, parent, title, desc, row, col):
        card = tk.Frame(parent, bg=self.secondary_bg, highlightbackground=self.accent_color,
                       highlightthickness=0)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        card.config(relief=tk.FLAT, bd=1)
        
        card_title = tk.Label(card, text=title, font=("Segoe UI", 12, "bold"),
                            bg=self.secondary_bg, fg=self.text_color)
        card_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        card_desc = tk.Label(card, text=desc, font=("Segoe UI", 9),
                           bg=self.secondary_bg, fg="#a0a0a0", wraplength=200)
        card_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        action_btn = tk.Button(card, text="Execute", font=("Segoe UI", 9, "bold"),
                             bg=self.accent_color, fg="white",
                             border=0, cursor="hand2", pady=8, padx=20,
                             activebackground=self.button_hover,
                             command=lambda: self.execute_action(title))
        action_btn.pack(anchor="w", padx=15, pady=(0, 15))
        
        def on_btn_enter(e):
            self.animate_button_color(action_btn, self.button_hover)
        
        def on_btn_leave(e):
            self.animate_button_color(action_btn, self.accent_color)
        
        action_btn.bind("<Enter>", on_btn_enter)
        action_btn.bind("<Leave>", on_btn_leave)
        
        def on_card_enter(e):
            card.config(highlightthickness=1, highlightbackground=self.accent_color)
        
        def on_card_leave(e):
            card.config(highlightthickness=0)
        
        card.bind("<Enter>", on_card_enter)
        card.bind("<Leave>", on_card_leave)
    
    def animate_button_color(self, button, target_color):
        """Smooth color transition for buttons"""
        button.config(bg=target_color)
    
    def show_console(self):
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Python Console",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Paste and execute Python code. Output appears in both the UI and PowerShell terminal.",
                       font=("Segoe UI", 9),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 10))
        
        tabs_frame = tk.Frame(container, bg=self.bg_color)
        tabs_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tab_buttons = {}
        self.create_tab_buttons(tabs_frame)
        
        code_label = tk.Label(container, text="Code Input:",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.bg_color, fg=self.text_color)
        code_label.pack(anchor="w", pady=(5, 5))
        
        input_container = tk.Frame(container, bg=self.bg_color)
        input_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        if self.settings['line_numbers'].get():
            self.line_numbers = tk.Text(input_container,
                                       width=4,
                                       font=("Consolas", 10),
                                       bg=self.secondary_bg,
                                       fg="#858585",
                                       state=tk.DISABLED,
                                       takefocus=0)
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        input_frame = tk.Frame(input_container, bg=self.bg_color)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.code_input = tk.Text(input_frame, 
                                  height=10,
                                  font=("Consolas", 10),
                                  bg=self.secondary_bg,
                                  fg=self.text_color,
                                  insertbackground=self.text_color,
                                  selectbackground=self.accent_color,
                                  wrap=tk.NONE,
                                  undo=True,
                                  maxundo=-1)
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        input_scrollbar = tk.Scrollbar(input_frame, command=self.code_input.yview,
                                      bg=self.secondary_bg,
                                      troughcolor=self.bg_color,
                                      activebackground="#505050",
                                      width=12)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_input.config(yscrollcommand=input_scrollbar.set)
        
        self.setup_syntax_tags()
        
        self.code_input.delete('1.0', tk.END)
        self.code_input.insert('1.0', self.tabs[self.current_tab])
        
        self.code_input.bind('<KeyRelease>', self.on_code_change)
        self.code_input.bind('<<Modified>>', self.update_line_numbers)
        
        if self.settings['autocomplete'].get():
            self.code_input.bind('<Control-space>', self.show_autocomplete)
        
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=5)
        
        left_buttons = tk.Frame(btn_frame, bg=self.bg_color)
        left_buttons.pack(side=tk.LEFT)
        
        run_btn = tk.Button(left_buttons, text="▶ Run", font=("Segoe UI", 9, "bold"),
                           bg=self.accent_color, fg="white",
                           border=0, cursor="hand2", pady=8, padx=12,
                           activebackground=self.button_hover,
                           command=self.run_code)
        run_btn.pack(side=tk.LEFT, padx=3)
        run_btn.bind("<Enter>", lambda e: run_btn.config(bg=self.button_hover))
        run_btn.bind("<Leave>", lambda e: run_btn.config(bg=self.accent_color))
        
        save_btn = tk.Button(left_buttons, text="💾 Save", font=("Segoe UI", 9, "bold"),
                           bg="#2e7d32", fg="white",
                           border=0, cursor="hand2", pady=8, padx=12,
                           activebackground="#43a047",
                           command=self.save_script_dialog)
        save_btn.pack(side=tk.LEFT, padx=3)
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#43a047"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg="#2e7d32"))
        
        load_btn = tk.Button(left_buttons, text="📂 Load", font=("Segoe UI", 9, "bold"),
                           bg="#1565c0", fg="white",
                           border=0, cursor="hand2", pady=8, padx=12,
                           activebackground="#1976d2",
                           command=self.load_script_dialog)
        load_btn.pack(side=tk.LEFT, padx=3)
        load_btn.bind("<Enter>", lambda e: load_btn.config(bg="#1976d2"))
        load_btn.bind("<Leave>", lambda e: load_btn.config(bg="#1565c0"))
        
        json_btn = tk.Button(left_buttons, text="📋 JSON", font=("Segoe UI", 9, "bold"),
                           bg="#6a1b9a", fg="white",
                           border=0, cursor="hand2", pady=8, padx=12,
                           activebackground="#8e24aa",
                           command=self.import_json_dialog)
        json_btn.pack(side=tk.LEFT, padx=3)
        json_btn.bind("<Enter>", lambda e: json_btn.config(bg="#8e24aa"))
        json_btn.bind("<Leave>", lambda e: json_btn.config(bg="#6a1b9a"))
        
        beautify_btn = tk.Button(left_buttons, text="✨ Format", font=("Segoe UI", 9, "bold"),
                                bg="#f57c00", fg="white",
                                border=0, cursor="hand2", pady=8, padx=12,
                                activebackground="#fb8c00",
                                command=self.beautify_code)
        beautify_btn.pack(side=tk.LEFT, padx=3)
        beautify_btn.bind("<Enter>", lambda e: beautify_btn.config(bg="#fb8c00"))
        beautify_btn.bind("<Leave>", lambda e: beautify_btn.config(bg="#f57c00"))
        
        clear_btn = tk.Button(left_buttons, text="Clear In", font=("Segoe UI", 9),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, cursor="hand2", pady=8, padx=12,
                             activebackground="#444444",
                             command=self.clear_input)
        clear_btn.pack(side=tk.LEFT, padx=3)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#444444"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg=self.secondary_bg))
        
        clear_output_btn = tk.Button(left_buttons, text="Clear Out", font=("Segoe UI", 9),
                                     bg=self.secondary_bg, fg=self.text_color,
                                     border=0, cursor="hand2", pady=8, padx=12,
                                     activebackground="#444444",
                                     command=self.clear_output)
        clear_output_btn.pack(side=tk.LEFT, padx=3)
        clear_output_btn.bind("<Enter>", lambda e: clear_output_btn.config(bg="#444444"))
        clear_output_btn.bind("<Leave>", lambda e: clear_output_btn.config(bg=self.secondary_bg))
        
        output_label = tk.Label(container, text="Output:",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        output_label.pack(anchor="w", pady=(10, 5))
        
        output_frame = tk.Frame(container, bg=self.bg_color)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console_output = tk.Text(output_frame, 
                                      height=8,
                                      font=("Consolas", 9),
                                      bg=self.secondary_bg,
                                      fg="#00ff00",
                                      insertbackground=self.text_color,
                                      wrap=tk.NONE)
        self.console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        output_scrollbar = tk.Scrollbar(output_frame, command=self.console_output.yview,
                                       bg=self.secondary_bg,
                                       troughcolor=self.bg_color,
                                       activebackground="#505050",
                                       width=12)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_output.config(yscrollcommand=output_scrollbar.set)
    
    def setup_syntax_tags(self):
        """Configure text tags for syntax highlighting"""
        self.code_input.tag_config('keyword', foreground=self.syntax_colors['keyword'])
        self.code_input.tag_config('string', foreground=self.syntax_colors['string'])
        self.code_input.tag_config('comment', foreground=self.syntax_colors['comment'])
        self.code_input.tag_config('function', foreground=self.syntax_colors['function'])
        self.code_input.tag_config('number', foreground=self.syntax_colors['number'])
    
    def highlight_syntax(self):
        """Apply syntax highlighting to code input"""
        if not self.settings['syntax_highlight'].get():
            return
        
        for tag in ['keyword', 'string', 'comment', 'function', 'number']:
            self.code_input.tag_remove(tag, '1.0', tk.END)
        
        code = self.code_input.get('1.0', tk.END)
        
        for match in re.finditer(r'#.*', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_input.tag_add('comment', start, end)
        
        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_input.tag_add('string', start, end)
        
        for keyword in self.keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add('keyword', start, end)
        
        for match in re.finditer(r'\b\d+\.?\d*\b', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_input.tag_add('number', start, end)
        
        for match in re.finditer(r'\bdef\s+(\w+)', code):
            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"
            self.code_input.tag_add('function', start, end)
    
    def update_line_numbers(self, event=None):
        """Update line numbers in the text widget"""
        if not self.settings['line_numbers'].get() or not hasattr(self, 'line_numbers'):
            return
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        
        line_count = self.code_input.get('1.0', tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers_string)
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def on_code_change(self, event=None):
        """Handle code changes"""
        self.save_current_tab()
        self.highlight_syntax()
        self.update_line_numbers()
        self.track_change()
    
    def show_autocomplete(self, event=None):
        """Show autocomplete suggestions"""
        cursor_pos = self.code_input.index(tk.INSERT)
        line = self.code_input.get(f"{cursor_pos} linestart", cursor_pos)
        words = line.split()
        
        if words:
            current_word = words[-1]
            suggestions = [kw for kw in self.keywords if kw.startswith(current_word)]
            
            if suggestions:
                popup = tk.Toplevel(self.root)
                popup.overrideredirect(True)
                popup.geometry(f"+{self.code_input.winfo_rootx()}+{self.code_input.winfo_rooty() + 50}")
                
                listbox = tk.Listbox(popup, font=("Consolas", 9), 
                                    bg=self.secondary_bg, fg=self.text_color,
                                    selectbackground=self.accent_color)
                listbox.pack()
                
                for suggestion in suggestions[:10]:
                    listbox.insert(tk.END, suggestion)
                
                def insert_suggestion(event):
                    if listbox.curselection():
                        selected = listbox.get(listbox.curselection())
                        self.code_input.delete(f"{cursor_pos} - {len(current_word)}c", cursor_pos)
                        self.code_input.insert(cursor_pos, selected)
                    popup.destroy()
                
                listbox.bind('<Return>', insert_suggestion)
                listbox.bind('<Double-Button-1>', insert_suggestion)
                listbox.bind('<Escape>', lambda e: popup.destroy())
                listbox.focus()
                
                popup.after(3000, popup.destroy)
        
        return "break"
    
    def beautify_code(self):
        """Format/beautify Python code"""
        code = self.code_input.get('1.0', tk.END).strip()
        
        if not code:
            return
        
        try:
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                
                if stripped.startswith(('elif', 'else', 'except', 'finally')) and indent_level > 0:
                    indent_level = max(0, indent_level - 1)
                
                if stripped:
                    formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('')
                
                if stripped.endswith(':'):
                    indent_level += 1
                
                if stripped.startswith(('return', 'break', 'continue', 'pass')):
                    indent_level = max(0, indent_level - 1)
            
            formatted_code = '\n'.join(formatted_lines)
            
            self.code_input.delete('1.0', tk.END)
            self.code_input.insert('1.0', formatted_code)
            self.save_current_tab()
            self.highlight_syntax()
            
            self.update_status("Code formatted")
            if self.settings['notifications'].get():
                messagebox.showinfo("Success", "Code formatted successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format code: {str(e)}")
    
    def show_find_replace(self):
        """Show find/replace dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Find & Replace")
        dialog.geometry("400x200")
        dialog.configure(bg=self.bg_color)
        dialog.overrideredirect(True)
        
        dialog.geometry(f"+{self.root.winfo_x() + 200}+{self.root.winfo_y() + 200}")
        
        frame = tk.Frame(dialog, bg=self.secondary_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        header = tk.Frame(frame, bg=self.secondary_bg)
        header.pack(fill=tk.X)
        header.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        header.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        title_label = tk.Label(header, text="Find & Replace", font=("Segoe UI", 12, "bold"),
                              bg=self.secondary_bg, fg=self.text_color)
        title_label.pack(pady=15)
        title_label.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        title_label.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        close_btn = tk.Button(header, text="✕", font=("Segoe UI", 12),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, command=dialog.destroy, cursor="hand2")
        close_btn.place(relx=0.95, rely=0.3, anchor="center")
        
        find_label = tk.Label(frame, text="Find:", font=("Segoe UI", 10),
                             bg=self.secondary_bg, fg=self.text_color)
        find_label.pack(anchor="w", padx=20, pady=(5, 2))
        
        find_entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color)
        find_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        replace_label = tk.Label(frame, text="Replace with:", font=("Segoe UI", 10),
                                bg=self.secondary_bg, fg=self.text_color)
        replace_label.pack(anchor="w", padx=20, pady=(5, 2))
        
        replace_entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color)
        replace_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        btn_frame = tk.Frame(frame, bg=self.secondary_bg)
        btn_frame.pack(pady=15)
        
        def do_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            
            if find_text:
                code = self.code_input.get('1.0', tk.END)
                new_code = code.replace(find_text, replace_text)
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', new_code)
                self.save_current_tab()
                self.highlight_syntax()
                self.update_status(f"Replaced '{find_text}'")
                dialog.destroy()
        
        replace_btn = tk.Button(btn_frame, text="Replace All", font=("Segoe UI", 9, "bold"),
                               bg=self.accent_color, fg="white",
                               border=0, cursor="hand2", pady=6, padx=20,
                               command=do_replace)
        replace_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, cursor="hand2", pady=6, padx=20,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def show_history(self):
        """Show terminal history page"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Execution History",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="View previously executed commands and their results.",
                       font=("Segoe UI", 9),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 10))
        
        history_frame = tk.Frame(container, bg=self.bg_color)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_list = tk.Listbox(history_frame, font=("Consolas", 9),
                                 bg=self.secondary_bg, fg=self.text_color,
                                 selectbackground=self.accent_color,
                                 yscrollcommand=scrollbar.set)
        history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_list.yview)
        
        if self.command_history:
            for i, cmd in enumerate(reversed(self.command_history), 1):
                preview = cmd[:100] + "..." if len(cmd) > 100 else cmd
                history_list.insert(tk.END, f"{i}. {preview}")
        else:
            history_list.insert(tk.END, "No command history yet...")
            history_list.config(state=tk.DISABLED)
        
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        def load_from_history():
            selection = history_list.curselection()
            if selection:
                index = len(self.command_history) - selection[0] - 1
                cmd = self.command_history[index]
                
                self.switch_page("Console")
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', cmd)
                self.update_status("Command loaded from history")
        
        load_btn = tk.Button(btn_frame, text="Load Selected", font=("Segoe UI", 10, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=8, padx=20,
                            command=load_from_history)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        clear_history_btn = tk.Button(btn_frame, text="Clear History", font=("Segoe UI", 10),
                                      bg="#d32f2f", fg="white",
                                      border=0, cursor="hand2", pady=8, padx=20,
                                      command=lambda: self.command_history.clear() or self.switch_page("History"))
        clear_history_btn.pack(side=tk.LEFT, padx=5)
    
    def show_snippets(self):
        """Show code snippets library"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Code Snippets Library",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Quick access to common code patterns and templates.",
                       font=("Segoe UI", 9),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 10))
        
        snippets_frame = tk.Frame(container, bg=self.bg_color)
        snippets_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        col = 0
        for name, code in self.snippets.items():
            snippet_card = tk.Frame(snippets_frame, bg=self.secondary_bg, 
                                   highlightbackground=self.accent_color,
                                   highlightthickness=1)
            snippet_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            snippets_frame.grid_rowconfigure(row, weight=1)
            snippets_frame.grid_columnconfigure(col, weight=1)
            
            name_label = tk.Label(snippet_card, text=name.replace("_", " ").title(),
                                 font=("Segoe UI", 11, "bold"),
                                 bg=self.secondary_bg, fg=self.text_color)
            name_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            code_preview = tk.Label(snippet_card, text=code[:50] + "...",
                                   font=("Consolas", 8),
                                   bg=self.secondary_bg, fg="#a0a0a0",
                                   wraplength=180, justify="left")
            code_preview.pack(anchor="w", padx=15, pady=(0, 10))
            
            insert_btn = tk.Button(snippet_card, text="Insert", font=("Segoe UI", 9, "bold"),
                                  bg=self.accent_color, fg="white",
                                  border=0, cursor="hand2", pady=6, padx=15,
                                  command=lambda c=code: self.insert_snippet(c))
            insert_btn.pack(anchor="w", padx=15, pady=(0, 15))
            
            col += 1
            if col > 1:
                col = 0
                row += 1
    
    def insert_snippet(self, code):
        """Insert snippet into code editor"""
        self.switch_page("Console")
        self.code_input.insert(tk.INSERT, code + "\n")
        self.save_current_tab()
        self.highlight_syntax()
        self.update_status("Snippet inserted")
    
    def create_tab_buttons(self, parent):
        """Create tab buttons with + button"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        self.tab_buttons.clear()
        
        for tab_name in self.tabs.keys():
            tab_btn = tk.Button(parent, text=tab_name, font=("Segoe UI", 9),
                              bg=self.accent_color if tab_name == self.current_tab else self.secondary_bg,
                              fg="white" if tab_name == self.current_tab else self.text_color,
                              border=0, cursor="hand2", pady=5, padx=15,
                              command=lambda t=tab_name: self.switch_tab(t))
            tab_btn.pack(side=tk.LEFT, padx=2)
            
            tab_btn.bind("<Double-Button-1>", lambda e, t=tab_name: self.rename_tab(t))
            tab_btn.bind("<Button-3>", lambda e, t=tab_name: self.close_tab(t))
            
            self.tab_buttons[tab_name] = tab_btn
        
        add_tab_btn = tk.Button(parent, text="+", font=("Segoe UI", 12, "bold"),
                              bg=self.secondary_bg, fg=self.accent_color,
                              border=0, cursor="hand2", pady=3, padx=10,
                              command=self.add_new_tab)
        add_tab_btn.pack(side=tk.LEFT, padx=5)
        add_tab_btn.bind("<Enter>", lambda e: add_tab_btn.config(bg="#444444"))
        add_tab_btn.bind("<Leave>", lambda e: add_tab_btn.config(bg=self.secondary_bg))
    
    def add_new_tab(self):
        """Add a new tab"""
        self.tab_counter += 1
        new_tab_name = f"Tab {self.tab_counter}"
        self.tabs[new_tab_name] = ""
        self.undo_stacks[new_tab_name] = deque(maxlen=50)
        self.redo_stacks[new_tab_name] = deque(maxlen=50)
        self.current_tab = new_tab_name
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.show_console()
        
        self.update_status(f"Created {new_tab_name}")
    
    def switch_tab(self, tab_name):
        """Switch to a different tab"""
        if tab_name != self.current_tab:
            self.save_current_tab()
            
            self.current_tab = tab_name
            
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.show_console()
            
            self.update_status(f"Switched to {tab_name}")
    
    def save_current_tab(self):
        """Save current tab content"""
        if hasattr(self, 'code_input'):
            self.tabs[self.current_tab] = self.code_input.get('1.0', tk.END)
    
    def rename_tab(self, old_name):
        """Rename a tab"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Rename Tab")
        dialog.geometry("300x120")
        dialog.configure(bg=self.bg_color)
        dialog.overrideredirect(True)
        
        dialog.geometry(f"+{self.root.winfo_x() + 250}+{self.root.winfo_y() + 200}")
        
        frame = tk.Frame(dialog, bg=self.secondary_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        frame.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        frame.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        label = tk.Label(frame, text="New Tab Name:", font=("Segoe UI", 10, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        label.pack(pady=(15, 5))
        label.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        label.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color,
                        insertbackground=self.text_color)
        entry.pack(pady=5, padx=20, fill=tk.X)
        entry.insert(0, old_name)
        entry.select_range(0, tk.END)
        entry.focus()
        
        btn_frame = tk.Frame(frame, bg=self.secondary_bg)
        btn_frame.pack(pady=10)
        
        def do_rename():
            new_name = entry.get().strip()
            if new_name and new_name not in self.tabs and new_name != old_name:
                self.tabs[new_name] = self.tabs.pop(old_name)
                if old_name in self.undo_stacks:
                    self.undo_stacks[new_name] = self.undo_stacks.pop(old_name)
                if old_name in self.redo_stacks:
                    self.redo_stacks[new_name] = self.redo_stacks.pop(old_name)
                    
                if self.current_tab == old_name:
                    self.current_tab = new_name
                
                dialog.destroy()
                
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
                self.show_console()
                
                self.update_status(f"Renamed to {new_name}")
            elif new_name == old_name:
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Name", "Tab name already exists or is empty!")
        
        ok_btn = tk.Button(btn_frame, text="Rename", font=("Segoe UI", 9, "bold"),
                          bg=self.accent_color, fg="white",
                          border=0, cursor="hand2", pady=5, padx=20,
                          command=do_rename)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, cursor="hand2", pady=5, padx=20,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: do_rename())
        entry.bind('<Escape>', lambda e: dialog.destroy())
    
    def close_tab(self, tab_name):
        """Close a tab (right-click)"""
        if len(self.tabs) > 1:
            del self.tabs[tab_name]
            if tab_name in self.undo_stacks:
                del self.undo_stacks[tab_name]
            if tab_name in self.redo_stacks:
                del self.redo_stacks[tab_name]
                
            if self.current_tab == tab_name:
                self.current_tab = list(self.tabs.keys())[0]
            
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.show_console()
            
            self.update_status(f"Closed {tab_name}")
        else:
            messagebox.showinfo("Cannot Close", "You must have at least one tab open!")
    
    def save_script_dialog(self):
        """Show save dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Script")
        dialog.geometry("350x140")
        dialog.configure(bg=self.bg_color)
        dialog.overrideredirect(True)
        
        dialog.geometry(f"+{self.root.winfo_x() + 225}+{self.root.winfo_y() + 200}")
        
        frame = tk.Frame(dialog, bg=self.secondary_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        frame.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        frame.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        label = tk.Label(frame, text="Save As:", font=("Segoe UI", 12, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        label.pack(pady=(15, 5))
        label.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        label.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color,
                        insertbackground=self.text_color)
        entry.pack(pady=5, padx=20, fill=tk.X)
        entry.focus()
        
        btn_frame = tk.Frame(frame, bg=self.secondary_bg)
        btn_frame.pack(pady=15)
        
        def do_save():
            filename = entry.get().strip()
            if filename:
                if not filename.endswith('.txt'):
                    filename += '.txt'
                filepath = os.path.join(self.scripts_dir, filename)
                
                code = self.code_input.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                dialog.destroy()
                self.update_status(f"Saved: {filename}")
                if self.settings['notifications'].get():
                    messagebox.showinfo("Success", f"Script saved as {filename}")
            else:
                messagebox.showwarning("Invalid Name", "Please enter a filename!")
        
        save_btn = tk.Button(btn_frame, text="Save", font=("Segoe UI", 9, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=6, padx=25,
                            command=do_save)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, cursor="hand2", pady=6, padx=25,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: do_save())
        entry.bind('<Escape>', lambda e: dialog.destroy())
    
    def load_script_dialog(self):
        """Show load dialog with list of saved scripts"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Script")
        dialog.geometry("400x400")
        dialog.configure(bg=self.bg_color)
        dialog.overrideredirect(True)
        
        dialog.geometry(f"+{self.root.winfo_x() + 200}+{self.root.winfo_y() + 100}")
        
        frame = tk.Frame(dialog, bg=self.secondary_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        header = tk.Frame(frame, bg=self.secondary_bg)
        header.pack(fill=tk.X)
        header.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        header.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        label = tk.Label(header, text="Load Script", font=("Segoe UI", 12, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        label.pack(pady=15)
        label.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        label.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        close_btn = tk.Button(header, text="✕", font=("Segoe UI", 12),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, command=dialog.destroy, cursor="hand2")
        close_btn.place(relx=0.95, rely=0.3, anchor="center")
        
        listbox_frame = tk.Frame(frame, bg=self.secondary_bg)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 10),
                            bg=self.bg_color, fg=self.text_color,
                            selectbackground=self.accent_color,
                            selectforeground="white",
                            yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        try:
            scripts = [f for f in os.listdir(self.scripts_dir) if f.endswith('.txt')]
            for script in sorted(scripts):
                listbox.insert(tk.END, script)
        except:
            pass
        
        if listbox.size() == 0:
            listbox.insert(tk.END, "No saved scripts found...")
            listbox.config(state=tk.DISABLED)
        
        btn_frame = tk.Frame(frame, bg=self.secondary_bg)
        btn_frame.pack(pady=15)
        
        def do_load():
            selection = listbox.curselection()
            if selection:
                filename = listbox.get(selection[0])
                filepath = os.path.join(self.scripts_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    self.code_input.delete('1.0', tk.END)
                    self.code_input.insert('1.0', code)
                    self.save_current_tab()
                    self.highlight_syntax()
                    
                    dialog.destroy()
                    self.update_status(f"Loaded: {filename}")
                    if self.settings['notifications'].get():
                        messagebox.showinfo("Success", f"Script loaded: {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load script: {str(e)}")
            else:
                messagebox.showwarning("No Selection", "Please select a script to load!")
        
        load_btn = tk.Button(btn_frame, text="Load", font=("Segoe UI", 10, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=8, padx=30,
                            command=do_load)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, cursor="hand2", pady=8, padx=30,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        listbox.bind('<Double-Button-1>', lambda e: do_load())
        listbox.bind('<Return>', lambda e: do_load())
    
    def import_json_dialog(self):
        """Show import JSON dialog with auto-formatting (JSON LINT)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import JSON")
        dialog.geometry("500x450")
        dialog.configure(bg=self.bg_color)
        dialog.overrideredirect(True)
        
        dialog.geometry(f"+{self.root.winfo_x() + 150}+{self.root.winfo_y() + 75}")
        
        frame = tk.Frame(dialog, bg=self.secondary_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        header = tk.Frame(frame, bg=self.secondary_bg)
        header.pack(fill=tk.X)
        header.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        header.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        title_label = tk.Label(header, text="Import JSON File", font=("Segoe UI", 12, "bold"),
                              bg=self.secondary_bg, fg=self.text_color)
        title_label.pack(pady=15)
        title_label.bind("<Button-1>", lambda e: self.start_dialog_drag(e, dialog))
        title_label.bind("<B1-Motion>", lambda e: self.do_dialog_drag(e, dialog))
        
        close_btn = tk.Button(header, text="✕", font=("Segoe UI", 12),
                             bg=self.secondary_bg, fg=self.text_color,
                             border=0, command=dialog.destroy, cursor="hand2")
        close_btn.place(relx=0.95, rely=0.3, anchor="center")
        
        dir_label = tk.Label(frame, text="Directory:", font=("Segoe UI", 10, "bold"),
                            bg=self.secondary_bg, fg=self.text_color)
        dir_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        dir_entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color,
                            insertbackground=self.text_color)
        dir_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
        dir_entry.insert(0, os.getcwd())
        
        filename_label = tk.Label(frame, text="Filename:", font=("Segoe UI", 10, "bold"),
                                 bg=self.secondary_bg, fg=self.text_color)
        filename_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        filename_entry = tk.Entry(frame, font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color,
                                 insertbackground=self.text_color)
        filename_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
        filename_entry.insert(0, "data.json")
        
        code_label = tk.Label(frame, text="JSON Code:", font=("Segoe UI", 10, "bold"),
                             bg=self.secondary_bg, fg=self.text_color)
        code_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        text_frame = tk.Frame(frame, bg=self.secondary_bg)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        json_text = tk.Text(text_frame, font=("Consolas", 9),
                           bg=self.bg_color, fg=self.text_color,
                           insertbackground=self.text_color,
                           height=12, wrap=tk.NONE)
        json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        json_scrollbar = tk.Scrollbar(text_frame, command=json_text.yview,
                                     bg=self.secondary_bg,
                                     troughcolor=self.bg_color,
                                     activebackground="#505050",
                                     width=12)
        json_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        json_text.config(yscrollcommand=json_scrollbar.set)
        
        json_text.insert('1.0', '{\n  "key": "value",\n  "items": []\n}')
        
        def auto_format_json(event=None):
            try:
                content = json_text.get('1.0', tk.END).strip()
                if content:
                    parsed = json.loads(content)
                    formatted = json.dumps(parsed, indent=2)
                    
                    cursor_pos = json_text.index(tk.INSERT)
                    
                    json_text.delete('1.0', tk.END)
                    json_text.insert('1.0', formatted)
                    
                    try:
                        json_text.mark_set(tk.INSERT, cursor_pos)
                    except:
                        pass
            except json.JSONDecodeError:
                pass
        
        btn_frame = tk.Frame(frame, bg=self.secondary_bg)
        btn_frame.pack(pady=15)
        
        format_btn = tk.Button(btn_frame, text="✨ Format", font=("Segoe UI", 9, "bold"),
                              bg="#f57c00", fg="white",
                              border=0, cursor="hand2", pady=6, padx=20,
                              command=auto_format_json)
        format_btn.pack(side=tk.LEFT, padx=5)
        
        def do_import():
            directory = dir_entry.get().strip()
            filename = filename_entry.get().strip()
            json_code = json_text.get('1.0', tk.END).strip()
            
            if not directory or not filename or not json_code:
                messagebox.showwarning("Missing Info", "Please fill in all fields!")
                return
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(directory, filename)
            
            try:
                parsed = json.loads(json_code)
                formatted_json = json.dumps(parsed, indent=2)
                
                os.makedirs(directory, exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(formatted_json)
                
                dialog.destroy()
                self.update_status(f"JSON imported: {filename}")
                if self.settings['notifications'].get():
                    messagebox.showinfo("Success", f"JSON file created:\n{filepath}")
            except json.JSONDecodeError as e:
                messagebox.showerror("Invalid JSON", f"JSON syntax error:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create JSON file:\n{str(e)}")
        
        import_btn = tk.Button(btn_frame, text="Import", font=("Segoe UI", 9, "bold"),
                              bg=self.accent_color, fg="white",
                              border=0, cursor="hand2", pady=6, padx=20,
                              command=do_import)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9),
                              bg=self.secondary_bg, fg=self.text_color,
                              border=0, cursor="hand2", pady=6, padx=20,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def start_dialog_drag(self, event, dialog):
        self.dialog_drag_x = event.x
        self.dialog_drag_y = event.y
    
    def do_dialog_drag(self, event, dialog):
        x = dialog.winfo_x() + event.x - self.dialog_drag_x
        y = dialog.winfo_y() + event.y - self.dialog_drag_y
        dialog.geometry(f"+{x}+{y}")
    
    def clear_input(self):
        self.code_input.delete('1.0', tk.END)
        self.update_status("Input cleared")
    
    def clear_output(self):
        self.console_output.delete('1.0', tk.END)
        self.update_status("Output cleared")
    
    def run_code(self):
        code = self.code_input.get('1.0', tk.END).strip()
        
        if not code:
            if self.settings['notifications'].get():
                messagebox.showwarning("Warning", "Please enter some code to execute!")
            return
        
        self.command_history.append(code)
        
        self.console_output.delete('1.0', tk.END)
        
        print("\n" + "="*50)
        print("EXECUTING CODE FROM UI:")
        print("="*50)
        print(code)
        print("="*50)
        print("OUTPUT:")
        print("="*50)
        
        redirected_output = StringIO()
        redirected_error = StringIO()
        
        class DualWriter:
            def __init__(self, *writers):
                self.writers = writers
            
            def write(self, text):
                for writer in self.writers:
                    writer.write(text)
                    if hasattr(writer, 'flush'):
                        writer.flush()
            
            def flush(self):
                for writer in self.writers:
                    if hasattr(writer, 'flush'):
                        writer.flush()
        
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        sys.stdout = DualWriter(original_stdout, redirected_output)
        sys.stderr = DualWriter(original_stderr, redirected_error)
        
        import_time = time.time()
        
        try:
            self.console_output.insert(tk.END, f">>> Executing code...\n", 'info')
            
            exec_globals = globals().copy()
            exec(code, exec_globals)
            
            exec_time = time.time() - import_time
            
            output = redirected_output.getvalue()
            errors = redirected_error.getvalue()
            
            if output:
                self.console_output.insert(tk.END, f"\n{output}", 'output')
            if errors:
                self.console_output.insert(tk.END, f"\nErrors:\n{errors}", 'error')
            
            success_msg = f"\n✓ Executed in {exec_time:.3f}s"
            if not output and not errors:
                success_msg += " (no output)"
            
            self.console_output.insert(tk.END, success_msg, 'success')
            print(success_msg)
            
            self.update_status(f"Code executed in {exec_time:.3f}s")
            print("\n" + "="*50)
            print("EXECUTION COMPLETE")
            print("="*50 + "\n")
            
            if self.settings['notifications'].get():
                messagebox.showinfo("Success", f"Code executed successfully in {exec_time:.3f}s!")
                
        except Exception as e:
            error_msg = f"\n❌ Error: {str(e)}"
            self.console_output.insert(tk.END, error_msg, 'error')
            print(error_msg)
            print("\n" + "="*50 + "\n")
            self.update_status("Execution failed")
            
            try:
                import traceback
                tb = traceback.format_exc()
                self.console_output.insert(tk.END, f"\n{tb}", 'error')
            except:
                pass
            
            if self.settings['notifications'].get():
                messagebox.showerror("Error", f"Execution failed: {str(e)}")
        
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
        self.console_output.tag_config('info', foreground='#00aaff')
        self.console_output.tag_config('output', foreground='#00ff00')
        self.console_output.tag_config('error', foreground='#ff4444')
        self.console_output.tag_config('success', foreground='#00ff00')
    
    def show_progress_page(self):
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Progress Monitor",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 20))
        
        self.progress_bars = []
        tasks = [
            ("Task 1: Data Processing", 0),
            ("Task 2: File Analysis", 0),
            ("Task 3: Report Generation", 0),
            ("Task 4: Cleanup", 0)
        ]
        
        for task_name, initial_value in tasks:
            task_frame = tk.Frame(container, bg=self.bg_color)
            task_frame.pack(fill=tk.X, pady=10)
            
            label = tk.Label(task_frame, text=task_name, font=("Segoe UI", 10),
                           bg=self.bg_color, fg=self.text_color)
            label.pack(anchor="w")
            
            progress_frame = tk.Frame(task_frame, bg=self.bg_color)
            progress_frame.pack(fill=tk.X, pady=5)
            
            progress = ttk.Progressbar(progress_frame, 
                                      style="Loading.Horizontal.TProgressbar",
                                      length=500, mode='determinate')
            progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
            progress['value'] = initial_value
            
            percent_label = tk.Label(progress_frame, text="0%", font=("Segoe UI", 9),
                                   bg=self.bg_color, fg="#a0a0a0", width=5)
            percent_label.pack(side=tk.LEFT, padx=10)
            
            self.progress_bars.append((progress, percent_label))
        
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=20)
        
        start_btn = tk.Button(btn_frame, text="Start All Tasks", font=("Segoe UI", 10, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=10, padx=30,
                            activebackground=self.button_hover,
                            command=self.start_progress)
        start_btn.pack(side=tk.LEFT, padx=5)
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg=self.button_hover))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=self.accent_color))
        
        reset_btn = tk.Button(btn_frame, text="Reset", font=("Segoe UI", 10),
                            bg=self.secondary_bg, fg=self.text_color,
                            border=0, cursor="hand2", pady=10, padx=30,
                            activebackground="#444444",
                            command=self.reset_progress)
        reset_btn.pack(side=tk.LEFT, padx=5)
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#444444"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg=self.secondary_bg))
    
    def start_progress(self):
        threading.Thread(target=self.animate_progress, daemon=True).start()
    
    def animate_progress(self):
        for progress, label in self.progress_bars:
            current = 0
            while current <= 100:
                progress['value'] = current
                label.config(text=f"{current}%")
                self.root.update()
                time.sleep(0.02)
                current += 1
            time.sleep(0.3)
        
        self.update_status("All tasks completed!")
        if self.settings['notifications'].get():
            messagebox.showinfo("Complete", "All tasks finished successfully!")
    
    def reset_progress(self):
        for progress, label in self.progress_bars:
            progress['value'] = 0
            label.config(text="0%")
        self.update_status("Progress reset")
    
    def show_settings(self):
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Settings",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 20))
        
        settings_container = tk.Frame(container, bg=self.bg_color)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        settings_config = [
            ("Enable Notifications", "notifications", "Show popup notifications for events"),
            ("Auto-start on Launch", "autostart", "Start the application automatically"),
            ("Dark Mode", "darkmode", "Use dark color theme"),
            ("Save Logs", "savelogs", "Save execution logs to file"),
            ("Syntax Highlighting", "syntax_highlight", "Highlight Python syntax in code editor"),
            ("Line Numbers", "line_numbers", "Show line numbers in code editor"),
            ("Autocomplete", "autocomplete", "Enable code autocomplete (Ctrl+Space)")
        ]
        
        for setting_name, var_key, description in settings_config:
            frame = tk.Frame(settings_container, bg=self.secondary_bg, highlightbackground=self.accent_color,
                           highlightthickness=1)
            frame.pack(fill=tk.X, pady=8)
            
            left_frame = tk.Frame(frame, bg=self.secondary_bg)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            label = tk.Label(left_frame, text=setting_name, font=("Segoe UI", 11, "bold"),
                           bg=self.secondary_bg, fg=self.text_color)
            label.pack(anchor="w")
            
            desc_label = tk.Label(left_frame, text=description, font=("Segoe UI", 8),
                                bg=self.secondary_bg, fg="#a0a0a0")
            desc_label.pack(anchor="w")
            
            checkbox = tk.Checkbutton(frame, variable=self.settings[var_key], 
                                    bg=self.secondary_bg,
                                    activebackground=self.secondary_bg,
                                    selectcolor=self.accent_color,
                                    command=lambda: self.auto_apply_settings())
            checkbox.pack(side=tk.RIGHT, padx=15)
    
    def auto_apply_settings(self):
        """Automatically apply settings when changed with smooth fade transition"""
        self.fade_theme_transition()
        
        self.update_status("Settings applied automatically")
    
    def fade_theme_transition(self):
        """Smooth fade transition between themes"""
        self.apply_theme()
        
        def fade_out(alpha=1.0):
            if alpha > 0.3:
                self.root.attributes('-alpha', alpha)
                self.root.after(10, lambda: fade_out(alpha - 0.05))
            else:
                self.refresh_ui()
                fade_in()
        
        def fade_in(alpha=0.3):
            if alpha < 1.0:
                self.root.attributes('-alpha', alpha)
                self.root.after(10, lambda: fade_in(alpha + 0.05))
            else:
                self.root.attributes('-alpha', 1.0)
        
        fade_out()
    
    def refresh_ui(self):
        """Refresh all UI components with new theme"""
        self.header.config(bg=self.secondary_bg)
        for widget in self.header.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=self.secondary_bg, fg=self.text_color)
            elif isinstance(widget, tk.Button):
                widget.config(bg=self.secondary_bg, fg=self.text_color)
        
        self.sidebar.config(bg=self.secondary_bg)
        for btn in self.menu_buttons.values():
            if btn.cget('bg') == self.accent_color:
                btn.config(bg=self.accent_color, fg="white")
            else:
                btn.config(bg=self.secondary_bg, fg=self.text_color)
        
        self.content_frame.config(bg=self.bg_color)
        
        self.footer.config(bg=self.secondary_bg)
        for widget in self.footer.winfo_children():
            widget.config(bg=self.secondary_bg)
        
        current = self.current_page
        self.current_page = None
        self.switch_page(current)
    
    def show_about(self):
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        center_frame = tk.Frame(container, bg=self.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title = tk.Label(center_frame, text="CipherV2",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(pady=(0, 10))
        
        version = tk.Label(center_frame, text="Version 2.0.0 - Ultimate Edition",
                          font=("Segoe UI", 12),
                          bg=self.bg_color, fg="#a0a0a0")
        version.pack(pady=5)
        
        desc = tk.Label(center_frame, 
                       text="The Ultimate JSON Injector & Code Manipulation Tool\n\n"
                            "✨ Features:\n"
                            "• Syntax Highlighting & Line Numbers\n"
                            "• Code Snippets & Autocomplete\n"
                            "• Execution History & Undo/Redo\n"
                            "• JSON LINT Formatting & Multi-tab Support\n"
                            "• Keyboard Shortcuts & Auto-formatting\n\n"
                            "Built with Python & Tkinter\n"
                            "Version 2.0.0 - 2025",
                       font=("Segoe UI", 9),
                       bg=self.bg_color, fg=self.text_color,
                       justify="center")
        desc.pack(pady=20)
        
        shortcuts_label = tk.Label(center_frame,
                                   text="⌨️ Keyboard Shortcuts:\n"
                                        "Ctrl+S: Save | F5: Run Code\n"
                                        "Ctrl+Z: Undo | Ctrl+Y: Redo\n"
                                        "Ctrl+F: Find/Replace | Ctrl+B: Format Code\n"
                                        "Ctrl+Space: Autocomplete",
                                   font=("Consolas", 8),
                                   bg=self.bg_color, fg="#a0a0a0",
                                   justify="center")
        shortcuts_label.pack(pady=10)
        
        github_btn = tk.Button(center_frame, text="Documentation", 
                              font=("Segoe UI", 10),
                              bg=self.accent_color, fg="white",
                              border=0, cursor="hand2", pady=8, padx=20,
                              activebackground=self.button_hover,
                              command=lambda: self.show_notification("Info", "Documentation coming soon!"))
        github_btn.pack(pady=5)
        
        def doc_enter(e):
            github_btn.config(bg=self.button_hover)
        
        def doc_leave(e):
            github_btn.config(bg=self.accent_color)
        
        github_btn.bind("<Enter>", doc_enter)
        github_btn.bind("<Leave>", doc_leave)
    
    def create_footer(self):
        self.footer = tk.Frame(self.root, bg=self.secondary_bg, height=30)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        
        self.status_label = tk.Label(self.footer, text="Ready", font=("Segoe UI", 8),
                                    bg=self.secondary_bg, fg="#a0a0a0")
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        time_label = tk.Label(self.footer, text="", font=("Segoe UI", 8),
                            bg=self.secondary_bg, fg="#a0a0a0")
        time_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        def update_time():
            current_time = time.strftime("%I:%M:%S %p")
            time_label.config(text=current_time)
            self.root.after(1000, update_time)
        
        update_time()
    
    def update_status(self, message):
        self.status_label.config(text=message)
    
    def show_notification(self, title, message):
        if self.settings['notifications'].get():
            if title == "Error":
                messagebox.showerror(title, message)
            elif title == "Warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
        
    def execute_action(self, feature):
        self.update_status(f"Executing {feature}...")
        if self.settings['notifications'].get():
            messagebox.showinfo("Action", f"Executed: {feature}")
        self.update_status("Ready")

def main():
    root = tk.Tk()
    app = ModernUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
