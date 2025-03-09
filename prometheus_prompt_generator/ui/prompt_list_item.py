"""
Prometheus AI Prompt List Item

A custom widget for displaying prompt items in a list widget.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt

from ..utils.constants import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE

class PromptListItem(QWidget):
    """Custom widget for displaying prompt types in the list"""
    
    def __init__(self, prompt_type, display_name, parent=None):
        """Initialize the prompt list item widget.
        
        Args:
            prompt_type (str): The type/identifier of the prompt
            display_name (str): The display name to show to the user
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.prompt_type = prompt_type
        self.display_name = display_name
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        layout.setSpacing(5)
        
        # Create item layout for better spacing
        self.item_layout = QVBoxLayout()
        
        # Main prompt name label
        self.name_label = QLabel(display_name)
        self.name_label.setObjectName("promptName")
        self.name_label.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, QFont.Weight.Bold))
        
        # Type label (smaller, right-aligned)
        self.type_label = QLabel(prompt_type)
        self.type_label.setObjectName("promptType")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.type_label.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE - 1))
        
        # Add labels to layout
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.type_label)
        
        # Set styling for selected state
        self.setAutoFillBackground(True)
        self.updateStyle(True)  # Default to dark mode
    
    def updateStyle(self, is_dark_mode, accent_color=None):
        """Update the styling based on dark/light mode and accent color.
        
        Args:
            is_dark_mode (bool): Whether the app is in dark mode
            accent_color (QColor, optional): Accent color to use. Defaults to None.
        """
        if accent_color is None:
            accent_color = QColor("#2980b9")  # Default blue
            
        # Create palettes for normal and selected states
        normal_palette = self.palette()
        selected_palette = QPalette(normal_palette)
        
        if is_dark_mode:
            # Dark mode
            normal_palette.setColor(QPalette.ColorRole.Window, QColor(51, 51, 51))
            normal_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            
            # Selected state - use accent color
            selected_palette.setColor(QPalette.ColorRole.Window, accent_color.darker(110))
            selected_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            
            # Type label
            self.type_label.setStyleSheet(f"color: rgba(255, 255, 255, 180);")
        else:
            # Light mode
            normal_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            normal_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            
            # Selected state - use accent color
            selected_palette.setColor(QPalette.ColorRole.Window, accent_color.lighter(140))
            selected_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            
            # Type label
            self.type_label.setStyleSheet(f"color: rgba(0, 0, 0, 180);")
        
        # Store palettes for use when selection state changes
        self.normal_palette = normal_palette
        self.selected_palette = selected_palette
        
        # Apply initial palette
        self.setPalette(normal_palette) 