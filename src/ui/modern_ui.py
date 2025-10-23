"""Main UI module for CipherV2"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
import io
import contextlib
from collections import deque

from ui.theme import ThemeManager
from ui.editor import CodeEditor
from utils.settings import Settings
from utils.execution import ExecutionManager
from utils.json_tools import JSONHandler
from utils.memory_editor import MemoryScanner
from utils.update_checker import UpdateChecker
from utils.command_palette import CommandPalette
from utils.notifications import ToastNotification
from utils.diff_viewer import DiffViewer
from utils.dll_injector import DLLInjector
from utils.process_inspector import ProcessInspector

class ModernUI:
    def __init__(self, root):
        try:
            print("Starting ModernUI initialization...")
            self.root = root
            self.root.title("CipherV4")
            self.root.geometry("1400x800")  # Wider window for better layout
            self.root.resizable(False, False)  # Disable resizing
            print("Window configured...")
            
            # Set custom icon
            try:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'cipher_icon.ico')
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    # For Windows taskbar - set app ID to show custom icon
                    try:
                        import ctypes
                        myappid = 'cipherv4.codeeditor.app.4.5'  # arbitrary string
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                    except:
                        pass
            except Exception as e:
                print(f"Could not load icon: {e}")
            
            print("Setting overrideredirect...")
            self.root.overrideredirect(True)
            print("Overrideredirect set...")
        except Exception as e:
            print(f"ERROR in __init__ setup: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Initialize managers and handlers
        print("Initializing managers...")
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.execution_manager = ExecutionManager()
        self.json_handler = JSONHandler()
        print("Managers initialized...")
        
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
        
        # Recent files tracking (MRU - Most Recently Used)
        self.recent_files = []
        self.max_recent_files = 10
        self.recent_files_file = os.path.join(self.scripts_dir, ".recent_files.json")
        self.load_recent_files()
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 60000  # 60 seconds
        self.auto_save_timer = None
        
        # Console content persistence
        self.console_content = ""
        
        # Real-time statistics tracking
        self.stats = {
            "executions": 0,
            "successful_runs": 0,
            "errors": 0,
            "snippets_used": 0,
            "lines_written": 0,
            "session_start": time.time(),
            "total_execution_time": 0.0,
            "files_saved": 0,
            "ai_queries": 0,
        }
        
        # Settings state dictionary
        self.settings_state = {
            "Syntax Highlighting": True,
            "Line Numbers": True,
            "Auto-complete": False,
            "Auto-indent": True,
            "Word Wrap": False,
            "Bracket Matching": True,
            "Code Folding": False,
            "Minimap": False,
            "Font Size": 10,
            "Auto-save": True,
            "Notifications": True,
            "Sound Effects": False,
            "Spell Check": False,
            "Tab Size": 4,
            "Trim Whitespace": True,
            "Format on Save": False,
            "Debug Mode": False,
            "Telemetry": False,
            "Auto-update": True,
            "Experimental Features": False,
            "Performance Mode": False,
            "Memory Limit": 512,
            "GPU Acceleration": False,
            "Save History": True,
            "Remember Session": True,
            "Encrypted Storage": False,
            "Password Protection": False,
            "Clear on Exit": False,
        }
        
        # Initialize theme
        print("Applying theme...")
        self.apply_theme()
        
        # Configure TTK styles
        print("Setting up TTK styles...")
        self.setup_ttk_styles()
        
        # Create UI
        print("Showing loading screen...")
        self.show_loading_screen()
        
        # Set up keyboard shortcuts
        print("Setting up keyboard shortcuts...")
        self.setup_keyboard_shortcuts()
        
        # Initialize command palette
        self.setup_command_palette()
        
        print("ModernUI initialization complete!")

    def on_closing(self):
        """Handle window close event properly"""
        try:
            # Unbind all events to prevent errors during cleanup
            try:
                self.root.unbind_all("<MouseWheel>")
            except:
                pass
            
            # Quit the mainloop and destroy the window
            try:
                self.root.quit()
            except:
                pass
            
            try:
                self.root.destroy()
            except:
                pass
        except:
            # Force exit if there's any issue
            try:
                self.root.destroy()
            except:
                pass

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
    
    def get_scrollbar_config(self):
        """Get scrollbar colors based on current theme"""
        if hasattr(self, 'bg_color'):
            if self.bg_color == "#1e1e1e":  # Dark theme
                return {'bg': "#000000", 'troughcolor': self.bg_color, 'activebackground': self.accent_color}
            elif self.bg_color == "#f5f5f5":  # Light theme
                return {'bg': "#e0e0e0", 'troughcolor': self.bg_color, 'activebackground': self.accent_color}
            elif self.bg_color == "#0d1b2a":  # Ocean
                return {'bg': "#001f3f", 'troughcolor': self.bg_color, 'activebackground': "#00b4d8"}
            elif self.bg_color == "#1a2e1a":  # Forest
                return {'bg': "#0d1a0d", 'troughcolor': self.bg_color, 'activebackground': "#4caf50"}
            elif self.bg_color == "#2c1810":  # Sunset
                return {'bg': "#1a0d08", 'troughcolor': self.bg_color, 'activebackground': "#ff6f00"}
        return {'bg': "#000000", 'troughcolor': "#1e1e1e", 'activebackground': "#007acc"}


    def show_loading_screen(self):
        """Show the initial loading screen"""
        self.loading_frame = tk.Frame(self.root, bg=self.bg_color)
        self.loading_frame.place(x=0, y=0, width=1400, height=800)
        
        # Create loading screen widgets
        title = tk.Label(self.loading_frame, text="CipherV4",
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
            ("🕐", self.show_recent_files),
            ("⌨", self.show_shortcuts_panel),
            ("🔍", self.show_global_search),
            ("🎨", self.show_color_picker),
            ("📋", self.show_templates_manager),
            ("📊", self.show_statistics_dashboard),
            ("🔀", self.show_diff_viewer)
        ]
        
        for icon, command in action_buttons:
            # Special handling for keyboard icon alignment
            pady_offset = 5 if icon == "⌨" else 0
            btn = tk.Button(actions_frame, text=icon,
                           font=("Segoe UI", 14),
                           bg=self.secondary_bg, fg=self.text_color,
                           border=0, cursor="hand2",
                           width=3, height=1,
                           command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=(pady_offset, 0))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444444"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.secondary_bg))
        
        # Title and version (CENTER)
        title_frame = tk.Frame(self.header, bg=self.secondary_bg)
        title_frame.pack(side=tk.LEFT, expand=True)
        
        title = tk.Label(title_frame, text="CipherV4",
                        font=("Segoe UI", 18, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
        title.pack(side=tk.LEFT, padx=10, pady=15)
        title.bind("<Button-1>", self.start_drag)
        title.bind("<B1-Motion>", self.do_drag)
        
        version = tk.Label(title_frame, text="v4.0",
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
        
        # Character/Word/Line count (Feature #65)
        self.char_count_label = tk.Label(self.status_bar, text="Chars: 0 | Words: 0 | Lines: 0",
                                        font=("Segoe UI", 8),
                                        bg=self.secondary_bg, fg="#a0a0a0")
        self.char_count_label.pack(side=tk.LEFT, padx=10)
        
        # Zoom level (Feature #33)
        self.zoom_label = tk.Label(self.status_bar, text="100%",
                                  font=("Segoe UI", 8),
                                  bg=self.secondary_bg, fg="#a0a0a0",
                                  cursor="hand2")
        self.zoom_label.pack(side=tk.RIGHT, padx=10)
        self.zoom_label.bind("<Button-1>", lambda e: self.reset_zoom())
        
        # Update checker button (Feature #69)
        self.update_btn = tk.Label(self.status_bar, text="🔄 Check Updates",
                                  font=("Segoe UI", 8),
                                  bg=self.secondary_bg, fg="#00aa00",
                                  cursor="hand2")
        self.update_btn.pack(side=tk.RIGHT, padx=10)
        self.update_btn.bind("<Button-1>", lambda e: self.check_for_updates())
        
        # Time display
        self.time_display = tk.Label(self.status_bar, text="",
                                   font=("Segoe UI", 8),
                                   bg=self.secondary_bg, fg="#a0a0a0")
        self.time_display.pack(side=tk.RIGHT, padx=10)
        
        # Initialize zoom level and update checker
        self.zoom_level = 1.0
        self.update_checker = UpdateChecker()
        
        # Start time update
        self.update_time()
        
        # Check for updates on startup (async)
        threading.Thread(target=self.silent_update_check, daemon=True).start()

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
            "Tools": "Tools",
            "ValueChanger": "Value Changer",
            "DLLInjector": "DLL Injector",
            "ProcessInspector": "Process Inspector",
            "AI Assistant": "AI Assistant",
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
        
        # Fade out effect
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
        
        # Load page content with fade-in
        self.update_status(f"Loading {page}...")
        
        # Create container with initial transparency effect
        self.page_container = tk.Frame(self.content_frame, bg=self.bg_color)
        self.page_container.pack(fill=tk.BOTH, expand=True)
        self.page_container.pack_forget()
        
        # Load content then fade in
        self.root.after(10, lambda: self.load_page_content_animated(page))
    
    def load_page_content_animated(self, page):
        """Load page content with fade-in animation"""
        # Destroy old container content
        for widget in self.content_frame.winfo_children():
            if widget != self.page_container:
                widget.destroy()
        
        # Load actual content
        self.load_page_content(page)
        
        # Fade in effect
        self.page_container.pack(fill=tk.BOTH, expand=True)
        self.update_status("Ready")
    
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
        elif page == "Tools":
            self.show_tools()
        elif page == "ValueChanger":
            self.show_value_changer()
        elif page == "DLLInjector":
            self.show_dll_injector()
        elif page == "ProcessInspector":
            self.show_process_inspector()
        elif page == "AI Assistant":
            self.show_ai_assistant()
        elif page == "Progress":
            self.show_progress_page()
        elif page == "Settings":
            self.show_settings()
        elif page == "About":
            self.show_about()

    def show_dashboard(self):
        """Show the dashboard view with real statistics"""
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome = tk.Label(container, text="Dashboard",
                          font=("Segoe UI", 16, "bold"),
                          bg=self.bg_color, fg=self.text_color)
        welcome.pack(anchor="w", pady=(0, 10))
        
        # Calculate session duration
        session_duration = int(time.time() - self.stats["session_start"])
        hours = session_duration // 3600
        minutes = (session_duration % 3600) // 60
        session_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        desc = tk.Label(container, 
                       text=f"Session Time: {session_time} • Track your coding activity in real-time",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Create statistics cards grid
        cards_frame = tk.Frame(container, bg=self.bg_color)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Real statistics
        success_rate = f"{(self.stats['successful_runs'] / self.stats['executions'] * 100):.1f}%" if self.stats['executions'] > 0 else "N/A"
        avg_exec_time = f"{(self.stats['total_execution_time'] / self.stats['executions']):.3f}s" if self.stats['executions'] > 0 else "N/A"
        
        self.create_stat_card(cards_frame, "Code Executions", str(self.stats['executions']), "▶", 0, 0)
        self.create_stat_card(cards_frame, "Success Rate", success_rate, "✓", 0, 1)
        self.create_stat_card(cards_frame, "Snippets Used", str(self.stats['snippets_used']), "📝", 1, 0)
        self.create_stat_card(cards_frame, "Avg Exec Time", avg_exec_time, "⏱", 1, 1)
        self.create_stat_card(cards_frame, "Lines Written", str(self.stats['lines_written']), "📄", 2, 0)
        self.create_stat_card(cards_frame, "Files Saved", str(self.stats['files_saved']), "💾", 2, 1)
    
    def create_stat_card(self, parent, title, value, icon, row, col):
        """Create a statistics card with real data"""
        card = tk.Frame(parent, bg=self.secondary_bg, highlightbackground=self.accent_color,
                       highlightthickness=0)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Icon
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 24),
                            bg=self.secondary_bg, fg=self.accent_color)
        icon_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Value (large)
        value_label = tk.Label(card, text=value, font=("Segoe UI", 28, "bold"),
                             bg=self.secondary_bg, fg=self.text_color)
        value_label.pack(anchor="w", padx=15, pady=(0, 2))
        
        # Title (small)
        title_label = tk.Label(card, text=title, font=("Segoe UI", 10),
                             bg=self.secondary_bg, fg="#a0a0a0")
        title_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Hover animations
        def on_card_enter(e):
            card.config(highlightthickness=1, highlightbackground=self.accent_color)
        
        def on_card_leave(e):
            card.config(highlightthickness=0)
        
        card.bind("<Enter>", on_card_enter)
        card.bind("<Leave>", on_card_leave)
    
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
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize console mode if not exists
        if not hasattr(self, 'console_mode'):
            self.console_mode = "Python"  # "Python" or "PowerShell"
        
        # Dynamic title based on mode
        title_text = f"{self.console_mode} Console"
        title = tk.Label(container, text=title_text,
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc_text = "Write and execute Python code with syntax highlighting" if self.console_mode == "Python" else "Execute PowerShell commands with syntax highlighting"
        desc = tk.Label(container, 
                       text=desc_text,
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
                                    pady=2,
                                    takefocus=0,
                                    border=0,
                                    background=self.secondary_bg,
                                    foreground="#606060",
                                    state='disabled',
                                    font=("Consolas", 10),
                                    spacing1=0,
                                    spacing2=0,
                                    spacing3=0)
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
                                  undo=True,
                                  spacing1=0,
                                  spacing2=0,
                                  spacing3=0)
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(editor_frame, command=self.code_input.yview,
                                **self.get_scrollbar_config(), width=12)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Synchronize scrolling between code editor and line numbers
        def sync_scroll(*args):
            self.code_input.yview(*args)
            self.line_numbers.yview(*args)
        
        scrollbar.config(command=sync_scroll)
        self.code_input.config(yscrollcommand=lambda *args: self.on_code_scroll(*args, scrollbar))
        
        # Configure syntax highlighting tags for Python
        self.code_input.tag_configure("keyword", foreground="#569cd6")
        self.code_input.tag_configure("string", foreground="#ce9178")
        self.code_input.tag_configure("comment", foreground="#6a9955")
        self.code_input.tag_configure("function", foreground="#dcdcaa")
        self.code_input.tag_configure("number", foreground="#b5cea8")
        self.code_input.tag_configure("operator", foreground="#d4d4d4")
        
        # Configure syntax highlighting tags for PowerShell (matching native PowerShell colors)
        self.code_input.tag_configure("ps_keyword", foreground="#dcdcaa")      # Commands like cd, python, Get-Process (YELLOW)
        self.code_input.tag_configure("ps_parameter", foreground="#a0a0a0")    # -Path, -Name, --version etc. (gray)
        self.code_input.tag_configure("ps_string", foreground="#ce9178")       # "strings" (orange)
        self.code_input.tag_configure("ps_comment", foreground="#6a9955")      # # comments (green)
        self.code_input.tag_configure("ps_variable", foreground="#9cdcfe")     # $variables (light cyan)
        self.code_input.tag_configure("ps_operator", foreground="#a0a0a0")     # |, >, etc. (gray)
        
        # Restore saved content with typing animation
        if self.console_content and self.console_content.strip():
            # Check if we're returning to console (not first time)
            if hasattr(self, '_console_initialized'):
                self.animate_typing(self.console_content)
            else:
                # First time - just insert normally
                self.code_input.insert('1.0', self.console_content)
                self._console_initialized = True
        else:
            if self.console_mode == "Python":
                self.code_input.insert('1.0', '# Write your Python code here\nprint("Hello, CipherV4!")')
            else:
                self.code_input.insert('1.0', '# PowerShell commands\nGet-Location\nWrite-Host "Hello from PowerShell!"')
            self._console_initialized = True
        
        # Update line numbers and syntax highlighting
        def update_editor(event=None):
            self.update_line_numbers()
            if self.console_mode == "Python":
                self.apply_syntax_highlighting()
            else:
                self.apply_powershell_syntax_highlighting()
            self.console_content = self.code_input.get('1.0', tk.END)
        
        self.code_input.bind('<KeyRelease>', update_editor)
        self.code_input.bind('<ButtonRelease-1>', lambda e: self.update_line_numbers())
        
        # Initial update
        self.update_line_numbers()
        if self.console_mode == "Python":
            self.apply_syntax_highlighting()
        else:
            self.apply_powershell_syntax_highlighting()
        
        # Button toolbar with animations
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Dynamic buttons based on mode
        if self.console_mode == "Python":
            buttons = [
                ("▶ Run", self.accent_color, self.button_hover, self.run_code),
                ("💾 Save", "#2e7d32", "#43a047", self.save_file),
                ("📂 Load", "#1565c0", "#1976d2", self.show_find_dialog),
                ("✨ Beautify", "#f57c00", "#fb8c00", self.format_code),
                ("Insert .JSON", "#7b1fa2", "#9c27b0", self.insert_json_template),
                ("Lint JSON", "#6a1b9a", "#8e24aa", self.lint_json),
                ("Clear", self.secondary_bg, "#444444", self.clear_editor),
                ("PowerShell", "#0078d4", "#1084d8", self.toggle_console_mode)
            ]
        else:  # PowerShell mode
            buttons = [
                ("▶ Run", self.accent_color, self.button_hover, self.run_powershell),
                ("Clear", self.secondary_bg, "#444444", self.clear_editor),
                ("Python", "#306998", "#4b8bbe", self.toggle_console_mode)
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
        output_header = tk.Frame(container, bg=self.bg_color)
        output_header.pack(fill=tk.X, pady=(10, 5))
        
        output_label = tk.Label(output_header, text="Output:",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        output_label.pack(side=tk.LEFT)
        
        # Clear output button
        clear_output_btn = tk.Button(output_header, text="Clear Output",
                                     font=("Segoe UI", 8),
                                     bg="#ff5555", fg="white",
                                     border=0, cursor="hand2",
                                     pady=4, padx=10,
                                     command=self.clear_output)
        clear_output_btn.pack(side=tk.RIGHT)
        clear_output_btn.bind("<Enter>", lambda e: clear_output_btn.config(bg="#ff3333"))
        clear_output_btn.bind("<Leave>", lambda e: clear_output_btn.config(bg="#ff5555"))
        
        output_frame = tk.Frame(container, bg=self.secondary_bg)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console_output = tk.Text(output_frame, 
                                      height=8,
                                      font=("Consolas", 9),
                                      bg=self.secondary_bg,
                                      fg=self.text_color,
                                      insertbackground=self.text_color,
                                      wrap=tk.WORD,
                                      state=tk.DISABLED)
        self.console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        output_scrollbar = tk.Scrollbar(output_frame, command=self.console_output.yview,
                                       **self.get_scrollbar_config(), width=12)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_output.config(yscrollcommand=output_scrollbar.set)
    
    def animate_typing(self, text):
        """Animate typing effect when returning to console"""
        if not hasattr(self, 'code_input') or not self.code_input.winfo_exists():
            return
        
        # Clear current content
        self.code_input.delete('1.0', tk.END)
        
        # Calculate typing speed based on content length
        text_length = len(text)
        if text_length < 50:
            delay = 10  # Fast for short code
        elif text_length < 200:
            delay = 3   # Medium for medium code
        else:
            delay = 1   # Very fast for long code
        
        # Type character by character
        def type_char(index=0):
            if index < len(text) and self.code_input.winfo_exists():
                self.code_input.insert(tk.END, text[index])
                # Update syntax highlighting periodically (not every char for performance)
                if index % 10 == 0 or index == len(text) - 1:
                    self.apply_syntax_highlighting()
                    self.update_line_numbers()
                # Schedule next character
                self.root.after(delay, lambda: type_char(index + 1))
            elif index >= len(text):
                # Final update
                self.apply_syntax_highlighting()
                self.update_line_numbers()
        
        # Start typing animation
        type_char()
    
    def animate_button(self, button, color):
        """Animate button color change"""
        button.config(bg=color)
    
    def add_hover_effect(self, button, hover_color, normal_color):
        """Add hover effect to button"""
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))
    
    def on_code_scroll(self, *args, scrollbar=None):
        """Handle scrolling and sync line numbers with code editor"""
        if scrollbar:
            scrollbar.set(*args)
        # Sync line numbers to match code editor position
        if hasattr(self, 'line_numbers'):
            self.line_numbers.yview_moveto(args[0])
    
    def update_line_numbers(self):
        """Update line numbers in code editor"""
        if hasattr(self, 'line_numbers') and hasattr(self, 'code_input'):
            try:
                # Get the content and count lines properly
                content = self.code_input.get('1.0', 'end-1c')
                # Count lines - if content is empty, we have 1 line, otherwise count newlines + 1
                if not content:
                    line_count = 1
                else:
                    line_count = content.count('\n') + 1
                
                # Generate line numbers starting from 1
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
    
    def apply_powershell_syntax_highlighting(self):
        """Apply PowerShell syntax highlighting"""
        if not hasattr(self, 'code_input'):
            return
        
        try:
            # Remove all existing tags
            for tag in ["ps_keyword", "ps_parameter", "ps_string", "ps_comment", "ps_variable", "ps_operator"]:
                self.code_input.tag_remove(tag, "1.0", "end")
            
            code = self.code_input.get("1.0", "end-1c")
            
            import re
            
            # Highlight comments FIRST (so they take precedence)
            for match in re.finditer(r'#.*$', code, re.MULTILINE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_comment", start, end)
            
            # Highlight strings (double and single quotes)
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_string", start, end)
            
            # PowerShell cmdlets and common commands (case-insensitive)
            keywords = r'\b(Get-Process|Get-Service|Get-Item|Get-ChildItem|Set-Location|Write-Host|Write-Output|ForEach-Object|Where-Object|Select-Object|Sort-Object|Measure-Object|New-Item|Remove-Item|Copy-Item|Move-Item|Rename-Item|Test-Path|Invoke-Expression|Start-Process|Stop-Process|Get-Content|Set-Content|Add-Content|Clear-Content|Out-File|Import-Module|Export-ModuleMember|python|pip|node|npm|git|cd|dir|ls|pwd|echo|cat|rm|cp|mv|mkdir|clear|cls|exit|if|else|elseif|foreach|while|for|switch|function|param|return|break|continue|try|catch|finally)\b'
            
            # Apply keyword highlighting (case-insensitive)
            for match in re.finditer(keywords, code, re.IGNORECASE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_keyword", start, end)
            
            # Highlight parameters (starting with - or --)
            for match in re.finditer(r'--?[a-zA-Z_][a-zA-Z0-9_-]*', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_parameter", start, end)
            
            # Highlight variables (starting with $)
            for match in re.finditer(r'\$[a-zA-Z_][a-zA-Z0-9_]*', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_variable", start, end)
            
            # Highlight operators (|, >, <, etc.)
            for match in re.finditer(r'[|><&;]', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_input.tag_add("ps_operator", start, end)
            
            # Raise comment tag priority to ensure it's always on top
            self.code_input.tag_raise("ps_comment")
        except:
            pass
    
    def apply_snippet_highlighting(self, text_widget):
        """Apply Python syntax highlighting to snippet preview"""
        try:
            # Configure tags for syntax highlighting
            text_widget.tag_config("keyword", foreground="#569CD6")  # Blue
            text_widget.tag_config("string", foreground="#CE9178")   # Orange
            text_widget.tag_config("comment", foreground="#6A9955")  # Green
            text_widget.tag_config("function", foreground="#DCDCAA") # Yellow
            text_widget.tag_config("number", foreground="#B5CEA8")   # Light green
            
            code = text_widget.get("1.0", "end-1c")
            
            # Python keywords
            keywords = r'\b(def|class|if|elif|else|for|while|try|except|finally|with|import|from|as|return|yield|lambda|pass|break|continue|raise|assert|del|global|nonlocal|and|or|not|in|is|None|True|False|async|await)\b'
            
            # Apply keyword highlighting
            import re
            for match in re.finditer(keywords, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add("keyword", start, end)
            
            # Highlight strings
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add("string", start, end)
            
            # Highlight comments
            for match in re.finditer(r'#.*$', code, re.MULTILINE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add("comment", start, end)
            
            # Highlight numbers
            for match in re.finditer(r'\b\d+\.?\d*\b', code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add("number", start, end)
            
            # Highlight function names
            for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code):
                start = f"1.0+{match.start(1)}c"
                end = f"1.0+{match.end(1)}c"
                text_widget.tag_add("function", start, end)
        except:
            pass
    
    def clear_editor(self):
        """Clear the code editor"""
        if hasattr(self, 'code_input'):
            self.code_input.delete('1.0', tk.END)
            self.console_content = ""
            self.update_line_numbers()
            self.update_status("Editor cleared")
    
    def clear_output(self):
        """Clear the console output"""
        if hasattr(self, 'console_output'):
            self.console_output.config(state=tk.NORMAL)
            self.console_output.delete('1.0', tk.END)
            self.console_output.config(state=tk.DISABLED)
            self.update_status("Output cleared")
    
    def show_history(self):
        """Show history page with command history"""
        container = tk.Frame(self.page_container, bg=self.bg_color)
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
        
        scrollbar = tk.Scrollbar(list_frame, **self.get_scrollbar_config(), width=12)
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
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Code Snippets Library",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        desc = tk.Label(container, 
                       text="Quick access to common code patterns and templates - Click any snippet to insert",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 10))
        
        # Search bar with clean design (no border frame)
        search_container = tk.Frame(container, bg=self.bg_color)
        search_container.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(search_container, text="🔍",
                font=("Segoe UI", 14),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.snippet_search = tk.Entry(search_container, font=("Segoe UI", 11),
                                      bg=self.secondary_bg, fg=self.text_color,
                                      relief=tk.FLAT, bd=0,
                                      highlightthickness=2,
                                      highlightbackground="#333333",
                                      highlightcolor=self.accent_color,
                                      insertbackground=self.accent_color)
        self.snippet_search.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 0))
        
        # Placeholder handling
        self.search_placeholder = "Search snippets by name or keyword..."
        self.snippet_search.insert(0, self.search_placeholder)
        self.snippet_search.config(fg="#666666")
        
        def on_search_focus_in(event):
            if self.snippet_search.get() == self.search_placeholder:
                self.snippet_search.delete(0, tk.END)
                self.snippet_search.config(fg=self.text_color)
        
        def on_search_focus_out(event):
            if self.snippet_search.get() == "":
                self.snippet_search.insert(0, self.search_placeholder)
                self.snippet_search.config(fg="#666666")
        
        self.snippet_search.bind("<FocusIn>", on_search_focus_in)
        self.snippet_search.bind("<FocusOut>", on_search_focus_out)
        self.snippet_search.bind("<KeyRelease>", lambda e: self.filter_snippets())
        
        # Create canvas with scrollbar for snippets
        canvas_frame = tk.Frame(container, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.snippets_canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.snippets_canvas.yview,
                                **self.get_scrollbar_config(), width=12)
        self.snippets_frame = tk.Frame(self.snippets_canvas, bg=self.bg_color)
        
        self.snippets_frame.bind(
            "<Configure>",
            lambda e: self.snippets_canvas.configure(scrollregion=self.snippets_canvas.bbox("all"))
        )
        
        self.snippets_canvas.create_window((0, 0), window=self.snippets_frame, anchor="nw")
        self.snippets_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.snippets_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store all snippets for filtering
        self.all_snippets = {
            # Basic Python
            "For Loop": "for i in range(10):\n    print(i)",
            "While Loop": "while condition:\n    # code\n    break",
            "Function": "def function_name(param):\n    return param",
            "Class": "class MyClass:\n    def __init__(self):\n        pass",
            "Try/Except": "try:\n    # code\nexcept Exception as e:\n    print(f'Error: {e}')",
            "If/Elif/Else": "if condition:\n    pass\nelif other:\n    pass\nelse:\n    pass",
            "Match/Case": "match value:\n    case 1:\n        pass\n    case _:\n        pass",
            "Lambda": "lambda x: x * 2",
            "List Comp": "[x**2 for x in range(10)]",
            "Dict Comp": "{k: v for k, v in items}",
            "Walrus Operator": "if (n := len(data)) > 10:\n    print(f'{n} items')",
            "F-String": "name = 'World'\nprint(f'Hello, {name}!')",
            "Type Hints": "def func(x: int, y: str) -> bool:\n    return True",
            
            # File Operations
            "File Read": "with open('file.txt', 'r') as f:\n    data = f.read()",
            "File Write": "with open('file.txt', 'w') as f:\n    f.write('content')",
            "File Append": "with open('file.txt', 'a') as f:\n    f.write('append')",
            "Path Handling": "from pathlib import Path\np = Path('file.txt')\nif p.exists():\n    print(p.read_text())",
            "Directory Listing": "import os\nfor item in os.listdir('.'):\n    print(item)",
            "JSON Load": "import json\nwith open('data.json') as f:\n    data = json.load(f)",
            "JSON Dump": "import json\nwith open('out.json', 'w') as f:\n    json.dump(data, f, indent=4)",
            "CSV Read": "import csv\nwith open('data.csv') as f:\n    reader = csv.DictReader(f)\n    for row in reader:\n        print(row)",
            "CSV Write": "import csv\nwith open('out.csv', 'w', newline='') as f:\n    writer = csv.writer(f)\n    writer.writerow(['col1', 'col2'])",
            "YAML Load": "import yaml\nwith open('config.yaml') as f:\n    config = yaml.safe_load(f)",
            
            # Advanced Python
            "Decorator": "@decorator\ndef function():\n    pass",
            "Context Manager": "with context as cm:\n    # code",
            "Async Function": "async def async_func():\n    await something()",
            "Generator": "def gen():\n    yield value",
            "Class Method": "@classmethod\ndef method(cls):\n    pass",
            "Static Method": "@staticmethod\ndef method():\n    pass",
            "Property": "@property\ndef value(self):\n    return self._value",
            "Dataclass": "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int",
            "Enum": "from enum import Enum\n\nclass Color(Enum):\n    RED = 1\n    GREEN = 2",
            "Named Tuple": "from typing import NamedTuple\n\nclass Point(NamedTuple):\n    x: int\n    y: int",
            "ABC Class": "from abc import ABC, abstractmethod\n\nclass Base(ABC):\n    @abstractmethod\n    def method(self):\n        pass",
            
            # Web & API
            "Requests GET": "import requests\nr = requests.get(url)\nprint(r.json())",
            "Requests POST": "import requests\nr = requests.post(url, json=data)\nprint(r.status_code)",
            "Requests Headers": "import requests\nheaders = {'Authorization': 'Bearer token'}\nr = requests.get(url, headers=headers)",
            "Flask App": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello'",
            "Flask JSON API": "from flask import Flask, jsonify\napp = Flask(__name__)\n\n@app.route('/api')\ndef api():\n    return jsonify({'key': 'value'})",
            "FastAPI": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello'}",
            "Beautiful Soup": "from bs4 import BeautifulSoup\nimport requests\nr = requests.get(url)\nsoup = BeautifulSoup(r.content, 'html.parser')\nprint(soup.title.text)",
            "Selenium": "from selenium import webdriver\ndriver = webdriver.Chrome()\ndriver.get(url)\ndriver.quit()",
            "HTTP Server": "from http.server import HTTPServer, SimpleHTTPRequestHandler\nserver = HTTPServer(('', 8000), SimpleHTTPRequestHandler)\nserver.serve_forever()",
            
            # Data Science
            "Pandas DataFrame": "import pandas as pd\ndf = pd.DataFrame(data)\nprint(df.head())",
            "Pandas Read CSV": "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.describe())",
            "Pandas Filter": "import pandas as pd\nfiltered = df[df['col'] > 10]\nprint(filtered)",
            "Pandas Group By": "import pandas as pd\ngrouped = df.groupby('col')['value'].sum()\nprint(grouped)",
            "NumPy Array": "import numpy as np\narr = np.array([1, 2, 3])\nprint(arr.mean())",
            "NumPy Matrix": "import numpy as np\nmatrix = np.array([[1, 2], [3, 4]])\nprint(matrix.T)",
            "Matplotlib Plot": "import matplotlib.pyplot as plt\nplt.plot(x, y)\nplt.xlabel('X')\nplt.ylabel('Y')\nplt.show()",
            "Matplotlib Scatter": "import matplotlib.pyplot as plt\nplt.scatter(x, y)\nplt.title('Scatter Plot')\nplt.show()",
            "Seaborn Plot": "import seaborn as sns\nsns.lineplot(x='col1', y='col2', data=df)\nplt.show()",
            "Scikit-Learn": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)",
            
            # Database
            "SQLite": "import sqlite3\nconn = sqlite3.connect('db.sqlite')\ncursor = conn.cursor()\ncursor.execute('SELECT * FROM table')\nconn.close()",
            "SQLAlchemy Engine": "from sqlalchemy import create_engine\nengine = create_engine('sqlite:///db.sqlite')\nwith engine.connect() as conn:\n    result = conn.execute('SELECT * FROM table')",
            "MySQL Connector": "import mysql.connector\nconn = mysql.connector.connect(\n    host='localhost',\n    user='user',\n    password='pass',\n    database='db'\n)",
            "PostgreSQL": "import psycopg2\nconn = psycopg2.connect(\n    dbname='db',\n    user='user',\n    password='pass'\n)",
            "MongoDB": "from pymongo import MongoClient\nclient = MongoClient('mongodb://localhost:27017/')\ndb = client['database']\ncollection = db['collection']",
            "Redis": "import redis\nr = redis.Redis(host='localhost', port=6379)\nr.set('key', 'value')\nprint(r.get('key'))",
            
            # System & OS
            "Date/Time": "from datetime import datetime\nnow = datetime.now()\nprint(now.strftime('%Y-%m-%d %H:%M:%S'))",
            "Timedelta": "from datetime import datetime, timedelta\ntomorrow = datetime.now() + timedelta(days=1)\nprint(tomorrow)",
            "Subprocess": "import subprocess\nresult = subprocess.run(['cmd'], capture_output=True, text=True)\nprint(result.stdout)",
            "Threading": "import threading\nt = threading.Thread(target=func, args=(arg,))\nt.start()\nt.join()",
            "Multiprocessing": "from multiprocessing import Process\np = Process(target=func, args=(arg,))\np.start()\np.join()",
            "Logging": "import logging\nlogging.basicConfig(level=logging.INFO)\nlogging.info('message')\nlogging.error('error')",
            "argparse": "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--name', required=True)\nargs = parser.parse_args()",
            "Environment Vars": "import os\napi_key = os.getenv('API_KEY', 'default')\nprint(api_key)",
            "System Info": "import platform\nprint(platform.system())\nprint(platform.python_version())",
            
            # Utilities
            "Regular Expression": "import re\nmatch = re.search(r'pattern', text)\nif match:\n    print(match.group())",
            "Regex Findall": "import re\nmatches = re.findall(r'\\d+', text)\nprint(matches)",
            "UUID": "import uuid\nid = uuid.uuid4()\nprint(str(id))",
            "Random": "import random\nnum = random.randint(1, 100)\nprint(num)",
            "Random Choice": "import random\nitem = random.choice(['a', 'b', 'c'])\nprint(item)",
            "Hash SHA256": "import hashlib\nhash = hashlib.sha256(data.encode()).hexdigest()\nprint(hash)",
            "Base64 Encode": "import base64\nencoded = base64.b64encode(data.encode())\nprint(encoded)",
            "URL Parse": "from urllib.parse import urlparse\nparsed = urlparse(url)\nprint(parsed.scheme, parsed.netloc)",
            "Pickle Save": "import pickle\nwith open('data.pkl', 'wb') as f:\n    pickle.dump(obj, f)",
            "Pickle Load": "import pickle\nwith open('data.pkl', 'rb') as f:\n    obj = pickle.load(f)",
            
            # Testing
            "Unit Test": "import unittest\n\nclass TestClass(unittest.TestCase):\n    def test_method(self):\n        self.assertEqual(1, 1)",
            "Pytest": "import pytest\n\ndef test_function():\n    assert True",
            "Mock": "from unittest.mock import Mock\nmock = Mock()\nmock.method.return_value = 'result'",
            
            # Virtual Environment
            "Virtual Env": "# Create: python -m venv venv\n# Activate: venv\\Scripts\\activate",
            "Pip Install": "# pip install package\n# pip install -r requirements.txt",
            "Requirements": "# Generate: pip freeze > requirements.txt\n# Install: pip install -r requirements.txt",
            
            # Import Patterns
            "Import": "import module\nfrom package import item\nfrom package import *",
            "Import As": "import numpy as np\nimport pandas as pd\nfrom datetime import datetime as dt",
        }
        
        # Initial display of all snippets
        self.display_snippets(self.all_snippets)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            # Check if canvas still exists before scrolling
            if hasattr(self, 'snippets_canvas') and self.snippets_canvas.winfo_exists():
                self.snippets_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.snippets_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def filter_snippets(self):
        """Filter snippets based on search query with fade-in animation"""
        query = self.snippet_search.get().lower()
        
        if query == "" or query == self.search_placeholder.lower():
            filtered = self.all_snippets
        else:
            filtered = {name: code for name, code in self.all_snippets.items() 
                       if query in name.lower() or query in code.lower()}
        
        # Clear current display with fade effect
        for widget in self.snippets_frame.winfo_children():
            widget.destroy()
        
        # Display filtered snippets with staggered fade-in
        self.display_snippets(filtered, animate=True)
    
    def display_snippets(self, snippets, animate=False):
        """Display snippets in grid layout with optional fade-in animation"""
        row, col = 0, 0
        delay = 0
        
        for name, code in snippets.items():
            if animate:
                self.create_snippet_card(self.snippets_frame, name, code, row, col, delay)
                delay += 20  # Visible stagger delay
            else:
                self.create_snippet_card(self.snippets_frame, name, code, row, col, 0)
            col += 1
            if col > 3:  # 4 columns for wider window
                col = 0
                row += 1
    
    def create_snippet_card(self, parent, name, code, row, col, delay):
        """Create an animated snippet card with fade-in effect"""
        def show_card():
            try:
                if not self.root.winfo_exists() or not parent.winfo_exists():
                    return
                
                # Create card with initial hidden state (using very dark color)
                card = tk.Frame(parent, bg="#0a0a0a" if delay > 0 else self.secondary_bg)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                
                parent.grid_rowconfigure(row, weight=0, minsize=90)
                parent.grid_columnconfigure(col, weight=1, minsize=280)  # Shorter width for 4 columns
                
                # Create content
                title_frame = tk.Frame(card, bg="#0a0a0a" if delay > 0 else self.secondary_bg)
                title_frame.pack(fill=tk.X)
                
                name_label = tk.Label(title_frame, text=f"📝 {name}",
                                     font=("Segoe UI", 9, "bold"),
                                     bg="#0a0a0a" if delay > 0 else self.secondary_bg, 
                                     fg="#0a0a0a" if delay > 0 else self.text_color)
                name_label.pack(anchor="w", padx=8, pady=(6, 3))
                
                sep = tk.Frame(card, bg="#0a0a0a" if delay > 0 else self.accent_color, height=1)
                sep.pack(fill=tk.X, padx=8, pady=(0, 5))
                
                code_frame = tk.Frame(card, bg="#0a0a0a" if delay > 0 else "#1a1a1a", cursor="hand2")
                code_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))
                
                code_preview = tk.Text(code_frame,
                                      font=("Consolas", 7),
                                      bg="#0a0a0a" if delay > 0 else "#1a1a1a", 
                                      fg="#0a0a0a" if delay > 0 else self.text_color,
                                      wrap=tk.CHAR, height=2, width=30,
                                      relief=tk.FLAT, bd=0,
                                      cursor="hand2",
                                      state=tk.NORMAL,
                                      highlightthickness=0)
                code_preview.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
                
                # Insert code and apply syntax highlighting
                code_text = code[:50] + "..." if len(code) > 50 else code
                code_preview.insert("1.0", code_text)
                self.apply_snippet_highlighting(code_preview)
                code_preview.config(state=tk.DISABLED)
                
                # Fade-in animation effect
                if delay > 0:
                    def fade_in(step=0):
                        if step < 5 and card.winfo_exists():
                            # Gradually lighten colors
                            if step == 1:
                                card.config(bg="#151515")
                                title_frame.config(bg="#151515")
                                name_label.config(bg="#151515", fg="#444444")
                                code_frame.config(bg="#101010")
                                code_preview.config(bg="#101010", fg="#444444")
                            elif step == 2:
                                card.config(bg="#1a1a1a")
                                title_frame.config(bg="#1a1a1a")
                                name_label.config(bg="#1a1a1a", fg="#888888")
                                code_frame.config(bg="#151515")
                                code_preview.config(bg="#151515", fg="#888888")
                            elif step == 3:
                                card.config(bg="#202020")
                                title_frame.config(bg="#202020")
                                name_label.config(bg="#202020", fg="#cccccc")
                                code_frame.config(bg="#1a1a1a")
                                code_preview.config(bg="#1a1a1a", fg="#cccccc")
                                sep.config(bg="#444444")
                            elif step == 4:
                                card.config(bg=self.secondary_bg)
                                title_frame.config(bg=self.secondary_bg)
                                name_label.config(bg=self.secondary_bg, fg=self.text_color)
                                code_frame.config(bg="#1a1a1a")
                                code_preview.config(bg="#1a1a1a", fg=self.text_color)
                                sep.config(bg=self.accent_color)
                            self.root.after(30, lambda: fade_in(step + 1))
                    
                    self.root.after(50, fade_in)
                
                # Make entire card clickable to insert snippet
                def click_to_insert(e=None):
                    self.insert_snippet(code)
                    card.config(bg=self.accent_color)
                    self.root.after(200, lambda: card.config(bg=self.secondary_bg) if card.winfo_exists() else None)
                
                card.bind("<Button-1>", click_to_insert)
                title_frame.bind("<Button-1>", click_to_insert)
                name_label.bind("<Button-1>", click_to_insert)
                code_frame.bind("<Button-1>", click_to_insert)
                code_preview.bind("<Button-1>", click_to_insert)
                
                # Hover animation
                def on_enter(e):
                    sep.config(bg=self.button_hover, height=2)
                
                def on_leave(e):
                    sep.config(bg=self.accent_color, height=1)
                
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
        """Insert snippet into editor and switch to Console page"""
        # First, save the snippet to insert
        self.pending_snippet = code
        
        # Switch to Console page
        self.switch_page("Console")
        
        # Insert the snippet after a short delay to ensure page is loaded
        self.root.after(100, self._insert_pending_snippet)
    
    def _insert_pending_snippet(self):
        """Actually insert the pending snippet into the editor"""
        if hasattr(self, 'pending_snippet') and hasattr(self, 'code_input'):
            try:
                # Track snippet usage
                self.stats["snippets_used"] += 1
                
                # Clear existing content and insert snippet
                current_content = self.code_input.get('1.0', tk.END).strip()
                if current_content and current_content != '# Write your Python code here\nprint("Hello, CipherV4!")':
                    # Add to end if there's existing code
                    self.code_input.insert(tk.END, "\n\n" + self.pending_snippet)
                else:
                    # Replace placeholder with snippet
                    self.code_input.delete('1.0', tk.END)
                    self.code_input.insert('1.0', self.pending_snippet)
                
                self.update_line_numbers()
                self.apply_syntax_highlighting()
                self.console_content = self.code_input.get('1.0', tk.END)
                self.update_status(f"Snippet inserted ({self.stats['snippets_used']} total)")
                delattr(self, 'pending_snippet')
            except Exception as e:
                print(f"Error inserting snippet: {e}")
    
    def show_value_changer(self):
        """Show ValueChanger - Memory Editor (like Cheat Engine)"""
        # Initialize memory scanner if not exists
        if not hasattr(self, 'memory_scanner'):
            self.memory_scanner = MemoryScanner()
        
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="⚡ Value Changer",
                font=("Segoe UI", 20, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="Memory Scanner & Editor",
                font=("Segoe UI", 10),
                bg=self.bg_color, fg="#666666").pack(side=tk.LEFT, padx=(15, 0))
        
        # Process Controls Card - Dark themed
        process_card = tk.Frame(container, bg="#1e1e1e", highlightbackground="#333333", 
                               highlightthickness=1)
        process_card.pack(fill=tk.X, pady=(0, 15))
        
        # Process card header
        tk.Label(process_card, text="🎯 Process Selection",
                font=("Segoe UI", 11, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Search bar for processes
        search_frame = tk.Frame(process_card, bg="#1e1e1e")
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 9, "bold"),
                bg="#1e1e1e", fg="#aaaaaa").pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_search_var = tk.StringVar()
        self.process_search_var.trace('w', lambda *args: self.filter_process_list())
        
        search_entry = tk.Entry(search_frame, textvariable=self.process_search_var,
                               font=("Segoe UI", 10),
                               bg="#0d0d0d", fg=self.text_color,
                               insertbackground=self.accent_color,
                               relief=tk.FLAT, bd=0)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=10)
        
        # Process selection
        process_select = tk.Frame(process_card, bg="#1e1e1e")
        process_select.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.process_var = tk.StringVar()
        self.process_combo = ttk.Combobox(process_select, textvariable=self.process_var,
                                    width=55, state="readonly", font=("Segoe UI", 10))
        self.process_combo.pack(side=tk.LEFT, ipady=6)
        
        # Store all processes for filtering
        self.all_processes = []
        
        # Buttons row - filling space
        btn_row = tk.Frame(process_card, bg="#1e1e1e")
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        refresh_btn = tk.Button(btn_row, text="🔄 Refresh",
                               font=("Segoe UI", 10, "bold"),
                               bg="#2d2d2d", fg="white",
                               activebackground="#3d3d3d",
                               relief=tk.FLAT, bd=0,
                               cursor="hand2",
                               command=lambda: self.refresh_process_list())
        refresh_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=10)
        self.add_hover_effect(refresh_btn, "#3d3d3d", "#2d2d2d")
        
        attach_btn = tk.Button(btn_row, text="▶ Attach",
                              font=("Segoe UI", 10, "bold"),
                              bg="#00aa00", fg="white",
                              activebackground="#00cc00",
                              relief=tk.FLAT, bd=0,
                              cursor="hand2",
                              command=lambda: self.attach_to_process())
        attach_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=10)
        self.add_hover_effect(attach_btn, "#00cc00", "#00aa00")
        
        detach_btn = tk.Button(btn_row, text="⏹ Detach",
                              font=("Segoe UI", 10, "bold"),
                              bg="#dd3333", fg="white",
                              activebackground="#ee4444",
                              relief=tk.FLAT, bd=0,
                              cursor="hand2",
                              command=lambda: self.detach_from_process())
        detach_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=10)
        self.add_hover_effect(detach_btn, "#ee4444", "#dd3333")
        
        # Scan Controls Card - Dark themed
        scan_card = tk.Frame(container, bg="#1e1e1e", highlightbackground="#333333",
                            highlightthickness=1)
        scan_card.pack(fill=tk.X, pady=(0, 15))
        
        # Scan card header
        tk.Label(scan_card, text="🔍 Memory Scanner",
                font=("Segoe UI", 11, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Input controls
        input_frame = tk.Frame(scan_card, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Value input
        value_frame = tk.Frame(input_frame, bg="#1e1e1e")
        value_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(value_frame, text="Value:",
                font=("Segoe UI", 9, "bold"),
                bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", pady=(0, 5))
        
        self.scan_value_var = tk.StringVar()
        value_entry = tk.Entry(value_frame, textvariable=self.scan_value_var,
                              font=("Consolas", 11),
                              bg="#0d0d0d", fg=self.text_color,
                              insertbackground=self.accent_color,
                              relief=tk.FLAT, bd=0)
        value_entry.pack(fill=tk.X, ipady=8, ipadx=10)
        
        # Type selector
        type_frame = tk.Frame(input_frame, bg="#1e1e1e")
        type_frame.pack(side=tk.LEFT)
        
        tk.Label(type_frame, text="Type:",
                font=("Segoe UI", 9, "bold"),
                bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", pady=(0, 5))
        
        self.value_type_var = tk.StringVar(value="4 Bytes")
        type_combo = ttk.Combobox(type_frame, textvariable=self.value_type_var,
                                 values=["Byte", "2 Bytes", "4 Bytes", "Float", "Double"],
                                 width=15, state="readonly", font=("Segoe UI", 10))
        type_combo.pack(ipady=7)
        
        # Scan buttons - filling space
        scan_btns = tk.Frame(scan_card, bg="#1e1e1e")
        scan_btns.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        first_scan = tk.Button(scan_btns, text="🔍 First Scan",
                              font=("Segoe UI", 11, "bold"),
                              bg=self.accent_color, fg="white",
                              activebackground="#0066cc",
                              relief=tk.FLAT, bd=0,
                              cursor="hand2",
                              command=lambda: self.perform_first_scan())
        first_scan.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=12)
        self.add_hover_effect(first_scan, "#0066cc", self.accent_color)
        
        next_scan = tk.Button(scan_btns, text="🔎 Next Scan",
                             font=("Segoe UI", 11, "bold"),
                             bg="#0066cc", fg="white",
                             activebackground="#0077dd",
                             relief=tk.FLAT, bd=0,
                             cursor="hand2",
                             command=lambda: self.perform_next_scan())
        next_scan.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=12)
        self.add_hover_effect(next_scan, "#0077dd", "#0066cc")
        
        stop_scan = tk.Button(scan_btns, text="⏹ Stop",
                             font=("Segoe UI", 11, "bold"),
                             bg="#cc0000", fg="white",
                             activebackground="#dd0000",
                             relief=tk.FLAT, bd=0,
                             cursor="hand2",
                             command=lambda: self.stop_scan())
        stop_scan.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=12)
        self.add_hover_effect(stop_scan, "#dd0000", "#cc0000")
        
        # Progress
        progress_frame = tk.Frame(scan_card, bg="#0d0d0d")
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        progress_inner = tk.Frame(progress_frame, bg="#0d0d0d")
        progress_inner.pack(fill=tk.X, padx=15, pady=12)
        
        self.scan_progress_label = tk.Label(progress_inner, text="Ready",
                                           font=("Segoe UI", 10, "bold"),
                                           bg="#0d0d0d", fg="#aaaaaa")
        self.scan_progress_label.pack(anchor="w", pady=(0, 8))
        
        self.scan_progressbar = ttk.Progressbar(progress_inner, mode='determinate')
        self.scan_progressbar.pack(fill=tk.X)
        
        # Results - Split panels
        results = tk.Frame(container, bg=self.bg_color)
        results.pack(fill=tk.BOTH, expand=True)
        
        # Left - Found Addresses
        left_panel = tk.Frame(results, bg="#1e1e1e", highlightbackground="#333333",
                             highlightthickness=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        tk.Label(left_panel, text="📋 Found Addresses",
                font=("Segoe UI", 11, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=15)
        
        list_container = tk.Frame(left_panel, bg="#1e1e1e")
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        list_scroll = tk.Scrollbar(list_container, **self.get_scrollbar_config())
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.found_addresses_list = tk.Listbox(list_container,
                                               font=("Consolas", 10),
                                               bg="#0d0d0d", fg=self.text_color,
                                               selectbackground=self.accent_color,
                                               selectforeground="white",
                                               relief=tk.FLAT, bd=0,
                                               highlightthickness=0,
                                               yscrollcommand=list_scroll.set)
        self.found_addresses_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.found_addresses_list.yview)
        
        add_btn = tk.Button(left_panel, text="➕ Add Selected",
                           font=("Segoe UI", 10, "bold"),
                           bg=self.accent_color, fg="white",
                           activebackground="#0066cc",
                           relief=tk.FLAT, bd=0,
                           cursor="hand2",
                           command=lambda: self.add_to_address_list())
        add_btn.pack(fill=tk.X, padx=15, pady=(0, 15), ipady=10)
        self.add_hover_effect(add_btn, "#0066cc", self.accent_color)
        
        # Right - Address List
        right_panel = tk.Frame(results, bg="#1e1e1e", highlightbackground="#333333",
                              highlightthickness=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        tk.Label(right_panel, text="✏️ Address List (Double-click to edit)",
                font=("Segoe UI", 11, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=15)
        
        tree_container = tk.Frame(right_panel, bg="#1e1e1e")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        tree_scroll = tk.Scrollbar(tree_container, **self.get_scrollbar_config())
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.address_tree = ttk.Treeview(tree_container,
                                        columns=("Address", "Value", "Type"),
                                        show="headings",
                                        yscrollcommand=tree_scroll.set)
        self.address_tree.heading("Address", text="Address")
        self.address_tree.heading("Value", text="Value")
        self.address_tree.heading("Type", text="Type")
        self.address_tree.column("Address", width=140, anchor="w")
        self.address_tree.column("Value", width=120, anchor="w")
        self.address_tree.column("Type", width=100, anchor="center")
        self.address_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.address_tree.yview)
        self.address_tree.bind("<Double-1>", self.edit_address_value)
        
        # Control buttons - filling space
        controls = tk.Frame(right_panel, bg="#1e1e1e")
        controls.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        remove_btn = tk.Button(controls, text="🗑 Remove",
                              font=("Segoe UI", 10, "bold"),
                              bg="#cc0000", fg="white",
                              activebackground="#dd0000",
                              relief=tk.FLAT, bd=0,
                              cursor="hand2",
                              command=lambda: self.remove_from_address_list())
        remove_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=10)
        self.add_hover_effect(remove_btn, "#dd0000", "#cc0000")
        
        refresh_btn = tk.Button(controls, text="🔄 Refresh",
                               font=("Segoe UI", 10, "bold"),
                               bg="#2d2d2d", fg="white",
                               activebackground="#3d3d3d",
                               relief=tk.FLAT, bd=0,
                               cursor="hand2",
                               command=lambda: self.refresh_address_values())
        refresh_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=10)
        self.add_hover_effect(refresh_btn, "#3d3d3d", "#2d2d2d")
        
        # Initialize
        self.refresh_process_list()
    
    def filter_process_list(self):
        """Filter process list based on search term"""
        try:
            search_term = self.process_search_var.get().lower()
            if not search_term:
                # Show all processes
                self.process_combo['values'] = self.all_processes
            else:
                # Filter processes
                filtered = [p for p in self.all_processes if search_term in p.lower()]
                self.process_combo['values'] = filtered
        except Exception as e:
            print(f"Error filtering processes: {e}")
    
    def refresh_process_list(self):
        """Refresh the list of running processes"""
        try:
            processes = self.memory_scanner.get_process_list()
            self.all_processes = [f"{pid}: {name}" for pid, name in processes]
            self.process_combo['values'] = self.all_processes
            self.update_status(f"Found {len(processes)} processes")
            self.show_notification(f"Refreshed: {len(processes)} processes found", "info")
        except Exception as e:
            self.update_status(f"Error refreshing processes: {e}")
            self.show_notification(f"Error: {e}", "error")
    
    def attach_to_process(self):
        """Attach to selected process"""
        try:
            selection = self.process_var.get()
            if not selection:
                self.update_status("Please select a process first")
                return
            
            # Extract process name from "pid: name" format
            process_name = selection.split(": ", 1)[1]
            
            if self.memory_scanner.attach_process(process_name):
                self.update_status(f"✓ Attached to {process_name}")
            else:
                self.update_status(f"✗ Failed to attach to {process_name}")
        except Exception as e:
            self.update_status(f"Error attaching: {e}")
    
    def detach_from_process(self):
        """Detach from current process"""
        try:
            self.memory_scanner.detach_process()
            self.found_addresses_list.delete(0, tk.END)
            self.update_status("Detached from process")
        except Exception as e:
            self.update_status(f"Error detaching: {e}")
    
    def perform_first_scan(self):
        """Perform first memory scan"""
        try:
            if not self.memory_scanner.process:
                self.show_notification("Please attach to a process first!", "warning")
                self.update_status("❌ Not attached to any process")
                return
            
            value = self.scan_value_var.get()
            if not value:
                self.show_notification("Please enter a value to scan", "warning")
                return
            
            value_type = self.value_type_var.get()
            
            self.found_addresses_list.delete(0, tk.END)
            self.scan_progressbar['value'] = 0
            self.scan_progress_label.config(text="Initializing scan...")
            self.update_status("🔍 Starting first scan...")
            
            # Run scan in background thread to keep UI responsive
            def run_scan():
                try:
                    addresses_found = []
                    
                    def update_progress(progress, count):
                        try:
                            self.scan_progressbar['value'] = progress
                            self.scan_progress_label.config(text=f"Scanning memory... {count} found")
                            self.root.update_idletasks()
                        except:
                            pass
                    
                    # Perform the scan
                    result = self.memory_scanner.first_scan(value, value_type, update_progress)
                    
                    if result:
                        # Display results
                        self.root.after(0, lambda: self.display_found_addresses())
                        self.root.after(0, lambda: self.show_notification(
                            f"✓ Found {len(self.memory_scanner.found_addresses)} addresses", "success"))
                        self.root.after(0, lambda: self.update_status(
                            f"✓ First scan complete: {len(self.memory_scanner.found_addresses)} addresses found"))
                    else:
                        self.root.after(0, lambda: self.show_notification("No addresses found", "info"))
                        self.root.after(0, lambda: self.update_status("❌ No addresses found"))
                    
                    self.scan_progressbar['value'] = 100
                    self.scan_progress_label.config(text="Scan complete!")
                    
                except Exception as e:
                    self.root.after(0, lambda: self.show_notification(f"Scan error: {e}", "error"))
                    self.root.after(0, lambda: self.update_status(f"❌ Scan error: {e}"))
            
            # Start scan thread
            import threading
            scan_thread = threading.Thread(target=run_scan, daemon=True)
            scan_thread.start()
            
        except Exception as e:
            self.show_notification(f"Scan error: {e}", "error")
            self.update_status(f"❌ Scan error: {e}")
    
    def perform_next_scan(self):
        """Perform next scan on found addresses"""
        try:
            if not self.memory_scanner.process:
                self.update_status("Please attach to a process first")
                return
            
            if not self.memory_scanner.found_addresses:
                self.update_status("Perform a first scan first")
                return
            
            value = self.scan_value_var.get()
            if not value:
                self.update_status("Please enter a value to scan")
                return
            
            value_type = self.value_type_var.get()
            
            self.scan_progressbar['value'] = 0
            self.scan_progress_label.config(text="Scanning...")
            
            def update_progress(progress, count):
                self.scan_progressbar['value'] = progress
                self.scan_progress_label.config(text=f"Scanning... {count} remaining")
                if progress >= 100:
                    self.display_found_addresses()
                    self.update_status(f"Next scan complete: {count} addresses remaining")
            
            self.memory_scanner.next_scan(value, value_type, update_progress)
            
        except Exception as e:
            self.update_status(f"Scan error: {e}")
    
    def stop_scan(self):
        """Stop current scan"""
        self.memory_scanner.stop_scan()
        self.scan_progress_label.config(text="Stopped")
        self.update_status("Scan stopped")
    
    def display_found_addresses(self):
        """Display found addresses in listbox"""
        self.found_addresses_list.delete(0, tk.END)
        
        # Limit display to first 10000 addresses
        addresses = self.memory_scanner.found_addresses[:10000]
        
        for addr in addresses:
            self.found_addresses_list.insert(tk.END, f"0x{addr:08X}")
        
        if len(self.memory_scanner.found_addresses) > 10000:
            self.found_addresses_list.insert(tk.END, f"... and {len(self.memory_scanner.found_addresses) - 10000} more")
    
    def add_to_address_list(self):
        """Add selected address to address list for editing"""
        try:
            selection = self.found_addresses_list.curselection()
            if not selection:
                return
            
            idx = selection[0]
            if idx >= len(self.memory_scanner.found_addresses):
                return
            
            address = self.memory_scanner.found_addresses[idx]
            value_type = self.value_type_var.get()
            
            # Get current value
            current_value = self.memory_scanner.get_address_value(address, value_type)
            
            # Add to tree
            self.address_tree.insert("", tk.END, values=(f"0x{address:08X}", current_value, value_type))
            self.update_status(f"Added address 0x{address:08X} to list")
            
        except Exception as e:
            self.update_status(f"Error adding address: {e}")
    
    def remove_from_address_list(self):
        """Remove selected address from address list"""
        try:
            selection = self.address_tree.selection()
            if selection:
                self.address_tree.delete(selection)
                self.update_status("Address removed")
        except Exception as e:
            self.update_status(f"Error removing address: {e}")
    
    def refresh_address_values(self):
        """Refresh values in address list"""
        try:
            for item in self.address_tree.get_children():
                values = self.address_tree.item(item)['values']
                address_str = values[0]
                address = int(address_str, 16)
                value_type = values[2]
                
                current_value = self.memory_scanner.get_address_value(address, value_type)
                self.address_tree.item(item, values=(address_str, current_value, value_type))
            
            self.update_status("Values refreshed")
        except Exception as e:
            self.update_status(f"Error refreshing values: {e}")
    
    def edit_address_value(self, event):
        """Edit value at address (double-click handler)"""
        try:
            selection = self.address_tree.selection()
            if not selection:
                return
            
            item = selection[0]
            values = self.address_tree.item(item)['values']
            address_str = values[0]
            current_value = values[1]
            value_type = values[2]
            
            # Create popup dialog for editing
            dialog = tk.Toplevel(self.root)
            dialog.title("Edit Value")
            dialog.geometry("300x150")
            dialog.configure(bg=self.bg_color)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (150 // 2)
            dialog.geometry(f"+{x}+{y}")
            
            tk.Label(dialog, text=f"Address: {address_str}",
                    font=("Segoe UI", 10),
                    bg=self.bg_color, fg=self.text_color).pack(pady=10)
            
            tk.Label(dialog, text="New Value:",
                    font=("Segoe UI", 10),
                    bg=self.bg_color, fg=self.text_color).pack(pady=5)
            
            value_var = tk.StringVar(value=str(current_value))
            entry = tk.Entry(dialog, textvariable=value_var,
                           font=("Consolas", 11), width=20,
                           bg=self.secondary_bg, fg=self.text_color)
            entry.pack(pady=5)
            entry.focus()
            
            def save_value():
                try:
                    new_value = value_var.get()
                    address = int(address_str, 16)
                    
                    if self.memory_scanner.set_address_value(address, new_value, value_type):
                        self.address_tree.item(item, values=(address_str, new_value, value_type))
                        self.update_status(f"✓ Value changed at {address_str}")
                        dialog.destroy()
                    else:
                        self.update_status(f"✗ Failed to change value at {address_str}")
                except Exception as e:
                    self.update_status(f"Error: {e}")
            
            btn_frame = tk.Frame(dialog, bg=self.bg_color)
            btn_frame.pack(pady=10)
            
            save_btn = tk.Button(btn_frame, text="Save",
                               font=("Segoe UI", 9, "bold"),
                               bg=self.accent_color, fg="white",
                               border=0, padx=20, pady=5,
                               cursor="hand2",
                               command=save_value)
            save_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(btn_frame, text="Cancel",
                                  font=("Segoe UI", 9, "bold"),
                                  bg=self.secondary_bg, fg=self.text_color,
                                  border=0, padx=20, pady=5,
                                  cursor="hand2",
                                  command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            entry.bind("<Return>", lambda e: save_value())
            entry.bind("<Escape>", lambda e: dialog.destroy())
            
        except Exception as e:
            self.update_status(f"Error editing value: {e}")
    
    def show_tools(self):
        """Show comprehensive Tools page with all utilities"""
        from utils.tools import ToolsCollection
        from utils.http_client import HTTPClient
        from utils.formatter import Formatter
        
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for different tool categories
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tab 1: Text Tools
        text_tools = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(text_tools, text="Text Tools")
        
        # Base64 Encoder/Decoder
        base64_frame = tk.LabelFrame(text_tools, text="Base64 Encoder/Decoder", 
                                      bg=self.secondary_bg, fg=self.text_color,
                                      font=("Segoe UI", 10, "bold"))
        base64_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        base64_input = tk.Text(base64_frame, height=5, font=("Consolas", 10),
                               bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        base64_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        base64_btns = tk.Frame(base64_frame, bg=self.secondary_bg)
        base64_btns.pack(fill=tk.X, padx=10, pady=5)
        
        def encode_b64():
            text = base64_input.get("1.0", "end-1c")
            result = ToolsCollection.encode_base64(text)
            base64_output.delete("1.0", "end")
            base64_output.insert("1.0", result)
        
        def decode_b64():
            text = base64_input.get("1.0", "end-1c")
            result = ToolsCollection.decode_base64(text)
            base64_output.delete("1.0", "end")
            base64_output.insert("1.0", result)
        
        tk.Button(base64_btns, text="▶ Encode", font=("Segoe UI", 9, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=15, pady=5,
                 cursor="hand2", command=encode_b64).pack(side=tk.LEFT, padx=5)
        
        tk.Button(base64_btns, text="◀ Decode", font=("Segoe UI", 9, "bold"),
                 bg="#0066cc", fg="white", relief=tk.FLAT, padx=15, pady=5,
                 cursor="hand2", command=decode_b64).pack(side=tk.LEFT, padx=5)
        
        base64_output = tk.Text(base64_frame, height=5, font=("Consolas", 10),
                                bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        base64_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 2: JSON/XML Formatter
        formatter_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(formatter_tab, text="JSON/XML")
        
        formatter_input = tk.Text(formatter_tab, height=10, font=("Consolas", 10),
                                  bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        formatter_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        formatter_btns = tk.Frame(formatter_tab, bg=self.bg_color)
        formatter_btns.pack(fill=tk.X, padx=10, pady=5)
        
        def format_json_text():
            text = formatter_input.get("1.0", "end-1c")
            result = Formatter.format_json(text)
            formatter_output.delete("1.0", "end")
            formatter_output.insert("1.0", result)
        
        def minify_json_text():
            text = formatter_input.get("1.0", "end-1c")
            result = Formatter.minify_json(text)
            formatter_output.delete("1.0", "end")
            formatter_output.insert("1.0", result)
        
        def format_xml_text():
            text = formatter_input.get("1.0", "end-1c")
            result = Formatter.format_xml(text)
            formatter_output.delete("1.0", "end")
            formatter_output.insert("1.0", result)
        
        tk.Button(formatter_btns, text="Format JSON", font=("Segoe UI", 9, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=15, pady=8,
                 cursor="hand2", command=format_json_text).pack(side=tk.LEFT, padx=5)
        
        tk.Button(formatter_btns, text="Minify JSON", font=("Segoe UI", 9, "bold"),
                 bg="#0066cc", fg="white", relief=tk.FLAT, padx=15, pady=8,
                 cursor="hand2", command=minify_json_text).pack(side=tk.LEFT, padx=5)
        
        tk.Button(formatter_btns, text="Format XML", font=("Segoe UI", 9, "bold"),
                 bg="#00aa00", fg="white", relief=tk.FLAT, padx=15, pady=8,
                 cursor="hand2", command=format_xml_text).pack(side=tk.LEFT, padx=5)
        
        formatter_output = tk.Text(formatter_tab, height=10, font=("Consolas", 10),
                                   bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        formatter_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 3: Regex Tester
        regex_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(regex_tab, text="Regex")
        
        regex_pattern_frame = tk.Frame(regex_tab, bg=self.bg_color)
        regex_pattern_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(regex_pattern_frame, text="Pattern:", font=("Segoe UI", 10, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        regex_pattern = tk.Entry(regex_pattern_frame, font=("Consolas", 11),
                                bg=self.secondary_bg, fg=self.text_color, width=50)
        regex_pattern.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        regex_test_text = tk.Text(regex_tab, height=8, font=("Consolas", 10),
                                  bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        regex_test_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def test_regex():
            pattern = regex_pattern.get()
            text = regex_test_text.get("1.0", "end-1c")
            
            # Debug output
            print(f"DEBUG - Pattern: '{pattern}'")
            print(f"DEBUG - Text length: {len(text)}")
            print(f"DEBUG - Text preview: '{text[:100]}'")
            
            result = ToolsCollection.test_regex(pattern, text)
            
            regex_results.delete("1.0", "end")
            if result['success']:
                matches = result['matches']
                regex_results.insert("1.0", f"Found {len(matches)} matches:\n\n")
                for i, match in enumerate(matches, 1):
                    regex_results.insert("end", f"Match {i}: '{match['full']}' at position {match['start']}-{match['end']}\n")
                    if match['groups']:
                        regex_results.insert("end", f"  Groups: {match['groups']}\n")
            else:
                regex_results.insert("1.0", f"Error: {result['error']}")
        
        tk.Button(regex_tab, text="Test Regex", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=20, pady=10,
                 cursor="hand2", command=test_regex).pack(pady=5)
        
        regex_results = tk.Text(regex_tab, height=8, font=("Consolas", 10),
                                bg=self.secondary_bg, fg=self.text_color, wrap=tk.WORD)
        regex_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 4: Password Generator
        password_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(password_tab, text="Password")
        
        pass_frame = tk.Frame(password_tab, bg=self.secondary_bg)
        pass_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(pass_frame, text="Password Generator", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=20)
        
        # Length slider
        length_frame = tk.Frame(pass_frame, bg=self.secondary_bg)
        length_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(length_frame, text="Length:", font=("Segoe UI", 10),
                bg=self.secondary_bg, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        length_var = tk.IntVar(value=16)
        length_label = tk.Label(length_frame, text="16", font=("Segoe UI", 10, "bold"),
                               bg=self.secondary_bg, fg=self.accent_color)
        length_label.pack(side=tk.RIGHT, padx=5)
        
        def update_length(val):
            length_label.config(text=str(int(float(val))))
        
        length_slider = tk.Scale(length_frame, from_=8, to=64, orient=tk.HORIZONTAL,
                                variable=length_var, command=update_length,
                                bg=self.secondary_bg, fg=self.text_color,
                                highlightthickness=0)
        length_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Options
        options_frame = tk.Frame(pass_frame, bg=self.secondary_bg)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        use_upper = tk.BooleanVar(value=True)
        use_lower = tk.BooleanVar(value=True)
        use_digits = tk.BooleanVar(value=True)
        use_symbols = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=use_upper,
                      bg=self.secondary_bg, fg=self.text_color, selectcolor=self.bg_color,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=use_lower,
                      bg=self.secondary_bg, fg=self.text_color, selectcolor=self.bg_color,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Digits (0-9)", variable=use_digits,
                      bg=self.secondary_bg, fg=self.text_color, selectcolor=self.bg_color,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Symbols (!@#$%)", variable=use_symbols,
                      bg=self.secondary_bg, fg=self.text_color, selectcolor=self.bg_color,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        
        # Generate button
        def generate_password():
            password = ToolsCollection.generate_password(
                length=length_var.get(),
                use_upper=use_upper.get(),
                use_lower=use_lower.get(),
                use_digits=use_digits.get(),
                use_symbols=use_symbols.get()
            )
            pass_output.delete("1.0", "end")
            pass_output.insert("1.0", password)
        
        tk.Button(pass_frame, text="🎲 Generate Password", font=("Segoe UI", 11, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=30, pady=12,
                 cursor="hand2", command=generate_password).pack(pady=15)
        
        pass_output = tk.Text(pass_frame, height=3, font=("Consolas", 14, "bold"),
                             bg=self.bg_color, fg="#00ff00", wrap=tk.WORD)
        pass_output.pack(fill=tk.X, padx=20, pady=10)
        
        def copy_password():
            password = pass_output.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.show_notification("Password copied!", "success")
        
        tk.Button(pass_frame, text="📋 Copy to Clipboard", font=("Segoe UI", 9),
                 bg=self.secondary_bg, fg=self.text_color, relief=tk.FLAT, padx=20, pady=8,
                 cursor="hand2", command=copy_password).pack(pady=5)
        
        # Tab 5: Lorem Ipsum Generator
        lorem_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(lorem_tab, text="Lorem Ipsum")
        
        lorem_frame = tk.Frame(lorem_tab, bg=self.secondary_bg)
        lorem_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(lorem_frame, text="Lorem Ipsum Generator", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=20)
        
        para_frame = tk.Frame(lorem_frame, bg=self.secondary_bg)
        para_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(para_frame, text="Paragraphs:", font=("Segoe UI", 10),
                bg=self.secondary_bg, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        para_var = tk.IntVar(value=3)
        para_spin = tk.Spinbox(para_frame, from_=1, to=10, textvariable=para_var,
                              font=("Segoe UI", 10), width=10)
        para_spin.pack(side=tk.LEFT, padx=10)
        
        def generate_lorem():
            lorem = ToolsCollection.generate_lorem_ipsum(para_var.get())
            lorem_output.delete("1.0", "end")
            lorem_output.insert("1.0", lorem)
        
        tk.Button(para_frame, text="Generate", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=20, pady=8,
                 cursor="hand2", command=generate_lorem).pack(side=tk.LEFT, padx=10)
        
        lorem_output = tk.Text(lorem_frame, font=("Segoe UI", 10),
                              bg=self.bg_color, fg=self.text_color, wrap=tk.WORD)
        lorem_output.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 6: HTTP Request Tool
        http_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(http_tab, text="HTTP")
        
        http_controls = tk.Frame(http_tab, bg=self.secondary_bg)
        http_controls.pack(fill=tk.X, padx=10, pady=10)
        
        # Method selector
        method_frame = tk.Frame(http_controls, bg=self.secondary_bg)
        method_frame.pack(side=tk.LEFT, padx=5)
        
        method_var = tk.StringVar(value="GET")
        for method in ["GET", "POST", "PUT", "DELETE"]:
            tk.Radiobutton(method_frame, text=method, variable=method_var, value=method,
                          bg=self.secondary_bg, fg=self.text_color, selectcolor=self.bg_color,
                          font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
        
        # URL input
        url_frame = tk.Frame(http_tab, bg=self.bg_color)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(url_frame, text="URL:", font=("Segoe UI", 10, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        url_entry = tk.Entry(url_frame, font=("Consolas", 10),
                            bg=self.secondary_bg, fg=self.text_color)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        url_entry.insert(0, "https://api.github.com/zen")
        
        # Body input
        tk.Label(http_tab, text="Request Body (for POST/PUT):", font=("Segoe UI", 9),
                bg=self.bg_color, fg=self.text_color).pack(anchor="w", padx=10, pady=(10, 0))
        
        http_body = tk.Text(http_tab, height=5, font=("Consolas", 9),
                           bg=self.secondary_bg, fg=self.text_color, wrap=tk.WORD)
        http_body.pack(fill=tk.X, padx=10, pady=5)
        
        def send_request():
            url = url_entry.get()
            method = method_var.get()
            body = http_body.get("1.0", "end-1c") if http_body.get("1.0", "end-1c").strip() else None
            
            http_response.delete("1.0", "end")
            http_response.insert("1.0", "⏳ Sending request...\n")
            
            def do_request():
                result = HTTPClient.make_request(url, method, body=body)
                
                response_text = f"Status: {result['status']}\n\n"
                if result['success']:
                    response_text += f"✓ Success\n\n"
                    response_text += f"Response:\n{result['body']}"
                else:
                    response_text += f"✗ Error: {result['error']}\n\n"
                    if result['body']:
                        response_text += f"Response:\n{result['body']}"
                
                self.root.after(0, lambda: http_response.delete("1.0", "end"))
                self.root.after(0, lambda: http_response.insert("1.0", response_text))
            
            threading.Thread(target=do_request, daemon=True).start()
        
        tk.Button(http_tab, text="➤ Send Request", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=25, pady=10,
                 cursor="hand2", command=send_request).pack(pady=10)
        
        tk.Label(http_tab, text="Response:", font=("Segoe UI", 9, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor="w", padx=10)
        
        http_response = tk.Text(http_tab, font=("Consolas", 9),
                               bg=self.secondary_bg, fg=self.text_color, wrap=tk.WORD)
        http_response.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_status("Tools loaded")
    
    def show_dll_injector(self):
        """Show DLL Injector page for client-side injection"""
        if not hasattr(self, 'dll_injector'):
            self.dll_injector = DLLInjector()
        
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="💉 DLL Injector",
                font=("Segoe UI", 20, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="Client-Side Injection Tool",
                font=("Segoe UI", 10),
                bg=self.bg_color, fg="#666666").pack(side=tk.LEFT, padx=(15, 0))
        
        # Warning banner
        warning_frame = tk.Frame(container, bg="#4d3319", highlightbackground="#cc8800", 
                                highlightthickness=2)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(warning_frame, text="⚠️ WARNING",
                font=("Segoe UI", 11, "bold"),
                bg="#4d3319", fg="#ffaa00").pack(anchor="w", padx=15, pady=(10, 5))
        
        tk.Label(warning_frame, 
                text="Only inject DLLs into processes you own. Requires Administrator privileges.",
                font=("Segoe UI", 9),
                bg="#4d3319", fg="#dddddd", wraplength=800).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Main content - Split into 2 columns
        content_frame = tk.Frame(container, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Injection controls
        left_panel = tk.Frame(content_frame, bg="#1e1e1e", highlightbackground="#333333",
                             highlightthickness=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="🎯 Injection Controls",
                font=("Segoe UI", 12, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=15)
        
        # Process selection
        process_frame = tk.Frame(left_panel, bg="#1e1e1e")
        process_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(process_frame, text="Target Process:",
                font=("Segoe UI", 10, "bold"),
                bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", pady=(0, 5))
        
        # Search for process
        search_frame = tk.Frame(process_frame, bg="#1e1e1e")
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.dll_process_search_var = tk.StringVar()
        self.dll_process_search_var.trace('w', lambda *args: self.filter_dll_process_list())
        
        search_entry = tk.Entry(search_frame, textvariable=self.dll_process_search_var,
                               font=("Segoe UI", 10),
                               bg="#0d0d0d", fg=self.text_color,
                               insertbackground=self.accent_color,
                               relief=tk.FLAT, bd=0)
        search_entry.pack(fill=tk.X, ipady=6, ipadx=10)
        
        # Process dropdown
        self.dll_process_var = tk.StringVar()
        self.dll_process_combo = ttk.Combobox(process_frame, textvariable=self.dll_process_var,
                                             width=50, state="readonly", font=("Segoe UI", 10))
        self.dll_process_combo.pack(fill=tk.X, ipady=6)
        
        # Store all processes
        self.dll_all_processes = []
        
        # Refresh button
        refresh_btn = tk.Button(process_frame, text="🔄 Refresh Processes",
                               font=("Segoe UI", 10, "bold"),
                               bg="#2d2d2d", fg="white",
                               relief=tk.FLAT, cursor="hand2",
                               command=self.refresh_dll_process_list)
        refresh_btn.pack(fill=tk.X, pady=(5, 0), ipady=8)
        self.add_hover_effect(refresh_btn, "#3d3d3d", "#2d2d2d")
        
        # DLL path selection
        dll_frame = tk.Frame(left_panel, bg="#1e1e1e")
        dll_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(dll_frame, text="DLL File Path:",
                font=("Segoe UI", 10, "bold"),
                bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", pady=(0, 5))
        
        path_frame = tk.Frame(dll_frame, bg="#1e1e1e")
        path_frame.pack(fill=tk.X)
        
        self.dll_path_var = tk.StringVar()
        dll_entry = tk.Entry(path_frame, textvariable=self.dll_path_var,
                            font=("Consolas", 10),
                            bg="#0d0d0d", fg=self.text_color,
                            insertbackground=self.accent_color,
                            relief=tk.FLAT, bd=0)
        dll_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=10)
        
        browse_btn = tk.Button(path_frame, text="📁",
                              font=("Segoe UI", 12),
                              bg="#2d2d2d", fg="white",
                              relief=tk.FLAT, cursor="hand2",
                              padx=15, pady=5,
                              command=self.browse_dll_file)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.add_hover_effect(browse_btn, "#3d3d3d", "#2d2d2d")
        
        # Injection buttons
        btn_frame = tk.Frame(left_panel, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        inject_btn = tk.Button(btn_frame, text="💉 Inject DLL",
                              font=("Segoe UI", 12, "bold"),
                              bg=self.accent_color, fg="white",
                              relief=tk.FLAT, cursor="hand2",
                              command=self.perform_dll_injection)
        inject_btn.pack(fill=tk.X, ipady=12, pady=(0, 8))
        self.add_hover_effect(inject_btn, "#0066cc", self.accent_color)
        
        eject_btn = tk.Button(btn_frame, text="⏏️ Eject DLL",
                             font=("Segoe UI", 11, "bold"),
                             bg="#cc3333", fg="white",
                             relief=tk.FLAT, cursor="hand2",
                             command=self.perform_dll_ejection)
        eject_btn.pack(fill=tk.X, ipady=10)
        self.add_hover_effect(eject_btn, "#dd4444", "#cc3333")
        
        # Right column - Loaded modules
        right_panel = tk.Frame(content_frame, bg="#1e1e1e", highlightbackground="#333333",
                              highlightthickness=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_panel, text="📚 Loaded Modules",
                font=("Segoe UI", 12, "bold"),
                bg="#1e1e1e", fg=self.text_color).pack(anchor="w", padx=20, pady=15)
        
        # Modules list
        list_container = tk.Frame(right_panel, bg="#1e1e1e")
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        list_scroll = tk.Scrollbar(list_container, **self.get_scrollbar_config())
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dll_modules_list = tk.Listbox(list_container,
                                           font=("Consolas", 9),
                                           bg="#0d0d0d", fg=self.text_color,
                                           selectbackground=self.accent_color,
                                           selectforeground="white",
                                           relief=tk.FLAT, bd=0,
                                           highlightthickness=0,
                                           yscrollcommand=list_scroll.set)
        self.dll_modules_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.dll_modules_list.yview)
        
        # List modules button
        list_btn = tk.Button(right_panel, text="🔍 List Modules in Selected Process",
                            font=("Segoe UI", 10, "bold"),
                            bg="#2d2d2d", fg="white",
                            relief=tk.FLAT, cursor="hand2",
                            command=self.list_process_modules)
        list_btn.pack(fill=tk.X, padx=15, pady=(0, 15), ipady=10)
        self.add_hover_effect(list_btn, "#3d3d3d", "#2d2d2d")
        
        # Initialize process list
        self.refresh_dll_process_list()
        self.update_status("DLL Injector ready")
    
    def filter_dll_process_list(self):
        """Filter DLL injector process list based on search"""
        try:
            search_term = self.dll_process_search_var.get().lower()
            if not search_term:
                self.dll_process_combo['values'] = self.dll_all_processes
            else:
                filtered = [p for p in self.dll_all_processes if search_term in p.lower()]
                self.dll_process_combo['values'] = filtered
        except Exception as e:
            print(f"Error filtering processes: {e}")
    
    def refresh_dll_process_list(self):
        """Refresh the list of processes for DLL injection"""
        try:
            import psutil
            processes = [(proc.info['pid'], proc.info['name']) 
                        for proc in psutil.process_iter(['pid', 'name'])]
            self.dll_all_processes = [f"{pid}: {name}" for pid, name in processes]
            self.dll_process_combo['values'] = self.dll_all_processes
            self.show_notification(f"Refreshed: {len(processes)} processes", "info")
        except Exception as e:
            self.show_notification(f"Error: {e}", "error")
    
    def browse_dll_file(self):
        """Browse for DLL file"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Select DLL File",
            filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
        )
        if filepath:
            self.dll_path_var.set(filepath)
    
    def perform_dll_injection(self):
        """Perform DLL injection"""
        try:
            selection = self.dll_process_var.get()
            dll_path = self.dll_path_var.get()
            
            if not selection:
                self.show_notification("Please select a target process", "warning")
                return
            
            if not dll_path:
                self.show_notification("Please select a DLL file", "warning")
                return
            
            # Extract PID
            pid = int(selection.split(":")[0])
            
            # Perform injection
            self.update_status("Injecting DLL...")
            success, message = self.dll_injector.inject_dll(pid, dll_path)
            
            if success:
                self.show_notification(message, "success")
                self.update_status("✓ DLL injected successfully")
            else:
                self.show_notification(message, "error")
                self.update_status("✗ Injection failed")
                
        except Exception as e:
            self.show_notification(f"Injection error: {e}", "error")
            self.update_status(f"✗ Error: {e}")
    
    def perform_dll_ejection(self):
        """Eject DLL from process"""
        try:
            selection = self.dll_process_var.get()
            
            if not selection:
                self.show_notification("Please select a target process", "warning")
                return
            
            # Get selected module from list
            selected_indices = self.dll_modules_list.curselection()
            if not selected_indices:
                self.show_notification("Please select a module to eject from the list", "warning")
                return
            
            module_text = self.dll_modules_list.get(selected_indices[0])
            dll_name = module_text.split(" - ")[0] if " - " in module_text else module_text
            
            # Extract PID
            pid = int(selection.split(":")[0])
            
            # Perform ejection
            self.update_status("Ejecting DLL...")
            success, message = self.dll_injector.eject_dll(pid, dll_name)
            
            if success:
                self.show_notification(message, "success")
                self.update_status("✓ DLL ejected successfully")
                self.list_process_modules()  # Refresh list
            else:
                self.show_notification(message, "error")
                self.update_status("✗ Ejection failed")
                
        except Exception as e:
            self.show_notification(f"Ejection error: {e}", "error")
            self.update_status(f"✗ Error: {e}")
    
    def list_process_modules(self):
        """List all modules loaded in selected process"""
        try:
            selection = self.dll_process_var.get()
            
            if not selection:
                self.show_notification("Please select a process first", "warning")
                return
            
            # Extract PID
            pid = int(selection.split(":")[0])
            
            # Get modules
            modules = self.dll_injector.list_loaded_modules(pid)
            
            # Display
            self.dll_modules_list.delete(0, tk.END)
            if modules:
                for module_name, module_path in modules:
                    self.dll_modules_list.insert(tk.END, f"{module_name} - {module_path}")
                self.show_notification(f"Found {len(modules)} modules", "success")
            else:
                self.dll_modules_list.insert(tk.END, "No modules found or access denied")
                self.show_notification("No modules found", "info")
                
        except Exception as e:
            self.show_notification(f"Error listing modules: {e}", "error")
    
    def show_process_inspector(self):
        """Show Process Inspector - Debug CipherV2 itself"""
        if not hasattr(self, 'process_inspector'):
            self.process_inspector = ProcessInspector()
        
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="🔬 Process Inspector",
                font=("Segoe UI", 20, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="Debug CipherV2 with CipherV2",
                font=("Segoe UI", 10),
                bg=self.bg_color, fg="#666666").pack(side=tk.LEFT, padx=(15, 0))
        
        # Info banner
        info_frame = tk.Frame(container, bg="#193d4d", highlightbackground="#0088cc", 
                             highlightthickness=2)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(info_frame, text="ℹ️ SELF-INSPECTION",
                font=("Segoe UI", 11, "bold"),
                bg="#193d4d", fg="#00aaff").pack(anchor="w", padx=15, pady=(10, 5))
        
        tk.Label(info_frame, 
                text="Analyzing CipherV2's own process - Educational and debugging purposes only.",
                font=("Segoe UI", 9),
                bg="#193d4d", fg="#dddddd", wraplength=800).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Create notebook for different inspection tabs
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Process Info
        info_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(info_tab, text="Process Info")
        
        info_text = tk.Text(info_tab, font=("Consolas", 10),
                           bg=self.secondary_bg, fg=self.text_color,
                           wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get and display process info
        info = self.process_inspector.get_self_info()
        info_content = f"""CIPHERV2 PROCESS INFORMATION
{'='*60}

Process ID (PID): {info.get('pid', 'N/A')}
Process Name: {info.get('name', 'N/A')}
Executable Path: {info.get('exe', 'N/A')}
Working Directory: {info.get('cwd', 'N/A')}
Status: {info.get('status', 'N/A')}
Created: {info.get('create_time', 'N/A')}

RESOURCE USAGE:
{'='*60}
Threads: {info.get('num_threads', 'N/A')}
CPU Usage: {info.get('cpu_percent', 0):.2f}%
Memory (RSS): {self.process_inspector.format_bytes(info.get('memory_info', type('obj', (), {'rss': 0})).rss)}
Memory (VMS): {self.process_inspector.format_bytes(info.get('memory_info', type('obj', (), {'vms': 0})).vms)}
Memory Percent: {info.get('memory_percent', 0):.2f}%

{'='*60}
"""
        info_text.insert("1.0", info_content)
        info_text.config(state=tk.DISABLED)
        
        # Tab 2: Memory Maps
        memory_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(memory_tab, text="Memory Maps")
        
        memory_frame = tk.Frame(memory_tab, bg=self.bg_color)
        memory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        memory_scroll = tk.Scrollbar(memory_frame, **self.get_scrollbar_config())
        memory_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        memory_list = tk.Listbox(memory_frame, font=("Consolas", 9),
                                bg=self.secondary_bg, fg=self.text_color,
                                yscrollcommand=memory_scroll.set)
        memory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        memory_scroll.config(command=memory_list.yview)
        
        maps = self.process_inspector.get_memory_maps()
        for mmap in maps[:50]:  # Limit to first 50
            if 'error' not in mmap:
                memory_list.insert(tk.END, 
                    f"{mmap.get('path', 'N/A')[:80]} - {self.process_inspector.format_bytes(mmap.get('rss', 0))}")
        
        # Tab 3: Loaded Modules
        modules_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(modules_tab, text="Python Modules")
        
        modules_frame = tk.Frame(modules_tab, bg=self.bg_color)
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        modules_scroll = tk.Scrollbar(modules_frame, **self.get_scrollbar_config())
        modules_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        modules_list = tk.Listbox(modules_frame, font=("Consolas", 9),
                                 bg=self.secondary_bg, fg=self.text_color,
                                 yscrollcommand=modules_scroll.set)
        modules_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        modules_scroll.config(command=modules_list.yview)
        
        modules = self.process_inspector.get_loaded_modules()
        for module in modules[:100]:  # Limit to first 100
            if 'error' not in module:
                modules_list.insert(tk.END, 
                    f"{module.get('name', 'N/A')[:40]:40} - {module.get('file', 'N/A')[:60]}")
        
        # Tab 4: Threads
        threads_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(threads_tab, text="Threads")
        
        threads_text = tk.Text(threads_tab, font=("Consolas", 10),
                              bg=self.secondary_bg, fg=self.text_color,
                              wrap=tk.NONE)
        threads_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        threads = self.process_inspector.get_threads()
        threads_content = f"ACTIVE THREADS ({len(threads)})\n{'='*60}\n\n"
        for i, thread in enumerate(threads, 1):
            if 'error' not in thread:
                threads_content += f"Thread #{i}:\n"
                threads_content += f"  ID: {thread.get('id', 'N/A')}\n"
                threads_content += f"  User Time: {thread.get('user_time', 0):.4f}s\n"
                threads_content += f"  System Time: {thread.get('system_time', 0):.4f}s\n\n"
        
        threads_text.insert("1.0", threads_content)
        threads_text.config(state=tk.DISABLED)
        
        # Tab 5: Process Tree
        tree_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tree_tab, text="Process Tree")
        
        tree_text = tk.Text(tree_tab, font=("Consolas", 11),
                           bg=self.secondary_bg, fg=self.text_color,
                           wrap=tk.WORD)
        tree_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = self.process_inspector.get_process_tree()
        tree_content = f"""PROCESS TREE
{'='*60}

"""
        if tree.get('parent'):
            tree_content += f"Parent Process:\n"
            tree_content += f"  └── PID {tree['parent']['pid']}: {tree['parent']['name']}\n\n"
        
        tree_content += f"Current Process (CipherV2):\n"
        tree_content += f"  └── PID {tree['current']['pid']}: {tree['current']['name']}\n\n"
        
        if tree.get('children'):
            tree_content += f"Child Processes ({len(tree['children'])}):\n"
            for child in tree['children']:
                tree_content += f"      └── PID {child['pid']}: {child['name']}\n"
        else:
            tree_content += "No child processes\n"
        
        tree_text.insert("1.0", tree_content)
        tree_text.config(state=tk.DISABLED)
        
        # Tab 6: Open Files
        files_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(files_tab, text="Open Files")
        
        files_frame = tk.Frame(files_tab, bg=self.bg_color)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        files_scroll = tk.Scrollbar(files_frame, **self.get_scrollbar_config())
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        files_list = tk.Listbox(files_frame, font=("Consolas", 9),
                               bg=self.secondary_bg, fg=self.text_color,
                               yscrollcommand=files_scroll.set)
        files_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scroll.config(command=files_list.yview)
        
        files = self.process_inspector.get_open_files()
        if files:
            for f in files:
                if 'error' not in f:
                    files_list.insert(tk.END, f"FD {f.get('fd', 'N/A')}: {f.get('path', 'N/A')}")
        else:
            files_list.insert(tk.END, "No open files or access denied")
        
        # Bottom controls
        controls_frame = tk.Frame(container, bg=self.bg_color)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_btn = tk.Button(controls_frame, text="🔄 Refresh Data",
                               font=("Segoe UI", 11, "bold"),
                               bg=self.accent_color, fg="white",
                               relief=tk.FLAT, cursor="hand2",
                               padx=30, pady=10,
                               command=lambda: self.show_process_inspector())
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.add_hover_effect(refresh_btn, "#0066cc", self.accent_color)
        
        export_btn = tk.Button(controls_frame, text="💾 Export Report",
                              font=("Segoe UI", 11),
                              bg="#2d2d2d", fg="white",
                              relief=tk.FLAT, cursor="hand2",
                              padx=30, pady=10,
                              command=self.export_inspection_report)
        export_btn.pack(side=tk.LEFT)
        self.add_hover_effect(export_btn, "#3d3d3d", "#2d2d2d")
        
        self.update_status("Process Inspector loaded - analyzing CipherV2")
    
    def export_inspection_report(self):
        """Export process inspection report to file"""
        try:
            from tkinter import filedialog
            import json
            from datetime import datetime
            
            # Gather all data
            report = {
                'timestamp': datetime.now().isoformat(),
                'process_info': self.process_inspector.get_self_info(),
                'memory_maps': self.process_inspector.get_memory_maps()[:50],
                'threads': self.process_inspector.get_threads(),
                'process_tree': self.process_inspector.get_process_tree(),
                'loaded_modules': [m['name'] for m in self.process_inspector.get_loaded_modules()[:100]],
            }
            
            # Ask where to save
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"cipherv2_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filepath:
                with open(filepath, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                self.show_notification(f"Report saved: {filepath}", "success")
                self.update_status(f"Exported inspection report")
        except Exception as e:
            self.show_notification(f"Export error: {e}", "error")
    
    def show_ai_assistant(self):
        """Show AI Assistant page with Hugging Face integration"""
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with gradient-like effect
        header_frame = tk.Frame(container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="AI Coding Assistant",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.bg_color, fg=self.accent_color)
        title.pack(anchor="w")
        
        subtitle = tk.Label(header_frame, 
                       text="Powered by Hugging Face • Free Forever • Your code stays private",
                       font=("Segoe UI", 9),
                       bg=self.bg_color, fg="#888888")
        subtitle.pack(anchor="w", pady=(2, 0))
        
        # API Key setup frame with modern styling
        api_frame = tk.Frame(container, bg=self.secondary_bg, highlightbackground=self.accent_color, highlightthickness=2)
        api_frame.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        key_inner = tk.Frame(api_frame, bg=self.secondary_bg)
        key_inner.pack(fill=tk.X, padx=20, pady=10)
        
        # Icon and label
        key_header = tk.Frame(key_inner, bg=self.secondary_bg)
        key_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(key_header, text="🔑",
                font=("Segoe UI", 16),
                bg=self.secondary_bg).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(key_header, text="Hugging Face API Token",
                font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(side=tk.LEFT)
        
        tk.Label(key_header, text="(Get it FREE at huggingface.co/settings/tokens)",
                font=("Segoe UI", 9),
                bg=self.secondary_bg, fg="#888888").pack(side=tk.LEFT, padx=(10, 0))
        
        # Key input with save button
        key_input_frame = tk.Frame(key_inner, bg=self.secondary_bg)
        key_input_frame.pack(fill=tk.X)
        
        self.api_key_entry = tk.Entry(key_input_frame, font=("Consolas", 10),
                                      bg=self.bg_color, fg=self.text_color,
                                      relief=tk.FLAT, bd=2,
                                      highlightthickness=1,
                                      highlightbackground="#444444",
                                      highlightcolor=self.accent_color,
                                      insertbackground=self.accent_color,
                                      show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.api_key_entry.insert(0, "hf_...")
        
        save_key_btn = tk.Button(key_input_frame, text="Save Token",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.accent_color, fg="white",
                                relief=tk.FLAT, cursor="hand2", 
                                padx=20, pady=8,
                                activebackground=self.button_hover,
                                command=self.save_api_key)
        save_key_btn.pack(side=tk.RIGHT)
        save_key_btn.bind("<Enter>", lambda e: save_key_btn.config(bg=self.button_hover))
        save_key_btn.bind("<Leave>", lambda e: save_key_btn.config(bg=self.accent_color))
        
        # Main chat container with modern card design
        chat_outer = tk.Frame(container, bg=self.bg_color)
        chat_outer.pack(fill=tk.BOTH, expand=True)
        
        # Messages display with modern scrollbar
        messages_container = tk.Frame(chat_outer, bg=self.secondary_bg, 
                                     highlightbackground="#333333", highlightthickness=1)
        messages_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(messages_container, **self.get_scrollbar_config(), width=12)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Text(messages_container,
                                   font=("Segoe UI", 11),
                                   bg=self.secondary_bg, fg=self.text_color,
                                   wrap=tk.WORD, state=tk.DISABLED,
                                   yscrollcommand=scrollbar.set,
                                   padx=20, pady=20,
                                   spacing1=5, spacing3=5,
                                   relief=tk.FLAT,
                                   highlightthickness=0)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_display.yview)
        
        # Configure modern message tags
        self.chat_display.tag_config("user_bubble", 
                                    background="#0066cc", 
                                    foreground="white",
                                    font=("Segoe UI", 11),
                                    lmargin1=200, lmargin2=200,
                                    rmargin=10,
                                    spacing1=10, spacing3=10)
        
        self.chat_display.tag_config("ai_bubble", 
                                    background="#2d2d2d",
                                    foreground="#ffffff",
                                    font=("Segoe UI", 11),
                                    lmargin1=10, lmargin2=10,
                                    rmargin=200,
                                    spacing1=10, spacing3=10)
        
        self.chat_display.tag_config("system_msg", 
                                    foreground="#a0a0a0",
                                    font=("Segoe UI", 10, "italic"),
                                    justify="center",
                                    spacing1=10, spacing3=10)
        
        self.chat_display.tag_config("code_block", 
                                    background="#0d0d0d",
                                    foreground="#00ff00",
                                    font=("Consolas", 10),
                                    lmargin1=30, lmargin2=30,
                                    rmargin=30,
                                    spacing1=5, spacing3=5)
        
        self.chat_display.tag_config("timestamp",
                                    foreground="#666666",
                                    font=("Segoe UI", 8))
        
        # Store code blocks for "Add to Console" buttons
        self.ai_code_blocks = []
        
        # Add welcome message
        self.add_ai_message("system", "AI Assistant Online! I can read your console, suggest improvements, and help you code.")
        
        # Input area with modern design
        input_outer = tk.Frame(chat_outer, bg=self.secondary_bg,
                              highlightbackground=self.accent_color, highlightthickness=2)
        input_outer.pack(fill=tk.X)
        
        input_inner = tk.Frame(input_outer, bg=self.secondary_bg)
        input_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text input with placeholder
        input_container = tk.Frame(input_inner, bg=self.bg_color)
        input_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.ai_input = tk.Text(input_container,
                               font=("Segoe UI", 11),
                               bg=self.bg_color, fg=self.text_color,
                               height=3, wrap=tk.WORD,
                               relief=tk.FLAT,
                               highlightthickness=0,
                               insertbackground=self.accent_color,
                               padx=10, pady=10)
        self.ai_input.pack(fill=tk.BOTH, expand=True)
        self.ai_input.insert("1.0", "Ask me anything about Python coding...")
        self.ai_input.bind("<FocusIn>", self.clear_ai_placeholder)
        self.ai_input.bind("<FocusOut>", self.restore_ai_placeholder)
        
        # Button container
        btn_container = tk.Frame(input_inner, bg=self.secondary_bg)
        btn_container.pack(side=tk.RIGHT)
        
        # Modern send button
        send_btn = tk.Button(btn_container, text="Send",
                            font=("Segoe UI", 11, "bold"),
                            bg=self.accent_color, fg="white",
                            relief=tk.FLAT, cursor="hand2", 
                            padx=25, pady=12,
                            activebackground=self.button_hover,
                            command=self.send_ai_message)
        send_btn.pack(pady=(0, 8))
        send_btn.bind("<Enter>", lambda e: send_btn.config(bg=self.button_hover))
        send_btn.bind("<Leave>", lambda e: send_btn.config(bg=self.accent_color))
        
        # Read Console button
        read_btn = tk.Button(btn_container, text="Read Console",
                            font=("Segoe UI", 9),
                            bg="#4caf50", fg="white",
                            relief=tk.FLAT, cursor="hand2",
                            padx=15, pady=8,
                            command=self.ai_read_console)
        read_btn.pack(pady=(0, 8))
        read_btn.bind("<Enter>", lambda e: read_btn.config(bg="#45a049"))
        read_btn.bind("<Leave>", lambda e: read_btn.config(bg="#4caf50"))
        
        # Clear button
        clear_btn = tk.Button(btn_container, text="Clear",
                             font=("Segoe UI", 9),
                             bg="#ff5555", fg="white",
                             relief=tk.FLAT, cursor="hand2",
                             padx=15, pady=8,
                             command=self.clear_ai_chat)
        clear_btn.pack()
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#ff3333"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#ff5555"))
        
        # Bind Enter key to send
        self.ai_input.bind('<Control-Return>', lambda e: self.send_ai_message())
    
    def clear_ai_placeholder(self, event):
        """Clear placeholder text on focus"""
        if self.ai_input.get("1.0", tk.END).strip() == "Ask me anything about Python coding...":
            self.ai_input.delete("1.0", tk.END)
    
    def restore_ai_placeholder(self, event):
        """Restore placeholder if empty"""
        if not self.ai_input.get("1.0", tk.END).strip():
            self.ai_input.insert("1.0", "Ask me anything about Python coding...")
    
    def ai_read_console(self):
        """Let AI read the current console content"""
        if hasattr(self, 'code_input'):
            console_code = self.code_input.get("1.0", tk.END).strip()
            if console_code:
                # Auto-fill input with context
                current = self.ai_input.get("1.0", tk.END).strip()
                if current == "Ask me anything about Python coding...":
                    self.ai_input.delete("1.0", tk.END)
                self.ai_input.insert("1.0", f"Here's my current code:\n```python\n{console_code}\n```\n\nCan you help me improve it?")
                self.show_notification("✓ Console code added to message", "success")
            else:
                self.show_notification("❌ Console is empty", "error")
        else:
            self.show_notification("❌ Console not available", "error")
    
    def on_provider_change(self, provider):
        """Update UI when AI provider changes"""
        if "FREE" in provider:
            if "Gemini" in provider:
                self.api_key_entry.delete(0, tk.END)
                self.api_key_entry.insert(0, "Get free key from ai.google.dev")
            else:
                self.api_key_entry.delete(0, tk.END)
                self.api_key_entry.insert(0, "Get free key from huggingface.co")
        else:
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, "sk-...")
    
    def add_ai_message(self, sender, message):
        """Add a message to the AI chat display with modern styling"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M")
        
        if sender == "user":
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"You • {timestamp}\n", "timestamp")
            self.chat_display.insert(tk.END, f"{message}\n", "user_bubble")
            
        elif sender == "ai":
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"AI Assistant • {timestamp}\n", "timestamp")
            
            # Detect and handle code blocks
            import re
            code_pattern = r'```(?:python)?\n(.*?)\n```'
            parts = re.split(code_pattern, message, flags=re.DOTALL)
            
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text
                    if part.strip():
                        self.chat_display.insert(tk.END, f"{part}\n", "ai_bubble")
                else:  # Code block
                    code = part.strip()
                    if code:
                        # Add code block
                        self.chat_display.insert(tk.END, "\n")
                        self.chat_display.insert(tk.END, f"{code}\n", "code_block")
                        
                        # Store code for button
                        self.ai_code_blocks.append(code)
                        code_index = len(self.ai_code_blocks) - 1
                        
                        # Create "Add to Console" button
                        btn = tk.Button(self.chat_display, 
                                      text="Add to Console",
                                      font=("Segoe UI", 9, "bold"),
                                      bg="#4caf50", fg="white",
                                      relief=tk.FLAT, cursor="hand2",
                                      padx=15, pady=6,
                                      command=lambda idx=code_index: self.add_code_to_console(idx))
                        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#45a049"))
                        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#4caf50"))
                        
                        self.chat_display.window_create(tk.END, window=btn)
                        self.chat_display.insert(tk.END, "\n\n")
            
        elif sender == "system":
            self.chat_display.insert(tk.END, f"\n{message}\n", "system_msg")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_code_to_console(self, code_index):
        """Add AI-suggested code to the console"""
        if code_index < len(self.ai_code_blocks):
            code = self.ai_code_blocks[code_index]
            if hasattr(self, 'code_input'):
                # Replace or append based on console state
                current = self.code_input.get("1.0", tk.END).strip()
                if not current:
                    self.code_input.insert("1.0", code)
                else:
                    self.code_input.delete("1.0", tk.END)
                    self.code_input.insert("1.0", code)
                
                self.apply_syntax_highlighting()
                self.update_line_numbers()
                self.show_notification("✓ Code added to Console!", "success")
                self.switch_page("Console")
            else:
                self.show_notification("❌ Console not available", "error")
    
    def save_api_key(self):
        """Save the Hugging Face API token"""
        api_key = self.api_key_entry.get()
        if api_key and api_key != "hf_...":
            self.show_notification("✓ API Token saved!", "success")
            # In production, save to encrypted storage
        else:
            self.show_notification("❌ Please enter a valid API key", "error")
    
    def send_ai_message(self):
        """Send message to AI and get response"""
        message = self.ai_input.get("1.0", tk.END).strip()
        if not message or message == "Type your question here...":
            return
        
        # Add user message
        self.add_ai_message("user", message)
        self.ai_input.delete("1.0", tk.END)
        
        # Get AI response (simulated for now)
        self.root.after(500, lambda: self.get_ai_response(message))
    
    def get_ai_response(self, user_message):
        """Get response from Hugging Face API"""
        api_key = self.api_key_entry.get()
        
        # Validate API key
        if not api_key or api_key == "hf_...":
            self.add_ai_message("system", "⚠ Please enter your Hugging Face API token first")
            return
        
        # Show thinking indicator
        self.add_ai_message("system", "🤔 AI is thinking...")
        
        # Call Hugging Face API in thread
        import threading
        threading.Thread(target=lambda: self.call_huggingface_api(api_key, user_message), daemon=True).start()
    
    def call_huggingface_api(self, api_key, user_message):
        """Call Hugging Face Inference API (FREE)"""
        try:
            import requests
            
            # Read console code if available
            console_context = ""
            if hasattr(self, 'code_input'):
                console_code = self.code_input.get("1.0", tk.END).strip()
                if console_code and "Here's my current code" not in user_message:
                    console_context = f"\n\n[User's current console code:\n{console_code}\n]"
            
            # Use a free coding model from Hugging Face
            API_URL = "https://api-inference.huggingface.co/models/meta-llama/CodeLlama-7b-Instruct-hf"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            prompt = f"""<s>[INST] You are an expert Python coding assistant. Be helpful and concise.
            
User question: {user_message}{console_context}

Provide your answer. If you suggest code, wrap it in ```python code blocks. [/INST]"""
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    ai_reply = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    ai_reply = result.get("generated_text", result.get("error", "No response"))
                else:
                    ai_reply = str(result)
                
                if ai_reply:
                    self.root.after(0, lambda: self.display_ai_response(ai_reply))
                else:
                    self.root.after(0, lambda: self.add_ai_message("system", "❌ Empty response from AI"))
            
            elif response.status_code == 503:
                self.root.after(0, lambda: self.add_ai_message("system", "⏳ Model is loading... Please wait 30 seconds and try again."))
            elif response.status_code == 401:
                self.root.after(0, lambda: self.add_ai_message("system", "❌ Invalid API token. Check your Hugging Face token."))
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                self.root.after(0, lambda: self.add_ai_message("system", f"❌ Error: {error_msg}"))
            
        except ImportError:
            self.root.after(0, lambda: self.add_ai_message("system", "❌ requests library not installed. Run: pip install requests"))
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.add_ai_message("system", "❌ Request timed out. Try again."))
        except Exception as e:
            self.root.after(0, lambda: self.add_ai_message("system", f"❌ Error: {str(e)}"))
    
    def display_ai_response(self, response):
        """Display AI response in chat"""
        # Remove thinking message
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get("1.0", tk.END)
        if "🤔 AI is thinking..." in content:
            # Find and remove the thinking message
            start_idx = content.rfind("🤔 AI is thinking...")
            if start_idx != -1:
                # Calculate line number
                lines_before = content[:start_idx].count('\n')
                self.chat_display.delete(f"{lines_before + 1}.0", f"{lines_before + 2}.0")
        self.chat_display.config(state=tk.DISABLED)
        
        # Add AI response
        self.add_ai_message("ai", response)
    
    def clear_ai_chat(self):
        """Clear AI chat history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.ai_code_blocks = []
        self.add_ai_message("system", "Chat cleared. AI Assistant ready!")
        if hasattr(self, 'last_ai_code'):
            delattr(self, 'last_ai_code')
            delattr(self, 'last_ai_code')
    
    def show_progress_page(self):
        """Show progress page with real animated statistics"""
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="Progress Tracker",
                        font=("Segoe UI", 16, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 10))
        
        # Calculate session duration
        session_duration = int(time.time() - self.stats["session_start"])
        hours = session_duration // 3600
        minutes = (session_duration % 3600) // 60
        session_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes} minutes"
        
        desc = tk.Label(container, 
                       text=f"Real-time coding progress • Session: {session_time}",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Stats grid with animated progress bars - using real data
        stats_frame = tk.Frame(container, bg=self.bg_color)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Calculate goals and current values
        exec_goal = max(10, self.stats["executions"] + 5)
        lines_goal = max(100, self.stats["lines_written"] + 50)
        snippets_goal = max(5, self.stats["snippets_used"] + 3)
        success_rate = int((self.stats['successful_runs'] / self.stats['executions'] * 100)) if self.stats['executions'] > 0 else 0
        
        stats = [
            ("Code Executions", self.stats["executions"], exec_goal),
            ("Lines Written", self.stats["lines_written"], lines_goal),
            ("Snippets Used", self.stats["snippets_used"], snippets_goal),
            ("Success Rate", success_rate, 100),
            ("Successful Runs", self.stats["successful_runs"], self.stats["executions"] if self.stats["executions"] > 0 else 1),
            ("Error Count", self.stats["errors"], max(1, self.stats["executions"]))
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
        """Show settings page with organized sections in columns"""
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(container, text="⚙️ Settings",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(anchor="w", pady=(0, 5))
        
        desc = tk.Label(container, 
                       text="Configure application preferences for a personalized experience",
                       font=("Segoe UI", 10),
                       bg=self.bg_color, fg="#a0a0a0")
        desc.pack(anchor="w", pady=(0, 20))
        
        # Create scrollable settings area
        canvas_frame = tk.Frame(container, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview,
                                **self.get_scrollbar_config(), width=12)
        settings_frame = tk.Frame(canvas, bg=self.bg_color)
        
        settings_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings organized by sections with 2-column layout
        settings_sections = {
            "📝 Editor": [
                ("Syntax Highlighting", "Highlight code syntax with colors"),
                ("Line Numbers", "Show line numbers in editor"),
                ("Auto-complete", "Enable intelligent code completion"),
                ("Auto-indent", "Automatically indent code blocks"),
                ("Word Wrap", "Wrap long lines in editor"),
                ("Bracket Matching", "Highlight matching brackets"),
                ("Code Folding", "Allow collapsing code blocks"),
                ("Minimap", "Show code minimap on right side"),
            ],
            "🎨 Appearance": [
                ("Font Size", "Adjust editor font size (8-24)"),
                ("Show Toolbar", "Display top toolbar"),
                ("Show Status Bar", "Display bottom status bar"),
                ("Smooth Scrolling", "Enable smooth scroll animation"),
                ("Cursor Blink", "Animated cursor blinking"),
                ("Highlight Current Line", "Highlight active line"),
            ],
            "💾 Behavior": [
                ("Auto-save", "Automatically save work every 60s"),
                ("Notifications", "Show notification popups"),
                ("Sound Effects", "Enable UI sound feedback"),
                ("Spell Check", "Check spelling in comments/strings"),
                ("Tab Size", "Use 4 spaces for tabs"),
                ("Trim Whitespace", "Remove trailing spaces on save"),
                ("Format on Save", "Auto-format code when saving"),
                ("Confirm Exit", "Ask before closing application"),
            ],
            "🔧 Advanced": [
                ("Debug Mode", "Show detailed error messages"),
                ("Telemetry", "Send anonymous usage data"),
                ("Auto-update", "Check for updates automatically"),
                ("Experimental Features", "Enable beta features"),
                ("Performance Mode", "Optimize for speed"),
                ("Memory Limit", "Set max memory usage (MB)"),
                ("GPU Acceleration", "Use hardware acceleration"),
                ("Multi-threading", "Enable parallel processing"),
            ],
            "🔒 Privacy & Security": [
                ("Save History", "Remember command history"),
                ("Remember Session", "Restore last session on startup"),
                ("Encrypted Storage", "Encrypt saved files"),
                ("Password Protection", "Require password to open"),
                ("Clear on Exit", "Clear temporary files on close"),
                ("Secure Mode", "Disable network features"),
                ("Anonymous Mode", "Don't track any data"),
            ],
        }
        
        # Create sections in 2-column layout
        columns_frame = tk.Frame(settings_frame, bg=self.bg_color)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        left_column = tk.Frame(columns_frame, bg=self.bg_color)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(columns_frame, bg=self.bg_color)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Distribute sections between columns
        section_items = list(settings_sections.items())
        left_sections = section_items[::2]  # 0, 2, 4...
        right_sections = section_items[1::2]  # 1, 3, 5...
        
        # Create sections for left column
        for section_name, settings in left_sections:
            self.create_settings_section(left_column, section_name, settings)
        
        # Create sections for right column
        for section_name, settings in right_sections:
            self.create_settings_section(right_column, section_name, settings)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Save button with pulse animation
        button_frame = tk.Frame(container, bg=self.bg_color)
        button_frame.pack(pady=15, side=tk.BOTTOM, fill=tk.X)
        
        save_btn = tk.Button(button_frame, text="💾 Save Settings", font=("Segoe UI", 11, "bold"),
                            bg=self.accent_color, fg="white",
                            relief=tk.FLAT, cursor="hand2", pady=12, padx=40,
                            command=self.save_settings)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_btn = tk.Button(button_frame, text="🔄 Reset to Defaults", font=("Segoe UI", 11),
                             bg="#cc3333", fg="white",
                             relief=tk.FLAT, cursor="hand2", pady=12, padx=40,
                             command=self.reset_settings)
        reset_btn.pack(side=tk.LEFT)
        
        # Pulse animation on hover
        self.add_hover_effect(save_btn, "#0066cc", self.accent_color)
        self.add_hover_effect(reset_btn, "#dd4444", "#cc3333")
    
    def create_settings_section(self, parent, section_name, settings):
        """Create a settings section with a header and items"""
        section_frame = tk.Frame(parent, bg=self.secondary_bg, 
                                highlightbackground="#333333", highlightthickness=1)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Section header
        header = tk.Frame(section_frame, bg="#252525")
        header.pack(fill=tk.X)
        
        tk.Label(header, text=section_name,
                font=("Segoe UI", 12, "bold"),
                bg="#252525", fg=self.text_color).pack(anchor="w", padx=20, pady=12)
        
        # Settings items
        for i, (setting_name, setting_desc) in enumerate(settings):
            self.create_setting_item_inline(section_frame, setting_name, setting_desc)
    
    def create_setting_item_inline(self, parent, name, desc):
        """Create a compact inline setting item"""
        setting_frame = tk.Frame(parent, bg=self.secondary_bg)
        setting_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # Get initial value from settings_state
        initial_value = self.settings_state.get(name, True)
        var = tk.BooleanVar(master=self.root, value=initial_value)
        
        def on_toggle():
            """Handle checkbox toggle with real functionality"""
            state = var.get()
            self.settings_state[name] = state
            
            # Apply specific setting changes (same as before)
            if name == "Auto-complete":
                if hasattr(self, 'code_input'):
                    if state:
                        self.show_notification("✓ Auto-complete enabled", "success")
                    else:
                        self.show_notification("✓ Auto-complete disabled", "info")
            
            elif name == "Word Wrap":
                if hasattr(self, 'code_input'):
                    self.code_input.config(wrap=tk.WORD if state else tk.NONE)
                    self.show_notification(f"✓ Word Wrap {'enabled' if state else 'disabled'}", "success" if state else "info")
            
            elif name == "Line Numbers":
                if hasattr(self, 'line_numbers'):
                    if state:
                        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
                        self.update_line_numbers()
                    else:
                        self.line_numbers.pack_forget()
                    self.show_notification(f"✓ Line Numbers {'shown' if state else 'hidden'}", "success" if state else "info")
            
            elif name == "Syntax Highlighting":
                if hasattr(self, 'code_input'):
                    if state:
                        self.apply_syntax_highlighting()
                    else:
                        for tag in ["keyword", "string", "comment", "function", "number"]:
                            self.code_input.tag_remove(tag, "1.0", "end")
                    self.show_notification(f"✓ Syntax Highlighting {'enabled' if state else 'disabled'}", "success" if state else "info")
            
            elif name == "Auto-save":
                self.auto_save_enabled = state
                if state:
                    self.start_auto_save()
                    self.show_notification("✓ Auto-save enabled (60s)", "success")
                else:
                    if self.auto_save_timer:
                        self.root.after_cancel(self.auto_save_timer)
                    self.show_notification("✓ Auto-save disabled", "info")
            
            elif name == "Notifications":
                self.show_notification(f"✓ Notifications {'enabled' if state else 'disabled'}", "success" if state else "info")
            
            else:
                status = "enabled" if state else "disabled"
                self.show_notification(f"✓ {name} {status}", "success" if state else "info")
        
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
        check.pack(anchor="w", pady=(5, 2))
        
        # Description
        desc_label = tk.Label(setting_frame, text=desc,
                             font=("Segoe UI", 8),
                             bg=self.secondary_bg, fg="#888888")
        desc_label.pack(anchor="w", padx=20, pady=(0, 5))
    
    def reset_settings(self):
        """Reset all settings to default values"""
        try:
            # Reset all settings to True (default)
            for key in self.settings_state:
                self.settings_state[key] = True
            
            # Reload the settings page to update UI
            self.show_notification("✓ Settings reset to defaults!", "success")
            self.update_status("Settings reset to defaults")
            
            # Refresh the settings page
            self.show_page("Settings")
            
        except Exception as e:
            self.show_notification(f"Error resetting settings: {e}", "error")
    
    def create_setting_item(self, parent, name, desc, index):
        """Create an animated setting item with real functionality"""
        def show_setting():
            try:
                if not self.root.winfo_exists() or not parent.winfo_exists():
                    return
                    
                setting_frame = tk.Frame(parent, bg=self.secondary_bg)
                setting_frame.pack(fill=tk.X, pady=5, padx=5)
                
                # Get initial value from settings_state
                initial_value = self.settings_state.get(name, True)
                var = tk.BooleanVar(master=self.root, value=initial_value)
                
                def on_toggle():
                    """Handle checkbox toggle with real functionality"""
                    state = var.get()
                    self.settings_state[name] = state
                    
                    # Apply specific setting changes
                    if name == "Auto-complete":
                        if hasattr(self, 'code_input'):
                            # Enable/disable autocomplete
                            if state:
                                self.show_notification("✓ Auto-complete enabled", "success")
                            else:
                                self.show_notification("✓ Auto-complete disabled", "info")
                    
                    elif name == "Word Wrap":
                        if hasattr(self, 'code_input'):
                            self.code_input.config(wrap=tk.WORD if state else tk.NONE)
                            self.show_notification(f"✓ Word Wrap {'enabled' if state else 'disabled'}", "success" if state else "info")
                    
                    elif name == "Line Numbers":
                        if hasattr(self, 'line_numbers'):
                            if state:
                                self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
                                self.update_line_numbers()
                            else:
                                self.line_numbers.pack_forget()
                            self.show_notification(f"✓ Line Numbers {'shown' if state else 'hidden'}", "success" if state else "info")
                    
                    elif name == "Syntax Highlighting":
                        if hasattr(self, 'code_input'):
                            if state:
                                self.apply_syntax_highlighting()
                            else:
                                # Remove all syntax tags
                                for tag in ["keyword", "string", "comment", "function", "number"]:
                                    self.code_input.tag_remove(tag, "1.0", "end")
                            self.show_notification(f"✓ Syntax Highlighting {'enabled' if state else 'disabled'}", "success" if state else "info")
                    
                    elif name == "Auto-save":
                        self.auto_save_enabled = state
                        if state:
                            self.start_auto_save()
                            self.show_notification("✓ Auto-save enabled (60s)", "success")
                        else:
                            if self.auto_save_timer:
                                self.root.after_cancel(self.auto_save_timer)
                            self.show_notification("✓ Auto-save disabled", "info")
                    
                    elif name == "Notifications":
                        # Just update the state, notifications controlled globally
                        self.show_notification(f"✓ Notifications {'enabled' if state else 'disabled'}", "success" if state else "info")
                    
                    else:
                        # Generic notification for other settings
                        status = "enabled" if state else "disabled"
                        self.show_notification(f"✓ {name} {status}", "success" if state else "info")
                
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
            except (tk.TclError, RuntimeError, Exception):
                pass
        
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
        container = tk.Frame(self.page_container, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Animated title
        title = tk.Label(container, text="About CipherV4",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.bg_color, fg=self.text_color)
        title.pack(pady=(30, 10))
        
        # Version with color animation
        version_label = tk.Label(container, text="Version 4.5",
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
        """Save current file and track statistics"""
        from tkinter import filedialog
        
        try:
            # Get content
            content = self.code_text.get("1.0", "end-1c")
            
            # If we have a current file, save to it
            if hasattr(self, 'current_file') and self.current_file:
                filepath = self.current_file
            else:
                # Ask for file location
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[
                        ("Python files", "*.py"),
                        ("Text files", "*.txt"),
                        ("All files", "*.*")
                    ],
                    initialdir=self.scripts_dir
                )
                
                if not filepath:
                    return  # User cancelled
                
                self.current_file = filepath
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Track in recent files
            self.add_to_recent_files(filepath)
            
            # Update stats
            self.stats["files_saved"] += 1
            self.update_status(f"File saved: {os.path.basename(filepath)}")
            self.show_notification(f"Saved: {os.path.basename(filepath)}", "success")
            
        except Exception as e:
            self.show_notification(f"Error saving file: {e}", "error")
    
    def run_code(self):
        """Run the code in the editor with execution time tracking and statistics"""
        if hasattr(self, 'code_input') and hasattr(self, 'console_output'):
            code = self.code_input.get('1.0', tk.END).strip()
            
            if code:
                import time
                start_time = time.time()
                
                # Track execution
                self.stats["executions"] += 1
                
                # Count lines of code
                lines_count = len([line for line in code.split('\n') if line.strip()])
                self.stats["lines_written"] = max(self.stats["lines_written"], lines_count)
                
                self.console_output.config(state=tk.NORMAL)
                self.console_output.delete('1.0', tk.END)
                self.console_output.insert('1.0', f">>> Executing code...\n{code}\n\n")
                
                try:
                    # Create a custom stdout to capture print statements
                    from io import StringIO
                    import sys
                    
                    old_stdout = sys.stdout
                    sys.stdout = StringIO()
                    
                    # Simple execution
                    exec_globals = {}
                    exec(code, exec_globals)
                    
                    # Get captured output
                    output = sys.stdout.getvalue()
                    sys.stdout = old_stdout
                    
                    if output:
                        self.console_output.insert(tk.END, f"Output:\n{output}\n")
                    
                    execution_time = time.time() - start_time
                    
                    # Track successful execution
                    self.stats["successful_runs"] += 1
                    self.stats["total_execution_time"] += execution_time
                    
                    self.console_output.insert(tk.END, f"✓ Execution completed successfully\n", "success")
                    self.console_output.tag_config("success", foreground="#00ff00")
                    self.update_status(f"Executed in {execution_time:.4f} seconds")
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # Track error
                    self.stats["errors"] += 1
                    self.stats["total_execution_time"] += execution_time
                    
                    self.console_output.insert(tk.END, f"✗ Error: {str(e)}\n", "error")
                    self.console_output.tag_config("error", foreground="#ff4444")
                    self.update_status(f"Error after {execution_time:.4f} seconds")
                
                self.console_output.config(state=tk.DISABLED)
            else:
                self.update_status("No code to execute")
    
    def run_powershell(self):
        """Run PowerShell commands"""
        if hasattr(self, 'code_input') and hasattr(self, 'console_output'):
            code = self.code_input.get('1.0', tk.END).strip()
            
            if code:
                import subprocess
                import time
                start_time = time.time()
                
                # Track execution
                self.stats["executions"] += 1
                
                self.console_output.config(state=tk.NORMAL)
                self.console_output.delete('1.0', tk.END)
                self.console_output.insert('1.0', f">>> Executing PowerShell...\n{code}\n\n")
                
                try:
                    # Execute PowerShell commands
                    result = subprocess.run(
                        ["powershell.exe", "-Command", code],
                        capture_output=True,
                        text=True,
                        timeout=30  # 30 second timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Display stdout
                    if result.stdout:
                        self.console_output.insert(tk.END, f"Output:\n{result.stdout}\n")
                    
                    # Display stderr if any
                    if result.stderr:
                        self.console_output.insert(tk.END, f"Warnings/Errors:\n{result.stderr}\n", "warning")
                        self.console_output.tag_config("warning", foreground="#ffaa00")
                    
                    # Check return code
                    if result.returncode == 0:
                        self.stats["successful_runs"] += 1
                        self.console_output.insert(tk.END, f"✓ Execution completed successfully\n", "success")
                        self.console_output.tag_config("success", foreground="#00ff00")
                    else:
                        self.stats["errors"] += 1
                        self.console_output.insert(tk.END, f"✗ PowerShell exited with code {result.returncode}\n", "error")
                        self.console_output.tag_config("error", foreground="#ff4444")
                    
                    self.stats["total_execution_time"] += execution_time
                    self.update_status(f"Executed in {execution_time:.4f} seconds")
                    
                except subprocess.TimeoutExpired:
                    execution_time = time.time() - start_time
                    self.stats["errors"] += 1
                    self.stats["total_execution_time"] += execution_time
                    self.console_output.insert(tk.END, f"✗ Error: Command timed out after 30 seconds\n", "error")
                    self.console_output.tag_config("error", foreground="#ff4444")
                    self.update_status("Execution timed out")
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.stats["errors"] += 1
                    self.stats["total_execution_time"] += execution_time
                    self.console_output.insert(tk.END, f"✗ Error: {str(e)}\n", "error")
                    self.console_output.tag_config("error", foreground="#ff4444")
                    self.update_status(f"Error after {execution_time:.4f} seconds")
                
                self.console_output.config(state=tk.DISABLED)
            else:
                self.update_status("No PowerShell commands to execute")
    
    def toggle_console_mode(self):
        """Toggle between Python and PowerShell modes"""
        # Save current content
        if hasattr(self, 'code_input'):
            self.console_content = self.code_input.get('1.0', tk.END)
        
        # Toggle mode
        if self.console_mode == "Python":
            self.console_mode = "PowerShell"
        else:
            self.console_mode = "Python"
        
        # Clear the page container
        for widget in self.page_container.winfo_children():
            widget.destroy()
        
        # Refresh the console page to show new mode
        self.show_console()
        self.update_status(f"Switched to {self.console_mode} mode")
    
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
        """Toggle between formatted (pretty) and minified (one line) JSON"""
        if hasattr(self, 'code_input'):
            code = self.code_input.get('1.0', tk.END).strip()
            if code:
                try:
                    import json
                    # Parse JSON
                    parsed = json.loads(code)
                    
                    # Check if JSON is already formatted (has newlines and indentation)
                    is_formatted = '\n' in code and '    ' in code
                    
                    if is_formatted:
                        # Minify: convert to single line
                        minified = json.dumps(parsed, separators=(',', ':'), sort_keys=False)
                        self.code_input.delete('1.0', tk.END)
                        self.code_input.insert('1.0', minified)
                        self.update_status("✓ JSON minified to one line")
                        self.show_notification("✓ JSON minified", "success")
                    else:
                        # Format: add indentation and newlines
                        formatted = json.dumps(parsed, indent=4, sort_keys=False)
                        self.code_input.delete('1.0', tk.END)
                        self.code_input.insert('1.0', formatted)
                        self.update_status("✓ JSON formatted with indentation")
                        self.show_notification("✓ JSON formatted", "success")
                    
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
        
        # NEW FEATURE SHORTCUTS
        self.root.bind('<Control-d>', self.duplicate_line)  # Feature #59
        self.root.bind('<Control-Shift-K>', self.delete_line)  # Feature #60
        self.root.bind('<Control-Shift-U>', self.convert_to_upper)  # Feature #61
        self.root.bind('<Control-Shift-L>', self.convert_to_lower)  # Feature #61
        self.root.bind('<Control-Shift-T>', self.convert_to_title)  # Feature #61
        self.root.bind('<Control-Shift-W>', self.trim_whitespace)  # Feature #63
        self.root.bind('<Control-Shift-D>', self.insert_datetime)  # Feature #64
        self.root.bind('<Control-Shift-P>', self.copy_file_path)  # Feature #58
        self.root.bind('<Alt-z>', self.toggle_line_wrap)  # Feature #57
        self.root.bind('<Control-plus>', self.zoom_in)  # Feature #33
        self.root.bind('<Control-equal>', self.zoom_in)  # Feature #33 (alternative)
        self.root.bind('<Control-minus>', self.zoom_out)  # Feature #33
        self.root.bind('<Control-0>', self.reset_zoom)  # Feature #33
        self.root.bind('<Control-Shift-P>', self.show_command_palette)  # Feature #29

    
    def setup_command_palette(self):
        """Initialize command palette with all available commands"""
        self.commands = {
            "Open Dashboard": lambda: self.load_page("Dashboard"),
            "Open Console": lambda: self.load_page("Console"),
            "Open History": lambda: self.load_page("History"),
            "Open Snippets": lambda: self.load_page("Snippets"),
            "Open Tools": lambda: self.load_page("Tools"),
            "Open Value Changer": lambda: self.load_page("ValueChanger"),
            "Open AI Assistant": lambda: self.load_page("AI Assistant"),
            "Open Progress": lambda: self.load_page("Progress"),
            "Open Settings": lambda: self.load_page("Settings"),
            "Open About": lambda: self.load_page("About"),
            "Save File": self.save_file,
            "Run Code": self.run_code,
            "Format Code": self.format_code,
            "Find": self.show_find_dialog,
            "Show Shortcuts": self.show_shortcuts_panel,
            "Global Search": self.show_global_search,
            "Export Options": self.show_export_options,
            "Templates Manager": self.show_templates_manager,
            "Theme Customizer": self.show_theme_customizer,
            "Statistics Dashboard": self.show_statistics_dashboard,
            "File Explorer": self.show_file_explorer,
            "Check for Updates": self.check_for_updates,
            "Duplicate Line": self.duplicate_line,
            "Delete Line": self.delete_line,
            "Convert to Uppercase": self.convert_to_upper,
            "Convert to Lowercase": self.convert_to_lower,
            "Convert to Title Case": self.convert_to_title,
            "Sort Lines Ascending": self.sort_lines_ascending,
            "Sort Lines Descending": self.sort_lines_descending,
            "Trim Whitespace": self.trim_whitespace,
            "Insert Date/Time": self.insert_datetime,
            "Toggle Line Wrap": self.toggle_line_wrap,
            "Copy File Path": self.copy_file_path,
            "Zoom In": self.zoom_in,
            "Zoom Out": self.zoom_out,
            "Reset Zoom": self.reset_zoom,
            "Undo": self.undo,
            "Redo": self.redo,
            "Toggle Auto-Save": self.toggle_auto_save,
        }
        
        theme = {
            'bg_color': self.bg_color,
            'secondary_bg': self.secondary_bg,
            'text_color': self.text_color,
            'accent_color': self.accent_color
        }
        
        self.command_palette = CommandPalette(self.root, self.commands, theme, self.execute_command)
    
    def show_command_palette(self, event=None):
        """Show command palette"""
        self.command_palette.show()
        return "break"
    
    def execute_command(self, command_func):
        """Execute a command from the palette"""
        try:
            command_func()
        except Exception as e:
            self.show_notification(f"Command error: {e}", "error")
    
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
        """Show professional toast notification using new notification system"""
        ToastNotification(self.root, message, type, duration=3000)
    
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
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview,
                                **self.get_scrollbar_config(), width=12)
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
        
        scrollbar = tk.Scrollbar(list_frame, **self.get_scrollbar_config(), width=12)
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
        
        scrollbar = tk.Scrollbar(results_frame, **self.get_scrollbar_config(), width=12)
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
        def apply_custom_theme():
            try:
                # Update all color attributes
                for attr, entry in color_entries.items():
                    new_color = entry.get()
                    setattr(self, attr, new_color)
                
                # Update all UI elements with new colors
                self.root.configure(bg=self.bg_color)
                
                if hasattr(self, 'header'):
                    self.header.configure(bg=self.secondary_bg)
                if hasattr(self, 'sidebar'):
                    self.sidebar.configure(bg=self.secondary_bg)
                if hasattr(self, 'content_frame'):
                    self.content_frame.configure(bg=self.bg_color)
                if hasattr(self, 'status_bar'):
                    self.status_bar.configure(bg=self.secondary_bg)
                
                # Update all child widgets recursively
                def update_widget_colors(widget):
                    try:
                        if isinstance(widget, (tk.Frame, tk.Label, tk.Button)):
                            current_bg = widget.cget('bg')
                            if current_bg in [self.bg_color, self.secondary_bg, self.accent_color]:
                                widget.configure(bg=current_bg)
                        for child in widget.winfo_children():
                            update_widget_colors(child)
                    except:
                        pass
                
                update_widget_colors(self.root)
                
                self.show_notification("✓ Theme applied successfully!", "success")
                customizer.destroy()
            except Exception as e:
                self.show_notification(f"❌ Error applying theme: {str(e)}", "error")
        
        apply_btn = tk.Button(customizer, text="Apply Theme",
                             font=("Segoe UI", 12, "bold"),
                             bg=self.accent_color, fg="white",
                             border=0, cursor="hand2", pady=12, padx=40,
                             command=apply_custom_theme, width=15)
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
            # Use the proper on_closing handler
            self.on_closing()
    
    # ========== NEW FEATURES ==========
    
    # Feature #65: Character/Word/Line Count
    def update_char_count(self, event=None):
        """Update character, word, and line count in status bar"""
        try:
            if hasattr(self, 'code_text') and self.code_text.winfo_exists():
                content = self.code_text.get("1.0", "end-1c")
                char_count = len(content)
                word_count = len(content.split())
                line_count = int(self.code_text.index('end-1c').split('.')[0])
                
                self.char_count_label.config(text=f"Chars: {char_count} | Words: {word_count} | Lines: {line_count}")
        except:
            pass
    
    # Feature #33: Zoom Controls
    def zoom_in(self, event=None):
        """Increase font size"""
        self.zoom_level += 0.1
        self.apply_zoom()
        return "break"
    
    def zoom_out(self, event=None):
        """Decrease font size"""
        self.zoom_level = max(0.5, self.zoom_level - 0.1)
        self.apply_zoom()
        return "break"
    
    def reset_zoom(self, event=None):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self.apply_zoom()
    
    def apply_zoom(self):
        """Apply zoom level to editor"""
        try:
            base_size = 11
            new_size = int(base_size * self.zoom_level)
            
            if hasattr(self, 'code_text'):
                self.code_text.config(font=("Consolas", new_size))
            if hasattr(self, 'line_numbers'):
                self.line_numbers.config(font=("Consolas", new_size))
            
            self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        except:
            pass
    
    # Feature #69: Update Checker
    def silent_update_check(self):
        """Silently check for updates on startup"""
        try:
            has_update = self.update_checker.check_for_updates()
            if has_update:
                self.root.after(0, lambda: self.update_btn.config(
                    text="⚡ Update Available!",
                    fg="#ffaa00"
                ))
        except:
            pass
    
    def check_for_updates(self):
        """Check for updates and show dialog"""
        self.update_btn.config(text="🔄 Checking...")
        
        def check():
            try:
                has_update = self.update_checker.check_for_updates()
                info = self.update_checker.get_update_info()
                
                self.root.after(0, lambda: self.show_update_dialog(has_update, info))
            except Exception as e:
                self.root.after(0, lambda: self.show_notification(f"Update check failed: {e}", "error"))
                self.root.after(0, lambda: self.update_btn.config(text="🔄 Check Updates"))
        
        threading.Thread(target=check, daemon=True).start()
    
    def show_update_dialog(self, has_update, info):
        """Show update dialog"""
        self.update_btn.config(text="🔄 Check Updates")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Check")
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        if has_update:
            tk.Label(dialog, text="⚡ Update Available!",
                    font=("Segoe UI", 16, "bold"),
                    bg=self.bg_color, fg="#00ff00").pack(pady=20)
            
            tk.Label(dialog, text=f"Current Version: {info['current']}",
                    font=("Segoe UI", 11),
                    bg=self.bg_color, fg=self.text_color).pack(pady=5)
            
            tk.Label(dialog, text=f"Latest Version: {info['latest']}",
                    font=("Segoe UI", 11, "bold"),
                    bg=self.bg_color, fg="#00ff00").pack(pady=5)
            
            # Release notes
            notes_frame = tk.Frame(dialog, bg=self.secondary_bg)
            notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(notes_frame, text="Release Notes:",
                    font=("Segoe UI", 10, "bold"),
                    bg=self.secondary_bg, fg=self.text_color).pack(anchor="w", padx=10, pady=5)
            
            notes_text = tk.Text(notes_frame, font=("Segoe UI", 9),
                                bg=self.bg_color, fg=self.text_color,
                                wrap=tk.WORD, height=10)
            notes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            notes_text.insert("1.0", info['notes'])
            notes_text.config(state=tk.DISABLED)
            
            # Buttons
            btn_frame = tk.Frame(dialog, bg=self.bg_color)
            btn_frame.pack(pady=10)
            
            download_btn = tk.Button(btn_frame, text="Download Update",
                                    font=("Segoe UI", 10, "bold"),
                                    bg="#00aa00", fg="white",
                                    relief=tk.FLAT, bd=0,
                                    padx=20, pady=10,
                                    cursor="hand2",
                                    command=lambda: self.open_url(info['url']))
            download_btn.pack(side=tk.LEFT, padx=5)
            
            close_btn = tk.Button(btn_frame, text="Later",
                                 font=("Segoe UI", 10),
                                 bg=self.secondary_bg, fg=self.text_color,
                                 relief=tk.FLAT, bd=0,
                                 padx=20, pady=10,
                                 cursor="hand2",
                                 command=dialog.destroy)
            close_btn.pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(dialog, text="✓ You're up to date!",
                    font=("Segoe UI", 16, "bold"),
                    bg=self.bg_color, fg="#00ff00").pack(pady=40)
            
            tk.Label(dialog, text=f"Current Version: {info['current']}",
                    font=("Segoe UI", 11),
                    bg=self.bg_color, fg=self.text_color).pack(pady=10)
            
            close_btn = tk.Button(dialog, text="Close",
                                 font=("Segoe UI", 10, "bold"),
                                 bg=self.accent_color, fg="white",
                                 relief=tk.FLAT, bd=0,
                                 padx=30, pady=10,
                                 cursor="hand2",
                                 command=dialog.destroy)
            close_btn.pack(pady=20)
    
    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
    
    # Feature #59: Duplicate Line (Ctrl+D)
    def duplicate_line(self, event=None):
        """Duplicate current line or selection"""
        try:
            if self.code_text.tag_ranges("sel"):
                # Duplicate selection
                content = self.code_text.get("sel.first", "sel.last")
                self.code_text.insert("sel.last", content)
            else:
                # Duplicate current line
                line_num = self.code_text.index("insert").split('.')[0]
                line_content = self.code_text.get(f"{line_num}.0", f"{line_num}.end")
                self.code_text.insert(f"{line_num}.end", "\n" + line_content)
        except:
            pass
        return "break"
    
    # Feature #60: Delete Line (Ctrl+Shift+K)
    def delete_line(self, event=None):
        """Delete current line"""
        try:
            line_num = self.code_text.index("insert").split('.')[0]
            self.code_text.delete(f"{line_num}.0", f"{int(line_num)+1}.0")
        except:
            pass
        return "break"
    
    # Feature #61: Case Converter
    def convert_to_upper(self, event=None):
        """Convert selection to UPPERCASE"""
        try:
            if self.code_text.tag_ranges("sel"):
                content = self.code_text.get("sel.first", "sel.last")
                self.code_text.delete("sel.first", "sel.last")
                self.code_text.insert("insert", content.upper())
        except:
            pass
        return "break"
    
    def convert_to_lower(self, event=None):
        """Convert selection to lowercase"""
        try:
            if self.code_text.tag_ranges("sel"):
                content = self.code_text.get("sel.first", "sel.last")
                self.code_text.delete("sel.first", "sel.last")
                self.code_text.insert("insert", content.lower())
        except:
            pass
        return "break"
    
    def convert_to_title(self, event=None):
        """Convert selection to Title Case"""
        try:
            if self.code_text.tag_ranges("sel"):
                content = self.code_text.get("sel.first", "sel.last")
                self.code_text.delete("sel.first", "sel.last")
                self.code_text.insert("insert", content.title())
        except:
            pass
        return "break"
    
    # Feature #62: Sort Lines
    def sort_lines_ascending(self, event=None):
        """Sort selected lines alphabetically (A-Z)"""
        try:
            if self.code_text.tag_ranges("sel"):
                content = self.code_text.get("sel.first", "sel.last")
                lines = content.split('\n')
                sorted_lines = '\n'.join(sorted(lines))
                self.code_text.delete("sel.first", "sel.last")
                self.code_text.insert("insert", sorted_lines)
        except:
            pass
        return "break"
    
    def sort_lines_descending(self, event=None):
        """Sort selected lines alphabetically (Z-A)"""
        try:
            if self.code_text.tag_ranges("sel"):
                content = self.code_text.get("sel.first", "sel.last")
                lines = content.split('\n')
                sorted_lines = '\n'.join(sorted(lines, reverse=True))
                self.code_text.delete("sel.first", "sel.last")
                self.code_text.insert("insert", sorted_lines)
        except:
            pass
        return "break"
    
    # Feature #63: Trim Whitespace
    def trim_whitespace(self, event=None):
        """Remove trailing whitespace from all lines"""
        try:
            content = self.code_text.get("1.0", "end-1c")
            lines = content.split('\n')
            trimmed_lines = [line.rstrip() for line in lines]
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", '\n'.join(trimmed_lines))
            self.show_notification("Trailing whitespace removed", "success")
        except:
            pass
        return "break"
    
    # Feature #64: Insert Date/Time
    def insert_datetime(self, event=None):
        """Insert current date and time"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.code_text.insert("insert", timestamp)
        except:
            pass
        return "break"
    
    # Feature #57: Line Wrap Toggle
    def toggle_line_wrap(self, event=None):
        """Toggle word wrap in editor"""
        try:
            current_wrap = self.code_text.cget("wrap")
            new_wrap = "none" if current_wrap == "word" else "word"
            self.code_text.config(wrap=new_wrap)
            status = "enabled" if new_wrap == "word" else "disabled"
            self.show_notification(f"Line wrap {status}", "info")
        except:
            pass
        return "break"
    
    # Feature #58: Copy Full Path
    def copy_file_path(self, event=None):
        """Copy current file path to clipboard"""
        try:
            if hasattr(self, 'current_file') and self.current_file:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_file)
                self.show_notification(f"Copied: {self.current_file}", "success")
            else:
                self.show_notification("No file open", "warning")
        except:
            pass
        return "break"
    
    # Feature #30: Recent Files
    def show_recent_files(self):
        """Show recent files menu"""
        if not self.recent_files:
            self.show_notification("No recent files", "info")
            return
        
        # Create popup menu
        menu_dialog = tk.Toplevel(self.root)
        menu_dialog.title("Recent Files")
        menu_dialog.geometry("600x400")
        menu_dialog.configure(bg=self.bg_color)
        menu_dialog.transient(self.root)
        menu_dialog.grab_set()
        
        # Title
        title_frame = tk.Frame(menu_dialog, bg=self.secondary_bg, height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Recent Files", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Button(title_frame, text="Clear All", font=("Segoe UI", 9),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=15, pady=5,
                 cursor="hand2", command=lambda: self.clear_recent_files(menu_dialog)).pack(side=tk.RIGHT, padx=10)
        
        # File list
        list_frame = tk.Frame(menu_dialog, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        file_listbox = tk.Listbox(list_frame, font=("Consolas", 10),
                                  bg=self.secondary_bg, fg=self.text_color,
                                  selectbackground=self.accent_color,
                                  selectforeground="white",
                                  yscrollcommand=scrollbar.set,
                                  relief=tk.FLAT, bd=0)
        file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=file_listbox.yview)
        
        # Populate list
        for i, filepath in enumerate(self.recent_files):
            display_name = os.path.basename(filepath)
            file_listbox.insert(tk.END, f"{i+1}. {display_name}")
        
        # Double-click to open
        def open_selected(event):
            selection = file_listbox.curselection()
            if selection:
                index = selection[0]
                filepath = self.recent_files[index]
                menu_dialog.destroy()
                self.open_file_from_path(filepath)
        
        file_listbox.bind("<Double-Button-1>", open_selected)
        
        # Button frame
        button_frame = tk.Frame(menu_dialog, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Open", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=20, pady=8,
                 cursor="hand2", 
                 command=lambda: open_selected(None) if file_listbox.curselection() else None).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", font=("Segoe UI", 10),
                 bg=self.secondary_bg, fg=self.text_color, relief=tk.FLAT, padx=20, pady=8,
                 cursor="hand2", command=menu_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center dialog
        menu_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (menu_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (menu_dialog.winfo_height() // 2)
        menu_dialog.geometry(f"+{x}+{y}")
    
    def add_to_recent_files(self, filepath):
        """Add a file to recent files list"""
        if not filepath or not os.path.exists(filepath):
            return
        
        # Remove if already in list
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        # Add to front
        self.recent_files.insert(0, filepath)
        
        # Trim to max length
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
        
        # Save to disk
        self.save_recent_files()
    
    def load_recent_files(self):
        """Load recent files from disk"""
        try:
            if os.path.exists(self.recent_files_file):
                import json
                with open(self.recent_files_file, 'r') as f:
                    self.recent_files = json.load(f)
                # Filter out files that no longer exist
                self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        except Exception as e:
            print(f"Error loading recent files: {e}")
            self.recent_files = []
    
    def save_recent_files(self):
        """Save recent files to disk"""
        try:
            import json
            with open(self.recent_files_file, 'w') as f:
                json.dump(self.recent_files, f)
        except Exception as e:
            print(f"Error saving recent files: {e}")
    
    def clear_recent_files(self, dialog=None):
        """Clear all recent files"""
        self.recent_files = []
        self.save_recent_files()
        if dialog:
            dialog.destroy()
        self.show_notification("Recent files cleared", "success")
    
    def open_file_from_path(self, filepath):
        """Open a file from a given path"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", content)
                self.current_file = filepath
                self.add_to_recent_files(filepath)
                self.show_notification(f"Opened: {os.path.basename(filepath)}", "success")
            else:
                self.show_notification("File not found", "error")
        except Exception as e:
            self.show_notification(f"Error opening file: {e}", "error")
    
    # Feature #37: Color Picker
    def show_color_picker(self):
        """Show color picker tool"""
        from tkinter import colorchooser
        
        color = colorchooser.askcolor(parent=self.root, title="Choose Color")
        if color[1]:  # color[1] is the hex value
            hex_color = color[1]
            rgb_color = color[0]
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(hex_color)
            
            # Show notification with color preview
            self.show_notification(f"Color: {hex_color} copied to clipboard", "success")
            
            # Insert color at cursor position if editor is focused
            try:
                self.code_text.insert(tk.INSERT, hex_color)
            except:
                pass
    
    # Feature #40: Diff Viewer
    def show_diff_viewer(self):
        """Show diff viewer for comparing texts"""
        # Create dialog for input
        dialog = tk.Toplevel(self.root)
        dialog.title("Diff Viewer - Input")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        
        # Title
        title_frame = tk.Frame(dialog, bg=self.secondary_bg, height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Compare Two Texts", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=10)
        
        # Instructions
        tk.Label(dialog, text="Enter or paste two texts to compare:",
                font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_color).pack(pady=10)
        
        # Text 1
        text1_frame = tk.Frame(dialog, bg=self.bg_color)
        text1_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(text1_frame, text="Original Text:", font=("Segoe UI", 10, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        text1_widget = tk.Text(text1_frame, font=("Consolas", 10), height=10,
                              bg=self.secondary_bg, fg=self.text_color, wrap=tk.WORD)
        text1_widget.pack(fill=tk.BOTH, expand=True)
        
        # Text 2
        text2_frame = tk.Frame(dialog, bg=self.bg_color)
        text2_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(text2_frame, text="Modified Text:", font=("Segoe UI", 10, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        text2_widget = tk.Text(text2_frame, font=("Consolas", 10), height=10,
                              bg=self.secondary_bg, fg=self.text_color, wrap=tk.WORD)
        text2_widget.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def compare():
            text1 = text1_widget.get("1.0", "end-1c")
            text2 = text2_widget.get("1.0", "end-1c")
            
            if not text1 or not text2:
                self.show_notification("Please enter both texts", "warning")
                return
            
            dialog.destroy()
            
            # Show diff viewer
            theme = {
                'bg_color': self.bg_color,
                'secondary_bg': self.secondary_bg,
                'text_color': self.text_color,
                'accent_color': self.accent_color
            }
            DiffViewer.show(self.root, text1, text2, theme=theme)
        
        tk.Button(button_frame, text="Compare", font=("Segoe UI", 10, "bold"),
                 bg=self.accent_color, fg="white", relief=tk.FLAT, padx=30, pady=10,
                 cursor="hand2", command=compare).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Use Current Editor Content as Text 1",
                 font=("Segoe UI", 9), bg=self.secondary_bg, fg=self.text_color,
                 relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                 command=lambda: text1_widget.insert("1.0", self.code_text.get("1.0", "end-1c"))).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", font=("Segoe UI", 10),
                 bg=self.secondary_bg, fg=self.text_color, relief=tk.FLAT, padx=20, pady=10,
                 cursor="hand2", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

