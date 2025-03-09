#!/usr/bin/env python
"""
Prometheus AI Prompt Generator - Main Entry Point

This script serves as the main entry point for the application, using the Designer UI
if available and falling back to the original UI if not.
"""

import os
import sys
from PyQt6.QtWidgets import QApplication

# Add the current directory to the path
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Ensure the UI directory structure exists
UI_DIR = os.path.join(os.path.dirname(__file__), 
                      'prometheus_prompt_generator', 'ui', 'designer')
os.makedirs(UI_DIR, exist_ok=True)

# Generate the UI file if it doesn't exist
UI_FILE = os.path.join(UI_DIR, 'main_window.ui')
if not os.path.exists(UI_FILE):
    try:
        from scripts.generate_ui_file import generate_ui_file
        generate_ui_file()
        print(f"Generated UI file: {UI_FILE}")
    except Exception as e:
        print(f"Warning: Could not generate UI file: {e}")

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


def main():
    """Main entry point for the application."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Try to use the Designer UI first
    try:
        from prometheus_prompt_generator.ui.designer_main_window import get_designer_main_window_class
        
        MainWindowClass = get_designer_main_window_class()
        print("Using Designer UI...")
        
    except ImportError as e:
        print(f"Warning: Could not import Designer main window: {e}")
        print("Falling back to original UI...")
        
        # Fall back to the original UI
        try:
            from prometheus_prompt_generator.ui.main_window import PrometheusPromptGenerator
            
            MainWindowClass = PrometheusPromptGenerator
            
        except ImportError as e:
            print(f"Error: Could not import original main window: {e}")
            print("Could not run application.")
            return 1
    
    # Create and show the main window
    window = MainWindowClass()
    window.show()
    
    # Enter the application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 