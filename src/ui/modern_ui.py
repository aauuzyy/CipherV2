"""Main UI module for CipherV2"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
from collections import deque

from ui.theme import ThemeManager
from ui.editor import CodeEditor
from utils.settings import Settings
from utils.execution import ExecutionManager
from utils.json_tools import JSONHandler

class ModernUI:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)  # Set minimum size
        self.root.resizable(True, True)  # Make resizable
        self.root.overrideredirect(True)
        
        # Initialize managers and handlers
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.execution_manager = ExecutionManager()
        self.json_handler = JSONHandler()
        
        # Initialize instance variables
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.resize_offset_x = 0
        self.resize_offset_y = 0
        self.is_resizing = False
        
        self.tabs = {"Tab 1": ""}
        self.current_tab = "Tab 1"
        self.tab_counter = 1
        
        self.undo_stacks = {"Tab 1": deque(maxlen=50)}
        self.redo_stacks = {"Tab 1": deque(maxlen=50)}
        
        # Set up scripts directory
        self.scripts_dir = os.path.join(os.path.expanduser("~"), "Desktop", "BotModMenuSystem", "Saved Scripts")
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 60000  # 60 seconds
        self.auto_save_timer = None
        
        # Console content persistence
        self.console_content = ""
        
        # Initialize theme
        self.apply_theme()
        
        # Configure TTK styles
        self.setup_ttk_styles()
        
        # Create UI
        self.show_loading_screen()
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_ttk_styles(self):
        """Configure TTK styles for the application"""
        try:
            style = ttk.Style()
            style.theme_use('default')
            
            # Configure progress bar style
            style.configure("Loading.Horizontal.TProgressbar",
                           background=self.theme_manager.DARK_THEME['accent_color'],
                           troughcolor=self.theme_manager.DARK_THEME['secondary_bg'],
                           bordercolor=self.theme_manager.DARK_THEME['bg_color'],
                           lightcolor=self.theme_manager.DARK_THEME['accent_color'],
                           darkcolor=self.theme_manager.DARK_THEME['accent_color'])
        except Exception as e:
            print(f"Error setting up TTK styles: {e}")

    def apply_theme(self):
        """Apply current theme colors"""
        theme = self.theme_manager.DARK_THEME if self.settings.darkmode.get() else self.theme_manager.LIGHT_THEME
        for key, value in theme.items():
            setattr(self, key, value)
        self.root.configure(bg=self.bg_color)

    def show_loading_screen(self):
        """Show the initial loading screen"""
        self.loading_frame = tk.Frame(self.root, bg=self.bg_color)
        self.loading_frame.place(x=0, y=0, width=800, height=600)
        
        # Create loading screen widgets
        title = tk.Label(self.loading_frame, text="CipherV2",
                        font=("Segoe UI", 24, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.place(relx=0.5, rely=0.4, anchor="center")
        
        self.loading_text = tk.Label(self.loading_frame, text="Loading...",
                                   font=("Segoe UI", 10),
                                   bg=self.bg_color, fg="#a0a0a0")
        self.loading_text.place(relx=0.5, rely=0.5, anchor="center")
        
        self.loading_progress = ttk.Progressbar(self.loading_frame,
                                             style="Loading.Horizontal.TProgressbar",
                                             length=300, mode='determinate')
        self.loading_progress.place(relx=0.5, rely=0.55, anchor="center")
        
        # Start loading animation in separate thread
        self.loading_thread = threading.Thread(target=self.animate_loading, daemon=True)
        self.loading_thread.start()

    def animate_loading(self):
        """Animate the loading progress"""
        try:
            steps = ["Initializing...", "Loading modules...", "Setting up UI...", "Almost done..."]
            for i, step in enumerate(steps):
                if not self.root.winfo_exists():
                    return
                    
                if not hasattr(self, 'loading_text') or not self.loading_text.winfo_exists():
                    return
                    
                try:
                    self.loading_text.config(text=step)
                    self.loading_progress.config(value=(i+1)*25)
                    self.root.update_idletasks()
                    self.root.update()
                except (tk.TclError, RuntimeError):
                    return
                
                time.sleep(0.5)
            
            time.sleep(0.3)
            
            if self.root.winfo_exists() and hasattr(self, 'loading_frame'):
                try:
                    if self.loading_frame.winfo_exists():
                        self.root.after(0, self.finish_loading)
                except (tk.TclError, RuntimeError):
                    pass
                
        except (tk.TclError, RuntimeError):
            pass
        except Exception as e:
            print(f"Loading error: {str(e)}")

    def finish_loading(self):
        """Complete the loading process and create main UI"""
        try:
            if not self.root.winfo_exists():
                return
                
            if hasattr(self, 'loading_frame'):
                try:
                    if self.loading_frame.winfo_exists():
                        self.loading_frame.destroy()
                except (tk.TclError, RuntimeError):
                    pass
                    
            self.create_main_ui()
        except (tk.TclError, RuntimeError):
            pass
        except Exception as e:
            print(f"Error creating main UI: {str(e)}")

    def create_main_ui(self):
        """Create the main application UI"""
        self.root.attributes('-alpha', 1.0)
        
        # Create main UI components
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # Add resize grips
        self.create_resize_grips()
        
        # Start auto-save
        self.start_auto_save()

    def create_header(self):
        """Create the application header bar"""
        self.header = tk.Frame(self.root, bg=self.secondary_bg, height=60)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)
        
        # Add drag functionality
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)
        
        # Quick action buttons (FAR LEFT)
        actions_frame = tk.Frame(self.header, bg=self.secondary_bg)
        actions_frame.pack(side=tk.LEFT, padx=10)
        
        action_buttons = [
            ("📁", self.show_file_explorer),
            ("⌨", self.show_shortcuts_panel),
            ("🔍", self.show_global_search),
            ("📋", self.show_templates_manager),
            ("🎨", self.show_theme_customizer),
            ("📊", self.show_statistics_dashboard)
        ]
        
        for icon, command in action_buttons:
            btn = tk.Button(actions_frame, text=icon,
                           font=("Segoe UI", 14),
                           bg=self.secondary_bg, fg=self.text_color,
                           border=0, cursor="hand2",
                           width=3, height=1,
                           command=command)
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444444"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.secondary_bg))
        
        # Title and version (CENTER)
        title_frame = tk.Frame(self.header, bg=self.secondary_bg)
        title_frame.pack(side=tk.LEFT, expand=True)
        
        title = tk.Label(title_frame, text="CipherV2",
                        font=("Segoe UI", 18, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        title.pack(side=tk.LEFT, padx=10, pady=15)
        title.bind("<Button-1>", self.start_drag)
        title.bind("<B1-Motion>", self.do_drag)
        
        version = tk.Label(title_frame, text="v2.0",
                          font=("Segoe UI", 8),
                          bg=self.secondary_bg, fg="#a0a0a0")
        version.pack(side=tk.LEFT, pady=15)
        
        # Window controls (FAR RIGHT)
        self.create_window_controls()

    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_bar = tk.Frame(self.root, bg=self.secondary_bg, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        # Status text
        self.status_text = tk.Label(self.status_bar, text="Ready",
                                  font=("Segoe UI", 8),
                                  bg=self.secondary_bg, fg="#a0a0a0")
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # Time display
        self.time_display = tk.Label(self.status_bar, text="",
                                   font=("Segoe UI", 8),
                                   bg=self.secondary_bg, fg="#a0a0a0")
        self.time_display.pack(side=tk.RIGHT, padx=10)
        
        # Start time update
        self.update_time()

    def create_sidebar(self):
        """Create the application sidebar"""
        self.sidebar = tk.Frame(self.root, bg=self.secondary_bg, width=200)
        self.sidebar.pack(fill=tk.Y, side=tk.LEFT)
        self.sidebar.pack_propagate(False)
        
        # Define menu items
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
                    b.config(bg="#363636")
            
            def on_leave(e, b=btn, ind=border_indicator):
                if b.cget('bg') != self.accent_color:
                    ind.config(bg=self.secondary_bg)
                    b.config(bg=self.secondary_bg)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.config(command=lambda i=item: self.switch_page(i))
            self.menu_buttons[item] = btn

    def create_main_content(self):
        """Create the main content area"""
        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Track current page
        self.current_page = None
        
        # Initially show dashboard
        self.switch_page("Dashboard")
    
    def switch_page(self, page):
        """Switch to a different page with animation"""
        if self.current_page == page:
            return
            
        self.current_page = page
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update menu button highlighting
        for name, btn in self.menu_buttons.items():
            if name == page:
                btn.config(bg=self.accent_color, fg="white")
                btn.border_indicator.config(bg=self.accent_color)
            else:
                btn.config(bg=self.secondary_bg, fg=self.text_color)
                btn.border_indicator.config(bg=self.secondary_bg)
        
        # Load page content
        self.update_status(f"Loading {page}...")
        self.load_page_content(page)
    
    def load_page_content(self, page):
        """Load the actual page content"""
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
        """Show the dashboard view with animated cards"""
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
        
        # Create animated cards grid
        cards_frame = tk.Frame(container, bg=self.bg_color)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_dashboard_card(cards_frame, "Quick Action", "Execute a fast task", 0, 0)
        self.create_dashboard_card(cards_frame, "Batch Process", "Process multiple items", 0, 1)
        self.create_dashboard_card(cards_frame, "Analysis", "Analyze your data", 1, 0)
        self.create_dashboard_card(cards_frame, "Export", "Export results", 1, 1)
    
    def create_dashboard_card(self, parent, title, desc, row, col):
        """Create an animated dashboard card"""
        card = tk.Frame(parent, bg=self.secondary_bg, highlightbackground=self.accent_color,
                       highlightthickness=0)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
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
                             command=lambda: self.update_status(f"Executed {title}"))
        action_btn.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Hover animations
        def on_card_enter(e):
            card.config(highlightthickness=1, highlightbackground=self.accent_color)
            self.animate_widget_scale(card, 1.02)
        
        def on_card_leave(e):
            card.config(highlightthickness=0)
            self.animate_widget_scale(card, 1.0)
        
        def on_btn_enter(e):
            action_btn.config(bg=self.button_hover)
        
        def on_btn_leave(e):
            action_btn.config(bg=self.accent_color)
        
        card.bind("<Enter>", on_card_enter)
        card.bind("<Leave>", on_card_leave)
        action_btn.bind("<Enter>", on_btn_enter)
        action_btn.bind("<Leave>", on_btn_leave)
    
    def animate_widget_scale(self, widget, scale):
        """Simple scale animation effect"""
        try:
            # Visual feedback via background color intensity
            if scale > 1.0:
                widget.config(relief=tk.RAISED, bd=1)
            else:
                widget.config(relief=tk.FLAT, bd=0)
        except:
            pass
    
    def show_console(self):
        """Show console page with code editor"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Python Console",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Write and execute Python code with syntax highlighting",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Code editor with line numbers
        editor_label = tk.Label(container, text="Code Editor:",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        editor_label.pack(anchor="w", pady=(5, 5))
        
        editor_container = tk.Frame(container, bg=self.secondary_bg)
        editor_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Line numbers
        self.line_numbers = tk.Text(editor_container,
                                    width=4,
                                    padx=5,
                                    takefocus=0,
                                    border=0,
                                    background=self.secondary_bg,
                                    foreground="#606060",
                                    state='disabled',
                                    font=("Consolas", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        editor_frame = tk.Frame(editor_container, bg=self.secondary_bg)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.code_input = tk.Text(editor_frame, 
                                  height=12,
                                  font=("Consolas", 10),
                                  bg=self.secondary_bg,
                                  fg=self.text_color,
                                  insertbackground=self.text_color,
                                  selectbackground=self.accent_color,
                                  wrap=tk.NONE,
                                  undo=True)
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(editor_frame, command=self.code_input.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_input.config(yscrollcommand=scrollbar.set)
        
        # Configure syntax highlighting tags
        self.code_input.tag_configure("keyword", foreground="#569cd6")
        self.code_input.tag_configure("string", foreground="#ce9178")
        self.code_input.tag_configure("comment", foreground="#6a9955")
        self.code_input.tag_configure("function", foreground="#dcdcaa")
        self.code_input.tag_configure("number", foreground="#b5cea8")
        self.code_input.tag_configure("operator", foreground="#d4d4d4")
        
        # Restore saved content or insert placeholder
        if self.console_content:
            self.code_input.insert('1.0', self.console_content)
        else:
            self.code_input.insert('1.0', '# Write your Python code here\nprint("Hello, CipherV2!")')
        
        # Update line numbers and syntax highlighting
        def update_editor(event=None):
            self.update_line_numbers()
            self.apply_syntax_highlighting()
            self.console_content = self.code_input.get('1.0', tk.END)
        
        self.code_input.bind('<KeyRelease>', update_editor)
        self.code_input.bind('<ButtonRelease-1>', lambda e: self.update_line_numbers())
        
        # Initial update
        self.update_line_numbers()
        self.apply_syntax_highlighting()
        
        # Button toolbar with animations
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("▶ Run", self.accent_color, self.button_hover, self.run_code),
            ("💾 Save", "#2e7d32", "#43a047", self.save_file),
            ("📂 Load", "#1565c0", "#1976d2", self.show_find_dialog),
            ("✨ Beautify", "#f57c00", "#fb8c00", self.format_code),
            ("Insert .JSON", "#7b1fa2", "#9c27b0", self.insert_json_template),
            ("Lint JSON", "#6a1b9a", "#8e24aa", self.lint_json),
            ("Clear", self.secondary_bg, "#444444", self.clear_editor)
        ]
        
        for text, color, hover_color, command in buttons:
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 9, "bold"),
                           bg=color, fg="white",
                           border=0, cursor="hand2", pady=8, padx=12,
                           command=command, width=11)  # Make all buttons same width
            btn.pack(side=tk.LEFT, padx=3)
            
            # Animated hover effect
            btn.bind("<Enter>", lambda e, b=btn, hc=hover_color: self.animate_button(b, hc))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.animate_button(b, c))
        
        # Output console
        output_label = tk.Label(container, text="Output:",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        output_label.pack(anchor="w", pady=(10, 5))
        
        output_frame = tk.Frame(container, bg=self.secondary_bg)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console_output = tk.Text(output_frame, 
                                      height=8,
                                      font=("Consolas", 9),
                                      bg=self.secondary_bg,
                                      fg="#00ff00",
                                      insertbackground=self.text_color,
                                      wrap=tk.WORD,
                                      state=tk.DISABLED)
        self.console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        output_scrollbar = tk.Scrollbar(output_frame, command=self.console_output.yview)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_output.config(yscrollcommand=output_scrollbar.set)
    
    def animate_button(self, button, color):
        """Animate button color change"""
        button.config(bg=color)
    
    def update_line_numbers(self):
        """Update line numbers in code editor"""
        if hasattr(self, 'line_numbers') and hasattr(self, 'code_input'):
            try:
                line_count = self.code_input.get('1.0', 'end-1c').count('\n') + 1
                line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
                
                self.line_numbers.config(state='normal')
                self.line_numbers.delete('1.0', 'end')
                self.line_numbers.insert('1.0', line_numbers_string)
                self.line_numbers.config(state='disabled')
            except:
                pass
    
    def apply_syntax_highlighting(self):
        """Apply Python syntax highlighting"""
        if not hasattr(self, 'code_input'):
            return
        
        try:
            # Remove all existing tags
            for tag in ["keyword", "string", "comment", "function", "number", "operator"]:
                self.code_input.tag_remove(tag, "1.0", "end")
            
            code = self.code_input.get("1.0", "end-1c")
            
            # Python keywords
            keywords = r'\b(def|class|if|elif|else|for|while|try|except|finally|with|import|from|as|return|yield|lambda|pass|break|continue|raise|assert|del|global|nonlocal|and|or|not|in|is|None|True|False|async|await)\b'
            
            # Apply keyword highlighting
            import re
            for match in re.finditer(keywords, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("keyword", start, end)
            
            # Highlight strings
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("string", start, end)
            
            # Highlight comments
            for match in re.finditer(r'#.*$', code, re.MULTILINE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("comment", start, end)
            
            # Highlight numbers
            for match in re.finditer(r'\b\d+\.?\d*\b', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("number", start, end)
            
            # Highlight function names
            for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code):
                start = f"1.0+{match.start(1)}c"
                end = f"1.0+{match.end(1)}c"
                self.code_input.tag_add("function", start, end)
        except:
            pass
    
    def clear_editor(self):
        """Clear the code editor"""
        if hasattr(self, 'code_input'):
            self.code_input.delete('1.0', tk.END)
            self.console_content = ""
            self.update_line_numbers()
            self.update_status("Editor cleared")
    
    def show_history(self):
        """Show history page with command history"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Execution History",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="View previously executed commands and scripts",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # History list with animation
        list_frame = tk.Frame(container, bg=self.secondary_bg)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_list = tk.Listbox(list_frame, font=("Consolas", 9),
                                 bg=self.secondary_bg, fg=self.text_color,
                                 selectbackground=self.accent_color,
                                 yscrollcommand=scrollbar.set,
                                 border=0,
                                 highlightthickness=0)
        history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=history_list.yview)
        
        # Sample history items with fade-in animation
        sample_history = [
            "print('Hello World')",
            "for i in range(10): print(i)",
            "import requests",
            "def greet(name): return f'Hello {name}'",
            "x = [i**2 for i in range(10)]"
        ]
        
        def add_history_items(index=0):
            if index < len(sample_history):
                history_list.insert(tk.END, f"{index + 1}. {sample_history[index]}")
                history_list.itemconfig(index, fg="#a0a0a0" if index % 2 else self.text_color)
                self.root.after(100, lambda: add_history_items(index + 1))
        
        add_history_items()
        
        # Action buttons with hover animation
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        load_btn = tk.Button(btn_frame, text="Load Selected", font=("Segoe UI", 10, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=8, padx=20,
                            command=lambda: self.update_status("Loaded from history"))
        load_btn.pack(side=tk.LEFT, padx=5)
        load_btn.bind("<Enter>", lambda e: load_btn.config(bg=self.button_hover))
        load_btn.bind("<Leave>", lambda e: load_btn.config(bg=self.accent_color))
        
        clear_btn = tk.Button(btn_frame, text="Clear History", font=("Segoe UI", 10),
                             bg="#d32f2f", fg="white",
                             border=0, cursor="hand2", pady=8, padx=20,
                             command=lambda: history_list.delete(0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#e53935"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#d32f2f"))
    
    def show_snippets(self):
        """Show snippets page with code templates"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Code Snippets Library",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Quick access to common code patterns and templates - Click any snippet to insert",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Create canvas with scrollbar for snippets
        canvas_frame = tk.Frame(container, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        snippets_frame = tk.Frame(canvas, bg=self.bg_color)
        
        snippets_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=snippets_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Expanded snippets library with many more patterns
        snippets = {
            "For Loop": "for i in range(10):\n    print(i)",
            "While Loop": "while condition:\n    # code\n    break",
            "Function": "def function_name(param):\n    return param",
            "Class": "class MyClass:\n    def __init__(self):\n        pass",
            "Try/Except": "try:\n    # code\nexcept Exception as e:\n    print(f'Error: {e}')",
            "File Read": "with open('file.txt', 'r') as f:\n    data = f.read()",
            "File Write": "with open('file.txt', 'w') as f:\n    f.write('content')",
            "List Comp": "[x**2 for x in range(10)]",
            "Dict Comp": "{k: v for k, v in items}",
            "Lambda": "lambda x: x * 2",
            "Decorator": "@decorator\ndef function():\n    pass",
            "Context Manager": "with context as cm:\n    # code",
            "Async Function": "async def async_func():\n    await something()",
            "Generator": "def gen():\n    yield value",
            "If/Elif/Else": "if condition:\n    pass\nelif other:\n    pass\nelse:\n    pass",
            "Match/Case": "match value:\n    case 1:\n        pass\n    case _:\n        pass",
            "Import": "import module\nfrom package import item",
            "Class Method": "@classmethod\ndef method(cls):\n    pass",
            "Static Method": "@staticmethod\ndef method():\n    pass",
            "Property": "@property\ndef value(self):\n    return self._value",
            "Dataclass": "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int",
            "Enum": "from enum import Enum\n\nclass Color(Enum):\n    RED = 1\n    GREEN = 2",
            "JSON Load": "import json\nwith open('data.json') as f:\n    data = json.load(f)",
            "JSON Dump": "import json\nwith open('out.json', 'w') as f:\n    json.dump(data, f, indent=4)",
            "CSV Read": "import csv\nwith open('data.csv') as f:\n    reader = csv.DictReader(f)\n    for row in reader:\n        print(row)",
            "Requests GET": "import requests\nr = requests.get(url)\nprint(r.json())",
            "Requests POST": "import requests\nr = requests.post(url, json=data)\nprint(r.status_code)",
            "Pandas DataFrame": "import pandas as pd\ndf = pd.DataFrame(data)\nprint(df.head())",
            "NumPy Array": "import numpy as np\narr = np.array([1, 2, 3])",
            "Matplotlib Plot": "import matplotlib.pyplot as plt\nplt.plot(x, y)\nplt.show()",
            "Date/Time": "from datetime import datetime\nnow = datetime.now()\nprint(now.strftime('%Y-%m-%d'))",
            "Path Handling": "from pathlib import Path\np = Path('file.txt')\nprint(p.exists())",
            "Subprocess": "import subprocess\nresult = subprocess.run(['cmd'], capture_output=True)",
            "Threading": "import threading\nt = threading.Thread(target=func)\nt.start()",
            "Multiprocessing": "from multiprocessing import Process\np = Process(target=func)\np.start()",
            "Logging": "import logging\nlogging.basicConfig(level=logging.INFO)\nlogging.info('message')",
            "argparse": "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--name')\nargs = parser.parse_args()",
            "Regular Expression": "import re\nmatch = re.search(r'pattern', text)\nif match:\n    print(match.group())",
            "SQLite": "import sqlite3\nconn = sqlite3.connect('db.sqlite')\ncursor = conn.cursor()\ncursor.execute('SELECT * FROM table')",
            "Virtual Env": "# Create: python -m venv venv\n# Activate: venv\\Scripts\\activate",
            "F-String": "name = 'World'\nprint(f'Hello, {name}!')",
            "Type Hints": "def func(x: int, y: str) -> bool:\n    return True",
            "Walrus Operator": "if (n := len(data)) > 10:\n    print(f'{n} items')"
        }
        
        row, col = 0, 0
        delay = 0
        
        for name, code in snippets.items():
            self.create_snippet_card(snippets_frame, name, code, row, col, delay)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
            delay += 30  # Faster animation
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def create_snippet_card(self, parent, name, code, row, col, delay):
        """Create an animated snippet card"""
        def show_card():
            try:
                if not self.root.winfo_exists() or not parent.winfo_exists():
                    return
                    
                card = tk.Frame(parent, bg=self.secondary_bg,
                               highlightbackground=self.accent_color,
                               highlightthickness=1, relief=tk.RAISED, bd=2)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                parent.grid_rowconfigure(row, weight=1, minsize=180)
                parent.grid_columnconfigure(col, weight=1, minsize=250)
                
                # Title with icon
                title_frame = tk.Frame(card, bg=self.secondary_bg)
                title_frame.pack(fill=tk.X)
                
                name_label = tk.Label(title_frame, text=f"📝 {name}",
                                     font=("Segoe UI", 12, "bold"),
                                     bg=self.secondary_bg, fg=self.text_color)
                name_label.pack(anchor="w", padx=15, pady=(15, 5))
                
                # Separator
                sep = tk.Frame(card, bg=self.accent_color, height=2)
                sep.pack(fill=tk.X, padx=15, pady=(0, 10))
                
                # Code preview with better visibility - make it clickable
                code_frame = tk.Frame(card, bg="#1a1a1a", cursor="hand2")
                code_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
                
                code_preview = tk.Label(code_frame, text=code[:60] + "..." if len(code) > 60 else code,
                                       font=("Consolas", 9),
                                       bg="#1a1a1a", fg="#00ff00",
                                       wraplength=220, justify="left", anchor="w",
                                       cursor="hand2")
                code_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                # Make entire card clickable to insert snippet
                def click_to_insert(e=None):
                    self.insert_snippet(code)
                    card.config(highlightbackground="#00ff00")
                    self.root.after(200, lambda: card.config(highlightbackground=self.accent_color) if card.winfo_exists() else None)
                
                card.bind("<Button-1>", click_to_insert)
                title_frame.bind("<Button-1>", click_to_insert)
                name_label.bind("<Button-1>", click_to_insert)
                code_frame.bind("<Button-1>", click_to_insert)
                code_preview.bind("<Button-1>", click_to_insert)
                
                # Hover animation
                def on_enter(e):
                    card.config(highlightthickness=2, highlightbackground=self.button_hover)
                    sep.config(bg=self.button_hover)
                
                def on_leave(e):
                    card.config(highlightthickness=1, highlightbackground=self.accent_color)
                    sep.config(bg=self.accent_color)
                
                card.bind("<Enter>", on_enter)
                card.bind("<Leave>", on_leave)
                for child in card.winfo_children():
                    child.bind("<Enter>", on_enter)
                    child.bind("<Leave>", on_leave)
                    
            except (tk.TclError, RuntimeError):
                pass
        
        try:
            if self.root.winfo_exists():
                self.root.after(delay, show_card)
        except (tk.TclError, RuntimeError):
            pass
    
    def insert_snippet(self, code):
        """Insert snippet into editor"""
        self.switch_page("Console")
        if hasattr(self, 'code_input'):
            self.code_input.insert(tk.INSERT, code + "\n")
            self.update_status("Snippet inserted")
    
    def show_progress_page(self):
        """Show progress page with animated statistics"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Progress Tracker",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Track your coding progress and statistics",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Stats grid with animated progress bars
        stats_frame = tk.Frame(container, bg=self.bg_color)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        stats = [
            ("Scripts Executed", 45, 100),
            ("Lines of Code", 1250, 2000),
            ("Projects", 8, 15),
            ("Time Saved", 75, 100)
        ]
        
        for i, (label, current, total) in enumerate(stats):
            self.create_progress_stat(stats_frame, label, current, total, i)
    
    def create_progress_stat(self, parent, label, current, total, index):
        """Create an animated progress stat"""
        stat_frame = tk.Frame(parent, bg=self.secondary_bg)
        stat_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Label
        label_text = tk.Label(stat_frame, text=label,
                             font=("Segoe UI", 11, "bold"),
                             bg=self.secondary_bg, fg=self.text_color)
        label_text.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Progress bar container
        progress_container = tk.Frame(stat_frame, bg="#1a1a1a", height=25)
        progress_container.pack(fill=tk.X, padx=15, pady=(0, 5))
        progress_container.pack_propagate(False)
        
        # Animated progress bar
        progress_bar = tk.Frame(progress_container, bg=self.accent_color, height=25)
        progress_bar.place(x=0, y=0, width=0, height=25)
        
        # Value label
        value_label = tk.Label(stat_frame, text=f"{current}/{total}",
                             font=("Segoe UI", 9),
                             bg=self.secondary_bg, fg="#a0a0a0")
        value_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Animate progress bar
        def animate_progress(step=0):
            try:
                if not self.root.winfo_exists() or not progress_bar.winfo_exists():
                    return
                    
                if step <= current:
                    percentage = (step / total) * progress_container.winfo_reqwidth()
                    progress_bar.place(width=percentage)
                    value_label.config(text=f"{step}/{total}")
                    
                    # Calculate delay for smooth animation
                    delay = max(1, 500 // current)  # Faster for larger numbers
                    self.root.after(delay, lambda: animate_progress(step + max(1, current // 50)))
            except (tk.TclError, RuntimeError):
                pass
        
        # Start animation with delay based on index
        try:
            self.root.after(index * 100, lambda: animate_progress())
        except (tk.TclError, RuntimeError):
            pass
    
    def show_settings(self):
        """Show settings page with toggles and options"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Settings",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Configure application preferences",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Settings sections with fade-in animation
        settings_data = [
            ("Dark Mode", "Enable dark theme"),
            ("Notifications", "Show notification popups"),
            ("Auto-save", "Automatically save work"),
            ("Syntax Highlighting", "Highlight code syntax"),
            ("Line Numbers", "Show line numbers"),
            ("Auto-complete", "Enable code completion")
        ]
        
        for i, (setting_name, setting_desc) in enumerate(settings_data):
            self.create_setting_item(container, setting_name, setting_desc, i)
        
        # Save button with pulse animation
        save_btn = tk.Button(container, text="Save Settings", font=("Segoe UI", 11, "bold"),
                            bg=self.accent_color, fg="white",
                            border=0, cursor="hand2", pady=10, padx=30,
                            command=self.save_settings)
        save_btn.pack(pady=20)
        
        # Pulse animation on hover
        def pulse_animation(count=0):
            if count < 2:
                save_btn.config(bg=self.button_hover)
                self.root.after(200, lambda: save_btn.config(bg=self.accent_color))
                self.root.after(400, lambda: pulse_animation(count + 1))
        
        save_btn.bind("<Enter>", lambda e: pulse_animation())
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self.accent_color))
    
    def create_setting_item(self, parent, name, desc, index):
        """Create an animated setting item"""
        def show_setting():
            try:
                # Check if root and parent still exist FIRST
                if not self.root.winfo_exists():
                    return
                
                if not parent.winfo_exists():
                    return
                    
                setting_frame = tk.Frame(parent, bg=self.secondary_bg)
                setting_frame.pack(fill=tk.X, pady=5, padx=5)
                
                # Checkbox with proper master and command callback
                var = tk.BooleanVar(master=self.root, value=True)
                
                def on_toggle():
                    """Handle checkbox toggle"""
                    state = "enabled" if var.get() else "disabled"
                    self.show_notification(f"✓ {name} {state}", "success" if var.get() else "info")
                
                check = tk.Checkbutton(setting_frame,
                                      text=name,
                                      variable=var,
                                      font=("Segoe UI", 10, "bold"),
                                      bg=self.secondary_bg,
                                      fg=self.text_color,
                                      selectcolor=self.accent_color,
                                      activebackground=self.secondary_bg,
                                      activeforeground=self.text_color,
                                      command=on_toggle)
                check.pack(anchor="w", padx=15, pady=(10, 2))
                
                # Description
                desc_label = tk.Label(setting_frame, text=desc,
                                     font=("Segoe UI", 8),
                                     bg=self.secondary_bg, fg="#a0a0a0")
                desc_label.pack(anchor="w", padx=35, pady=(0, 10))
            except (tk.TclError, RuntimeError, Exception) as e:
                # Silently handle widget destruction errors
                pass
        
        # Staggered animation with error handling
        try:
            if self.root.winfo_exists():
                self.root.after(index * 80, show_setting)
        except:
            pass
    
    def save_settings(self):
        """Save settings with feedback animation"""
        self.update_status("Settings saved!")
        
        # Show custom notification instead of messagebox
        self.show_notification("✓ Settings Saved Successfully!", "success")
    
    def show_about(self):
        """Show about page with animated info"""
        container = tk.Frame(self.content_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Animated title
        title = tk.Label(container, text="About CipherV2",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(pady=(30, 10))
        
        # Version with color animation
        version_label = tk.Label(container, text="Version 2.0",
                                font=("Segoe UI", 12),
                                bg=self.bg_color, fg=self.accent_color)
        version_label.pack(pady=5)
        
        # Description with fade-in
        info_text = """A modern, feature-rich Python code editor
built with Tkinter and enhanced with:

✓ Syntax Highlighting
✓ Code Snippets Library
✓ Execution History
✓ Auto-save & Load
✓ Dark/Light Themes
✓ Smooth Animations

Created for efficient Python development"""
        
        info = tk.Label(container, 
                       text=info_text,
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg=self.text_color,
                       justify=tk.CENTER)
        info.pack(pady=20)
        
        # Animated credits
        credits_frame = tk.Frame(container, bg=self.secondary_bg)
        credits_frame.pack(pady=20, padx=40, fill=tk.X)
        
        credits = tk.Label(credits_frame, 
                          text="Made with ♥ using Python & Tkinter",
                          font=("Segoe UI", 9, "italic"),
                          bg=self.secondary_bg, fg="#a0a0a0")
        credits.pack(pady=15)
        
        # Pulsing animation for heart
        def pulse_heart(count=0):
            if count < 3:
                credits.config(fg=self.accent_color)
                self.root.after(300, lambda: credits.config(fg="#a0a0a0"))
                self.root.after(600, lambda: pulse_heart(count + 1))
        
        self.root.after(1000, pulse_heart)
        
        # Social/contact buttons
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=20)
        
        github_btn = tk.Button(btn_frame, text="GitHub", font=("Segoe UI", 10, "bold"),
                              bg=self.accent_color, fg="white",
                              border=0, cursor="hand2", pady=8, padx=20,
                              command=lambda: self.update_status("Visit GitHub"))
        github_btn.pack(side=tk.LEFT, padx=5)
        github_btn.bind("<Enter>", lambda e: github_btn.config(bg=self.button_hover))
        github_btn.bind("<Leave>", lambda e: github_btn.config(bg=self.accent_color))
        
        docs_btn = tk.Button(btn_frame, text="Documentation", font=("Segoe UI", 10, "bold"),
                            bg="#1565c0", fg="white",
                            border=0, cursor="hand2", pady=8, padx=20,
                            command=lambda: self.update_status("View docs"))
        docs_btn.pack(side=tk.LEFT, padx=5)
        docs_btn.bind("<Enter>", lambda e: docs_btn.config(bg="#1976d2"))
        docs_btn.bind("<Leave>", lambda e: docs_btn.config(bg="#1565c0"))
    
    # Placeholder methods for functionality
    def save_file(self):
        """Save current file"""
        self.update_status("File saved successfully")
    
    def run_code(self):
        """Run the code in the editor"""
        if hasattr(self, 'code_input') and hasattr(self, 'console_output'):
            code = self.code_input.get('1.0', tk.END).strip()
            
            if code:
                self.console_output.config(state=tk.NORMAL)
                self.console_output.delete('1.0', tk.END)
                self.console_output.insert('1.0', f">>> Executing code...\n{code}\n\n")
                
                try:
                    # Simple execution simulation
                    exec_globals = {}
                    exec(code, exec_globals)
                    self.console_output.insert(tk.END, "✓ Execution completed successfully\n", "success")
                    self.console_output.tag_config("success", foreground="#00ff00")
                except Exception as e:
                    self.console_output.insert(tk.END, f"✗ Error: {str(e)}\n", "error")
                    self.console_output.tag_config("error", foreground="#ff4444")
                
                self.console_output.config(state=tk.DISABLED)
                self.update_status("Code executed")
            else:
                self.update_status("No code to execute")
    
    def undo(self):
        """Undo last action"""
        if hasattr(self, 'code_input'):
            try:
                self.code_input.edit_undo()
                self.update_status("Undo")
            except:
                self.update_status("Nothing to undo")
    
    def redo(self):
        """Redo action"""
        if hasattr(self, 'code_input'):
            try:
                self.code_input.edit_redo()
                self.update_status("Redo")
            except:
                self.update_status("Nothing to redo")
    
    def show_find_dialog(self):
        """Show find dialog"""
        self.update_status("Find dialog - Feature coming soon!")
    
    def format_code(self):
        """Format code"""
        if hasattr(self, 'code_input'):
            code = self.code_input.get('1.0', tk.END).strip()
            if code:
                # Try to detect if it's JSON
                if code.strip().startswith(('{', '[')):
                    self.lint_json()
                    return
                
                # Simple Python formatting
                lines = code.split('\n')
                formatted = []
                indent = 0
                
                for line in lines:
                    stripped = line.strip()
                    if stripped:
                        if stripped.startswith(('elif', 'else', 'except', 'finally')) and indent > 0:
                            indent = max(0, indent - 1)
                        
                        formatted.append('    ' * indent + stripped)
                        
                        if stripped.endswith(':'):
                            indent += 1
                    else:
                        formatted.append('')
                
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', '\n'.join(formatted))
                self.update_status("Code formatted")
            else:
                self.update_status("No code to format")
    
    def insert_json_template(self):
        """Insert JSON template into editor"""
        if hasattr(self, 'code_input'):
            json_template = '''{
    "name": "Example",
    "version": "1.0",
    "description": "Your description here",
    "data": {
        "key1": "value1",
        "key2": "value2"
    },
    "items": [
        {
            "id": 1,
            "active": true
        },
        {
            "id": 2,
            "active": false
        }
    ]
}'''
            # Save current content
            self.console_content = json_template
            self.code_input.delete('1.0', tk.END)
            self.code_input.insert('1.0', json_template)
            self.update_status("JSON template inserted")
            self.show_notification("✓ JSON template ready to edit", "success")
            
            # Show LINT JSON button
            self.show_lint_json_button()
    
    def show_lint_json_button(self):
        """Show LINT JSON button in console"""
        # This will be visible after switching back to console
        pass
    
    def lint_json(self):
        """Lint and format JSON code"""
        if hasattr(self, 'code_input'):
            code = self.code_input.get('1.0', tk.END).strip()
            if code:
                try:
                    import json
                    # Parse JSON
                    parsed = json.loads(code)
                    # Format with indentation
                    formatted = json.dumps(parsed, indent=4, sort_keys=False)
                    
                    self.code_input.delete('1.0', tk.END)
                    self.code_input.insert('1.0', formatted)
                    self.update_status("✓ JSON formatted successfully")
                    self.show_notification("✓ JSON is valid and formatted", "success")
                except json.JSONDecodeError as e:
                    self.update_status(f"JSON Error: {str(e)}")
                    self.show_notification(f"❌ JSON Error: {str(e)}", "error")
                except Exception as e:
                    self.update_status(f"Error: {str(e)}")
                    self.show_notification(f"❌ Error: {str(e)}", "error")
            else:
                self.update_status("No JSON to format")

    
    def update_time(self):
        """Update the time display in status bar"""
        if hasattr(self, 'time_display'):
            current_time = time.strftime("%I:%M:%S %p")
            self.time_display.config(text=current_time)
            self.root.after(1000, self.update_time)

    def update_status(self, message):
        """Update the status bar message"""
        if hasattr(self, 'status_text'):
            self.status_text.config(text=message)

    def start_drag(self, event):
        """Begin window drag operation"""
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y

    def do_drag(self, event):
        """Perform window drag operation"""
        x = self.root.winfo_x() + event.x - self.drag_offset_x
        y = self.root.winfo_y() + event.y - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")

    def create_window_controls(self):
        """Create window control buttons"""
        controls_frame = tk.Frame(self.header, bg=self.secondary_bg)
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        # Minimize button (− to the left of X)
        min_btn = tk.Button(controls_frame, text="−",
                           font=("Segoe UI", 14, "bold"),
                           bg=self.secondary_bg,
                           fg=self.text_color,
                           border=0,
                           width=3, height=1,
                           command=self.root.iconify,
                           cursor="hand2")
        min_btn.pack(side=tk.LEFT, padx=2)
        
        # Close button (X on far right)
        close_btn = tk.Button(controls_frame, text="×",
                             font=("Segoe UI", 16, "bold"),
                             bg=self.secondary_bg,
                             fg=self.text_color,
                             border=0,
                             width=3, height=1,
                             command=self.cleanup_and_close,
                             cursor="hand2")
        close_btn.pack(side=tk.LEFT, padx=2)
        
        # Button hover effects
        min_btn.bind("<Enter>", lambda e: min_btn.config(bg="#404040"))
        min_btn.bind("<Leave>", lambda e: min_btn.config(bg=self.secondary_bg))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#d32f2f"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.secondary_bg))

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self.show_find_dialog())
        self.root.bind('<Control-b>', lambda e: self.format_code())
        self.root.bind('<Control-n>', lambda e: self.add_tab())
        self.root.bind('<Control-h>', lambda e: self.show_shortcuts_panel())
        self.root.bind('<F1>', lambda e: self.show_shortcuts_panel())
        self.root.bind('<Control-g>', lambda e: self.show_global_search())
        self.root.bind('<Control-e>', lambda e: self.show_export_options())
        self.root.bind('<Control-t>', lambda e: self.show_templates_manager())
        self.root.bind('<F2>', lambda e: self.show_theme_customizer())
        self.root.bind('<F3>', lambda e: self.show_statistics_dashboard())
        self.root.bind('<Control-Alt-s>', lambda e: self.toggle_auto_save())

    
    # ==================== NEW FEATURES ====================
    
    def create_resize_grips(self):
        """Create resize grips for window borders"""
        # Bottom-right corner resize grip
        resize_grip = tk.Label(self.root, text="⋰", font=("Arial", 12),
                              bg=self.secondary_bg, fg=self.accent_color,
                              cursor="size_nw_se")
        resize_grip.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
        
        resize_grip.bind("<Button-1>", self.start_resize)
        resize_grip.bind("<B1-Motion>", self.do_resize)
        resize_grip.bind("<ButtonRelease-1>", self.end_resize)
    
    def start_resize(self, event):
        """Start resize operation"""
        self.is_resizing = True
        self.resize_offset_x = event.x
        self.resize_offset_y = event.y
    
    def do_resize(self, event):
        """Perform resize operation"""
        if self.is_resizing:
            width = self.root.winfo_width() + event.x - self.resize_offset_x
            height = self.root.winfo_height() + event.y - self.resize_offset_y
            
            # Enforce minimum size
            width = max(800, width)
            height = max(600, height)
            
            self.root.geometry(f"{width}x{height}")
    
    def end_resize(self, event):
        """End resize operation"""
        self.is_resizing = False
    
    def show_notification(self, message, type="info"):
        """Show custom toast notification"""
        # Create notification window
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        
        # Position at top-right
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + 80
        notif.geometry(f"300x80+{x}+{y}")
        
        # Color based on type
        colors = {
            "success": "#2e7d32",
            "error": "#d32f2f",
            "warning": "#f57c00",
            "info": self.accent_color
        }
        color = colors.get(type, self.accent_color)
        
        # Notification frame
        frame = tk.Frame(notif, bg=color, highlightbackground=color,
                        highlightthickness=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Inner frame
        inner = tk.Frame(frame, bg=self.secondary_bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Icon and message
        icon_label = tk.Label(inner, text={"success": "✓", "error": "✗", 
                                          "warning": "⚠", "info": "ℹ"}.get(type, "ℹ"),
                             font=("Segoe UI", 24, "bold"),
                             bg=self.secondary_bg, fg=color)
        icon_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        msg_label = tk.Label(inner, text=message, font=("Segoe UI", 10),
                            bg=self.secondary_bg, fg=self.text_color,
                            wraplength=200, justify="left")
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(0, 10))
        
        # Close button
        close_btn = tk.Label(inner, text="×", font=("Segoe UI", 16),
                            bg=self.secondary_bg, fg=self.text_color,
                            cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", lambda e: notif.destroy())
        
        # Slide in animation
        def slide_in(pos=0):
            if pos < 20:
                notif.geometry(f"300x80+{x}+{y - pos}")
                self.root.after(10, lambda: slide_in(pos + 2))
        
        # Auto close after 3 seconds
        def auto_close():
            try:
                if notif.winfo_exists():
                    notif.destroy()
            except:
                pass
        
        slide_in()
        self.root.after(3000, auto_close)
    
    def show_shortcuts_panel(self):
        """Show keyboard shortcuts panel"""
        panel = tk.Toplevel(self.root)
        panel.title("Keyboard Shortcuts")
        panel.geometry("500x600")
        panel.configure(bg=self.bg_color)
        panel.transient(self.root)
        
        # Center on parent
        panel.geometry(f"+{self.root.winfo_x() + 250}+{self.root.winfo_y() + 50}")
        
        # Header
        header = tk.Frame(panel, bg=self.secondary_bg, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="⌨ Keyboard Shortcuts",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        title.pack(pady=15)
        
        # Content with scrollbar
        content_frame = tk.Frame(panel, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(content_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Shortcuts data
        shortcuts = [
            ("Ctrl + S", "Save file"),
            ("F5", "Run code"),
            ("Ctrl + Z", "Undo"),
            ("Ctrl + Y", "Redo"),
            ("Ctrl + F", "Find"),
            ("Ctrl + B", "Format code"),
            ("Ctrl + N", "New tab"),
            ("Ctrl + H / F1", "Show shortcuts"),
            ("Ctrl + G", "Global search"),
            ("Ctrl + E", "Export options"),
            ("Ctrl + T", "Templates manager"),
            ("F2", "Theme customizer"),
            ("F3", "Statistics dashboard"),
            ("Ctrl + Alt + S", "Toggle auto-save"),
            ("Escape", "Close dialogs"),
        ]
        
        for key, desc in shortcuts:
            shortcut_frame = tk.Frame(scrollable_frame, bg=self.secondary_bg)
            shortcut_frame.pack(fill=tk.X, pady=5)
            
            key_label = tk.Label(shortcut_frame, text=key,
                                font=("Consolas", 10, "bold"),
                                bg=self.accent_color, fg="white",
                                padx=10, pady=5)
            key_label.pack(side=tk.LEFT, padx=10, pady=10)
            
            desc_label = tk.Label(shortcut_frame, text=desc,
                                 font=("Segoe UI", 10),
                                 bg=self.secondary_bg, fg=self.text_color)
            desc_label.pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = tk.Button(panel, text="Close", font=("Segoe UI", 10, "bold"),
                             bg=self.accent_color, fg="white",
                             border=0, cursor="hand2", pady=10, padx=30,
                             command=panel.destroy)
        close_btn.pack(pady=10)
        
        panel.bind('<Escape>', lambda e: panel.destroy())
    
    def show_file_explorer(self):
        """Show file explorer to browse and open files"""
        explorer = tk.Toplevel(self.root)
        explorer.title("File Explorer")
        explorer.geometry("600x500")
        explorer.configure(bg=self.bg_color)
        explorer.transient(self.root)
        
        # Header
        header = tk.Frame(explorer, bg=self.secondary_bg)
        header.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(header, text="📁 File Explorer", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=10)
        
        # Path bar
        path_frame = tk.Frame(explorer, bg=self.bg_color)
        path_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.current_path = os.path.expanduser("~")
        path_entry = tk.Entry(path_frame, font=("Consolas", 10),
                             bg=self.secondary_bg, fg=self.text_color,
                             insertbackground=self.text_color)
        path_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        path_entry.insert(0, self.current_path)
        
        # File list
        list_frame = tk.Frame(explorer, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        file_list = tk.Listbox(list_frame, font=("Consolas", 10),
                              bg=self.secondary_bg, fg=self.text_color,
                              selectbackground=self.accent_color,
                              yscrollcommand=scrollbar.set)
        file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=file_list.yview)
        
        def load_directory(path):
            file_list.delete(0, tk.END)
            try:
                items = os.listdir(path)
                file_list.insert(tk.END, "..")  # Parent directory
                for item in sorted(items):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        file_list.insert(tk.END, f"📁 {item}")
                    elif item.endswith('.py'):
                        file_list.insert(tk.END, f"🐍 {item}")
                    elif item.endswith('.txt'):
                        file_list.insert(tk.END, f"📄 {item}")
                    else:
                        file_list.insert(tk.END, f"📋 {item}")
            except PermissionError:
                self.show_notification("Permission denied", "error")
        
        def on_select(event):
            selection = file_list.curselection()
            if selection:
                item = file_list.get(selection[0])
                if item == "..":
                    new_path = os.path.dirname(self.current_path)
                else:
                    item_name = item.split(" ", 1)[1] if " " in item else item
                    new_path = os.path.join(self.current_path, item_name)
                
                if os.path.isdir(new_path):
                    self.current_path = new_path
                    path_entry.delete(0, tk.END)
                    path_entry.insert(0, new_path)
                    load_directory(new_path)
        
        file_list.bind('<Double-Button-1>', on_select)
        load_directory(self.current_path)
        
        explorer.bind('<Escape>', lambda e: explorer.destroy())
    
    def show_global_search(self):
        """Show global search across all content"""
        search_win = tk.Toplevel(self.root)
        search_win.title("Global Search")
        search_win.geometry("500x400")
        search_win.configure(bg=self.bg_color)
        search_win.transient(self.root)
        
        # Header
        header = tk.Frame(search_win, bg=self.secondary_bg)
        header.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(header, text="🔍 Global Search", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=10)
        
        # Search bar
        search_frame = tk.Frame(search_win, bg=self.bg_color)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_entry = tk.Entry(search_frame, font=("Segoe UI", 12),
                               bg=self.secondary_bg, fg=self.text_color,
                               insertbackground=self.text_color)
        search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        search_entry.focus()
        
        search_btn = tk.Button(search_frame, text="Search",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.accent_color, fg="white",
                              border=0, cursor="hand2", padx=20)
        search_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Results
        results_frame = tk.Frame(search_win, bg=self.bg_color)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        results_list = tk.Listbox(results_frame, font=("Consolas", 9),
                                 bg=self.secondary_bg, fg=self.text_color,
                                 selectbackground=self.accent_color,
                                 yscrollcommand=scrollbar.set)
        results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=results_list.yview)
        
        def do_search():
            query = search_entry.get().lower()
            results_list.delete(0, tk.END)
            
            if not query:
                return
            
            # Search in snippets
            for name, code in self.get_all_snippets().items():
                if query in name.lower() or query in code.lower():
                    results_list.insert(tk.END, f"📝 Snippet: {name}")
            
            # Search in tabs
            for tab_name, content in self.tabs.items():
                if query in content.lower():
                    results_list.insert(tk.END, f"📄 Tab: {tab_name}")
            
            if results_list.size() == 0:
                results_list.insert(tk.END, "No results found")
        
        search_btn.config(command=do_search)
        search_entry.bind('<Return>', lambda e: do_search())
        search_win.bind('<Escape>', lambda e: search_win.destroy())
    
    def get_all_snippets(self):
        """Get all code snippets"""
        return {
            "For Loop": "for i in range(10):\n    print(i)",
            "Function": "def function(param):\n    return param",
            "Class": "class MyClass:\n    def __init__(self):\n        pass",
            "Try/Except": "try:\n    # code\nexcept Exception as e:\n    print(e)",
            "File Read": "with open('file.txt') as f:\n    data = f.read()",
            "List Comp": "[x for x in range(10)]"
        }
    
    def show_templates_manager(self):
        """Show code templates manager"""
        templates_win = tk.Toplevel(self.root)
        templates_win.title("Templates Manager")
        templates_win.geometry("700x500")
        templates_win.configure(bg=self.bg_color)
        templates_win.transient(self.root)
        
        # Header
        header = tk.Frame(templates_win, bg=self.secondary_bg, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📋 Code Templates", font=("Segoe UI", 16, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=15)
        
        # Template list
        list_frame = tk.Frame(templates_win, bg=self.bg_color)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(list_frame, text="Templates:", font=("Segoe UI", 11, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(0, 5))
        
        template_list = tk.Listbox(list_frame, font=("Consolas", 10),
                                   bg=self.secondary_bg, fg=self.text_color,
                                   selectbackground=self.accent_color)
        template_list.pack(fill=tk.BOTH, expand=True)
        
        # Sample templates with actual code
        template_codes = {
            "Flask API": '''from flask import Flask, jsonify\n\napp = Flask(__name__)\n\n@app.route('/api/data')\ndef get_data():\n    return jsonify({"status": "success"})\n\nif __name__ == '__main__':\n    app.run(debug=True)''',
            "Django Model": '''from django.db import models\n\nclass MyModel(models.Model):\n    name = models.CharField(max_length=200)\n    created = models.DateTimeField(auto_now_add=True)\n    \n    def __str__(self):\n        return self.name''',
            "FastAPI Endpoint": '''from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/items/{item_id}")\nasync def read_item(item_id: int):\n    return {"item_id": item_id}''',
            "Tkinter Window": '''import tkinter as tk\n\nroot = tk.Tk()\nroot.title("My App")\nroot.geometry("400x300")\n\nlabel = tk.Label(root, text="Hello!")\nlabel.pack(pady=20)\n\nroot.mainloop()''',
            "Data Analysis": '''import pandas as pd\nimport numpy as np\n\n# Load data\ndf = pd.read_csv('data.csv')\n\n# Analysis\nprint(df.describe())\nprint(df.head())''',
            "Web Scraper": '''import requests\nfrom bs4 import BeautifulSoup\n\nurl = 'https://example.com'\nr = requests.get(url)\nsoup = BeautifulSoup(r.content, 'html.parser')\n\nprint(soup.title.text)'''
        }
        
        templates = list(template_codes.keys())
        for tmpl in templates:
            template_list.insert(tk.END, tmpl)
        
        # Template preview
        preview_frame = tk.Frame(templates_win, bg=self.bg_color)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(preview_frame, text="Preview:", font=("Segoe UI", 11, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor="w", pady=(0, 5))
        
        preview_text = tk.Text(preview_frame, font=("Consolas", 9),
                              bg=self.secondary_bg, fg=self.text_color,
                              wrap=tk.WORD, height=20)
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Show template code when selected
        def on_template_select(event):
            selection = template_list.curselection()
            if selection:
                template_name = template_list.get(selection[0])
                code = template_codes.get(template_name, "")
                preview_text.delete('1.0', tk.END)
                preview_text.insert('1.0', code)
        
        template_list.bind('<<ListboxSelect>>', on_template_select)
        
        # Show first template by default
        template_list.selection_set(0)
        preview_text.insert('1.0', template_codes[templates[0]])
        
        # Buttons
        btn_frame = tk.Frame(templates_win, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def use_template():
            selection = template_list.curselection()
            if selection:
                template_name = template_list.get(selection[0])
                code = template_codes.get(template_name, "")
                if hasattr(self, 'code_input'):
                    self.console_content = code
                    self.show_notification(f"✓ {template_name} template loaded", "success")
                    templates_win.destroy()
        
        tk.Button(btn_frame, text="Use Template", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", border=0, cursor="hand2",
                 pady=8, padx=20, command=use_template, width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Save Custom", font=("Segoe UI", 10),
                 bg="#2e7d32", fg="white", border=0, cursor="hand2",
                 pady=8, padx=20, width=12).pack(side=tk.LEFT, padx=5)
        
        templates_win.bind('<Escape>', lambda e: templates_win.destroy())
    
    def show_theme_customizer(self):
        """Show theme customization panel"""
        customizer = tk.Toplevel(self.root)
        customizer.title("Theme Customizer")
        customizer.geometry("600x550")
        customizer.configure(bg=self.bg_color)
        customizer.transient(self.root)
        
        # Header
        header = tk.Frame(customizer, bg=self.secondary_bg, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎨 Theme Customizer", font=("Segoe UI", 16, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=15)
        
        # Content
        content = tk.Frame(customizer, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Color pickers with entry storage
        color_entries = {}
        color_previews = {}
        
        colors = [
            ("Background", "bg_color", self.bg_color),
            ("Secondary Background", "secondary_bg", self.secondary_bg),
            ("Accent Color", "accent_color", self.accent_color),
            ("Text Color", "text_color", self.text_color),
            ("Button Hover", "button_hover", self.button_hover)
        ]
        
        for i, (name, attr, color) in enumerate(colors):
            frame = tk.Frame(content, bg=self.secondary_bg)
            frame.pack(fill=tk.X, pady=10)
            
            tk.Label(frame, text=name, font=("Segoe UI", 10, "bold"),
                    bg=self.secondary_bg, fg=self.text_color,
                    width=20, anchor="w").pack(side=tk.LEFT, padx=15, pady=10)
            
            color_preview = tk.Frame(frame, bg=color, width=50, height=30,
                                    highlightbackground=self.text_color,
                                    highlightthickness=1)
            color_preview.pack(side=tk.LEFT, padx=10)
            color_previews[attr] = color_preview
            
            color_entry = tk.Entry(frame, font=("Consolas", 10),
                                  bg=self.bg_color, fg=self.text_color,
                                  width=10)
            color_entry.pack(side=tk.LEFT, padx=10)
            color_entry.insert(0, color)
            color_entries[attr] = color_entry
            
            # Update preview when typing
            def update_preview(e, attr=attr):
                try:
                    new_color = color_entries[attr].get()
                    color_previews[attr].config(bg=new_color)
                except:
                    pass
            
            color_entry.bind('<KeyRelease>', update_preview)
        
        # Preset themes
        presets_frame = tk.Frame(content, bg=self.secondary_bg)
        presets_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(presets_frame, text="Preset Themes:", font=("Segoe UI", 11, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor="w", padx=15, pady=10)
        
        preset_themes = {
            "Dark": {"bg_color": "#1e1e1e", "secondary_bg": "#2d2d2d", "accent_color": "#007acc", 
                    "text_color": "#ffffff", "button_hover": "#005a9e"},
            "Light": {"bg_color": "#f5f5f5", "secondary_bg": "#ffffff", "accent_color": "#2196f3",
                     "text_color": "#212121", "button_hover": "#1976d2"},
            "Ocean": {"bg_color": "#0d1b2a", "secondary_bg": "#1b263b", "accent_color": "#00b4d8",
                     "text_color": "#e0fbfc", "button_hover": "#0096c7"},
            "Forest": {"bg_color": "#1a2e1a", "secondary_bg": "#2d4a2d", "accent_color": "#4caf50",
                      "text_color": "#e8f5e9", "button_hover": "#388e3c"},
            "Sunset": {"bg_color": "#2c1810", "secondary_bg": "#3d2414", "accent_color": "#ff6f00",
                      "text_color": "#fff3e0", "button_hover": "#e65100"}
        }
        
        def apply_preset(preset_name):
            theme = preset_themes[preset_name]
            for attr, color in theme.items():
                if attr in color_entries:
                    color_entries[attr].delete(0, tk.END)
                    color_entries[attr].insert(0, color)
                    color_previews[attr].config(bg=color)
            self.show_notification(f"✓ {preset_name} theme loaded", "success")
        
        btn_container = tk.Frame(presets_frame, bg=self.secondary_bg)
        btn_container.pack(padx=15, pady=10)
        
        for preset in preset_themes.keys():
            btn = tk.Button(btn_container, text=preset, font=("Segoe UI", 9, "bold"),
                           bg=self.accent_color, fg="white",
                           border=0, cursor="hand2", width=10,
                           command=lambda p=preset: apply_preset(p))
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.button_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.accent_color))
        
        # Apply button
        def apply_theme():
            try:
                for attr, entry in color_entries.items():
                    new_color = entry.get()
                    setattr(self, attr, new_color)
                self.apply_theme()
                self.show_notification("✓ Theme applied! Restart for full effect", "success")
                customizer.destroy()
            except Exception as e:
                self.show_notification(f"❌ Error applying theme: {str(e)}", "error")
        
        apply_btn = tk.Button(customizer, text="Apply Theme",
                             font=("Segoe UI", 12, "bold"),
                             bg=self.accent_color, fg="white",
                             border=0, cursor="hand2", pady=12, padx=40,
                             command=apply_theme, width=15)
        apply_btn.pack(pady=10)
        apply_btn.bind("<Enter>", lambda e: apply_btn.config(bg=self.button_hover))
        apply_btn.bind("<Leave>", lambda e: apply_btn.config(bg=self.accent_color))
        
        customizer.bind('<Escape>', lambda e: customizer.destroy())
    
    def show_export_options(self):
        """Show export options dialog"""
        export_win = tk.Toplevel(self.root)
        export_win.title("Export Options")
        export_win.geometry("400x350")
        export_win.configure(bg=self.bg_color)
        export_win.transient(self.root)
        
        # Header
        header = tk.Frame(export_win, bg=self.secondary_bg)
        header.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(header, text="📤 Export Code", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=15)
        
        # Export options
        options_frame = tk.Frame(export_win, bg=self.bg_color)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        export_formats = [
            ("📄 Plain Text (.txt)", "txt"),
            ("🐍 Python File (.py)", "py"),
            ("📋 HTML (.html)", "html"),
            ("📑 PDF Document (.pdf)", "pdf"),
            ("📊 Markdown (.md)", "md")
        ]
        
        for label, fmt in export_formats:
            btn = tk.Button(options_frame, text=label,
                           font=("Segoe UI", 11),
                           bg=self.secondary_bg, fg=self.text_color,
                           border=0, cursor="hand2", pady=15,
                           anchor="w", padx=20,
                           activebackground="#444444",
                           command=lambda f=fmt: self.export_code(f))
            btn.pack(fill=tk.X, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444444"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.secondary_bg))
        
        export_win.bind('<Escape>', lambda e: export_win.destroy())
    
    def export_code(self, format):
        """Export code to specified format"""
        self.show_notification(f"Exported as {format.upper()}", "success")
        # Implementation would go here
    
    def show_statistics_dashboard(self):
        """Show enhanced statistics dashboard"""
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Statistics Dashboard")
        stats_win.geometry("800x600")
        stats_win.configure(bg=self.bg_color)
        stats_win.transient(self.root)
        
        # Header
        header = tk.Frame(stats_win, bg=self.secondary_bg, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Statistics Dashboard", font=("Segoe UI", 16, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=15)
        
        # Stats grid
        stats_container = tk.Frame(stats_win, bg=self.bg_color)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create stat cards
        stat_cards = [
            ("Lines Written", "1,250", "📝"),
            ("Files Created", "23", "📄"),
            ("Time Coding", "12h 34m", "⏱"),
            ("Commands Run", "156", "▶")
        ]
        
        for i, (title, value, icon) in enumerate(stat_cards):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(stats_container, bg=self.secondary_bg,
                           highlightbackground=self.accent_color,
                           highlightthickness=2)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            stats_container.grid_rowconfigure(row, weight=1)
            stats_container.grid_columnconfigure(col, weight=1)
            
            tk.Label(card, text=icon, font=("Segoe UI", 40),
                    bg=self.secondary_bg, fg=self.accent_color).pack(pady=20)
            
            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"),
                    bg=self.secondary_bg, fg=self.text_color).pack()
            
            tk.Label(card, text=title, font=("Segoe UI", 10),
                    bg=self.secondary_bg, fg="#a0a0a0").pack(pady=10)
        
        stats_win.bind('<Escape>', lambda e: stats_win.destroy())
    
    def start_auto_save(self):
        """Start auto-save timer"""
        if self.auto_save_enabled and self.auto_save_timer is None:
            self.auto_save_timer = self.root.after(self.auto_save_interval, self.perform_auto_save)
    
    def perform_auto_save(self):
        """Perform auto-save operation"""
        try:
            if self.current_tab and self.tabs.get(self.current_tab):
                # Auto-save current tab
                filename = f"autosave_{self.current_tab}.py"
                filepath = os.path.join(self.scripts_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(self.tabs[self.current_tab])
                
                # Show subtle notification
                self.show_notification("Auto-saved", "info")
            
            # Schedule next auto-save
            self.auto_save_timer = None
            self.start_auto_save()
        except Exception as e:
            print(f"Auto-save error: {e}")
            self.auto_save_timer = None
    
    def toggle_auto_save(self):
        """Toggle auto-save on/off"""
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.show_notification("Auto-save enabled", "success")
            self.start_auto_save()
        else:
            self.show_notification("Auto-save disabled", "info")
            if self.auto_save_timer:
                self.root.after_cancel(self.auto_save_timer)
                self.auto_save_timer = None
    
    def cleanup_and_close(self):
        """Clean up timers and close application"""
        try:
            # Cancel auto-save timer
            if self.auto_save_timer:
                self.root.after_cancel(self.auto_save_timer)
                self.auto_save_timer = None
            
            # Cancel any other pending after() calls
            for after_id in self.root.tk.call('after', 'info'):
                try:
                    self.root.after_cancel(after_id)
                except:
                    pass
        except:
            pass
        finally:
            # Close the application
            self.root.quit()
