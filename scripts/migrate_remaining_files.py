#!/usr/bin/env python3
"""
Migration Script

This script migrates the remaining files from the old structure to the new one.
It preserves the original files but creates copies in the new structure.
"""

import os
import shutil
import sys

# Ensure we're in the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)

# Create scripts directory if it doesn't exist
os.makedirs('scripts', exist_ok=True)

# Create data directory in the package
os.makedirs('prometheus_prompt_generator/data', exist_ok=True)
with open('prometheus_prompt_generator/data/__init__.py', 'w') as f:
    f.write('"""Data modules for the Prometheus AI Prompt Generator"""\n')

# Mapping of files to migrate
migration_map = {
    # Old path -> New path
    'prompt_library/prompt_loader.py': 'prometheus_prompt_generator/data/prompt_loader.py',
    'prompt_library/prompt_manager.py': 'prometheus_prompt_generator/data/prompt_manager.py',
    'prompt_library/base_prompt.py': 'prometheus_prompt_generator/data/base_prompt.py',
    'utils/draw_map.py': 'prometheus_prompt_generator/utils/draw_map.py',
    'standardize_json_format.py': 'scripts/standardize_json_format.py',
    'standardize_names.py': 'scripts/standardize_names.py',
    'extract_prompts.py': 'scripts/extract_prompts.py',
    'prompt_generator_app.py': 'scripts/prompt_generator_app.py',
    'prompt_generator_gui.py': 'scripts/prompt_generator_gui.py',
    'run_prompt_generator.py': 'scripts/run_prompt_generator.py',
}

# Copy the files to their new locations
for old_path, new_path in migration_map.items():
    if os.path.exists(old_path):
        print(f"Migrating {old_path} to {new_path}")
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.copy2(old_path, new_path)
        
        # Update imports in the copied file if it's Python
        if new_path.endswith('.py'):
            try:
                # Try UTF-8 first
                with open(new_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update imports to use the new package structure
                content = content.replace('from prompt_library', 'from prometheus_prompt_generator.data')
                content = content.replace('import prompt_library', 'import prometheus_prompt_generator.data')
                
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except UnicodeDecodeError:
                # If UTF-8 fails, try with error handling
                try:
                    with open(new_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Update imports to use the new package structure
                    content = content.replace('from prompt_library', 'from prometheus_prompt_generator.data')
                    content = content.replace('import prompt_library', 'import prometheus_prompt_generator.data')
                    
                    with open(new_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Note: Fixed encoding issues in {new_path}")
                except Exception as e:
                    print(f"  Warning: Could not process {new_path}: {e}")
    else:
        print(f"Warning: {old_path} does not exist and cannot be migrated.")

# Create cleanup script
cleanup_script = """#!/usr/bin/env python3
\"\"\"
Cleanup Script

This script removes the duplicate files from the root directory
after confirming they've been properly migrated to the new structure.
\"\"\"

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
    \"\"\"Ask for confirmation before proceeding\"\"\"
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
"""

with open('scripts/cleanup_root_directory.py', 'w', encoding='utf-8') as f:
    f.write(cleanup_script)

print("Migration complete. Created scripts/cleanup_root_directory.py for removing duplicates.")
print("Review the migrated files and run cleanup script when ready.") 