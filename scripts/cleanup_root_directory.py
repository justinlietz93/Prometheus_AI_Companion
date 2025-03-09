#!/usr/bin/env python
"""
Cleanup Script for the Prometheus AI Prompt Generator

This script identifies and moves duplicate files from the root directory
to a backup folder. These files have been migrated to the new modular structure.
"""

import os
import shutil
from datetime import datetime

# Ensure we're in the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

# Create backup directory with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = os.path.join(root_dir, f"backup_{timestamp}")
os.makedirs(backup_dir, exist_ok=True)
print(f"Created backup directory: {backup_dir}")

# List of files to move from root to backup
# These files have been migrated to the new structure
files_to_move = [
    # Root files -> Already migrated to new locations
    "constants.py",              # -> prometheus_prompt_generator/utils/constants.py
    "utils.py",                  # -> prometheus_prompt_generator/utils/utils.py
    "prompt_library.py",         # -> prometheus_prompt_generator/utils/prompt_library.py
    "metadata_dialog.py",        # -> prometheus_prompt_generator/ui/metadata_dialog.py
    "prompt_list_item.py",       # -> prometheus_prompt_generator/ui/prompt_list_item.py
    "main_window.py",            # -> prometheus_prompt_generator/ui/main_window.py
    
    # Additional script files already migrated to scripts/ directory
    "standardize_json_format.py", # -> scripts/standardize_json_format.py
    "standardize_names.py",       # -> scripts/standardize_names.py
    "extract_prompts.py",         # -> scripts/extract_prompts.py
    "prompt_generator_app.py",    # -> scripts/prompt_generator_app.py
    "prompt_generator_gui.py",    # -> scripts/prompt_generator_gui.py
    "run_prompt_generator.py",    # -> scripts/run_prompt_generator.py
    
    # Testing files that can be backed up
    "test_pyqt.py",
    "prompt_generator_qt_simple.py"
]

# Move files to backup directory
for file_name in files_to_move:
    src_path = os.path.join(root_dir, file_name)
    if os.path.exists(src_path):
        dest_path = os.path.join(backup_dir, file_name)
        print(f"Moving {file_name} to backup directory...")
        shutil.move(src_path, dest_path)
        print(f"  ✅ {file_name} moved successfully")
    else:
        print(f"  ❌ {file_name} not found in root directory")

print("\nBackup and cleanup completed!")
print(f"All duplicate files have been moved to: {backup_dir}")
print("\nYou can safely delete the backup directory if everything is working correctly.")
print("To restore any files, simply copy them back from the backup directory.")
