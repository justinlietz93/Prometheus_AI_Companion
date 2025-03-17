#!/usr/bin/env python
"""
Test script for the PromptEditorDialog with form validation.

This script creates a simple application that demonstrates the PromptEditorDialog
with form validation.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo

# Import the dialog
from prometheus_prompt_generator.ui.prompt_editor_dialog import PromptEditorDialog
from prometheus_prompt_generator.domain.models.prompt import Prompt


class TestWindow(QMainWindow):
    """Main window for testing the PromptEditorDialog."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PromptEditorDialog")
        self.resize(400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons
        new_button = QPushButton("Create New Prompt")
        new_button.clicked.connect(self.create_new_prompt)
        layout.addWidget(new_button)
        
        # Set up window
        self.show()
        
    def create_new_prompt(self):
        """Open the PromptEditorDialog to create a new prompt."""
        result = PromptEditorDialog.edit_prompt(self, None)
        if result:
            print("Dialog accepted")
        else:
            print("Dialog rejected")
        

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set up translation
    translator = QTranslator()
    translator.load(QLocale.system(), "qtbase", "_", 
                    QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(translator)
    
    # Create the main window
    window = TestWindow()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 