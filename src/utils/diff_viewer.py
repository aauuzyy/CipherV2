"""
Diff Viewer - Compare two text blocks side-by-side
"""
import tkinter as tk
from tkinter import scrolledtext
import difflib

class DiffViewer:
    """Side-by-side diff viewer"""
    
    @staticmethod
    def show(parent, text1, text2, title1="Original", title2="Modified", theme=None):
        """Show diff viewer dialog"""
        if theme is None:
            theme = {
                'bg_color': '#1e1e1e',
                'secondary_bg': '#2d2d2d',
                'text_color': '#ffffff',
                'accent_color': '#0078d4'
            }
        
        dialog = tk.Toplevel(parent)
        dialog.title("Diff Viewer")
        dialog.geometry("1000x600")
        dialog.configure(bg=theme['bg_color'])
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (1000 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=theme['secondary_bg'])
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header, text="🔍 Diff Viewer", font=("Segoe UI", 14, "bold"),
                bg=theme['secondary_bg'], fg=theme['text_color']).pack(pady=10)
        
        # Split pane
        pane = tk.Frame(dialog, bg=theme['bg_color'])
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Left side (Original)
        left_frame = tk.Frame(pane, bg=theme['secondary_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text=title1, font=("Segoe UI", 11, "bold"),
                bg=theme['secondary_bg'], fg=theme['text_color']).pack(pady=10)
        
        left_text = tk.Text(left_frame, font=("Consolas", 10),
                           bg=theme['bg_color'], fg=theme['text_color'],
                           wrap=tk.NONE, width=45)
        left_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right side (Modified)
        right_frame = tk.Frame(pane, bg=theme['secondary_bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text=title2, font=("Segoe UI", 11, "bold"),
                bg=theme['secondary_bg'], fg=theme['text_color']).pack(pady=10)
        
        right_text = tk.Text(right_frame, font=("Consolas", 10),
                            bg=theme['bg_color'], fg=theme['text_color'],
                            wrap=tk.NONE, width=45)
        right_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure tags for highlighting
        left_text.tag_configure("delete", background="#4d1f1f", foreground="#ff6b6b")
        left_text.tag_configure("equal", background=theme['bg_color'])
        
        right_text.tag_configure("insert", background="#1f4d1f", foreground="#6bff6b")
        right_text.tag_configure("equal", background=theme['bg_color'])
        
        # Perform diff
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        differ = difflib.Differ()
        diff = list(differ.compare(lines1, lines2))
        
        # Display diff
        left_line = 1
        right_line = 1
        
        for line in diff:
            if line.startswith('- '):
                # Deleted line (only in left)
                left_text.insert(f"{left_line}.0", line[2:] + "\n", "delete")
                left_line += 1
            elif line.startswith('+ '):
                # Added line (only in right)
                right_text.insert(f"{right_line}.0", line[2:] + "\n", "insert")
                right_line += 1
            elif line.startswith('  '):
                # Equal line (in both)
                left_text.insert(f"{left_line}.0", line[2:] + "\n", "equal")
                right_text.insert(f"{right_line}.0", line[2:] + "\n", "equal")
                left_line += 1
                right_line += 1
        
        # Make read-only
        left_text.config(state=tk.DISABLED)
        right_text.config(state=tk.DISABLED)
        
        # Sync scrolling
        def sync_scroll(*args):
            left_text.yview_moveto(args[0])
            right_text.yview_moveto(args[0])
        
        left_scrollbar = tk.Scrollbar(left_frame, command=sync_scroll)
        right_scrollbar = tk.Scrollbar(right_frame, command=sync_scroll)
        
        left_text.config(yscrollcommand=lambda *args: (left_scrollbar.set(*args), sync_scroll(*args)))
        right_text.config(yscrollcommand=lambda *args: (right_scrollbar.set(*args), sync_scroll(*args)))
        
        # Stats
        stats_frame = tk.Frame(dialog, bg=theme['secondary_bg'])
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        added = sum(1 for line in diff if line.startswith('+ '))
        deleted = sum(1 for line in diff if line.startswith('- '))
        
        stats_text = f"✓ {len(lines1)} lines → {len(lines2)} lines  |  +{added} additions  |  -{deleted} deletions"
        tk.Label(stats_frame, text=stats_text, font=("Segoe UI", 9),
                bg=theme['secondary_bg'], fg="#aaaaaa").pack(pady=8)
        
        # Close button
        tk.Button(dialog, text="Close", font=("Segoe UI", 10),
                 bg=theme['accent_color'], fg="white", relief=tk.FLAT,
                 padx=30, pady=10, cursor="hand2",
                 command=dialog.destroy).pack(pady=(0, 10))
