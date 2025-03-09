#!/usr/bin/env python
"""
Run Designer UI

This script runs the Prometheus AI Prompt Generator with the Qt Designer UI.
"""

import os
import sys
from PyQt6.QtWidgets import QApplication

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the designer main window class
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