import sys
import os
import signal

# Add the src directory to the Python path
if __name__ == "__main__":
    # Get the directory where this script is located (src directory)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # Add it to sys.path if it's not already there
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

import tkinter as tk
from auth import LoginScreen
from ui.modern_ui import ModernUI

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nExiting gracefully...")
    sys.exit(0)

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    root = tk.Tk()
    root.withdraw()  # Hide the root window initially
    
    def start_main_app():
        try:
            # Create main window
            main_window = tk.Tk()
            app = ModernUI(main_window)
            
            # Close login window safely
            try:
                root.quit()
                root.destroy()
            except:
                pass
            
            # Run main application loop
            try:
                main_window.mainloop()
            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user")
                try:
                    main_window.quit()
                except:
                    pass
        except Exception as e:
            print(f"Error starting main app: {e}")
            import traceback
            traceback.print_exc()
    
    # Show login screen
    root.deiconify()  # Show the root window for login
    login = LoginScreen(root, start_main_app)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted")
        try:
            root.quit()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()