#!/usr/bin/env python3
"""
Prometheus AI Prompt Generator

A professional desktop application for generating AI prompts with different
urgency levels using the prompt library, built with PyQt6 with dark mode support.
"""

import os
import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QSlider, QPushButton, QTextEdit, 
                           QSplitter, QFrame, QAbstractItemView, QStatusBar, 
                           QMessageBox, QInputDialog, QDialog, QFileDialog, QMenu, QMenuBar, QLineEdit)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QAction

# Ensure prompt_library is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the prompt library
from prompt_library.prompt_loader import PromptLibrary

# Prometheus AI brand colors
PROMETHEUS_BLUE = QColor(41, 128, 185)  # Main blue color
PROMETHEUS_LIGHT_BLUE = QColor(52, 152, 219)  # Lighter blue for accents
PROMETHEUS_DARK = QColor(33, 37, 41)     # Dark background
PROMETHEUS_LIGHT = QColor(248, 249, 250) # Light background
PROMETHEUS_ACCENT = QColor(255, 193, 7)  # Accent color

class PrometheusPromptGenerator(QMainWindow):
    """Prometheus AI Application for generating prompts with different urgency levels"""
    
    def __init__(self):
        super().__init__()
        
        # Set up application settings
        self.settings = QSettings("PrometheusAI", "PromptGenerator")
        
        # Load the prompt library
        self.prompt_library = PromptLibrary()
        self.prompt_types = sorted(self.prompt_library.get_prompt_types())
        
        # Dictionary to map display names to actual prompt type names
        self.display_to_type = {}
        
        # Default urgency level
        self.urgency_level = 5
        
        # Set up the UI
        self.initUI()
        
        # Set dark mode as default
        self.applyDarkMode()
        
        # Set status bar message
        self.statusBar().showMessage("Ready - Prometheus AI Prompt Generator loaded successfully")
        
    def initUI(self):
        """Set up the application UI"""
        # Main window settings
        self.setWindowTitle("Prometheus AI Prompt Generator")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create header with branding
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Prometheus logo/title
        logo_label = QLabel("Prometheus AI")
        logo_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo_label.setStyleSheet(f"color: {PROMETHEUS_BLUE.name()}")
        header_layout.addWidget(logo_label)
        
        # Version info on the right
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(version_label)
        
        main_layout.addWidget(header_widget)
        
        # Create menu bar
        self.createMenuBar()
        
        # Create a split layout
        splitter_widget = QWidget()
        splitter_layout = QHBoxLayout()
        splitter_widget.setLayout(splitter_layout)
        main_layout.addWidget(splitter_widget, 1)  # Set stretch factor
        
        # Create a splitter for left and right panels
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Horizontal)
        splitter_layout.addWidget(splitter)
        
        # Left panel (Prompt Selection)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Add title for the left panel
        self.left_title = QLabel(f"Available Prompt Types ({len(self.prompt_types)})")
        self.left_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_layout.addWidget(self.left_title)
        
        # Prompt type list with search/filter section
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter prompts...")
        self.filter_input.textChanged.connect(self.filterPrompts)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input, 1)  # Give stretch factor
        left_layout.addLayout(filter_layout)
        
        # Prompt type list
        self.prompt_list = QListWidget()
        self.prompt_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.prompt_list.setFont(QFont("Arial", 10))
        self.prompt_list.setMinimumHeight(200)  # Set minimum height
        self.prompt_list.setAlternatingRowColors(True)  # Better visual distinction
        
        # Populate the list with prompt types
        for prompt_type in self.prompt_types:
            # Get the description for this prompt type
            description = self.prompt_library.get_prompt_description(prompt_type)
            display_text = f"{prompt_type.replace('_', ' ').title()}"
            
            # Store mapping of display name to actual prompt type
            self.display_to_type[display_text] = prompt_type
            
            # Add item to list
            self.prompt_list.addItem(display_text)
        
        left_layout.addWidget(self.prompt_list)
        
        # Description panel
        self.description_label = QLabel("Select a prompt type to see its description.")
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont("Arial", 10))
        left_layout.addWidget(self.description_label)
        
        # Connect list selection to description update
        self.prompt_list.itemClicked.connect(self.updateDescription)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.selectAllPrompts)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.selectNoPrompts)
        
        selection_layout.addWidget(select_all_btn)
        selection_layout.addWidget(select_none_btn)
        
        left_layout.addLayout(selection_layout)
        
        # Urgency level section
        urgency_frame = QFrame()
        urgency_frame.setFrameShape(QFrame.Shape.StyledPanel)
        urgency_layout = QVBoxLayout()
        urgency_frame.setLayout(urgency_layout)
        
        urgency_title = QLabel("Urgency Level")
        urgency_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        urgency_layout.addWidget(urgency_title)
        
        # Slider and labels
        slider_layout = QHBoxLayout()
        
        low_label = QLabel("Low")
        self.urgency_slider = QSlider()
        self.urgency_slider.setOrientation(Qt.Orientation.Horizontal)
        self.urgency_slider.setMinimum(1)
        self.urgency_slider.setMaximum(10)
        self.urgency_slider.setValue(5)
        self.urgency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.urgency_slider.setTickInterval(1)
        self.urgency_slider.valueChanged.connect(self.updateUrgencyDisplay)
        high_label = QLabel("High")
        
        self.urgency_display = QLabel("5")
        self.urgency_display.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.urgency_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slider_layout.addWidget(low_label)
        slider_layout.addWidget(self.urgency_slider)
        slider_layout.addWidget(high_label)
        
        urgency_layout.addLayout(slider_layout)
        urgency_layout.addWidget(self.urgency_display)
        
        left_layout.addWidget(urgency_frame)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Prompts")
        generate_btn.clicked.connect(self.generatePrompts)
        generate_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        generate_btn.setStyleSheet(f"background-color: {PROMETHEUS_BLUE.name()}; color: white; padding: 8px;")
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copyToClipboard)
        
        # Button to add custom prompts
        add_custom_prompt_btn = QPushButton("Add Custom Prompt")
        add_custom_prompt_btn.clicked.connect(self.addCustomPrompt)
        
        # Style buttons
        for btn in [generate_btn, copy_btn, select_all_btn, select_none_btn, add_custom_prompt_btn]:
            btn.setMinimumHeight(30)
        
        buttons_layout.addWidget(generate_btn)
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addWidget(add_custom_prompt_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # Add theme toggle button
        theme_layout = QHBoxLayout()
        theme_btn = QPushButton("Toggle Light/Dark Mode")
        theme_btn.clicked.connect(self.toggleTheme)
        theme_layout.addWidget(theme_btn)
        
        left_layout.addLayout(theme_layout)
        
        # Right panel (Generated Prompts Output)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Add title for the right panel
        right_title = QLabel("Generated Prompts")
        right_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_layout.addWidget(right_title)
        
        # Result text field
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Arial", 11))
        self.result_text.setMinimumHeight(300)  # Ensure adequate height
        self.result_text.setStyleSheet("line-height: 150%;")  # Improve readability
        right_layout.addWidget(self.result_text)
        
        # Add the panels to the splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set the initial sizes for the splitter
        splitter.setSizes([300, 700])
        
        # Create status bar
        self.setStatusBar(QStatusBar())
        
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
            self.result_text.setHtml("<h3 style='color:#2980b9;'>Please select at least one prompt type.</h3>")
            self.statusBar().showMessage("Error: No prompt types selected")
            return
            
        # Get the urgency level
        urgency_level = self.urgency_slider.value()
        
        # Build output HTML
        output_html = f"<div style='font-family: Arial; padding: 10px;'>"
        output_html += f"<h2 style='color: #2980b9;'>Prometheus AI Prompts (Level {urgency_level})</h2>"
        
        # Generate prompts for each selected type
        for item in selected_items:
            display_text = item.text()
            prompt_type = self.display_to_type.get(display_text, "")
            
            if not prompt_type:
                continue
                
            # Get the prompt content
            prompt_content = self.prompt_library.get_prompt(prompt_type, urgency_level)
            
            # Add to output
            output_html += f"<h3 style='color: #2980b9;'>{display_text} (Level {urgency_level})</h3>"
            
            # Check if the prompt is an error message
            if prompt_content.startswith("Error:"):
                output_html += f"<p style='color: #e74c3c;'>{prompt_content}</p>"
            else:
                # Add prompt tag for easy copying with specific identifier
                tag_id = f"aiprompt{prompt_type.lower().replace(' ', '_')}"
                output_html += f"<div id='{tag_id}' style='background-color: #f8f9fa; padding: 10px; border-left: 4px solid #2980b9; margin-bottom: 15px;'>"
                output_html += f"<p>{prompt_content}</p>"
                output_html += "</div>"
        
        output_html += "</div>"
        self.result_text.setHtml(output_html)
        
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
    
    def applyDarkMode(self):
        """Apply dark mode styling to the application"""
        # Create a palette for dark mode using Prometheus brand colors
        dark_palette = QPalette()
        
        # Set colors for various palette roles
        dark_palette.setColor(QPalette.ColorRole.Window, PROMETHEUS_DARK)
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, PROMETHEUS_ACCENT)
        dark_palette.setColor(QPalette.ColorRole.Link, PROMETHEUS_BLUE)
        dark_palette.setColor(QPalette.ColorRole.Highlight, PROMETHEUS_BLUE)
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        # Apply the palette to the application
        QApplication.setPalette(dark_palette)
        
        # Store the current mode
        self.dark_mode = True
        self.settings.setValue("dark_mode", True)
        
        self.statusBar().showMessage("Dark mode enabled")
        
    def applyLightMode(self):
        """Apply light mode styling to the application"""
        # Create a custom light palette with Prometheus brand colors
        light_palette = QPalette()
        
        # Set colors for various palette roles
        light_palette.setColor(QPalette.ColorRole.Window, PROMETHEUS_LIGHT)
        light_palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 37, 41))
        light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(33, 37, 41))
        light_palette.setColor(QPalette.ColorRole.Text, QColor(33, 37, 41))
        light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(33, 37, 41))
        light_palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Link, PROMETHEUS_BLUE)
        light_palette.setColor(QPalette.ColorRole.Highlight, PROMETHEUS_BLUE)
        light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        QApplication.setPalette(light_palette)
        
        # Store the current mode
        self.dark_mode = False
        self.settings.setValue("dark_mode", False)
        
        self.statusBar().showMessage("Light mode enabled")
    
    def toggleTheme(self):
        """Toggle between light and dark mode"""
        if hasattr(self, 'dark_mode') and self.dark_mode:
            self.applyLightMode()
        else:
            self.applyDarkMode()
            
    def closeEvent(self, event):
        """Handle the close event - save settings"""
        # Save settings if needed
        self.settings.sync()
        event.accept()

    def updateDescription(self, item):
        """Update the description panel based on selected prompt type"""
        prompt_type = self.display_to_type.get(item.text(), "")
        if not prompt_type:
            return
            
        # Get prompt metadata
        description = self.prompt_library.get_prompt_description(prompt_type)
        metadata = self.prompt_library.get_prompt_metadata(prompt_type)
        
        # Build metadata display
        html = f"<div style='font-family: Arial; padding: 5px;'>"
        
        # Add description
        if description:
            html += f"<p><b>Description:</b> {description}</p>"
        else:
            html += "<p>No description available for this prompt type.</p>"
            
        # Add metadata if available
        if metadata:
            html += "<div style='background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-top: 10px;'>"
            html += "<p style='color: #7f8c8d; font-size: 0.9em;'><b>Metadata</b></p>"
            
            if "author" in metadata:
                html += f"<p style='margin: 2px; font-size: 0.9em;'><b>Author:</b> {metadata['author']}</p>"
                
            if "version" in metadata:
                html += f"<p style='margin: 2px; font-size: 0.9em;'><b>Version:</b> {metadata['version']}</p>"
                
            if "created" in metadata:
                html += f"<p style='margin: 2px; font-size: 0.9em;'><b>Created:</b> {metadata['created']}</p>"
                
            if "tags" in metadata and metadata["tags"]:
                tags = ", ".join(metadata["tags"])
                html += f"<p style='margin: 2px; font-size: 0.9em;'><b>Tags:</b> {tags}</p>"
                
            html += "</div>"
            
        html += "</div>"
        self.description_label.setText(html)
        self.description_label.setTextFormat(Qt.TextFormat.RichText)

    def addCustomPrompt(self):
        """Open a dialog to add a custom prompt"""
        prompt_type, ok = QInputDialog.getText(self, "Add Custom Prompt", "Enter new prompt type:")
        if ok and prompt_type:
            # Convert to snake_case for consistency
            prompt_type = prompt_type.lower().replace(' ', '_')
            
            # Check if prompt type already exists
            if prompt_type in self.prompt_types:
                QMessageBox.warning(self, "Duplicate Prompt", 
                                  f"A prompt type named '{prompt_type}' already exists.")
                return
                
            description, ok = QInputDialog.getText(self, "Prompt Description", "Enter description for the prompt:")
            if ok:
                success = self.prompt_library.add_custom_prompt(prompt_type, description)
                if success:
                    # Refresh the prompt list
                    self.refreshPromptList()
                    self.statusBar().showMessage(f"Custom prompt '{prompt_type}' added successfully")
                else:
                    QMessageBox.critical(self, "Error", "Failed to add custom prompt.")

    def createMenuBar(self):
        """Create the application menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # Export action
        export_action = QAction("&Export Prompts", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.exportPrompts)
        file_menu.addAction(export_action)
        
        # Import action
        import_action = QAction("&Import Prompts", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.importPrompts)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = self.menuBar().addMenu("&Settings")
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("&Theme")
        
        # Light theme action
        light_action = QAction("&Light", self)
        light_action.triggered.connect(self.applyLightMode)
        theme_menu.addAction(light_action)
        
        # Dark theme action
        dark_action = QAction("&Dark", self)
        dark_action.triggered.connect(self.applyDarkMode)
        theme_menu.addAction(dark_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
    
    def exportPrompts(self):
        """Export custom prompts to a file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Custom Prompts", 
                                                 "", "JSON Files (*.json)")
        if file_path:
            try:
                # Get custom prompts (those with custom: true in metadata)
                custom_prompts = {}
                for prompt_type, prompt_data in self.prompt_library.prompts.items():
                    metadata = prompt_data.get("metadata", {})
                    if metadata.get("custom", False):
                        custom_prompts[prompt_type] = prompt_data
                
                if not custom_prompts:
                    QMessageBox.information(self, "No Custom Prompts", 
                                           "No custom prompts to export. Create custom prompts first.")
                    return
                    
                # Export to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump({"custom_prompts": custom_prompts}, f, indent=2)
                    
                self.statusBar().showMessage(f"Prompts exported to {file_path}")
                QMessageBox.information(self, "Export Successful", 
                                       f"Successfully exported {len(custom_prompts)} custom prompts.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting prompts: {str(e)}")
    
    def importPrompts(self):
        """Import custom prompts from a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Custom Prompts", 
                                                 "", "JSON Files (*.json)")
        if file_path:
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                
                if "custom_prompts" not in data:
                    QMessageBox.warning(self, "Invalid Format", 
                                       "The selected file does not contain valid custom prompts.")
                    return
                
                # Import each prompt
                imported_count = 0
                for prompt_type, prompt_data in data["custom_prompts"].items():
                    # Add the custom flag if it doesn't exist
                    if "metadata" not in prompt_data:
                        prompt_data["metadata"] = {}
                    prompt_data["metadata"]["custom"] = True
                    
                    # Save to filesystem and add to library
                    file_path = os.path.join(self.prompt_library.library_dir, f"{prompt_type}.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(prompt_data, f, indent=2)
                    
                    # Add to in-memory prompts
                    self.prompt_library.prompts[prompt_type] = prompt_data
                    imported_count += 1
                
                # Refresh list
                if imported_count > 0:
                    self.refreshPromptList()
                    self.statusBar().showMessage(f"Imported {imported_count} prompts from {file_path}")
                    QMessageBox.information(self, "Import Successful", 
                                          f"Successfully imported {imported_count} custom prompts.")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Error importing prompts: {str(e)}")
    
    def refreshPromptList(self):
        """Refresh the prompt type list after adding or importing prompts"""
        # Clear the list
        self.prompt_list.clear()
        self.display_to_type.clear()
        
        # Reload prompt types
        self.prompt_types = self.prompt_library.get_prompt_types()
        
        # Repopulate the list
        for prompt_type in self.prompt_types:
            display_text = f"{prompt_type.replace('_', ' ').title()}"
            self.display_to_type[display_text] = prompt_type
            self.prompt_list.addItem(display_text)
            
        # Update the left panel title
        self.left_title.setText(f"Available Prompt Types ({len(self.prompt_types)})")
    
    def showAbout(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About Prometheus AI Prompt Generator",
                         """<h2>Prometheus AI Prompt Generator</h2>
                         <p>Version 1.0.0</p>
                         <p>A powerful tool for generating AI prompts.</p>
                         <p>© 2023 Prometheus AI</p>""")

    def filterPrompts(self, text):
        """Filter the prompt list based on search text"""
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

def main():
    """Run the Prometheus AI prompt generator application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Prometheus AI Prompt Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Prometheus AI")
    
    # Set application style
    app.setStyle("Fusion")  # Use Fusion style for better cross-platform appearance
    
    window = PrometheusPromptGenerator()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 