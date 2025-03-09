#!/usr/bin/env python
"""
Data Directories Migration Script

This script migrates the prompt data directories (prompts and rules)
from the old prompt_library structure to the new structure under
prometheus_prompt_generator/data.
"""

import os
import shutil
from pathlib import Path

# Ensure we're in the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

# Define source and destination paths
source_prompts = os.path.join(root_dir, "prompt_library", "prompts")
source_rules = os.path.join(root_dir, "prompt_library", "rules")

dest_data_dir = os.path.join(root_dir, "prometheus_prompt_generator", "data")
dest_prompts = os.path.join(dest_data_dir, "prompts")
dest_rules = os.path.join(dest_data_dir, "rules")

# Create destination directories if they don't exist
os.makedirs(dest_prompts, exist_ok=True)
os.makedirs(dest_rules, exist_ok=True)

def copy_directory_contents(src, dst):
    """Copy all files from source directory to destination directory"""
    # Get list of all files in source directory
    files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
    
    for file in files:
        src_file = os.path.join(src, file)
        dst_file = os.path.join(dst, file)
        
        # Skip if destination file exists and is identical
        if os.path.exists(dst_file) and os.path.getsize(src_file) == os.path.getsize(dst_file):
            print(f"Skipping identical file: {file}")
            continue
            
        # Copy file with metadata
        print(f"Copying: {file}")
        shutil.copy2(src_file, dst_file)

# Copy prompts directory contents
if os.path.exists(source_prompts):
    print(f"\nCopying prompts from {source_prompts} to {dest_prompts}")
    try:
        copy_directory_contents(source_prompts, dest_prompts)
        print("✅ Prompts copied successfully")
    except Exception as e:
        print(f"❌ Error copying prompts: {e}")
else:
    print(f"❌ Source prompts directory does not exist: {source_prompts}")

# Copy rules directory contents
if os.path.exists(source_rules):
    print(f"\nCopying rules from {source_rules} to {dest_rules}")
    try:
        copy_directory_contents(source_rules, dest_rules)
        print("✅ Rules copied successfully")
    except Exception as e:
        print(f"❌ Error copying rules: {e}")
else:
    print(f"❌ Source rules directory does not exist: {source_rules}")

print("\nData directories migration completed.")
print("The original files have been preserved in their original locations.")
print("You can now use the files in the new prometheus_prompt_generator/data directory.") 