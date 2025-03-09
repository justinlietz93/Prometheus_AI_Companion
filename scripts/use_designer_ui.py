#!/usr/bin/env python
"""
Use Designer UI Script

This script demonstrates how to use the Qt Designer UI file with the application.
It shows both the composition and inheritance approaches.
"""

import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import pyqtSlot
from PyQt6 import uic

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import the UI file
ui_file_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'prometheus_prompt_generator', 'ui', 'designer', 'main_window.ui'
)

# Check if UI file exists, if not generate it
if not os.path.exists(ui_file_path):
    from generate_ui_file import generate_ui_file
    ui_file_path = generate_ui_file()

# Approach 1: Composition - Using the UI file directly
class MainWindowComposition(QMainWindow):
    """Main window using composition approach with the UI file."""
    
    def __init__(self):
        super().__init__()
        
        # Load the UI file
        self.ui = uic.loadUi(ui_file_path, self)
        
        # Connect signals to slots
        self.ui.generatePromptsButton.clicked.connect(self.on_generate_prompts)
        self.ui.copyToClipboardButton.clicked.connect(self.on_copy_to_clipboard)
        self.ui.selectAllButton.clicked.connect(self.on_select_all)
        self.ui.selectNoneButton.clicked.connect(self.on_select_none)
        self.ui.urgencySlider.valueChanged.connect(self.on_urgency_changed)
        
        # Setup additional UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Setup additional UI elements not defined in the UI file."""
        # Set window title
        self.setWindowTitle("Prometheus AI Prompt Generator - Composition Approach")
        
        # Populate the prompt list (this would normally come from your data)
        for i in range(10):
            self.ui.promptList.addItem(f"Example Prompt {i+1}")
    
    @pyqtSlot()
    def on_generate_prompts(self):
        """Handle generate prompts button click."""
        self.ui.outputText.setText("Generated prompt example.\nThis is from the composition approach.")
    
    @pyqtSlot()
    def on_copy_to_clipboard(self):
        """Handle copy to clipboard button click."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ui.outputText.toPlainText())
        self.ui.statusbar.showMessage("Copied to clipboard", 2000)
    
    @pyqtSlot()
    def on_select_all(self):
        """Handle select all button click."""
        for i in range(self.ui.promptList.count()):
            item = self.ui.promptList.item(i)
            item.setSelected(True)
    
    @pyqtSlot()
    def on_select_none(self):
        """Handle select none button click."""
        self.ui.promptList.clearSelection()
    
    @pyqtSlot(int)
    def on_urgency_changed(self, value):
        """Handle urgency slider value change."""
        urgency_text = "Low"
        if value <= 3:
            urgency_text = "Low"
        elif value <= 7:
            urgency_text = "Normal"
        else:
            urgency_text = "High"
        
        self.ui.urgencyDisplay.setText(f"{urgency_text} ({value}/10)")


# Approach 2: Multiple Inheritance - Loading the UI class
# First, we need to convert the UI file to Python code
ui_py_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'prometheus_prompt_generator', 'ui', 'designer', 'ui_main_window.py'
)

# Generate the Python UI file using pyuic6
os.system(f"pyuic6 {ui_file_path} -o {ui_py_path}")

# Now import the generated UI class
sys.path.insert(0, os.path.dirname(os.path.dirname(ui_py_path)))
try:
    from prometheus_prompt_generator.ui.designer.ui_main_window import Ui_MainWindow
    
    class MainWindowInheritance(QMainWindow, Ui_MainWindow):
        """Main window using multiple inheritance approach with the UI class."""
        
        def __init__(self):
            super().__init__()
            
            # Setup the UI
            self.setupUi(self)
            
            # Connect signals to slots
            self.generatePromptsButton.clicked.connect(self.on_generate_prompts)
            self.copyToClipboardButton.clicked.connect(self.on_copy_to_clipboard)
            self.selectAllButton.clicked.connect(self.on_select_all)
            self.selectNoneButton.clicked.connect(self.on_select_none)
            self.urgencySlider.valueChanged.connect(self.on_urgency_changed)
            
            # Setup additional UI elements
            self.setup_ui()
        
        def setup_ui(self):
            """Setup additional UI elements not defined in the UI file."""
            # Set window title
            self.setWindowTitle("Prometheus AI Prompt Generator - Inheritance Approach")
            
            # Populate the prompt list (this would normally come from your data)
            for i in range(10):
                self.promptList.addItem(f"Example Prompt {i+1}")
        
        @pyqtSlot()
        def on_generate_prompts(self):
            """Handle generate prompts button click."""
            self.outputText.setText("Generated prompt example.\nThis is from the inheritance approach.")
        
        @pyqtSlot()
        def on_copy_to_clipboard(self):
            """Handle copy to clipboard button click."""
            clipboard = QApplication.clipboard()
            clipboard.setText(self.outputText.toPlainText())
            self.statusbar.showMessage("Copied to clipboard", 2000)
        
        @pyqtSlot()
        def on_select_all(self):
            """Handle select all button click."""
            for i in range(self.promptList.count()):
                item = self.promptList.item(i)
                item.setSelected(True)
        
        @pyqtSlot()
        def on_select_none(self):
            """Handle select none button click."""
            self.promptList.clearSelection()
        
        @pyqtSlot(int)
        def on_urgency_changed(self, value):
            """Handle urgency slider value change."""
            urgency_text = "Low"
            if value <= 3:
                urgency_text = "Low"
            elif value <= 7:
                urgency_text = "Normal"
            else:
                urgency_text = "High"
            
            self.urgencyDisplay.setText(f"{urgency_text} ({value}/10)")
except ImportError:
    print("Could not import Ui_MainWindow. Make sure pyuic6 is installed and the UI file was generated correctly.")
    MainWindowInheritance = None


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    # Create and show the main window using composition approach
    window_composition = MainWindowComposition()
    window_composition.show()
    
    # Create and show the main window using inheritance approach if available
    if MainWindowInheritance:
        window_inheritance = MainWindowInheritance()
        window_inheritance.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 