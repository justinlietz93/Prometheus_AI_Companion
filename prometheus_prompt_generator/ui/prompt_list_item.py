"""
Prometheus AI Prompt List Item

A custom widget for displaying prompt items in a list widget.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QToolButton
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from ..utils.constants import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE

class PromptListItem(QWidget):
    """Custom widget for displaying prompt types in the list"""
    
    clicked = pyqtSignal(str)
    info_clicked = pyqtSignal(str)  # Signal now includes the prompt_type
    
    def __init__(self, prompt_type, display_name, parent=None, show_info_icon=False):
        """Initialize the prompt list item widget.
        
        Args:
            prompt_type (str): The type/identifier of the prompt
            display_name (str): The display name to show to the user
            parent (QWidget, optional): Parent widget. Defaults to None.
            show_info_icon (bool, optional): Whether to show an info icon. Defaults to False.
        """
        super().__init__(parent)
        self.prompt_type = prompt_type
        self.display_name = display_name
        self.show_info_icon = show_info_icon
        
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Name label
        self.name_label = QLabel(self.display_name)
        self.name_label.setObjectName("promptName")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.name_label.setToolTip(self.display_name)  # Add tooltip to show full text on hover
        layout.addWidget(self.name_label)
        
        # Type tag (prompt_type as a colored tag)
        self.type_tag = QLabel(self.prompt_type)
        self.type_tag.setObjectName("promptTypeTag")
        self.type_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_tag.setMinimumWidth(120)  # Increased minimum width to reduce truncation
        # No fixed maximum width to allow text to display completely
        # Transparent background with border instead of colored background
        self.type_tag.setStyleSheet("background-color: transparent; color: #333333; border: 1px solid #CCCCCC; border-radius: 3px; padding: 2px 6px;")
        self.type_tag.setToolTip(f"Type: {self.prompt_type}")  # Add tooltip to tag
        layout.addWidget(self.type_tag)
        
        # Add info icon if requested
        if self.show_info_icon:
            self.info_button = QToolButton()
            self.info_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
            self.info_button.setToolTip("View metadata")
            self.info_button.setMaximumSize(QSize(20, 20))
            self.info_button.clicked.connect(self.onInfoClicked)
            layout.addWidget(self.info_button)
        
        self.setLayout(layout)
        
    def updateStyle(self, is_dark_mode, accent_color=None):
        """Update the styling based on the current theme"""
        if is_dark_mode:
            text_color = "#FFFFFF"
            border_color = "#555555"
        else:
            text_color = "#333333"
            border_color = "#CCCCCC"
            
        # Apply transparent background with border instead of colored background
        self.type_tag.setStyleSheet(f"background-color: transparent; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 2px 6px;")
            
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        self.clicked.emit(self.prompt_type)
        # Allow event to propagate for selection
        super().mousePressEvent(event)
        
    def onInfoClicked(self):
        """Handle info icon click"""
        # This will be connected to the metadata dialog
        self.info_clicked.emit(self.prompt_type) 