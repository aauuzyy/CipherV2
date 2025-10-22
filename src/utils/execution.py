"""Code execution and output handling utilities"""
import sys
import time
from io import StringIO
from typing import Tuple, Any, Dict
import traceback

class ExecutionManager:
    def __init__(self):
        self.history = []
        self.max_history = 100
    
    def execute_code(self, code: str, globals_dict: Dict[str, Any] = None) -> Tuple[bool, str, float, str]:
        """
        Execute Python code and capture output
        
        Returns:
        - Tuple of (success, output, execution_time, error_msg)
        """
        start_time = time.time()
        
        # Set up output capture
        stdout = StringIO()
        stderr = StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Redirect output
            sys.stdout = stdout
            sys.stderr = stderr
            
            # Create execution globals
            if globals_dict is None:
                globals_dict = globals().copy()
            
            # Execute code
            exec(code, globals_dict)
            
            # Get output
            output = stdout.getvalue()
            errors = stderr.getvalue()
            
            # Calculate execution time
            exec_time = time.time() - start_time
            
            # Add to history
            self._add_to_history(code)
            
            if errors:
                return False, output, exec_time, errors
            return True, output, exec_time, ""
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            error_msg += traceback.format_exc()
            return False, stdout.getvalue(), time.time() - start_time, error_msg
            
        finally:
            # Restore output
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    def _add_to_history(self, code: str):
        """Add executed code to history"""
        self.history.append({
            'code': code,
            'timestamp': time.time()
        })
        
        # Maintain maximum history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_history(self) -> list:
        """Get execution history"""
        return self.history
    
    def clear_history(self):
        """Clear execution history"""
        self.history = []