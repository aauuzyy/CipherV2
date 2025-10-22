"""Code editor component with advanced features"""
import tkinter as tk
from tkinter import ttk
import re

class CodeEditor:
    """Advanced code editor with syntax highlighting and features"""
    
    def __init__(self, parent, settings, theme):
        self.parent = parent
        self.settings = settings
        self.theme = theme
        
        self.setup_editor()
        self.setup_line_numbers()
        self.setup_syntax_highlighting()
        self.setup_autocomplete()
        
    def setup_editor(self):
        """Initialize the code editor widget"""
        self.editor = tk.Text(self.parent,
                            font=("Consolas", 10),
                            bg=self.theme['secondary_bg'],
                            fg=self.theme['text_color'],
                            insertbackground=self.theme['text_color'],
                            selectbackground=self.theme['accent_color'],
                            wrap=tk.NONE,
                            undo=True,
                            maxundo=50)
        
        # Create custom scrollbar
        self.scrollbar = ttk.Scrollbar(self.parent,
                                     orient=tk.VERTICAL,
                                     command=self.editor.yview)
        self.editor.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        if self.settings.line_numbers.get():
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.editor.bind('<<Modified>>', self.on_edit)
        self.editor.bind('<KeyRelease>', self.on_key_release)
        
    def setup_line_numbers(self):
        """Initialize line numbers widget"""
        self.line_numbers = tk.Text(self.parent,
                                  width=4,
                                  font=("Consolas", 10),
                                  bg=self.theme['bg_color'],
                                  fg="#858585",
                                  state=tk.DISABLED,
                                  takefocus=0)
                                  
    def setup_syntax_highlighting(self):
        """Configure syntax highlighting"""
        # Define syntax colors
        self.syntax_colors = {
            'keyword': '#569cd6',
            'string': '#ce9178',
            'comment': '#6a9955',
            'function': '#dcdcaa',
            'number': '#b5cea8',
            'error': '#ff4444'
        }
        
        # Configure tags
        for tag, color in self.syntax_colors.items():
            self.editor.tag_configure(tag, foreground=color)
            
        # Define keywords
        self.keywords = [
            'def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for',
            'while', 'return', 'try', 'except', 'finally', 'with', 'as',
            'lambda', 'yield', 'pass', 'break', 'continue', 'True', 'False',
            'None', 'and', 'or', 'not', 'in', 'is', 'async', 'await'
        ]
        
    def setup_autocomplete(self):
        """Initialize autocomplete functionality"""
        self.editor.bind('<Control-space>', self.show_autocomplete)
        
    def highlight_syntax(self):
        """Apply syntax highlighting to code"""
        if not self.settings.syntax_highlight.get():
            return
            
        # Remove existing tags
        for tag in self.syntax_colors.keys():
            self.editor.tag_remove(tag, '1.0', tk.END)
            
        code = self.editor.get('1.0', tk.END)
        
        # Highlight comments
        for match in re.finditer(r'#.*', code):
            self.editor.tag_add('comment',
                              f"1.0+{match.start()}c",
                              f"1.0+{match.end()}c")
                              
        # Highlight strings
        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
            self.editor.tag_add('string',
                              f"1.0+{match.start()}c", 
                              f"1.0+{match.end()}c")
                              
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, code):
                self.editor.tag_add('keyword',
                                  f"1.0+{match.start()}c",
                                  f"1.0+{match.end()}c")
                                  
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', code):
            self.editor.tag_add('number',
                              f"1.0+{match.start()}c",
                              f"1.0+{match.end()}c")
                              
        # Highlight function definitions
        for match in re.finditer(r'\bdef\s+(\w+)', code):
            self.editor.tag_add('function',
                              f"1.0+{match.start(1)}c",
                              f"1.0+{match.end(1)}c")
                              
    def update_line_numbers(self):
        """Update line numbers display"""
        if not self.settings.line_numbers.get():
            return
            
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        
        # Count lines
        line_count = self.editor.get('1.0', tk.END).count('\n')
        numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.insert('1.0', numbers)
        self.line_numbers.config(state=tk.DISABLED)
        
    def show_autocomplete(self, event=None):
        """Show autocomplete suggestions popup"""
        cursor_pos = self.editor.index(tk.INSERT)
        line = self.editor.get(f"{cursor_pos} linestart", cursor_pos)
        words = line.split()
        
        if words:
            current_word = words[-1]
            suggestions = [kw for kw in self.keywords if kw.startswith(current_word)]
            
            if suggestions:
                popup = tk.Toplevel(self.parent)
                popup.overrideredirect(True)
                
                # Position popup near cursor
                x = self.editor.winfo_rootx()
                y = self.editor.winfo_rooty() + 20
                popup.geometry(f"+{x}+{y}")
                
                # Create listbox
                listbox = tk.Listbox(popup,
                                   font=("Consolas", 9),
                                   bg=self.theme['secondary_bg'],
                                   fg=self.theme['text_color'],
                                   selectbackground=self.theme['accent_color'])
                listbox.pack()
                
                # Add suggestions
                for suggestion in suggestions[:10]:
                    listbox.insert(tk.END, suggestion)
                    
                def insert_suggestion(event):
                    if listbox.curselection():
                        selected = listbox.get(listbox.curselection())
                        self.editor.delete(f"{cursor_pos} - {len(current_word)}c",
                                         cursor_pos)
                        self.editor.insert(cursor_pos, selected)
                    popup.destroy()
                    
                listbox.bind('<Return>', insert_suggestion)
                listbox.bind('<Double-Button-1>', insert_suggestion)
                listbox.bind('<Escape>', lambda e: popup.destroy())
                
                # Auto-close after delay
                popup.after(3000, popup.destroy)
                
        return "break"
        
    def on_edit(self, event=None):
        """Handle text edit events"""
        self.update_line_numbers()
        self.highlight_syntax()
        
    def on_key_release(self, event=None):
        """Handle key release events"""
        self.highlight_syntax()
        
    def get_text(self):
        """Get editor content"""
        return self.editor.get('1.0', tk.END)
        
    def set_text(self, text):
        """Set editor content"""
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', text)
        self.highlight_syntax()
        
    def clear(self):
        """Clear editor content"""
        self.editor.delete('1.0', tk.END)