import traceback
import sys
from datetime import datetime

class DebugLogger:
    """A simple debug logger for tracking execution flow and variable states"""
    
    def __init__(self, enabled=True, log_to_file=False, log_file="debug_log.txt"):
        self.enabled = enabled
        self.log_to_file = log_to_file
        self.log_file = log_file
        
        if self.log_to_file:
            # Create or clear the log file
            with open(self.log_file, 'w') as f:
                f.write(f"Debug Log Started: {datetime.now()}\n")
    
    def log(self, message, obj=None, include_stack=False):
        """Log a message with optional object inspection and stack trace"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        
        if obj is not None:
            try:
                obj_type = type(obj).__name__
                obj_repr = repr(obj)
                if len(obj_repr) > 500:  # Truncate very long representations
                    obj_repr = obj_repr[:500] + "..."
                log_message += f"\n    Object ({obj_type}): {obj_repr}"
                
                # For QComboBox, add more details
                if obj_type == 'QComboBox':
                    try:
                        items = [obj.itemText(i) for i in range(obj.count())]
                        current = obj.currentText()
                        log_message += f"\n    Items: {items}"
                        log_message += f"\n    Current: {current}"
                    except Exception as e:
                        log_message += f"\n    Error getting QComboBox details: {str(e)}"
            except Exception as e:
                log_message += f"\n    Error inspecting object: {str(e)}"
        
        if include_stack:
            stack = traceback.format_stack()[:-1]  # Exclude this function call
            log_message += "\n    Stack Trace:\n    " + "    ".join(stack[-3:])  # Show last 3 frames
        
        print(log_message)
        
        if self.log_to_file:
            with open(self.log_file, 'a') as f:
                f.write(log_message + "\n")
    
    def exception(self, e, context=""):
        """Log an exception with full traceback"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        log_message = f"[{timestamp}] EXCEPTION in {context}: {str(e)}\n"
        log_message += "".join(tb_lines)
        
        print(log_message)
        
        if self.log_to_file:
            with open(self.log_file, 'a') as f:
                f.write(log_message + "\n")

# Create a global instance for easy import
debug = DebugLogger(enabled=True, log_to_file=True, log_file="skill_group_debug.log")
