#!/usr/bin/env python3
"""
Cleanup Script

This script removes the duplicate files from the root directory
after confirming they've been properly migrated to the new structure.
"""

import os
import sys

# Files to remove from root directory
files_to_remove = [
    'constants.py',
    'utils.py',
    'prompt_library.py',
    'metadata_dialog.py',
    'prompt_list_item.py',
    'main_window.py',
]

def confirm(prompt):
    """Ask for confirmation before proceeding"""
    response = input(f"{prompt} (y/n): ").lower().strip()
    return response == 'y' or response == 'yes'

if __name__ == "__main__":
    if not confirm("This will remove duplicate files from the root directory. Are you sure?"):
        print("Operation cancelled.")
        sys.exit(0)
        
    for filename in files_to_remove:
        if os.path.exists(filename):
            print(f"Removing {filename}")
            os.remove(filename)
        else:
            print(f"{filename} not found, skipping.")
            
    print("Cleanup complete.")
