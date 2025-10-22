import sys
import os
import signal
import io
import contextlib
import time

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
    # signal.signal(signal.SIGINT, signal_handler)  # Temporarily disabled for debugging
    
    print("Creating root window...")
    root = tk.Tk()
    root.withdraw()  # Hide the root window initially
    print("Root window created...")
    
    def start_main_app():
        print("start_main_app called...")
        
        # Close login window FIRST before creating main window
        print("Closing login window...")
        try:
            root.withdraw()
            root.update()  # Process pending events
            root.destroy()
            time.sleep(0.1)  # Give it time to fully destroy
        except:
            pass
        
        try:
            # Now create main window
            print("Creating main window...")
            main_window = tk.Tk()
            print("Creating ModernUI...")
            app = ModernUI(main_window)
            
            # Run main application loop
            print("Starting main window mainloop...")
            print(f"Window exists: {main_window.winfo_exists()}")
            print(f"Window viewable: {main_window.winfo_viewable()}")
            try:
                main_window.mainloop()
                print("Main window mainloop exited normally!")
                print(f"Window exists after mainloop: {main_window.winfo_exists()}")
            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user")
                try:
                    main_window.quit()
                except:
                    pass
            except Exception as e:
                print(f"Exception in mainloop: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"Error starting main app: {e}")
            import traceback
            traceback.print_exc()
    
    # Show login screen
    print("Creating login screen...")
    root.deiconify()  # Show the root window for login
    login = LoginScreen(root, start_main_app)
    print("Login screen created, starting mainloop...")
    
    try:
        root.mainloop()
        print("Mainloop exited normally...")
    except KeyboardInterrupt:
        print("\n\nApplication interrupted")
        try:
            root.quit()
        except:
            pass
        sys.exit(0)
    finally:
        # Suppress TTK theme cleanup errors
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()