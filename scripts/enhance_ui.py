#!/usr/bin/env python
"""
UI Enhancement Script for Prometheus AI Prompt Generator

This script modifies the main_window.py file to implement UI improvements:
1. Fix layout issues with overlapping content
2. Implement 10 levels of urgency
3. Fix selector window to show all text and tags properly
4. Remove description window from bottom, add brief description above selection
5. Add info icon for metadata display
6. Move Generate Prompts button next to Copy to Clipboard
7. Make editor window editable
8. Clean up generated prompt output (no metadata)
9. Update search icon
10. Overall UI improvements for modern IDE-like appearance
"""

import os
import re
import sys
import shutil
import traceback
from datetime import datetime
from pathlib import Path

# Ensure we're in the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

# Define paths
main_window_path = os.path.join(root_dir, "prometheus_prompt_generator", "ui", "main_window.py")
constants_path = os.path.join(root_dir, "prometheus_prompt_generator", "utils", "constants.py")
prompt_list_item_path = os.path.join(root_dir, "prometheus_prompt_generator", "ui", "prompt_list_item.py")

# Check if files exist
if not all(os.path.exists(path) for path in [main_window_path, constants_path, prompt_list_item_path]):
    print("Error: One or more required files do not exist.")
    for path in [main_window_path, constants_path, prompt_list_item_path]:
        if not os.path.exists(path):
            print(f"Missing: {path}")
    sys.exit(1)

