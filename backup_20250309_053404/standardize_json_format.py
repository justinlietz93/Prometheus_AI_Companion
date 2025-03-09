#!/usr/bin/env python3
"""
Prometheus AI JSON Standardization Tool

This script standardizes JSON prompt files according to the Prometheus AI
naming conventions, format standards, and theme guidelines.
"""

import os
import json
import glob
from pathlib import Path

# Constants
PROMPTS_DIR = "prompt_library/prompts"
DEFAULT_AUTHOR = "Prometheus AI"
DEFAULT_VERSION = "1.0.0"
DEFAULT_TAGS = ["ai", "prompt"]

def standardize_filename(old_name):
    """
    Standardize filename according to naming conventions:
    - All lowercase
    - Words separated by underscores
    - No "_prompt" suffix
    - .json extension
    """
    # Get the base name without extension
    base_name = os.path.splitext(os.path.basename(old_name))[0]
    
    # Remove "_prompt" suffix if present
    if base_name.endswith("_prompt"):
        base_name = base_name[:-7]  # Remove "_prompt"
    
    # Replace spaces with underscores and make lowercase
    new_name = base_name.replace(" ", "_").lower()
    
    return new_name + ".json"

def standardize_json_content(file_path, new_name_without_ext):
    """
    Standardize the content of a JSON file according to Prometheus AI conventions.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Standardize basic fields
        data["name"] = new_name_without_ext
        
        # Ensure description exists and is properly formatted
        if "description" not in data or not data["description"]:
            # Create a capitalized description from the name
            words = new_name_without_ext.replace("_", " ").split()
            capitalized_words = [word.capitalize() for word in words]
            data["description"] = " ".join(capitalized_words) + " Prompts"
        
        # Add standard metadata fields if they don't exist
        if "metadata" not in data:
            data["metadata"] = {}
            
        metadata = data["metadata"]
        if "author" not in metadata:
            metadata["author"] = DEFAULT_AUTHOR
        if "version" not in metadata:
            metadata["version"] = DEFAULT_VERSION
        if "created" not in metadata:
            import datetime
            metadata["created"] = datetime.datetime.now().strftime("%Y-%m-%d")
        if "tags" not in metadata:
            metadata["tags"] = DEFAULT_TAGS.copy()
            # Add the prompt type as a tag
            if new_name_without_ext not in metadata["tags"]:
                metadata["tags"].append(new_name_without_ext)
        
        # Ensure prompts are consistently structured
        if "prompts" not in data:
            data["prompts"] = {}
        
        # Convert prompt keys to strings if they're not already
        if data["prompts"] and not all(isinstance(k, str) for k in data["prompts"].keys()):
            prompts = {}
            for k, v in data["prompts"].items():
                prompts[str(k)] = v
            data["prompts"] = prompts
                
        return data
    except Exception as e:
        print(f"Error standardizing {file_path}: {e}")
        return None

def main():
    """
    Main function to standardize all JSON files in the prompts directory.
    """
    # Make sure the prompts directory exists
    if not os.path.exists(PROMPTS_DIR):
        print(f"Directory not found: {PROMPTS_DIR}")
        return
    
    # Get all JSON files in the prompts directory
    json_files = glob.glob(os.path.join(PROMPTS_DIR, "*.json"))
    if not json_files:
        print(f"No JSON files found in {PROMPTS_DIR}")
        return
    
    print(f"Found {len(json_files)} JSON files to standardize.")
    standardized_count = 0
    
    for file_path in json_files:
        # Get the old filename and new standardized filename
        old_name = os.path.basename(file_path)
        new_name = standardize_filename(old_name)
        new_path = os.path.join(PROMPTS_DIR, new_name)
        new_name_without_ext = os.path.splitext(new_name)[0]
        
        print(f"Processing: {old_name} -> {new_name}")
        
        # Standardize the JSON content
        standardized_data = standardize_json_content(file_path, new_name_without_ext)
        if not standardized_data:
            print(f"  ❌ Failed to standardize content for {old_name}")
            continue
        
        # Write the standardized content back to the file
        try:
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(standardized_data, f, indent=2, ensure_ascii=False)
            
            # If the original and new filenames are different, remove the original
            if old_name != new_name and os.path.exists(new_path) and file_path != new_path:
                os.remove(file_path)
                print(f"  ✅ Renamed and standardized: {old_name} -> {new_name}")
            else:
                print(f"  ✅ Standardized: {new_name}")
                
            standardized_count += 1
            
        except Exception as e:
            print(f"  ❌ Error writing {new_path}: {e}")
    
    print(f"\nStandardization complete. {standardized_count} of {len(json_files)} files standardized.")
    print("\nStandard Format Summary:")
    print("------------------------")
    print("1. Filenames: lowercase with underscores, no '_prompt' suffix")
    print("2. JSON Structure:")
    print("   - name: matches filename (without .json)")
    print("   - description: capitalized description of the prompt type")
    print("   - metadata: contains author, version, creation date, and tags")
    print("   - prompts: dictionary of prompts with string keys")
    print("\nTheme Guidelines:")
    print("----------------")
    print("- Author: Prometheus AI")
    print("- Version: 1.0.0")
    print("- Tags: include 'ai', 'prompt', and the prompt type")

if __name__ == "__main__":
    main() 