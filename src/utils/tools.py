"""
Utility Tools Collection
Includes: Regex Tester, Base64, Color Picker, Lorem Ipsum, Password Generator
"""
import tkinter as tk
from tkinter import ttk
import re
import base64
import random
import string

class ToolsCollection:
    """Collection of utility tools"""
    
    @staticmethod
    def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
        """Generate secure random password"""
        chars = ''
        if use_upper:
            chars += string.ascii_uppercase
        if use_lower:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += string.punctuation
        
        if not chars:
            return "ERROR: Select at least one character type"
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_lorem_ipsum(paragraphs=3):
        """Generate Lorem Ipsum placeholder text"""
        lorem = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.",
            "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.",
            "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem."
        ]
        
        result = []
        for i in range(paragraphs):
            result.append(lorem[i % len(lorem)])
        
        return "\n\n".join(result)
    
    @staticmethod
    def encode_base64(text):
        """Encode text to Base64"""
        try:
            return base64.b64encode(text.encode()).decode()
        except Exception as e:
            return f"ERROR: {e}"
    
    @staticmethod
    def decode_base64(text):
        """Decode Base64 to text"""
        try:
            return base64.b64decode(text.encode()).decode()
        except Exception as e:
            return f"ERROR: {e}"
    
    @staticmethod
    def test_regex(pattern, text, flags=0):
        """Test regex pattern against text"""
        try:
            matches = []
            for match in re.finditer(pattern, text, flags):
                matches.append({
                    'full': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups()
                })
            return {'success': True, 'matches': matches}
        except re.error as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def rgb_to_hex(r, g, b):
        """Convert RGB to HEX"""
        return f"#{r:02x}{g:02x}{b:02x}".upper()
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert HEX to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
