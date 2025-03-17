#!/usr/bin/env python3
"""
Import Prompts to Database

This script imports all prompts from the file system into the database.
It handles both the old format with urgency levels and the new format with templates.
"""

import os
import sys
import json
import glob
import sqlite3
import argparse
import datetime
from pathlib import Path

# Add parent directory to path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from domain.repositories.prompt_repository import PromptRepository
from utils.database import DatabaseManager

def find_prompt_files():
    """Find all prompt JSON files in both old and new directory structures."""
    # Find prompts in the old directory structure
    old_path = os.path.join(os.path.dirname(parent_dir), "prompt_library", "prompts")
    old_prompts = []
    if os.path.exists(old_path):
        old_prompts = glob.glob(os.path.join(old_path, "*.json"))
        
    # Find prompts in the new directory structure
    new_path = os.path.join(parent_dir, "data", "prompts")
    new_prompts = []
    if os.path.exists(new_path):
        new_prompts = glob.glob(os.path.join(new_path, "*.json"))
        
    # Combine and remove duplicates based on filename
    all_prompts = old_prompts + new_prompts
    unique_prompts = {}
    
    for prompt_file in all_prompts:
        filename = os.path.basename(prompt_file)
        # Prefer files from the new path if they exist in both
        if filename not in unique_prompts or prompt_file.startswith(new_path):
            unique_prompts[filename] = prompt_file
    
    return list(unique_prompts.values())

def import_prompts_to_db(db_path):
    """Import all prompts to the database."""
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
        
    # Get all prompt files
    prompt_files = find_prompt_files()
    if not prompt_files:
        print("No prompt files found")
        return False
        
    print(f"Found {len(prompt_files)} prompt files to import")
    
    # Initialize the database and repository
    db_manager = DatabaseManager(db_path)
    repository = PromptRepository(db_manager)
    
    # Import each prompt
    succeeded = 0
    failed = 0
    
    for prompt_file in prompt_files:
        try:
            print(f"Importing {os.path.basename(prompt_file)}...", end="")
            prompt_id = repository.import_prompt_from_file(prompt_file)
            
            if prompt_id:
                succeeded += 1
                print(" SUCCESS")
            else:
                failed += 1
                print(" FAILED")
        except Exception as e:
            failed += 1
            print(f" ERROR: {str(e)}")
    
    print(f"\nImport completed. {succeeded} succeeded, {failed} failed.")
    return succeeded > 0

def main():
    """Main function to parse arguments and run the import."""
    parser = argparse.ArgumentParser(description="Import prompts from files to database")
    parser.add_argument("--db-path", default=None, help="Path to the SQLite database file")
    args = parser.parse_args()
    
    # If no path provided, use the default location
    if args.db_path is None:
        db_dir = os.path.join(parent_dir, "data")
        os.makedirs(db_dir, exist_ok=True)
        args.db_path = os.path.join(db_dir, "prometheus.db")
    
    success = import_prompts_to_db(args.db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 