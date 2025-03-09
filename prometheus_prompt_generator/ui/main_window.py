"""
Prometheus AI Prompt Generator - Main Window

The main window of the Prometheus AI Prompt Generator application.
"""

import os
import sys
import random
import json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QSlider, QPushButton, QTextEdit, 
                           QSplitter, QFrame, QAbstractItemView, QStatusBar, 
                           QMessageBox, QInputDialog, QDialog, QFileDialog, QMenu, QMenuBar, QLineEdit, QListWidgetItem,
                           QDialogButtonBox, QFormLayout, QGridLayout, QToolButton, QFontDialog, QComboBox, QSizePolicy)
from PyQt6.QtCore import Qt, QSettings, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QAction, QActionGroup

# Import qt-material for improved theming
from qt_material import apply_stylesheet

# Import our modules
from ..utils.constants import (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, DEFAULT_HEADING_SIZE,
                              PROMETHEUS_BLUE, PROMETHEUS_LIGHT_BLUE, PROMETHEUS_DARK, 
                              PROMETHEUS_LIGHT, PROMETHEUS_ACCENT, AVAILABLE_THEMES, URGENCY_LEVELS)
from ..utils.prompt_library import PromptLibrary
from ..utils import utils
from .prompt_list_item import PromptListItem
from .metadata_dialog import MetadataDialog

