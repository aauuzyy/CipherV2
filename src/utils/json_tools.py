"""JSON validation and manipulation utilities"""
import json
from typing import Union, Dict, Any, Tuple

class JSONHandler:
    @staticmethod
    def validate_and_format(json_str: str) -> Tuple[bool, Union[str, Dict[str, Any]], str]:
        """
        Validate and format JSON string
        
        Returns:
        - Tuple of (success, result, message)
        - If success, result is formatted JSON string
        - If failure, result is original string and message contains error
        """
        try:
            # Parse JSON to validate
            parsed = json.loads(json_str)
            
            # Format with proper indentation
            formatted = json.dumps(parsed, indent=2)
            
            return True, formatted, "JSON is valid"
            
        except json.JSONDecodeError as e:
            line_no = e.lineno
            col_no = e.colno
            error_msg = f"JSON Error at line {line_no}, column {col_no}: {str(e)}"
            return False, json_str, error_msg
            
    @staticmethod
    def inject_json(target_json: str, injection: str, path: str = None) -> Tuple[bool, str, str]:
        """
        Inject JSON data into target JSON at specified path
        
        Args:
        - target_json: Original JSON string
        - injection: JSON string to inject
        - path: Dot notation path where to inject (e.g. "key1.key2")
        
        Returns:
        - Tuple of (success, result, message)
        """
        try:
            target = json.loads(target_json)
            injection_data = json.loads(injection)
            
            if not path:
                # Merge at root level
                if isinstance(target, dict) and isinstance(injection_data, dict):
                    target.update(injection_data)
                else:
                    return False, target_json, "Both target and injection must be objects for root merge"
            else:
                # Navigate to path
                current = target
                parts = path.split('.')
                
                # Navigate to parent of insertion point
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Insert at final location
                current[parts[-1]] = injection_data
            
            # Format result
            result = json.dumps(target, indent=2)
            return True, result, "JSON injection successful"
            
        except json.JSONDecodeError as e:
            return False, target_json, f"JSON Error: {str(e)}"
        except Exception as e:
            return False, target_json, f"Error: {str(e)}"
            
    @staticmethod
    def lint_json(json_str: str) -> Tuple[bool, str, list]:
        """
        Lint JSON string and return errors/warnings
        
        Returns:
        - Tuple of (valid, formatted_json, issues)
        """
        issues = []
        
        try:
            # Basic validation
            parsed = json.loads(json_str)
            
            # Check for common issues
            if isinstance(parsed, dict):
                # Check for empty objects
                empty_keys = [k for k, v in parsed.items() if not v]
                if empty_keys:
                    issues.append(f"Empty values found for keys: {', '.join(empty_keys)}")
                
                # Check for inconsistent key naming
                keys = list(parsed.keys())
                if any(k for k in keys if k.isupper()) and any(k for k in keys if k.islower()):
                    issues.append("Inconsistent key casing (mixed upper/lower case)")
                
            # Format with proper indentation
            formatted = json.dumps(parsed, indent=2)
            
            return True, formatted, issues
            
        except json.JSONDecodeError as e:
            return False, json_str, [f"JSON Error: {str(e)}"]