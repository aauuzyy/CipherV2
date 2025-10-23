"""
Recent Files Manager - Track and manage recently opened files
"""
import json
import os
from collections import deque

class RecentFilesManager:
    """Manage recently opened files list"""
    
    def __init__(self, max_files=10, storage_file=None):
        self.max_files = max_files
        self.storage_file = storage_file or os.path.join(
            os.path.expanduser("~"), ".cipherv4_recent.json"
        )
        self.recent_files = deque(maxlen=max_files)
        self.load()
    
    def add_file(self, filepath):
        """Add file to recent files list"""
        if not filepath or not os.path.exists(filepath):
            return
        
        # Remove if already exists (to move to front)
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        # Add to front
        self.recent_files.appendleft(filepath)
        
        # Save
        self.save()
    
    def get_recent_files(self):
        """Get list of recent files"""
        # Filter out files that no longer exist
        valid_files = [f for f in self.recent_files if os.path.exists(f)]
        self.recent_files = deque(valid_files, maxlen=self.max_files)
        return list(self.recent_files)
    
    def clear(self):
        """Clear all recent files"""
        self.recent_files.clear()
        self.save()
    
    def save(self):
        """Save recent files to disk"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(list(self.recent_files), f)
        except Exception as e:
            print(f"Failed to save recent files: {e}")
    
    def load(self):
        """Load recent files from disk"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    files = json.load(f)
                    self.recent_files = deque(files, maxlen=self.max_files)
        except Exception as e:
            print(f"Failed to load recent files: {e}")