class PrometheusPromptGenerator(QMainWindow):
    """Prometheus AI Application for generating prompts with different urgency levels"""
    
    resized = pyqtSignal()
    
    def __init__(self):
        """Initialize the application"""
        super().__init__()
        
        # Setup settings
        self.settings = QSettings("PrometheusAI", "PromptGenerator")
        self.font_family = self.settings.value("font_family", DEFAULT_FONT_FAMILY)
        self.font_size = int(self.settings.value("font_size", DEFAULT_FONT_SIZE))
        
        # Initialize theme attribute to prevent AttributeError
        self.current_theme = self.settings.value("theme", "Dark Blue")
        
        # Set window title and geometry
        self.setWindowTitle("Prometheus AI Prompt Generator")
        self.setMinimumSize(900, 600)
        
        # Create central widget for the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize prompt library
        self.prompt_library = PromptLibrary()
        
        # Initialize the user interface
        self.initUI()
        
        # Setup status bar
        self.statusBar().showMessage("Ready")
        
        # Apply font settings
        self.applyFontSettings()
        
        # Apply theme from settings or default to Dark Blue
        self.applyTheme(self.current_theme)
        
    def initUI(self):
        """Initialize the user interface"""
        self.app = self.get_app_instance()
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create left panel with fixed width for prompt types
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(300)
        left_panel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)
        
        # Create right panel with expanding width for generated content
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        
        # Add both panels to the main layout with a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Right panel stretches
        main_layout.addWidget(splitter)
        
        # LEFT PANEL - Available Prompt Types
        prompt_types_header = QLabel("Available Prompt Types")
        prompt_types_header.setObjectName("sectionHeader")
        prompt_types_header.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 2, QFont.Weight.Bold))
        left_layout.addWidget(prompt_types_header)
        
        # Search input with proper styling
        search_layout = QHBoxLayout()
        
        # Create a proper search icon using standard Qt icons instead of emoji
        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("searchInput")
        self.filter_input.setPlaceholderText("Search prompt types...")
        self.filter_input.textChanged.connect(self.filterPrompts)
        
        # Use standard Qt icon for search - this is the modern approach
        search_icon = self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogContentsView)
        self.filter_input.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)
        
        search_layout.addWidget(self.filter_input)
        left_layout.addLayout(search_layout)
        
        # Button row for selecting all/none
        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("selectAllButton")
        select_all_btn.clicked.connect(self.selectAllPrompts)
        select_none_btn = QPushButton("Select None")
        select_none_btn.setObjectName("selectNoneButton")
        select_none_btn.clicked.connect(self.selectNoPrompts)
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(select_none_btn)
        left_layout.addLayout(select_buttons_layout)
        
        # Prompt types list with checkboxes
        self.prompt_list = QListWidget()
        self.prompt_list.setObjectName("promptList")
        self.prompt_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.prompt_list.setAlternatingRowColors(True)
        self.prompt_list.itemClicked.connect(self.handleItemSelection)
        left_layout.addWidget(self.prompt_list)
        
        # Add new prompt button
        add_prompt_btn = QPushButton("Add Custom Prompt")
        add_prompt_btn.setObjectName("addPromptButton")
        add_prompt_btn.clicked.connect(self.addCustomPrompt)
        left_layout.addWidget(add_prompt_btn)
        
        # RIGHT PANEL - Urgency and Generated Prompt
        urgency_header = QLabel("Urgency Level")
        urgency_header.setObjectName("sectionHeader")
        urgency_header.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 2, QFont.Weight.Bold))
        right_layout.addWidget(urgency_header)
        
        # Urgency slider with labels
        urgency_layout = QVBoxLayout()
        
        # Display the current urgency level 
        self.urgency_display = QLabel("Normal (3)")
        self.urgency_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.urgency_display.setObjectName("urgencyDisplay")
        self.urgency_display.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, QFont.Weight.Bold))
        urgency_layout.addWidget(self.urgency_display)
        
        # Slider with min, max labels
        slider_row = QHBoxLayout()
        min_label = QLabel("Low")
        min_label.setObjectName("minLabel")
        slider_row.addWidget(min_label)
        
        self.urgency_slider = QSlider(Qt.Orientation.Horizontal)
        self.urgency_slider.setMinimum(1)
        self.urgency_slider.setMaximum(10)
        self.urgency_slider.setValue(5)
        self.urgency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.urgency_slider.setTickInterval(1)
        self.urgency_slider.setObjectName("urgencySlider")
        self.urgency_slider.valueChanged.connect(self.updateUrgencyDisplay)
        slider_row.addWidget(self.urgency_slider)
        
        max_label = QLabel("Extreme")
        max_label.setObjectName("maxLabel")
        slider_row.addWidget(max_label)
        
        urgency_layout.addLayout(slider_row)
        right_layout.addLayout(urgency_layout)
        
        # Generated prompt section
        generated_header = QLabel("Generated Prompt")
        generated_header.setObjectName("sectionHeader")
        generated_header.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 2, QFont.Weight.Bold))
        right_layout.addWidget(generated_header)
        
        # Output area
        self.output_text = QTextEdit()
        self.output_text.setObjectName("outputText")
        self.output_text.setReadOnly(False)
        self.output_text.setPlaceholderText("The generated prompt will appear here. You can edit it as needed.")
        right_layout.addWidget(self.output_text)
        
        # Create a button row for actions
        button_row = QHBoxLayout()
        
        # Generate Prompts button
        generate_btn = QPushButton("Generate Prompts")
        generate_btn.setObjectName("generateButton")
        generate_btn.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 1, QFont.Weight.Bold))
        generate_btn.setMinimumHeight(40)
        generate_btn.clicked.connect(self.generatePrompts)
        button_row.addWidget(generate_btn)
        
        # Button to copy to clipboard
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setObjectName("copyButton")
        copy_btn.setMinimumHeight(40)
        copy_btn.clicked.connect(self.copyToClipboard)
        button_row.addWidget(copy_btn)
        
        # Add the button row to the right layout
        right_layout.addLayout(button_row)
        
        # Set the central widget
        self.central_widget.setLayout(main_layout)
        
        # Populate prompt list
        self.populatePromptList()
        
        # Create menu bar
        self.createMenuBar()
        
        # Connect resize signal
        self.resized.connect(self.handleResize)
        
    def get_app_instance(self):
        """Get the QApplication instance"""
        from PyQt6.QtWidgets import QApplication
        return QApplication.instance()
        
    def applyFontSettings(self):
        """Apply font settings to all widgets"""
        # Create the base font
        base_font = QFont(self.font_family, self.font_size)
        
        # Apply to application
        self.app.setFont(base_font)
        
        # Apply to specific widgets (overriding as needed)
        heading_font = QFont(self.font_family, DEFAULT_HEADING_SIZE, QFont.Weight.Bold)
        
        for widget in self.findChildren(QLabel):
            if widget.objectName() == "sectionHeader":
                widget.setFont(heading_font)
            else:
                widget.setFont(base_font)
        
        # Apply to text editing widgets
        for widget in self.findChildren(QTextEdit):
            widget.setFont(base_font)
        
        # Refresh status bar
        self.statusBar().setFont(base_font)
        
    def applyTheme(self, theme_name):
        """Apply a theme to the application"""
        # Store theme name for reference
        self.current_theme = theme_name
        
        # Save theme setting
        self.settings.setValue("theme", theme_name)
        
        # Check if it's a dark or light theme
        is_dark = utils.is_dark_theme(theme_name)
        
        # Apply the theme using qt-material
        if theme_name in AVAILABLE_THEMES:
            apply_stylesheet(self.app, theme=AVAILABLE_THEMES[theme_name])
            
            # Get the primary color from the theme
            primary_color = utils.get_theme_color(theme_name)
            
            # Apply theme colors to custom widgets
            for item_idx in range(self.prompt_list.count()):
                item = self.prompt_list.item(item_idx)
                widget = self.prompt_list.itemWidget(item)
                if isinstance(widget, PromptListItem):
                    widget.updateStyle(is_dark, primary_color)
            
            # Set status bar message to confirm theme change
            self.statusBar().showMessage(f"Theme changed to {theme_name}", 3000)
        else:
            # Fallback if theme not found
            self.statusBar().showMessage(f"Theme '{theme_name}' not found, using default", 3000)
            
    def populatePromptList(self):
        """Populate the list of available prompt types"""
        # Clear the list first
        self.prompt_list.clear()
        
        # Get all prompt types
        prompt_types = self.prompt_library.get_types()
        
        # Add each prompt type to the list with a custom widget
        for prompt_type in sorted(prompt_types):
            # Get prompt info
            prompt_info = self.prompt_library.get(prompt_type, {})
            display_name = prompt_info.get("title", utils.format_display_name(prompt_type))
            
            # Create list item
            item = QListWidgetItem(self.prompt_list)
            
            # Create and set custom widget with info icon
            widget = PromptListItem(prompt_type, display_name, parent=self.prompt_list, show_info_icon=True)
            
            # Connect signals
            widget.clicked.connect(self.handleItemSelection)
            widget.info_clicked.connect(self.showMetadataDialog)
            
            # Set item size to match widget
            item.setSizeHint(widget.sizeHint())
            
            # Set widget for the item
            self.prompt_list.addItem(item)
            self.prompt_list.setItemWidget(item, widget)
        
    def showMetadataDialog(self, prompt_type):
        """Show dialog to view/edit prompt metadata"""
        dialog = MetadataDialog(prompt_type, self.prompt_library, parent=self)
        if dialog.exec():
            # Refresh the prompt list to show any updates
            self.populatePromptList()
            
    def updateUrgencyDisplay(self, value):
        """Update the urgency level display"""
        self.urgency_display.setText(URGENCY_LEVELS.get(value, f"Level {value}/10"))
            
    def handleItemSelection(self, item):
        """Handle item selection in the prompt list"""
        # We removed the brief description, so this method now just
        # handles the selection of an item in the prompt list
        pass
        
    def handleResize(self):
        """Handle window resize events"""
        # Adjust UI elements based on window size
        pass
        
    def resizeEvent(self, event):
        """Override resize event to emit a custom signal"""
        super().resizeEvent(event)
        self.resized.emit()
        
    def createMenuBar(self):
        """Create the menu bar with all menu items"""
        # Main menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Import/Export prompts
        import_action = QAction("Import Prompts...", self)
        import_action.triggered.connect(self.importPrompts)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export Prompts...", self)
        export_action.triggered.connect(self.exportPrompts)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        # Font selection
        font_action = QAction("Change Font...", self)
        font_action.triggered.connect(self.changeFont)
        edit_menu.addAction(font_action)
        
        # Reset font
        reset_font_action = QAction("Reset Font", self)
        reset_font_action.triggered.connect(self.resetFontToDefault)
        edit_menu.addAction(reset_font_action)
        
        # Theme submenu
        theme_menu = edit_menu.addMenu("Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        # Dark themes
        dark_menu = theme_menu.addMenu("Dark Themes")
        for theme_name in sorted([name for name in AVAILABLE_THEMES.keys() if name.startswith("Dark")]):
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            if theme_name == self.current_theme:
                theme_action.setChecked(True)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.applyTheme(name))
            dark_menu.addAction(theme_action)
            theme_group.addAction(theme_action)
            
        # Light themes
        light_menu = theme_menu.addMenu("Light Themes")
        for theme_name in sorted([name for name in AVAILABLE_THEMES.keys() if name.startswith("Light")]):
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            if theme_name == self.current_theme:
                theme_action.setChecked(True)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.applyTheme(name))
            light_menu.addAction(theme_action)
            theme_group.addAction(theme_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("About Prometheus AI", self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
    
    def changeFont(self):
        """Open a dialog to change the application font"""
        current_font = QFont(self.font_family, self.font_size)
        font, ok = QFontDialog.getFont(current_font, self, "Select Font")
        if ok:
            # Update font settings
            self.font_family = font.family()
            self.font_size = font.pointSize()
            
            # Save to settings
            self.settings.setValue("font_family", self.font_family)
            self.settings.setValue("font_size", self.font_size)
            
            # Apply the new font
            self.applyFontSettings()
            
            self.statusBar().showMessage(f"Font changed to {self.font_family}, {self.font_size}pt", 3000)
            
    def resetFontToDefault(self):
        """Reset the font to the default"""
        # Reset to defaults
        self.font_family = DEFAULT_FONT_FAMILY
        self.font_size = DEFAULT_FONT_SIZE
        
        # Save to settings
        self.settings.setValue("font_family", self.font_family)
        self.settings.setValue("font_size", self.font_size)
        
        # Apply the new font
        self.applyFontSettings()
        
        self.statusBar().showMessage("Font reset to default", 3000)
        
    def refreshPromptList(self):
        """Refresh the list of prompt types"""
        # Store the current filter text
        current_filter = self.filter_input.text()
        
        # Re-populate the list
        self.populatePromptList()
        
        # Re-apply the filter
        if current_filter:
            self.filterPrompts(current_filter)
            
    def filterPrompts(self, text):
        """Filter the prompt list based on search text"""
        for index in range(self.prompt_list.count()):
            item = self.prompt_list.item(index)
            widget = self.prompt_list.itemWidget(item)
            
            if text.lower() in widget.prompt_type.lower() or text.lower() in widget.display_name.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def selectAllPrompts(self):
        """Select all prompt types in the list"""
        for index in range(self.prompt_list.count()):
            item = self.prompt_list.item(index)
            if not item.isHidden():
                item.setSelected(True)
                
    def selectNoPrompts(self):
        """Deselect all prompt types"""
        self.prompt_list.clearSelection()
        
    def generatePrompts(self):
        """Generate prompts based on selected types and urgency level"""
        # Get selected items
        selected_items = self.prompt_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one prompt type.")
            return
            
        # Get urgency level
        urgency_level = self.urgency_slider.value()
        
        # Generate prompts
        generated_prompts = []
        
        for item in selected_items:
            widget = self.prompt_list.itemWidget(item)
            prompt_type = widget.prompt_type
            
            # Get prompt template
            prompt_data = self.prompt_library.get(prompt_type)
            template = prompt_data.get("template", "")
            
            if template:
                # Generate with urgency applied (clean output without metadata)
                prompt_text = utils.generate_template_with_urgency(template, urgency_level)
                
                # Add to results (without metadata header)
                generated_prompts.append(prompt_text)
        
        # Join all prompts with separator
        separator = "\n\n" + "-" * 40 + "\n\n"
        all_prompts = separator.join(generated_prompts)
        
        # Set the output text
        self.output_text.setText(all_prompts)
        
        # Update status
        self.statusBar().showMessage(f"Generated {len(selected_items)} prompt(s) with urgency level {urgency_level}/10", 3000)
        
    def copyToClipboard(self):
        """Copy the generated prompt to clipboard"""
        text = self.output_text.toPlainText()
        
        if not text:
            QMessageBox.information(self, "Nothing to Copy", "Please generate a prompt first.")
            return
            
        # Set the text to clipboard
        clipboard = self.app.clipboard()
        clipboard.setText(text)
        
        # Show confirmation
        self.statusBar().showMessage("Prompt copied to clipboard", 3000)
        
    def addCustomPrompt(self):
        """Add a custom prompt to the library"""
        # Get prompt type
        prompt_type, ok = QInputDialog.getText(self, "Add Custom Prompt", 
                                             "Enter a unique identifier for the prompt type\n(e.g. 'interview_questions'):")
        if not ok or not prompt_type:
            return
            
        # Check if prompt type already exists
        if prompt_type in self.prompt_library.get_types():
            QMessageBox.warning(self, "Duplicate", 
                               f"A prompt with the identifier '{prompt_type}' already exists.\nPlease choose a different identifier.")
            return
            
        # Get display name
        display_name, ok = QInputDialog.getText(self, "Add Custom Prompt", 
                                              "Enter a display name for the prompt type\n(e.g. 'Interview Questions'):",
                                              text=utils.format_display_name(prompt_type))
        if not ok:
            return
            
        # Get template
        template_dialog = QDialog(self)
        template_dialog.setWindowTitle("Enter Prompt Template")
        template_dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(template_dialog)
        
        instruction_label = QLabel("Enter the prompt template. Use {placeholders} for variables.")
        layout.addWidget(instruction_label)
        
        template_edit = QTextEdit()
        template_edit.setPlaceholderText("Enter your prompt template here...")
        layout.addWidget(template_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(template_dialog.accept)
        button_box.rejected.connect(template_dialog.reject)
        layout.addWidget(button_box)
        
        if not template_dialog.exec():
            return
            
        template = template_edit.toPlainText()
        
        # Create prompt data
        prompt_data = {
            "title": display_name,
            "description": f"Custom prompt for {display_name.lower()}",
            "template": template,
            "metadata": {
                "author": "User",
                "version": "1.0.0",
                "created": "2025-03-09",
                "updated": "2025-03-09",
                "tags": ["custom"]
            }
        }
        
        # Save to library
        self.prompt_library.save_prompt(prompt_type, prompt_data)
        
        # Refresh list
        self.refreshPromptList()
        
        # Show confirmation
        self.statusBar().showMessage(f"Added custom prompt: {display_name}", 3000)
        
    def exportPrompts(self):
        """Export all prompts to a JSON file"""
        # Ask for file location
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Prompts", "", "JSON Files (*.json)")
        
        if not file_path:
            return
            
        # Add .json extension if not present
        if not file_path.endswith('.json'):
            file_path += '.json'
            
        try:
            # Export all prompts
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.prompt_library.prompts, f, indent=2)
                
            self.statusBar().showMessage(f"Exported {len(self.prompt_library.prompts)} prompts to {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting prompts: {str(e)}")
            
    def importPrompts(self):
        """Import prompts from a JSON file"""
        # Ask for file location
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Prompts", "", "JSON Files (*.json)")
        
        if not file_path:
            return
            
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_prompts = json.load(f)
                
            # Validate the imported data
            if not isinstance(imported_prompts, dict):
                raise ValueError("Invalid format: Expected a dictionary of prompts")
                
            # Count of imported prompts
            import_count = 0
            
            # Process each prompt
            for prompt_type, prompt_data in imported_prompts.items():
                # Basic validation
                if not isinstance(prompt_data, dict) or "template" not in prompt_data:
                    continue
                    
                # Save to library
                self.prompt_library.save_prompt(prompt_type, prompt_data)
                import_count += 1
                
            # Refresh list
            self.refreshPromptList()
            
            self.statusBar().showMessage(f"Imported {import_count} prompts", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing prompts: {str(e)}")
            
    def showAbout(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About Prometheus AI", 
                        "Prometheus AI Prompt Generator v1.0.0\n\n"
                        "A professional tool for generating AI prompts with different urgency levels.\n\n"
                        "© 2025 Prometheus AI Team")
                        
    def closeEvent(self, event):
        """Handle application closure"""
        # Save settings
        self.settings.sync()
        event.accept()
        
    def deletePrompt(self, prompt_type):
        """Delete a prompt from the library"""
        response = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete the '{prompt_type}' prompt?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                      
        if response == QMessageBox.StandardButton.Yes:
            self.prompt_library.delete_prompt(prompt_type)
            self.refreshPromptList()
            self.statusBar().showMessage(f"Deleted prompt: {prompt_type}", 3000)
        
    def showMetadataDialog(self, prompt_type):
        """Show dialog to view/edit prompt metadata"""
        dialog = MetadataDialog(prompt_type, self.prompt_library, parent=self)
        if dialog.exec():
            # Refresh the prompt list to show any updates
            self.populatePromptList()
            
    def updateUrgencyDisplay(self, value):
        """Update the urgency level display"""
        self.urgency_display.setText(URGENCY_LEVELS.get(value, f"Level {value}/10"))
            
    def handleResize(self):
        """Handle window resize events"""
        # Adjust UI elements based on window size
        pass
        
    def resizeEvent(self, event):
        """Override resize event to emit a custom signal"""
        super().resizeEvent(event)
        self.resized.emit() 