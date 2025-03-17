#!/usr/bin/env python3
"""
Consolidate Prompts

This script identifies duplicate prompts across the old and new prompt directories,
consolidates them into the new location, and removes duplicates from the old location.
"""

import os
import sys
import json
import glob
import shutil
from pathlib import Path

def consolidate_prompts():
    """
    Identify duplicate prompts across directories and consolidate them
    into the new location, removing duplicates from the old location.
    """
    # Get script directory and determine project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define the old and new paths with absolute paths
    old_path = os.path.join(project_root, "prompt_library", "prompts")
    new_path = os.path.join(project_root, "prometheus_prompt_generator", "data", "prompts")
    
    print(f"Old path: {old_path}")
    print(f"New path: {new_path}")
    
    # Ensure the new path exists
    os.makedirs(new_path, exist_ok=True)
    
    # Check if old path exists
    if not os.path.exists(old_path):
        print(f"Old prompt directory not found: {old_path}")
        return
        
    # Find all JSON files in the old directory
    old_prompts = glob.glob(os.path.join(old_path, "*.json"))
    
    if not old_prompts:
        print("No prompt files found in the old directory")
        return
        
    print(f"Found {len(old_prompts)} prompt files in old directory")
    
    # Get list of existing files in new directory
    existing_files = {os.path.basename(f) for f in glob.glob(os.path.join(new_path, "*.json"))}
    print(f"Found {len(existing_files)} prompt files in new directory")
    
    # Track statistics
    moved = 0
    already_exists = 0
    errors = 0
    
    for old_file_path in old_prompts:
        filename = os.path.basename(old_file_path)
        new_file_path = os.path.join(new_path, filename)
        
        try:
            if filename in existing_files:
                # Compare contents to see if they're identical
                with open(old_file_path, 'r', encoding='utf-8') as f_old:
                    old_content = f_old.read()
                    
                with open(new_file_path, 'r', encoding='utf-8') as f_new:
                    new_content = f_new.read()
                    
                if old_content == new_content:
                    print(f"Removing duplicate file: {filename} (identical content)")
                    os.remove(old_file_path)
                    already_exists += 1
                else:
                    print(f"Warning: File {filename} exists in both locations with different content")
                    print(f"  Keeping both versions for manual review")
                    # Optionally rename the old one to indicate it needs review
                    review_path = os.path.join(old_path, f"{os.path.splitext(filename)[0]}_REVIEW.json")
                    os.rename(old_file_path, review_path)
                    errors += 1
            else:
                # Move file to new location
                print(f"Moving unique file: {filename}")
                shutil.copy2(old_file_path, new_file_path)
                os.remove(old_file_path)
                moved += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            errors += 1
            
    # Summary
    print(f"\nConsolidation complete:")
    print(f"  {moved} files moved to new location")
    print(f"  {already_exists} duplicate files removed")
    print(f"  {errors} files with issues (need manual review)")
    
    # Check if old directory is empty and can be removed
    remaining_files = glob.glob(os.path.join(old_path, "*.json"))
    if not remaining_files:
        print(f"\nOld prompt directory is now empty. You can safely remove it.")
    else:
        print(f"\n{len(remaining_files)} files remain in old directory and need manual review.")

def main():
    """Main function to run the consolidation process."""
    print("Starting prompt consolidation...")
    consolidate_prompts()
    print("Done.")

if __name__ == "__main__":
    main() 