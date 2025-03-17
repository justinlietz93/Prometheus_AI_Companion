from PySide6.QtWidgets import QDialog, QColorDialog, QAbstractItemView, QDialogButtonBox, QMessageBox
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QStandardItemModel, QStandardItem, QFontDatabase
from PySide6.QtCore import Qt, Signal

from prometheus_prompt_generator.ui.designer.ui_font_dialog import Ui_FontDialog

class FontDialog(QDialog):
    """
    Custom font dialog that provides a more user-friendly interface for selecting fonts
    than the standard QFontDialog. This dialog allows users to select font family, style,
    size, and effects (strikeout, underline, color).
    """
    
    fontSelected = Signal(QFont, QColor)
    
    def __init__(self, parent=None, initial_font=None, initial_color=None):
        """
        Initialize the font dialog.
        
        Args:
            parent: Parent widget
            initial_font: Initial font to display
            initial_color: Initial color to display
        """
        super().__init__(parent)
        self.ui = Ui_FontDialog()
        self.ui.setupUi(self)
        
        # Set modal to true to prevent parent window interaction
        self.setModal(True)
        
        # Initialize models
        self.font_family_model = QStandardItemModel(self)
        self.font_style_model = QStandardItemModel(self)
        self.font_size_model = QStandardItemModel(self)
        
        self.ui.fontFamilyListView.setModel(self.font_family_model)
        self.ui.fontStyleListView.setModel(self.font_style_model)
        self.ui.fontSizeListView.setModel(self.font_size_model)
        
        # Set selection behavior
        self.ui.fontFamilyListView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.fontStyleListView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.fontSizeListView.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Initialize font and color
        if initial_font:
            self.current_font = QFont(initial_font.family(), initial_font.pointSize())
            self.current_font.setBold(initial_font.bold())
            self.current_font.setItalic(initial_font.italic())
            self.current_font.setStrikeOut(initial_font.strikeOut())
            self.current_font.setUnderline(initial_font.underline())
        else:
            self.current_font = QFont("Arial", 12)
            
        self.current_color = QColor(initial_color) if initial_color else QColor(0, 0, 0)
        
        # Create font database
        self.font_db = QFontDatabase()
        
        # Set up font family list
        self.font_families = self.font_db.families()
        for family in self.font_families:
            item = QStandardItem(family)
            self.font_family_model.appendRow(item)
        
        # Set up font styles
        self.update_font_styles()
        
        # Set up font sizes
        standard_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        for size in standard_sizes:
            item = QStandardItem(str(size))
            self.font_size_model.appendRow(item)
        
        # Set up color preview
        self.update_color_preview()
        
        # Connect signals
        self.ui.fontFamilyListView.selectionModel().selectionChanged.connect(self.on_font_family_changed)
        self.ui.fontStyleListView.selectionModel().selectionChanged.connect(self.on_font_style_changed)
        self.ui.fontSizeListView.selectionModel().selectionChanged.connect(self.on_font_size_changed)
        self.ui.strikeoutCheckBox.toggled.connect(self.on_strikeout_toggled)
        self.ui.underlineCheckBox.toggled.connect(self.on_underline_toggled)
        self.ui.colorButton.clicked.connect(self.on_color_button_clicked)
        
        # Connect button box signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # If there's an apply button, connect it
        apply_button = self.ui.buttonBox.button(QDialogButtonBox.Apply)
        if apply_button:
            apply_button.clicked.connect(self.apply_changes)
        
        # Initialize UI with current font and color
        self.update_ui_from_font()
        
        # Debug - print initial font
        print(f"Initial font: {self.current_font.family()}, size: {self.current_font.pointSize()}, "
              f"bold: {self.current_font.bold()}, italic: {self.current_font.italic()}")
        
    def update_ui_from_font(self):
        """Update UI elements to reflect the current font and color."""
        # Block signals during update
        self.blockSignals(True)
        self.ui.fontFamilyListView.blockSignals(True)
        self.ui.fontStyleListView.blockSignals(True)
        self.ui.fontSizeListView.blockSignals(True)
        
        try:
            # Set font family
            family = self.current_font.family()
            for row in range(self.font_family_model.rowCount()):
                idx = self.font_family_model.index(row, 0)
                if self.font_family_model.data(idx) == family:
                    self.ui.fontFamilyListView.setCurrentIndex(idx)
                    break
            
            # Set font style
            self.update_font_styles()
            style_index = self.get_style_index()
            if style_index >= 0:
                self.ui.fontStyleListView.setCurrentIndex(self.font_style_model.index(style_index, 0))
            
            # Set font size
            size_str = str(self.current_font.pointSize())
            for row in range(self.font_size_model.rowCount()):
                idx = self.font_size_model.index(row, 0)
                if self.font_size_model.data(idx) == size_str:
                    self.ui.fontSizeListView.setCurrentIndex(idx)
                    break
            
            # Set effects
            self.ui.strikeoutCheckBox.setChecked(self.current_font.strikeOut())
            self.ui.underlineCheckBox.setChecked(self.current_font.underline())
            
            # Update preview
            self.update_preview()
        except Exception as e:
            print(f"Error updating UI from font: {e}")
        
        # Unblock signals
        self.ui.fontFamilyListView.blockSignals(False)
        self.ui.fontStyleListView.blockSignals(False)
        self.ui.fontSizeListView.blockSignals(False)
        self.blockSignals(False)
    
    def update_font_styles(self):
        """Update the font styles list based on the selected font family."""
        family = self.current_font.family()
        styles = self.font_db.styles(family)
        
        self.font_style_model.clear()
        for style in styles:
            item = QStandardItem(style)
            self.font_style_model.appendRow(item)
    
    def get_style_index(self):
        """Get the index of the current font style in the styles list."""
        family = self.current_font.family()
        styles = self.font_db.styles(family)
        
        # Determine the current style based on font properties
        current_style = ""
        if self.current_font.bold() and self.current_font.italic():
            current_style = "Bold Italic"
        elif self.current_font.bold():
            current_style = "Bold"
        elif self.current_font.italic():
            current_style = "Italic"
        else:
            current_style = "Regular"
        
        # Find the closest match
        for i, style in enumerate(styles):
            if style == current_style:
                return i
        
        return 0  # Default to first style if no match
    
    def update_color_preview(self):
        """Update the color preview widget with the current color."""
        style = f"background-color: {self.current_color.name()};"
        self.ui.colorPreview.setStyleSheet(style)
    
    def update_preview(self):
        """Update the preview text with the current font and color."""
        try:
            # Use a more direct approach to update the preview text
            preview_text = self.ui.previewTextEdit
            
            # Store current text
            current_text = preview_text.toPlainText()
            
            # Clear and set default document font
            preview_text.clear()
            preview_text.document().setDefaultFont(self.current_font)
            
            # Insert text with the current font and color
            preview_text.setTextColor(self.current_color)
            preview_text.insertPlainText(current_text or "AaBbCcDdEeFfGg 0123456789")
            
            # Reset cursor position
            cursor = preview_text.textCursor()
            cursor.setPosition(0)
            preview_text.setTextCursor(cursor)
            
            # Debug
            print(f"Updated preview with font: {self.current_font.family()}, size: {self.current_font.pointSize()}, "
                  f"bold: {self.current_font.bold()}, italic: {self.current_font.italic()}, "
                  f"color: {self.current_color.name()}")
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def on_font_family_changed(self, selected, deselected):
        """Handle font family selection change."""
        indexes = selected.indexes()
        if indexes:
            family = indexes[0].data()
            self.current_font.setFamily(family)
            print(f"Font family changed to: {family}")
            
            # Update font styles list for the new family
            self.update_font_styles()
            
            # Select a style
            self.ui.fontStyleListView.setCurrentIndex(self.font_style_model.index(0, 0))
            
            # Update preview
            self.update_preview()
    
    def on_font_style_changed(self, selected, deselected):
        """Handle font style selection change."""
        indexes = selected.indexes()
        if indexes:
            style = indexes[0].data()
            print(f"Font style changed to: {style}")
            
            # Apply style to font
            if "Bold" in style:
                self.current_font.setBold(True)
            else:
                self.current_font.setBold(False)
                
            if "Italic" in style:
                self.current_font.setItalic(True)
            else:
                self.current_font.setItalic(False)
            
            # Update preview
            self.update_preview()
    
    def on_font_size_changed(self, selected, deselected):
        """Handle font size selection change."""
        indexes = selected.indexes()
        if indexes:
            try:
                size_str = indexes[0].data()
                size = int(size_str)
                print(f"Font size changed to: {size}")
                self.current_font.setPointSize(size)
                
                # Update preview
                self.update_preview()
            except (ValueError, TypeError) as e:
                print(f"Error setting font size: {e}")
    
    def on_strikeout_toggled(self, checked):
        """Handle strikeout checkbox toggle."""
        print(f"Strikeout toggled: {checked}")
        self.current_font.setStrikeOut(checked)
        self.update_preview()
    
    def on_underline_toggled(self, checked):
        """Handle underline checkbox toggle."""
        print(f"Underline toggled: {checked}")
        self.current_font.setUnderline(checked)
        self.update_preview()
    
    def on_color_button_clicked(self):
        """Handle color button click"""
        from prometheus_prompt_generator.ui.color_dialog import ColorDialog
        
        color, ok = ColorDialog.get_color(self, self.current_color)
        if ok:
            print(f"Color changed to: {color.name()}")
            self.current_color = color
            self.update_color_preview()
            self.update_preview()
    
    def apply_changes(self):
        """Apply the current font and color changes."""
        print(f"Applying changes: {self.current_font.family()}, {self.current_font.pointSize()}")
        self.fontSelected.emit(self.current_font, self.current_color)
    
    def get_font(self):
        """Get the selected font."""
        return self.current_font
    
    def get_color(self):
        """Get the selected color."""
        return self.current_color
    
    def accept(self):
        """Accept dialog and apply changes"""
        print(f"Dialog accepted with font: {self.current_font.family()}, {self.current_font.pointSize()}")
        self.apply_changes()
        super().accept()
    
    def reject(self):
        """Reject dialog and do not apply changes"""
        print("Dialog rejected")
        super().reject()
    
    def closeEvent(self, event):
        """Handle window close event."""
        print("Dialog close event")
        self.reject()
        event.accept()
    
    @staticmethod
    def get_font_and_color(parent=None, initial_font=None, initial_color=None):
        """
        Static convenience method to get a font and color from the user.
        
        Args:
            parent: Parent widget
            initial_font: Initial font to display
            initial_color: Initial color to display
            
        Returns:
            tuple: (QFont, QColor, bool) - The selected font, color, and whether OK was pressed
        """
        dialog = FontDialog(parent, initial_font, initial_color)
        result = dialog.exec()
        
        font = dialog.get_font()
        color = dialog.get_color()
        
        print(f"Dialog returned font: {font.family()}, {font.pointSize()}, bold: {font.bold()}, italic: {font.italic()}")
        
        return font, color, result == QDialog.Accepted 