#!/usr/bin/env python
"""
Run Designer Application

This script runs the Prometheus AI Prompt Generator with the Qt Designer UI,
without requiring the resource compiler.
"""

import os
import sys
from PyQt6.QtWidgets import QApplication

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure the UI directory structure exists
UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                     'prometheus_prompt_generator', 'ui', 'designer')
os.makedirs(UI_DIR, exist_ok=True)

# Generate the UI file if it doesn't exist
UI_FILE = os.path.join(UI_DIR, 'main_window.ui')
if not os.path.exists(UI_FILE):
    from scripts.generate_ui_file import generate_ui_file
    generate_ui_file()

# Try to convert the UI file to Python code
UI_PY_FILE = os.path.join(UI_DIR, 'ui_main_window.py')
try:
    import subprocess
    result = subprocess.run(
        ['pyuic6', UI_FILE, '-o', UI_PY_FILE],
        check=True,
        capture_output=True,
        text=True
    )
    print(f"Successfully converted UI file to Python: {UI_PY_FILE}")
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"Warning: Could not convert UI file: {e}")
    print("Will try to use direct loading approach.")

# Now try to import the designer main window
try:
    from prometheus_prompt_generator.ui.designer_main_window import get_designer_main_window_class
    
    def main():
        """Main entry point for the application."""
        # Create QApplication instance
        app = QApplication(sys.argv)
        
        # Get the appropriate main window class
        MainWindowClass = get_designer_main_window_class()
        
        # Create and show the main window
        window = MainWindowClass()
        window.show()
        
        # Enter the application event loop
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Could not import designer main window: {e}")
    print("Falling back to original application.")
    
    try:
        # Import the original main window
        from prometheus_prompt_generator.ui.main_window import PrometheusPromptGenerator
        
        def main():
            """Main entry point for the application."""
            # Create QApplication instance
            app = QApplication(sys.argv)
            
            # Create and show the main window
            window = PrometheusPromptGenerator()
            window.show()
            
            # Enter the application event loop
            sys.exit(app.exec())
        
        if __name__ == "__main__":
            main()
            
    except ImportError as e:
        print(f"Error: Could not import original main window: {e}")
        print("Could not run application.") 