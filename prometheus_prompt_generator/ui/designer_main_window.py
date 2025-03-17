"""
Prometheus AI Prompt Generator - Designer UI Integration

This module provides a complete implementation of the PrometheusPromptGenerator main window
using the Qt Designer UI file for layout while preserving all functionality.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QListWidgetItem, QFontDialog, QColorDialog, 
    QFileDialog, QMessageBox, QMenu, QApplication, QListWidget
)
from PyQt6.QtGui import QFont, QAction, QColor, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6 import uic

# Import components from the package
from ..utils.constants import (
    DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, URGENCY_LEVELS, 
    DEFAULT_THEME_COLORS, DEFAULT_THEMES
)
# Fixed imports - use the correct paths to the actual modules
from ..utils.prompt_library import PromptLibrary
from ..utils import utils
from .prompt_list_item import PromptListItem
from .metadata_dialog import MetadataDialog

# Determine the UI file path
UI_DIR = os.path.join(os.path.dirname(__file__), 'designer')
UI_FILE = os.path.join(UI_DIR, 'main_window.ui')

# Check if UI file exists, generate it if not
if not os.path.exists(UI_FILE):
    from scripts.generate_ui_file import generate_ui_file
    generate_ui_file()

# Try to import the generated UI class
try:
    from .designer.ui_main_window import Ui_MainWindow
    USE_INHERITANCE = True
except ImportError:
    # Fall back to direct loading if the UI class isn't available
    USE_INHERITANCE = False


class DesignerPrometheusPromptGenerator(QMainWindow):
    """Prometheus AI Application for generating prompts with different urgency levels.
    
    This version uses the Qt Designer UI file for layout but preserves all functionality
    of the original hand-coded application.
    """
    
    resized = pyqtSignal()
    
    def __init__(self):
        """Initialize the Prometheus AI Prompt Generator application."""
        super().__init__()
        
        # Initialize UI either via inheritance or direct loading
        if USE_INHERITANCE and isinstance(self, Ui_MainWindow):
            self.setupUi(self)
        else:
            # Direct loading approach
            if os.path.exists(UI_FILE):
                self.ui = uic.loadUi(UI_FILE, self)
            else:
                raise FileNotFoundError(f"UI file not found: {UI_FILE}")
        
        # Application state
        self.selected_prompts = []
        self.prompt_library = PromptLibrary()
        self.current_theme = "Dark Blue"
        
        # Initialize the UI further
        self.setup_connections()
        self.setup_menus()
        self.apply_theme(self.current_theme)
        self.apply_font_settings()
        
        # Populate the prompt list
        self.populate_prompt_list()
    
    def setup_connections(self):
        """Connect signals to slots for all interactive elements."""
        # Access widgets via self or self.ui depending on approach
        widgets = self if USE_INHERITANCE else self.ui
        
        # Connect search input
        widgets.searchInput.textChanged.connect(self.filter_prompts)
        
        # Set up QListWidget selection behavior - use ExtendedSelection for drag-to-select
        widgets.promptList.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Connect prompt list selection
        widgets.promptList.itemClicked.connect(self.handle_item_selection)
        
        # Connect urgency slider
        widgets.urgencySlider.valueChanged.connect(self.update_urgency_display)
        
        # Connect buttons
        widgets.selectAllButton.clicked.connect(self.select_all_prompts)
        widgets.selectNoneButton.clicked.connect(self.select_no_prompts)
        widgets.generatePromptsButton.clicked.connect(self.generate_prompts)
        widgets.copyToClipboardButton.clicked.connect(self.copy_to_clipboard)
        widgets.addPromptButton.clicked.connect(self.add_custom_prompt)
        
        # Connect resize events
        self.resized.connect(self.handle_resize)
    
    def setup_menus(self):
        """Setup application menus and connect actions."""
        # Access widgets via self or self.ui depending on approach
        widgets = self if USE_INHERITANCE else self.ui
        
        # File menu actions
        widgets.actionImport.triggered.connect(self.import_prompts)
        widgets.actionExport.triggered.connect(self.export_prompts)
        widgets.actionExit.triggered.connect(self.close)
        
        # Edit menu actions
        widgets.actionChangeFont.triggered.connect(self.change_font)
        widgets.actionResetFont.triggered.connect(self.reset_font_to_default)
        
        # Theme menu actions
        if hasattr(widgets, 'actionLightTheme'):
            widgets.actionLightTheme.triggered.connect(lambda: self.apply_theme("Light"))
        if hasattr(widgets, 'actionDarkTheme'):
            widgets.actionDarkTheme.triggered.connect(lambda: self.apply_theme("Dark Blue"))
        
        # Help menu actions
        widgets.actionAbout.triggered.connect(self.show_about)
    
    def apply_font_settings(self):
        """Apply font settings to all text widgets."""
        # Load saved font settings or use defaults
        font_family = DEFAULT_FONT_FAMILY
        font_size = DEFAULT_FONT_SIZE
        
        # Create font object
        font = QFont(font_family, font_size)
        
        # Apply to application
        QApplication.setFont(font)
        
        # Apply to specific widgets that might need different styling
        # Access widgets via self or self.ui depending on approach
        widgets = self if USE_INHERITANCE else self.ui
        
        # Headers with larger font size
        header_font = QFont(font_family, font_size + 2, QFont.Weight.Bold)
        if hasattr(widgets, 'promptTypesHeader'):
            widgets.promptTypesHeader.setFont(header_font)
        if hasattr(widgets, 'urgencyHeader'):
            widgets.urgencyHeader.setFont(header_font)
        if hasattr(widgets, 'generatedPromptHeader'):
            widgets.generatedPromptHeader.setFont(header_font)
    
    def apply_theme(self, theme_name):
        """Apply a theme to the application UI."""
        if theme_name not in DEFAULT_THEMES:
            theme_name = "Dark Blue"  # Default to Dark Blue if theme not found
        
        # Set the current theme
        self.current_theme = theme_name
        
        # Get colors for the selected theme
        colors = DEFAULT_THEME_COLORS.get(theme_name, {})
        
        # Determine if this is a dark theme
        is_dark = theme_name.startswith("Dark")
        
        # Create stylesheet
        stylesheet = f"""
        QMainWindow, QDialog {{ background-color: {colors.get('background', '#2c2c2c')}; color: {colors.get('text', '#ffffff')}; }}
        QMenuBar, QMenu {{ background-color: {colors.get('menu_bg', '#333333')}; color: {colors.get('menu_text', '#ffffff')}; }}
        QMenuBar::item:selected, QMenu::item:selected {{ background-color: {colors.get('accent', '#2980b9')}; }}
        QLineEdit, QTextEdit {{ 
            background-color: {colors.get('input_bg', '#3c3c3c')}; 
            color: {colors.get('input_text', '#ffffff')}; 
            border: 1px solid {colors.get('border', '#555555')}; 
            padding: 4px;
        }}
        QPushButton {{ 
            background-color: {colors.get('button_bg', '#2980b9')}; 
            color: {colors.get('button_text', '#ffffff')}; 
            border: none; 
            padding: 6px 12px; 
            border-radius: 3px;
        }}
        QPushButton:hover {{ background-color: {colors.get('button_hover', '#3498db')}; }}
        QPushButton:pressed {{ background-color: {colors.get('button_pressed', '#1c5c8e')}; }}
        QListWidget {{ 
            background-color: {colors.get('list_bg', '#3c3c3c')}; 
            color: {colors.get('list_text', '#ffffff')}; 
            alternate-background-color: {colors.get('list_alt_bg', '#444444')};
            border: 1px solid {colors.get('border', '#555555')}; 
        }}
        QListWidget::item:selected {{ 
            background-color: {colors.get('accent', '#2980b9')}; 
            color: {colors.get('accent_text', '#ffffff')}; 
        }}
        QSlider::handle:horizontal {{ 
            background-color: {colors.get('accent', '#2980b9')}; 
            border-radius: 5px; 
            width: 10px; 
            margin: -4px 0; 
        }}
        QSlider::groove:horizontal {{ 
            height: 6px; 
            background-color: {colors.get('slider_bg', '#555555')}; 
            border-radius: 3px;
        }}
        QLabel {{ color: {colors.get('text', '#ffffff')}; }}
        QMessageBox {{ background-color: {colors.get('background', '#2c2c2c')}; color: {colors.get('text', '#ffffff')}; }}
        QLabel#sectionHeader {{ 
            color: {colors.get('header_text', '#ffffff')}; 
            font-weight: bold; 
        }}
        QStatusBar {{ 
            background-color: {colors.get('statusbar_bg', '#333333')}; 
            color: {colors.get('statusbar_text', '#ffffff')};
        }}
        """
        
        # Apply stylesheet
        self.setStyleSheet(stylesheet)
        
        # Apply to all existing prompt list items
        for i in range(self.promptList.count()):
            item = self.promptList.item(i)
            widget = self.promptList.itemWidget(item)
            if isinstance(widget, PromptListItem):
                widget.updateStyle(is_dark, colors.get('accent', '#2980b9'))
    
    def populate_prompt_list(self):
        """Populate the prompt list with available prompt types."""
        # First clear any existing items
        self.promptList.clear()
        self.selected_prompts = []  # Reset selected prompts when repopulating
        
        # Get all prompt types from the prompt library
        prompt_types = self.prompt_library.get_types()
        
        # Sort prompt types alphabetically for a better UI experience
        prompt_types.sort()
        
        # Add each prompt type to the list
        for prompt_type in prompt_types:
            # Get display name and info for this prompt type
            prompt_info = self.prompt_library.get(prompt_type, {})
            display_name = prompt_info.get("title", prompt_type)
            
            # Create list item
            item = QListWidgetItem()
            self.promptList.addItem(item)
            
            # Create custom widget for this item
            item_widget = PromptListItem(
                prompt_type=prompt_type,  # The exact key from the prompt library
                display_name=display_name,
                show_info_icon=True
            )
            
            # Connect the info button to show metadata
            item_widget.info_clicked.connect(self.show_metadata_dialog)
            
            # Set the item widget for this list item
            self.promptList.setItemWidget(item, item_widget)
            
        # Update the UI to reflect the current selection state
        self.update_selection_display()
    
    def show_metadata_dialog(self, prompt_type):
        """Show the metadata dialog for a prompt type."""
        # Get prompt information
        prompt_info = self.prompt_library.get(prompt_type, {})
        if not prompt_info:
            return
        
        # Create and show dialog
        dialog = MetadataDialog(prompt_type, prompt_info, parent=self)
        dialog.exec()
    
    def update_urgency_display(self, value):
        """Update the urgency display with the current slider value."""
        # Get urgency level text from the value
        urgency_text = URGENCY_LEVELS.get(value, "Normal")
        
        # Update the label
        self.urgencyDisplay.setText(f"{urgency_text} ({value}/10)")
    
    def handle_item_selection(self, item):
        """Handle selection of an item in the prompt list."""
        # Update selected_prompts to match the current UI selection state
        self.selected_prompts = []
        
        # Get all currently selected items
        for i in range(self.promptList.count()):
            item = self.promptList.item(i)
            if item.isSelected():
                item_widget = self.promptList.itemWidget(item)
                if item_widget:
                    self.selected_prompts.append(item_widget.prompt_type)
    
    def handle_resize(self):
        """Handle window resize events."""
        # Adjust UI elements if needed on resize
        pass
    
    def resizeEvent(self, event):
        """Override resize event to emit signal."""
        super().resizeEvent(event)
        self.resized.emit()
    
    def select_all_prompts(self):
        """Select all prompt types in the list."""
        # Block signals to prevent unnecessary updates
        self.promptList.blockSignals(True)
        
        try:
            # Clear and rebuild selected prompts list
            self.selected_prompts = []
            
            # Select all items in the UI and track them
            for i in range(self.promptList.count()):
                item = self.promptList.item(i)
                if not item.isHidden(): # Only select visible items if filtering is active
                    item.setSelected(True)
                    item_widget = self.promptList.itemWidget(item)
                    if item_widget:
                        self.selected_prompts.append(item_widget.prompt_type)
        finally:
            # Unblock signals
            self.promptList.blockSignals(False)
    
    def select_no_prompts(self):
        """Deselect all prompt types in the list."""
        # Block signals to prevent unnecessary updates
        self.promptList.blockSignals(True)
        
        try:
            # Clear selected prompts list
            self.selected_prompts = []
            
            # Deselect all items in the UI
            for i in range(self.promptList.count()):
                item = self.promptList.item(i)
                item.setSelected(False)
        finally:
            # Unblock signals
            self.promptList.blockSignals(False)
    
    def generate_prompts(self):
        """Generate prompts based on selected types and urgency level."""
        # Check if any prompts are selected
        if not self.selected_prompts:
            QMessageBox.information(
                self, 
                "No Prompts Selected",
                "Please select at least one prompt type."
            )
            return
            
        # DEBUG: Show what's in selected_prompts
        print(f"DEBUG: Selected prompts: {self.selected_prompts}")
        
        # DEBUG: Reconfirm what's actually selected in the UI
        ui_selected = []
        for i in range(self.promptList.count()):
            item = self.promptList.item(i)
            if item.isSelected():
                widget = self.promptList.itemWidget(item)
                if widget:
                    ui_selected.append(widget.prompt_type)
        print(f"DEBUG: UI Selected items: {ui_selected}")
        
        # Synchronize selected_prompts with UI selections to ensure consistency
        self.selected_prompts = ui_selected
        
        # Get urgency level
        urgency_level = self.urgencySlider.value()
        
        # Clear current output
        self.outputText.clear()
        
        # Track errors to show only one summary dialog at the end
        errors = []
        generated_count = 0
        
        # Generate prompts
        generated_texts = []
        
        # Process all selected prompts
        for prompt_type in self.selected_prompts:
            try:
                # Get prompt template
                prompt_data = self.prompt_library.get(prompt_type)
                
                # DEBUG: Show what data we're getting for each prompt
                print(f"DEBUG: Prompt type: {prompt_type}")
                print(f"DEBUG: Title: {prompt_data.get('title', 'MISSING TITLE')}")
                print(f"DEBUG: Has prompts array: {'prompts' in prompt_data}")
                
                if not prompt_data:
                    errors.append(f"Prompt type '{prompt_type}' not found in library")
                    continue
                    
                # Check if this is the new format (with prompts array) or old format (with template)
                if "prompts" in prompt_data and isinstance(prompt_data["prompts"], list):
                    # New format with urgency levels
                    urgency_idx = min(urgency_level - 1, len(prompt_data["prompts"]) - 1)
                    if urgency_idx < 0:
                        urgency_idx = 0
                    
                    if urgency_idx < len(prompt_data["prompts"]):
                        prompt_text = prompt_data["prompts"][urgency_idx]
                    else:
                        # Fallback to the first prompt if urgency level is out of range
                        prompt_text = prompt_data["prompts"][0]
                else:
                    # Old format with template
                    template = prompt_data.get("template", "")
                    
                    if not template:
                        errors.append(f"Template for '{prompt_type}' is empty")
                        continue
                    
                    # Generate with urgency applied
                    prompt_text = utils.generate_template_with_urgency(template, urgency_level)
                
                # Make sure the title always has a value, either from prompt_data or the prompt_type
                title = prompt_data.get('title', '')
                if not title:
                    title = prompt_type.replace('_', ' ').title()
                
                # Add to results with prompt type as header
                formatted_prompt = f"### {title} ###\n\n{prompt_text}"
                generated_texts.append(formatted_prompt)
                generated_count += 1
                
            except Exception as e:
                errors.append(f"Error generating '{prompt_type}': {str(e)}")
        
        # If we generated at least one prompt, show it
        if generated_texts:
            # Join all prompts with separator
            separator = "\n\n" + "-" * 60 + "\n\n"
            all_prompts = separator.join(generated_texts)
            
            # Set the output text
            self.outputText.setText(all_prompts)
            
            # Update status bar
            if hasattr(self, 'statusbar'):
                self.statusbar.showMessage(
                    f"Generated {generated_count} prompt(s) with urgency level {urgency_level}/10", 
                    3000
                )
        else:
            self.outputText.setText("No prompts could be generated. Please check the error message.")
        
        # If there were errors, show a single error dialog with all issues
        if errors:
            error_message = "The following errors occurred:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Prompt Generation Issues", error_message)
    
    def copy_to_clipboard(self):
        """Copy the generated prompt to the clipboard."""
        text = self.outputText.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Show confirmation in status bar if available
            if hasattr(self, 'statusbar'):
                self.statusbar.showMessage("Copied to clipboard", 2000)
    
    def filter_prompts(self, text):
        """Filter the prompt list based on search text."""
        # Block signals during updates
        self.promptList.blockSignals(True)
        
        try:
            # If text is empty, show all prompts
            if not text:
                for i in range(self.promptList.count()):
                    item = self.promptList.item(i)
                    item.setHidden(False)
                    
                    # Restore selection state
                    item_widget = self.promptList.itemWidget(item)
                    if item_widget and item_widget.prompt_type in self.selected_prompts:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
                return
            
            # Otherwise, filter based on text
            text = text.lower()
            for i in range(self.promptList.count()):
                item = self.promptList.item(i)
                widget = self.promptList.itemWidget(item)
                if widget:
                    display_name = widget.display_name.lower()
                    prompt_type = widget.prompt_type.lower()
                    
                    # Show if text is in display name or prompt type
                    matches = text in display_name or text in prompt_type
                    item.setHidden(not matches)
                    
                    # Restore selection state for visible items
                    if not item.isHidden() and widget.prompt_type in self.selected_prompts:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        finally:
            # Unblock signals
            self.promptList.blockSignals(False)
    
    def add_custom_prompt(self):
        """Add a custom prompt to the library."""
        # Display an informational message for now
        QMessageBox.information(
            self,
            "Add Custom Prompt",
            "This feature is not yet implemented."
        )
    
    def import_prompts(self):
        """Import prompts from a file."""
        # Display an informational message for now
        QMessageBox.information(
            self,
            "Import Prompts",
            "This feature is not yet implemented."
        )
    
    def export_prompts(self):
        """Export prompts to a file."""
        # Display an informational message for now
        QMessageBox.information(
            self,
            "Export Prompts",
            "This feature is not yet implemented."
        )
    
    def change_font(self):
        """Change the application font."""
        current_font = QApplication.font()
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            QApplication.setFont(font)
    
    def reset_font_to_default(self):
        """Reset the font to the default."""
        font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
        QApplication.setFont(font)
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Prometheus AI Prompt Generator",
            "<h3>Prometheus AI Prompt Generator</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A professional desktop application for generating AI prompts "
            "with various urgency levels.</p>"
            "<p>© 2025 Prometheus AI</p>"
        )

    def update_selection_display(self):
        """Update the UI to reflect the current selection state."""
        # Block signals during updates
        self.promptList.blockSignals(True)
        
        try:
            # Update selection states
            for i in range(self.promptList.count()):
                item = self.promptList.item(i)
                item_widget = self.promptList.itemWidget(item)
                
                if item_widget and item_widget.prompt_type in self.selected_prompts:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
        finally:
            # Unblock signals
            self.promptList.blockSignals(False)


# Create a version that uses inheritance if UI class is available
if USE_INHERITANCE:
    class DesignerPrometheusPromptGeneratorInheritance(DesignerPrometheusPromptGenerator, Ui_MainWindow):
        """Version of PrometheusPromptGenerator that uses multiple inheritance with the UI class."""
        
        def __init__(self):
            """Initialize the application using multiple inheritance."""
            super().__init__()
            
            # Note: setupUi is called in the parent class's __init__
            
            # Additional initialization if needed
            pass


# Function to get the appropriate class based on availability
def get_designer_main_window_class():
    """Return the appropriate designer main window class based on UI availability."""
    if USE_INHERITANCE:
        return DesignerPrometheusPromptGeneratorInheritance
    else:
        return DesignerPrometheusPromptGenerator 