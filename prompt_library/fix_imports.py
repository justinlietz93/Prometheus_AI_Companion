import os
import sys

def fix_import_paths():
    """Add the parent directory to Python's path so prompt_library can be imported properly"""
    # Get the directory containing this file (prompt_library)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    
    # Add to Python path if not already there
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir) 