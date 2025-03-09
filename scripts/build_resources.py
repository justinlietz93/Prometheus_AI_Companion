#!/usr/bin/env python
"""
Build Resources

This script compiles the Qt resource file into a Python module.
"""

import os
import sys
import subprocess

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
RESOURCES_DIR = os.path.join(ROOT_DIR, 'prometheus_prompt_generator', 'resources')
RESOURCE_FILE = os.path.join(RESOURCES_DIR, 'resources.qrc')
OUTPUT_FILE = os.path.join(RESOURCES_DIR, 'resources_rc.py')

def ensure_dirs_exist():
    """Ensure necessary directories exist."""
    dirs_to_create = [
        os.path.join(RESOURCES_DIR, 'icons'),
        os.path.join(RESOURCES_DIR, 'translations'),
        os.path.join(RESOURCES_DIR, 'styles')
    ]
    
    for directory in dirs_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


def generate_placeholder_files():
    """Generate placeholder files for resources if they don't exist."""
    # Create a simple placeholder PNG for icons
    icon_paths = [
        os.path.join(RESOURCES_DIR, 'icons', 'app_icon.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'search.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'info.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'copy.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'generate.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'add.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'import.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'export.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'settings.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'dark_theme.png'),
        os.path.join(RESOURCES_DIR, 'icons', 'light_theme.png')
    ]
    
    for icon_path in icon_paths:
        if not os.path.exists(icon_path):
            # We'll create an empty file for now
            with open(icon_path, 'wb') as f:
                # Minimal valid PNG file (1x1 transparent pixel)
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            print(f"Created placeholder icon: {icon_path}")
    
    # Create empty QSS files
    style_paths = [
        os.path.join(RESOURCES_DIR, 'styles', 'dark_blue.qss'),
        os.path.join(RESOURCES_DIR, 'styles', 'light.qss')
    ]
    
    for style_path in style_paths:
        if not os.path.exists(style_path):
            with open(style_path, 'w') as f:
                f.write('/* Placeholder stylesheet */\n')
            print(f"Created placeholder stylesheet: {style_path}")
    
    # Create empty QM files
    qm_paths = [
        os.path.join(RESOURCES_DIR, 'translations', 'prometheus_en.qm'),
        os.path.join(RESOURCES_DIR, 'translations', 'prometheus_es.qm'),
        os.path.join(RESOURCES_DIR, 'translations', 'prometheus_fr.qm'),
        os.path.join(RESOURCES_DIR, 'translations', 'prometheus_de.qm')
    ]
    
    for qm_path in qm_paths:
        if not os.path.exists(qm_path):
            with open(qm_path, 'wb') as f:
                # Empty QM file header
                f.write(b'\x3c\xb8\x64\x18\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            print(f"Created placeholder translation file: {qm_path}")


def build_resources():
    """Build the resource file into a Python module."""
    if not os.path.exists(RESOURCE_FILE):
        print(f"Error: Resource file not found: {RESOURCE_FILE}")
        return False
    
    try:
        # Run pyrcc6 to compile the resource file
        result = subprocess.run(
            ['pyrcc6', '-o', OUTPUT_FILE, RESOURCE_FILE], 
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Successfully compiled resources to: {OUTPUT_FILE}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running pyrcc6: {e}")
        print(f"Output: {e.output}")
        return False
    except FileNotFoundError:
        print("Error: pyrcc6 not found. Make sure PyQt6 is installed properly.")
        print("You can install it with: pip install PyQt6")
        return False


def main():
    """Main entry point for the script."""
    print("Building resources for Prometheus AI Prompt Generator...")
    
    # Ensure directories exist
    ensure_dirs_exist()
    
    # Generate placeholder files if needed
    generate_placeholder_files()
    
    # Build the resource file
    if build_resources():
        print("Resource building completed successfully.")
    else:
        print("Resource building failed.")
        sys.exit(1)


if __name__ == "__main__":
    main() 