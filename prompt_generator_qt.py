#!/usr/bin/env python3
"""
Prometheus AI Prompt Generator

A professional desktop application for generating AI prompts with different
urgency levels using the prompt library, built with PyQt6 with dark mode support.
"""

import os
import sys
import random
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QSlider, QPushButton, QTextEdit, 
                           QSplitter, QFrame, QAbstractItemView, QStatusBar, 
                           QMessageBox, QInputDialog, QDialog, QFileDialog, QMenu, QMenuBar, QLineEdit, QListWidgetItem,
                           QDialogButtonBox, QFormLayout, QGridLayout, QToolButton)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QAction, QActionGroup

# Import qt-material for improved theming
from qt_material import apply_stylesheet

# Ensure prompt_library is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the prompt library
from prompt_library.prompt_loader import PromptLibrary

# Prometheus AI theme colors - more subdued now
PROMETHEUS_BLUE = QColor(52, 152, 219)  # More subdued blue
PROMETHEUS_LIGHT_BLUE = QColor(85, 175, 237)  # Lighter blue for accents
PROMETHEUS_DARK = QColor(33, 37, 43)     # Slightly richer dark background
PROMETHEUS_LIGHT = QColor(240, 240, 245) # Softer light background (not pure white)
PROMETHEUS_ACCENT = QColor(243, 156, 18)  # Orange-gold accent

# Available themes from qt-material
AVAILABLE_THEMES = {
    "Dark Blue": "dark_blue.xml",
    "Dark Teal": "dark_teal.xml",
    "Dark Amber": "dark_amber.xml", 
    "Dark Purple": "dark_purple.xml",
    "Dark Pink": "dark_pink.xml",
    "Dark Red": "dark_red.xml",
    "Dark Yellow": "dark_yellow.xml",
    "Light Blue": "light_blue.xml",
    "Light Teal": "light_teal.xml",
    "Light Amber": "light_amber.xml",
    "Light Purple": "light_purple.xml",
    "Light Pink": "light_pink.xml",
    "Light Red": "light_red.xml",
    "Light Yellow": "light_yellow.xml",
}

