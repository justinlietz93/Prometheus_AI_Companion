#!/usr/bin/env python3
"""
Prometheus AI Name Standardizer

This script standardizes the names of all prompt JSON files in the prompt library
by removing "_prompt" suffixes and ensuring consistent naming.
"""

import os
import json
import glob
import shutil

# Directory for prompt library
PROMPT_LIBRARY_DIR = "prompt_library/prompts"

def standardize_filename(old_name):
    """Standardize a filename by removing _prompt suffix"""
    base_name = os.path.basename(old_name)
    name_without_ext, ext = os.path.splitext(base_name)
    
    # Remove _prompt suffix if present
    if name_without_ext.endswith("_prompt"):
        name_without_ext = name_without_ext[:-7]
        
    # Ensure all underscores for spaces and lowercase
    standardized_name = name_without_ext.lower().replace(" ", "_")
    
    return f"{standardized_name}{ext}"

def standardize_json_content(file_path, new_name_without_ext):
    """Update the name field in the JSON content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Update the name field to match the filename
        if "name" in data:
            data["name"] = new_name_without_ext
            
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating JSON content in {file_path}: {str(e)}")
        return False

def main():
    """Standardize all prompt JSON filenames"""
    # Find all JSON files
    json_pattern = os.path.join(PROMPT_LIBRARY_DIR, "*.json")
    json_files = glob.glob(json_pattern)
    
    renamed_count = 0
    updated_content_count = 0
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for file_path in json_files:
        old_name = os.path.basename(file_path)
        new_name = standardize_filename(old_name)
        
        # Skip if already standardized
        if old_name == new_name:
            print(f"Skipping already standardized: {old_name}")
            continue
        
        # Get the name without extension for the JSON content
        new_name_without_ext = os.path.splitext(new_name)[0]
        
        # Update the name in the JSON content first
        if standardize_json_content(file_path, new_name_without_ext):
            updated_content_count += 1
        
        # Rename the file
        new_path = os.path.join(PROMPT_LIBRARY_DIR, new_name)
        
        try:
            # If the target file already exists, we'll need to merge or handle it
            if os.path.exists(new_path):
                print(f"Warning: {new_name} already exists. Keeping both files.")
                # Create a unique name
                base, ext = os.path.splitext(new_name)
                count = 1
                while os.path.exists(os.path.join(PROMPT_LIBRARY_DIR, f"{base}_{count}{ext}")):
                    count += 1
                new_path = os.path.join(PROMPT_LIBRARY_DIR, f"{base}_{count}{ext}")
                shutil.copy2(file_path, new_path)
                print(f"Created copy as {os.path.basename(new_path)}")
            else:
                # Safe to rename
                os.rename(file_path, new_path)
                print(f"Renamed: {old_name} -> {new_name}")
            
            renamed_count += 1
        except Exception as e:
            print(f"Error renaming {old_name}: {str(e)}")
    
    print(f"\nStandardization complete. Renamed {renamed_count} files.")
    print(f"Updated content in {updated_content_count} files.")

if __name__ == "__main__":
    main() 