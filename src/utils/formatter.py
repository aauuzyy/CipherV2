"""
Text Formatting Tools - JSON, XML, etc.
"""
import json
import xml.dom.minidom as minidom

class Formatter:
    """Text formatting utilities"""
    
    @staticmethod
    def format_json(text, indent=2):
        """Format JSON with proper indentation"""
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=indent, sort_keys=False)
        except json.JSONDecodeError as e:
            return f"JSON Error: {e}"
    
    @staticmethod
    def minify_json(text):
        """Minify JSON (remove whitespace)"""
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, separators=(',', ':'))
        except json.JSONDecodeError as e:
            return f"JSON Error: {e}"
    
    @staticmethod
    def format_xml(text):
        """Format XML with proper indentation"""
        try:
            dom = minidom.parseString(text)
            return dom.toprettyxml(indent="  ")
        except Exception as e:
            return f"XML Error: {e}"
    
    @staticmethod
    def validate_json(text):
        """Validate JSON syntax"""
        try:
            json.loads(text)
            return {'valid': True, 'message': 'Valid JSON'}
        except json.JSONDecodeError as e:
            return {'valid': False, 'message': f"Line {e.lineno}, Col {e.colno}: {e.msg}"}