class PromptListItem(QWidget):
    """Custom widget to represent a prompt in the list with an info button"""
    def __init__(self, prompt_type, display_name, parent=None):
        super().__init__(parent)
        self.prompt_type = prompt_type
        self.display_name = display_name
        
        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Display name label
        self.name_label = QLabel(display_name)
        self.name_label.setFont(QFont("Arial", 11))
        
        # Prompt type in italics (semi-transparent)
        self.type_label = QLabel(prompt_type)
        font = QFont("Arial", 9)
        font.setItalic(True)
        self.type_label.setFont(font)
        self.type_label.setStyleSheet("color: rgba(180, 180, 180, 180);")  # More neutral color
        
        # Info button
        self.info_button = QToolButton()
        self.info_button.setText("i")
        self.info_button.setToolTip("View prompt details")
        self.info_button.setFixedSize(20, 20)
        self.info_button.setStyleSheet("""
            QToolButton {
                border-radius: 10px;
                background-color: #666;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #888;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.name_label, 1)  # 1 = stretch factor
        layout.addWidget(self.type_label, 0)  # 0 = no stretch
        layout.addWidget(self.info_button, 0)  # 0 = no stretch
        
        self.setLayout(layout)
        
        # Set a fixed height to ensure visibility in list
        self.setMinimumHeight(30)
        
    def updateStyle(self, is_dark_mode):
        """Update the style based on dark/light mode"""
        if is_dark_mode:
            self.type_label.setStyleSheet("color: rgba(180, 180, 180, 180);")
            self.info_button.setStyleSheet("""
                QToolButton {
                    border-radius: 10px;
                    background-color: #666;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }
                QToolButton:hover {
                    background-color: #888;
                }
            """)
        else:
            self.type_label.setStyleSheet("color: rgba(120, 120, 120, 180);")
            self.info_button.setStyleSheet("""
                QToolButton {
                    border-radius: 10px;
                    background-color: #888;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }
                QToolButton:hover {
                    background-color: #aaa;
                }
            """)

class MetadataDialog(QDialog):
    """Dialog to display and edit prompt metadata"""
    def __init__(self, prompt_type, prompt_library, parent=None):
        super().__init__(parent)
        self.prompt_type = prompt_type
        self.prompt_library = prompt_library
        self.prompt_data = prompt_library.prompts.get(prompt_type, {})
        
        self.setWindowTitle(f"Prompt Details: {prompt_type.replace('_', ' ').title()}")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for metadata
        form_layout = QFormLayout()
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter a description for this prompt")
        description = self.prompt_data.get("description", "")
        self.description_edit.setText(description)
        form_layout.addRow("Description:", self.description_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas")
        metadata = self.prompt_data.get("metadata", {})
        tags = metadata.get("tags", [])
        self.tags_edit.setText(", ".join(tags))
        form_layout.addRow("Tags:", self.tags_edit)
        
        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setText(metadata.get("author", ""))
        form_layout.addRow("Author:", self.author_edit)
        
        # Version
        self.version_edit = QLineEdit()
        self.version_edit.setText(metadata.get("version", "1.0.0"))
        form_layout.addRow("Version:", self.version_edit)
        
        # Created date
        self.created_edit = QLineEdit()
        self.created_edit.setText(metadata.get("created", "2025-03-09"))
        form_layout.addRow("Date Added:", self.created_edit)
        
        # Updated date
        self.updated_edit = QLineEdit()
        self.updated_edit.setText(metadata.get("updated", "2025-03-09"))
        form_layout.addRow("Last Updated:", self.updated_edit)
        
        # Add form to main layout
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def accept(self):
        """Save the metadata changes"""
        # Update the description
        self.prompt_data["description"] = self.description_edit.toPlainText()
        
        # Create or update metadata
        if "metadata" not in self.prompt_data:
            self.prompt_data["metadata"] = {}
        
        # Update metadata fields
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        self.prompt_data["metadata"]["tags"] = tags
        self.prompt_data["metadata"]["author"] = self.author_edit.text()
        self.prompt_data["metadata"]["version"] = self.version_edit.text()
        self.prompt_data["metadata"]["created"] = self.created_edit.text()
        self.prompt_data["metadata"]["updated"] = self.updated_edit.text()
        
        # Save the changes back to the library
        self.prompt_library.prompts[self.prompt_type] = self.prompt_data
        
        # Save to file
        try:
            file_path = os.path.join(self.prompt_library.library_dir, f"{self.prompt_type}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.prompt_data, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Error saving changes: {str(e)}")
            
        super().accept()

class PrometheusPromptGenerator(QMainWindow):
    """Prometheus AI Application for generating prompts with different urgency levels"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize prompt library
        self.prompt_library = PromptLibrary()
        
        # Get available prompt types
        self.prompt_types = self.prompt_library.get_prompt_types()
        
        # Map display names to actual prompt types
        self.display_to_type = {}
        
        # Settings
        self.settings = QSettings("Prometheus AI", "Prompt Generator")
        self.dark_mode = self.settings.value("dark_mode", True, bool)
        self.current_theme = self.settings.value("theme", "Dark Teal", str)
        
        # Initialize UI
        self.initUI()
        
        # Apply theme
        self.applyTheme(self.current_theme)
        
        # Set status bar message
        self.statusBar().showMessage("Ready - Prometheus AI Prompt Generator loaded successfully")
        
    def initUI(self):
        """Set up the application UI"""
        # Main window settings
        self.setWindowTitle("Prometheus AI Prompt Generator")
        self.setGeometry(100, 100, 1200, 800)  # Larger default size
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create header with branding in a card-like container
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFrameShape(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Prometheus logo/title
        logo_label = QLabel("Prometheus AI")
        logo_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        header_layout.addWidget(logo_label)
        
        # Subtitle
        subtitle_label = QLabel("Prompt Generator")
        subtitle_label.setFont(QFont("Arial", 14))
        header_layout.addWidget(subtitle_label)
        
        # Stretch to push version to right
        header_layout.addStretch(1)
        
        # Version info on the right
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(version_label)
        
        main_layout.addWidget(header_widget)
        
        # Create menu bar
        self.createMenuBar()
        
        # Create main content area with a splitter for resizable panels
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(8)  # Wider splitter handle for easier grabbing
        main_layout.addWidget(content_splitter, 1)  # Give it stretch
        
        # Left panel (Prompt Selection)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Add title for the left panel with icon
        left_header = QHBoxLayout()
        self.left_title = QLabel(f"Available Prompt Types ({len(self.prompt_types)})")
        self.left_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_header.addWidget(self.left_title)
        
        info_label = QLabel("Select prompt types to generate")
        info_label.setFont(QFont("Arial", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        left_header.addWidget(info_label, 1)
        
        left_layout.addLayout(left_header)
        
        # Prompt type search/filter with a modern look
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 8, 0, 8)
        filter_label = QLabel("🔍")
        filter_label.setFont(QFont("Arial", 12))
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search prompts...")
        self.filter_input.textChanged.connect(self.filterPrompts)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input, 1)
        left_layout.addLayout(filter_layout)
        
        # Prompt list with improved styling - make it sortable
        self.prompt_list = QListWidget()
        self.prompt_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.prompt_list.setSortingEnabled(True)  # Enable sorting
        
        # Populate the list with custom widgets
        self.populatePromptList()
        
        left_layout.addWidget(self.prompt_list, 1)  # Give it stretch
        
        # Selection buttons in a card
        buttons_card = QFrame()
        buttons_layout = QHBoxLayout()
        buttons_card.setLayout(buttons_layout)
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.selectAllPrompts)
        
        select_none_btn = QPushButton("Clear Selection")
        select_none_btn.clicked.connect(self.selectNoPrompts)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_none_btn)
        
        left_layout.addWidget(buttons_card)
        
        # Right panel (Generated Prompts Output)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Add title for the right panel
        right_title = QLabel("Generated Prompts")
        right_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        right_layout.addWidget(right_title)
        
        # Urgency level control in a card
        urgency_card = QFrame()
        urgency_layout = QVBoxLayout()
        urgency_card.setLayout(urgency_layout)
        
        urgency_header = QHBoxLayout()
        urgency_label = QLabel("Urgency Level")
        urgency_label.setFont(QFont("Arial", 12))
        urgency_header.addWidget(urgency_label)
        
        self.urgency_display = QLabel("5")
        self.urgency_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.urgency_display.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        urgency_header.addWidget(self.urgency_display)
        
        urgency_layout.addLayout(urgency_header)
        
        slider_layout = QHBoxLayout()
        low_label = QLabel("Low")
        slider_layout.addWidget(low_label)
        
        self.urgency_slider = QSlider(Qt.Orientation.Horizontal)
        self.urgency_slider.setMinimum(1)
        self.urgency_slider.setMaximum(10)
        self.urgency_slider.setValue(5)
        self.urgency_slider.valueChanged.connect(self.updateUrgencyDisplay)
        slider_layout.addWidget(self.urgency_slider, 1)
        
        high_label = QLabel("High")
        slider_layout.addWidget(high_label)
        
        urgency_layout.addLayout(slider_layout)
        right_layout.addWidget(urgency_card)
        
        # Result text field with better styling - make it editable
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(False)  # Make it editable
        self.result_text.setFont(QFont("Arial", 11))
        
        # Set welcome message
        welcome_text = (
            "Welcome to Prometheus AI Prompt Generator\n\n"
            "Select one or more prompt types from the list above, "
            "adjust the urgency level using the slider, and click \"Generate Prompts\".\n\n"
            "The generated prompts will appear here and you can edit them as needed."
        )
        self.result_text.setPlainText(welcome_text)
        
        right_layout.addWidget(self.result_text, 3)  # More stretch for the results
        
        # Button panel with improved styling
        button_panel = QFrame()
        button_layout = QHBoxLayout()
        button_panel.setLayout(button_layout)
        
        generate_btn = QPushButton("Generate Prompts")
        generate_btn.clicked.connect(self.generatePrompts)
        generate_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        generate_btn.setMinimumHeight(40)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copyToClipboard)
        copy_btn.setMinimumHeight(40)
        
        # Button to add custom prompts
        add_custom_prompt_btn = QPushButton("Add Custom Prompt")
        add_custom_prompt_btn.clicked.connect(self.addCustomPrompt)
        add_custom_prompt_btn.setMinimumHeight(40)
        
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(add_custom_prompt_btn)
        
        right_layout.addWidget(button_panel)
        
        # Add the panels to the splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        
        # Set the initial sizes of the splitter
        content_splitter.setSizes([400, 800])  # Left panel smaller, right panel larger

    def applyTheme(self, theme_name):
        """Apply the selected theme"""
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        # Get the dark/light status
        is_dark = "dark" in AVAILABLE_THEMES[theme_name].lower()
        self.dark_mode = is_dark
        self.settings.setValue("dark_mode", is_dark)
        
        # Apply the material theme
        extra = {
            # Extra parameters to customize theme
            'density_scale': '-1',  # Less dense UI
            'rounded': True,
        }
        apply_stylesheet(QApplication.instance(), theme=AVAILABLE_THEMES[theme_name], extra=extra)
        
        # Update the custom prompt list items
        for prompt_type, widget in self.item_widgets.items():
            widget.updateStyle(is_dark)
            
        # Add status message
        self.statusBar().showMessage(f"Applied {theme_name} theme")
        
    def populatePromptList(self):
        """Populate the prompt list with custom widgets for each prompt type"""
        self.prompt_list.clear()
        self.item_widgets = {}  # Store references to custom widgets
        
        for prompt_type in self.prompt_types:
            display_text = prompt_type.replace('_', ' ').title()
            self.display_to_type[display_text] = prompt_type
            
            # Create list item
            item = QListWidgetItem()
            self.prompt_list.addItem(item)
            
            # Create custom widget for this item
            widget = PromptListItem(prompt_type, display_text)
            
            # Calculate size for the item based on content
            item.setSizeHint(QSize(widget.sizeHint().width(), 36))  # Fixed height for consistency
            
            # Set widget for item
            self.prompt_list.setItemWidget(item, widget)
            
            # Connect info button
            widget.info_button.clicked.connect(lambda checked=False, pt=prompt_type: self.showMetadataDialog(pt))
            
            # Store widget reference
            self.item_widgets[prompt_type] = widget
            
        # Connect list item selection to handle multi-select properly
        self.prompt_list.itemClicked.connect(self.handleItemSelection)
    
    def showMetadataDialog(self, prompt_type):
        """Show dialog with prompt metadata"""
        dialog = MetadataDialog(prompt_type, self.prompt_library, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the prompt list to reflect any changes
            self.refreshPromptList()
            
    def createMenuBar(self):
        """Create the menu bar with actions"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Prompts", self)
        export_action.triggered.connect(self.exportPrompts)
        file_menu.addAction(export_action)
        
        import_action = QAction("Import Prompts", self)
        import_action.triggered.connect(self.importPrompts)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Enhancements menu
        enhancements_menu = menubar.addMenu("Enhancements")
        
        # Add actions to the Enhancements menu
        db_action = QAction("Database Integration", self)
        db_action.setEnabled(False)  # Not implemented yet
        enhancements_menu.addAction(db_action)
        
        llm_action = QAction("LLM Integration", self)
        llm_action.setEnabled(False)  # Not implemented yet
        enhancements_menu.addAction(llm_action)
        
        map_action = QAction("Codebase Map Generator", self)
        map_action.setEnabled(False)  # Not implemented yet
        enhancements_menu.addAction(map_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("Themes")
        
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        # Add all available themes to the menu
        for theme_name in AVAILABLE_THEMES.keys():
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            if theme_name == self.current_theme:
                theme_action.setChecked(True)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.applyTheme(name))
            theme_menu.addAction(theme_action)
            theme_group.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
        
    def refreshPromptList(self):
        """Refresh the prompt type list after adding or importing prompts"""
        # Reload prompt types
        self.prompt_types = self.prompt_library.get_prompt_types()
        
        # Update the left panel title
        self.left_title.setText(f"Available Prompt Types ({len(self.prompt_types)})")
        
        # Repopulate with custom widgets
        self.populatePromptList()
        
    def filterPrompts(self, text):
        """Filter the prompt list based on search text"""
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            widget = self.prompt_list.itemWidget(item)
            if widget:
                # Check if text in display name or prompt type
                if (text.lower() in widget.display_name.lower() or 
                    text.lower() in widget.prompt_type.lower()):
                    item.setHidden(False)
                else:
                    item.setHidden(True)
    
    def selectAllPrompts(self):
        """Select all prompt types in the list"""
        for i in range(self.prompt_list.count()):
            self.prompt_list.item(i).setSelected(True)
        self.statusBar().showMessage("Selected all prompt types")
    
    def selectNoPrompts(self):
        """Deselect all prompt types in the list"""
        for i in range(self.prompt_list.count()):
            self.prompt_list.item(i).setSelected(False)
        self.statusBar().showMessage("Cleared prompt selection")
    
    def updateUrgencyDisplay(self, value):
        """Update the urgency level display when slider is moved"""
        self.urgency_level = value
        self.urgency_display.setText(str(value))
        self.statusBar().showMessage(f"Urgency level set to {value}")
    
    def generatePrompts(self):
        """Generate prompts based on the selected types and urgency level"""
        # Get selected items
        selected_items = self.prompt_list.selectedItems()
        
        # Clear the output text
        self.result_text.clear()
        
        if not selected_items:
            self.result_text.setPlainText("Please select at least one prompt type.")
            self.statusBar().showMessage("Error: No prompt types selected")
            return
            
        # Get the urgency level
        urgency_level = self.urgency_slider.value()
        
        # Generate plain prompt content - no titles or metadata
        plain_output = ""
        
        # Generate prompts for each selected type
        for item in selected_items:
            # Get the custom widget for this item
            widget = self.prompt_list.itemWidget(item)
            if not widget:
                continue
                
            prompt_type = widget.prompt_type
            
            if not prompt_type:
                continue
                
            # Get the prompt content
            prompt_content = self.prompt_library.get_prompt(prompt_type, urgency_level)
            
            # Add just the content with no headers or labels
            plain_output += f"{prompt_content}\n\n"
            
            # Check if it's the last item
            if item != selected_items[-1]:
                plain_output += "---\n\n"  # Add simple separator between prompts
        
        # Set the plain text to make it editable
        self.result_text.setPlainText(plain_output)
        
        # Update status bar
        count = len(selected_items)
        self.statusBar().showMessage(f"Generated {count} prompts at urgency level {urgency_level}")
    
    def copyToClipboard(self):
        """Copy the generated prompts to the clipboard"""
        if self.result_text.toPlainText().strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.result_text.toPlainText())
            
            # Show a small popup message confirming the copy
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Prometheus AI")
            msg_box.setText("Prompts copied to clipboard!")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            
            self.statusBar().showMessage("Prompts copied to clipboard")
        else:
            self.statusBar().showMessage("Nothing to copy. Generate prompts first.")
    
    def addCustomPrompt(self):
        """Add a custom prompt to the library"""
        # Get prompt name
        name, ok = QInputDialog.getText(self, "Add Custom Prompt", "Enter prompt name:")
        if not ok or not name.strip():
            return
            
        # Convert to snake_case for filename
        prompt_type = name.lower().replace(' ', '_')
        
        # Check if it already exists
        if prompt_type in self.prompt_library.get_prompt_types():
            QMessageBox.warning(self, "Error", f"A prompt with name '{name}' already exists.")
            return
            
        # Get prompt description
        description, ok = QInputDialog.getText(self, "Add Custom Prompt", "Enter prompt description:")
        if not ok:
            return
            
        # Get prompt template
        template_dialog = QDialog(self)
        template_dialog.setWindowTitle("Enter Prompt Template")
        template_dialog.setMinimumWidth(600)
        template_dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Enter the prompt template. Use {urgency} as a placeholder for the urgency level.")
        layout.addWidget(instructions)
        
        # Template editor
        template_editor = QTextEdit()
        template_editor.setPlaceholderText("As an AI assistant with {urgency}/10 urgency, I will...")
        layout.addWidget(template_editor)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(template_dialog.accept)
        buttons.rejected.connect(template_dialog.reject)
        layout.addWidget(buttons)
        
        template_dialog.setLayout(layout)
        
        if template_dialog.exec() == QDialog.DialogCode.Accepted:
            template = template_editor.toPlainText()
            if not template.strip():
                QMessageBox.warning(self, "Error", "Template cannot be empty.")
                return
                
            # Create prompt data
            prompt_data = {
                "description": description,
                "template": template,
                "metadata": {
                    "author": "User",
                    "version": "1.0.0",
                    "created": "2023-03-09",
                    "updated": "2023-03-09",
                    "tags": ["custom"]
                }
            }
            
            # Add to library
            self.prompt_library.prompts[prompt_type] = prompt_data
            
            # Save to file
            try:
                file_path = os.path.join(self.prompt_library.library_dir, f"{prompt_type}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, indent=2)
                    
                # Update the list
                self.refreshPromptList()
                
                QMessageBox.information(self, "Success", f"Custom prompt '{name}' added successfully.")
                self.statusBar().showMessage(f"Added custom prompt: {name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save custom prompt: {str(e)}")
    
    def exportPrompts(self):
        """Export all prompts to a JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Prompts", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        try:
            # Get all prompts
            all_prompts = {}
            for prompt_type in self.prompt_library.get_prompt_types():
                all_prompts[prompt_type] = self.prompt_library.prompts[prompt_type]
                
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_prompts, f, indent=2)
                
            QMessageBox.information(self, "Export Successful", f"Exported {len(all_prompts)} prompts to {file_path}")
            self.statusBar().showMessage(f"Exported prompts to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting prompts: {str(e)}")
    
    def importPrompts(self):
        """Import prompts from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Prompts", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_prompts = json.load(f)
                
            if not isinstance(imported_prompts, dict):
                QMessageBox.warning(self, "Import Error", "Invalid format: expected a dictionary of prompts")
                return
                
            # Count of imported prompts
            count = 0
            
            # Process each prompt
            for prompt_type, prompt_data in imported_prompts.items():
                # Validate minimum required fields
                if not isinstance(prompt_data, dict) or "template" not in prompt_data:
                    continue
                    
                # Add to library
                self.prompt_library.prompts[prompt_type] = prompt_data
                
                # Save to file
                file_path = os.path.join(self.prompt_library.library_dir, f"{prompt_type}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, indent=2)
                    
                count += 1
                
            # Update the list
            self.refreshPromptList()
            
            QMessageBox.information(self, "Import Successful", f"Imported {count} prompts successfully")
            self.statusBar().showMessage(f"Imported {count} prompts")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing prompts: {str(e)}")
    
    def showAbout(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About Prometheus AI Prompt Generator", 
                          """<h2>Prometheus AI Prompt Generator</h2>
                           <p>Version 1.0.0</p>
                           <p>Generate AI prompts for various tasks with different urgency levels.</p>
                           <p>© 2023 Prometheus AI</p>""")
  
    def closeEvent(self, event):
        """Handle the close event - save settings"""
        # Save settings if needed
        self.settings.sync()
        event.accept()
        
    def updateDescription(self, item):
        """Legacy method for backwards compatibility"""
        # This method is kept for backwards compatibility but doesn't do anything now
        # as we're using the metadata dialog for showing prompt details
        pass
        
    def handleItemSelection(self, item):
        """Handle item selection in the list"""
        # This method helps maintain selection state for custom widget items
        pass
    
def main():
    """Run the Prometheus AI prompt generator application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Prometheus AI Prompt Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Prometheus AI")
    
    # Create window
    window = PrometheusPromptGenerator()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 