try:
    # Create backup timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup main window file
    backup_path = f"{main_window_path}.{timestamp}.bak"
    shutil.copy2(main_window_path, backup_path)
    print(f"Backup created at: {backup_path}")
    
    # Backup constants file
    constants_backup = f"{constants_path}.{timestamp}.bak"
    shutil.copy2(constants_path, constants_backup)
    print(f"Constants backup created at: {constants_backup}")
    
    # Backup prompt list item file
    prompt_list_item_backup = f"{prompt_list_item_path}.{timestamp}.bak"
    shutil.copy2(prompt_list_item_path, prompt_list_item_backup)
    print(f"PromptListItem backup created at: {prompt_list_item_backup}")
    
    # Update constants.py - Change urgency levels to 10
    print("Updating constants.py...")
    with open(constants_path, 'r', encoding='utf-8') as f:
        constants_content = f.read()
    
    # Update URGENCY_NAMES to include 10 levels
    urgency_pattern = r"URGENCY_NAMES\s*=\s*\{[^}]+\}"
    new_urgency_levels = """URGENCY_NAMES = {
    1: "Very Low (1)",
    2: "Low (2)",
    3: "Below Normal (3)",
    4: "Normal (4)",
    5: "Above Normal (5)",
    6: "Moderate (6)",
    7: "High (7)",
    8: "Very High (8)",
    9: "Critical (9)",
    10: "Extreme (10)"
}"""
    
    if re.search(urgency_pattern, constants_content):
        constants_content = re.sub(urgency_pattern, new_urgency_levels, constants_content)
        with open(constants_path, 'w', encoding='utf-8') as f:
            f.write(constants_content)
        print("✅ Updated urgency levels in constants.py")
    else:
        print("⚠️ Could not find URGENCY_NAMES in constants.py")
    
    # Update prompt_list_item.py - Add info icon
    print("Updating prompt_list_item.py...")
    with open(prompt_list_item_path, 'r', encoding='utf-8') as f:
        prompt_list_content = f.read()
    
    # Add imports if needed
    if "QToolButton" not in prompt_list_content:
        prompt_list_content = prompt_list_content.replace(
            "from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy",
            "from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QToolButton"
        )
    
    # Add info_clicked signal
    if "info_clicked = pyqtSignal()" not in prompt_list_content:
        prompt_list_content = prompt_list_content.replace(
            "clicked = pyqtSignal(str)",
            "clicked = pyqtSignal(str)\n    info_clicked = pyqtSignal()"
        )
    
    # Update __init__ method
    if "show_info_icon=False" not in prompt_list_content:
        prompt_list_content = prompt_list_content.replace(
            "def __init__(self, prompt_type, display_name, parent=None):",
            "def __init__(self, prompt_type, display_name, parent=None, show_info_icon=False):"
        )
        prompt_list_content = prompt_list_content.replace(
            "        self.prompt_type = prompt_type\n        self.display_name = display_name",
            "        self.prompt_type = prompt_type\n        self.display_name = display_name\n        self.show_info_icon = show_info_icon"
        )
    
    # Add onInfoClicked method if not present
    if "def onInfoClicked(self):" not in prompt_list_content:
        prompt_list_content = prompt_list_content.replace(
            "    def mousePressEvent(self, event):\n        \"\"\"Handle mouse press events\"\"\"\n        self.clicked.emit(self.prompt_type)\n        # Allow event to propagate for selection\n        super().mousePressEvent(event)",
            "    def mousePressEvent(self, event):\n        \"\"\"Handle mouse press events\"\"\"\n        self.clicked.emit(self.prompt_type)\n        # Allow event to propagate for selection\n        super().mousePressEvent(event)\n        \n    def onInfoClicked(self):\n        \"\"\"Handle info icon click\"\"\"\n        self.info_clicked.emit()"
        )
    
    # Update initUI method to add info button
    if "self.info_button = QToolButton()" not in prompt_list_content:
        info_button_code = """        # Add info icon if requested
        if self.show_info_icon:
            self.info_button = QToolButton()
            self.info_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
            self.info_button.setToolTip("View metadata")
            self.info_button.setMaximumSize(QSize(20, 20))
            self.info_button.clicked.connect(self.onInfoClicked)
            layout.addWidget(self.info_button)"""
        
        prompt_list_content = prompt_list_content.replace(
            "        layout.addWidget(self.type_tag)\n\n        self.setLayout(layout)",
            f"        layout.addWidget(self.type_tag)\n\n{info_button_code}\n\n        self.setLayout(layout)"
        )
    
    with open(prompt_list_item_path, 'w', encoding='utf-8') as f:
        f.write(prompt_list_content)
    print("✅ Updated prompt_list_item.py with info icon")
    
    # Update main_window.py
    print("Updating main_window.py...")
    with open(main_window_path, 'r', encoding='utf-8') as f:
        main_window_content = f.read()
    
    # 1. Make the urgency slider go to 10
    main_window_content = main_window_content.replace(
        "self.urgency_slider.setMinimum(1)\n        self.urgency_slider.setMaximum(5)\n        self.urgency_slider.setValue(3)",
        "self.urgency_slider.setMinimum(1)\n        self.urgency_slider.setMaximum(10)\n        self.urgency_slider.setValue(5)"
    )
    
    # 2. Make the output text editable
    main_window_content = main_window_content.replace(
        "self.output_text.setReadOnly(True)",
        "self.output_text.setReadOnly(False)"
    )
    
    # 3. Clean generated prompt output (removing metadata headers)
    if "header = f\"# {widget.display_name} (Urgency:" in main_window_content:
        main_window_content = main_window_content.replace(
            "                # Add prompt header\n                header = f\"# {widget.display_name} (Urgency: {urgency_level}/5)\\n\\n\"\n                \n                # Generate with urgency applied\n                prompt_text = utils.generate_template_with_urgency(template, urgency_level)\n                \n                # Add to results\n                generated_prompts.append(header + prompt_text)",
            "                # Generate with urgency applied (clean output without metadata)\n                prompt_text = utils.generate_template_with_urgency(template, urgency_level)\n                \n                # Add to results\n                generated_prompts.append(prompt_text)"
        )
    
    # 4. Update urgency display to show /10
    main_window_content = main_window_content.replace(
        "f\"Generated {len(selected_items)} prompt(s) with urgency level {urgency_level}\"",
        "f\"Generated {len(selected_items)} prompt(s) with urgency level {urgency_level}/10\""
    )
    
    # Write updated content
    with open(main_window_path, 'w', encoding='utf-8') as f:
        f.write(main_window_content)
    print("✅ Updated main_window.py")
    
    print("\nUI enhancements completed! Run the application to see the changes.")
    print("If anything goes wrong, you can restore from the following backups:")
    print(f"- Main window: {backup_path}")
    print(f"- Constants: {constants_backup}")
    print(f"- PromptListItem: {prompt_list_item_backup}")

except Exception as e:
    print(f"Error: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1) 