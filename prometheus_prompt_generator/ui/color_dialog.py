from PySide6.QtWidgets import QDialog, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal

class ColorDialog:
    """
    Color dialog that provides a user-friendly interface for selecting colors.
    This is a simplified wrapper around PySide6's QColorDialog.
    """
    
    @staticmethod
    def get_color(parent=None, initial_color=None):
        """
        Static convenience method to get a color from the user.
        
        Args:
            parent: Parent widget
            initial_color: Initial color to display
            
        Returns:
            tuple: (QColor, bool) - The selected color and whether OK was pressed
        """
        color = QColorDialog.getColor(
            initial_color or QColor(0, 0, 0), 
            parent,
            "Select Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        
        return color, color.isValid() 