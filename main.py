#!/usr/bin/env python3
"""
Prometheus AI Prompt Generator

Main entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication

from prometheus_prompt_generator import PrometheusPromptGenerator

def main():
    """Run the Prometheus AI prompt generator application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Prometheus AI Prompt Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Prometheus AI")
    
    # Create and show the main window
    window = PrometheusPromptGenerator()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 