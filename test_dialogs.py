#!/usr/bin/env python3
"""
Test script for the FontDialog and ColorDialog classes.
"""

import sys
import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit, QLabel
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

# Import our custom dialogs
try:
    from prometheus_prompt_generator.ui.font_dialog import FontDialog
    from prometheus_prompt_generator.ui.color_dialog import ColorDialog
    print("Successfully imported dialog classes")
except Exception as e:
    print(f"Error importing dialog classes: {e}")
    traceback.print_exc()
    sys.exit(1)

class TestWindow(QMainWindow):
    """Test window for the FontDialog and ColorDialog classes."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dialog Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons to open dialogs
        self.font_button = QPushButton("Open Font Dialog")
        self.font_button.clicked.connect(self.open_font_dialog)
        layout.addWidget(self.font_button)
        
        self.color_button = QPushButton("Open Color Dialog")
        self.color_button.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.color_button)
        
        # Add a label to show current settings
        self.settings_label = QLabel("Current Font: Arial, 12pt | Current Color: Black")
        layout.addWidget(self.settings_label)
        
        # Create a text editor to demonstrate the font and color
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(200)
        self.text_edit.setText("This is a sample text demonstrating the selected font and color.\n"
                              "Try selecting different fonts, styles, sizes, and colors using the dialogs.")
        layout.addWidget(self.text_edit)
        
        # Initialize font and color
        self.current_font = QFont("Arial", 12)
        self.current_color = QColor(0, 0, 0)
        self.apply_font_and_color()
        
        print("Test window initialized successfully")
    
    def apply_font_and_color(self):
        """Apply the current font and color to the text editor."""
        # Apply font and color based on selection
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            # If text is selected, only apply to the selection
            format = cursor.charFormat()
            format.setFont(self.current_font)
            format.setForeground(self.current_color)
            cursor.mergeCharFormat(format)
            self.text_edit.setTextCursor(cursor)
        else:
            # If no text is selected, apply to all text
            self.text_edit.selectAll()
            self.text_edit.setFont(self.current_font)
            self.text_edit.setTextColor(self.current_color)
            # Clear the selection
            cursor = self.text_edit.textCursor()
            cursor.clearSelection()
            self.text_edit.setTextCursor(cursor)
        
        # Update the settings label
        self.settings_label.setText(
            f"Current Font: {self.current_font.family()}, {self.current_font.pointSize()}pt, "
            f"Bold: {self.current_font.bold()}, Italic: {self.current_font.italic()} | "
            f"Current Color: {self.current_color.name()}"
        )
    
    def open_font_dialog(self):
        """Open the font dialog to select a font and color."""
        try:
            print("Creating font dialog...")
            font, color, ok = FontDialog.get_font_and_color(self, self.current_font, self.current_color)
            print(f"Font dialog result: ok={ok}")
            
            if ok:
                self.current_font = font
                self.current_color = color
                print(f"Applied font: {self.current_font.family()}, {self.current_font.pointSize()}pt, "
                     f"Bold: {self.current_font.bold()}, Italic: {self.current_font.italic()}")
                print(f"Applied color: {self.current_color.name()}")
                
                # Apply the font and color to the text editor
                self.apply_font_and_color()
        except Exception as e:
            print(f"Error in font dialog: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Font dialog error: {str(e)}")
    
    def open_color_dialog(self):
        """Open the color dialog to select a color."""
        try:
            print("Opening color dialog...")
            color, ok = ColorDialog.get_color(self, self.current_color)
            print(f"Color dialog result: ok={ok}")
            
            if ok:
                self.current_color = color
                print(f"Applied color: {self.current_color.name()}")
                
                # Apply the color to the text editor
                self.apply_font_and_color()
        except Exception as e:
            print(f"Error in color dialog: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Color dialog error: {str(e)}")

def main():
    """Main function to run the test application."""
    try:
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 