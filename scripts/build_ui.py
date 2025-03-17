#!/usr/bin/env python
"""
UI Builder Script for Prometheus AI Prompt Generator

This script automates the conversion of Qt Designer .ui files to Python code
using the pyuic6 tool. It scans the ui/designer directory for .ui files and
generates corresponding .py files with the ui_ prefix.

Usage:
    python build_ui.py [-h] [--force]

Options:
    -h, --help  Show this help message and exit
    --force     Force rebuild of all UI files, even if they are newer than the source
"""

import os
import sys
import glob
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
DESIGNER_DIR = Path('ui/designer')
RESOURCE_FILE = DESIGNER_DIR / 'resources.qrc'


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Convert Qt Designer UI files to Python')
    parser.add_argument('--force', action='store_true', help='Force rebuild of all UI files')
    return parser.parse_args()


def find_ui_files():
    """Find all .ui files in the designer directory"""
    ui_files = glob.glob(str(DESIGNER_DIR / '*.ui'))
    logger.info(f"Found {len(ui_files)} UI files")
    return ui_files


def build_ui_file(ui_file, force=False):
    """
    Build a single UI file
    
    Args:
        ui_file (str): Path to the .ui file
        force (bool): Whether to force rebuild even if target is newer
    
    Returns:
        bool: True if build was successful, False otherwise
    """
    ui_path = Path(ui_file)
    py_file = ui_path.with_name(f"ui_{ui_path.stem}.py")
    
    # Check if we need to rebuild
    if not force and py_file.exists():
        if py_file.stat().st_mtime > ui_path.stat().st_mtime:
            logger.info(f"Skipping {ui_file} (target is newer)")
            return True
    
    logger.info(f"Building {ui_file} -> {py_file}")
    try:
        result = subprocess.run(
            ['pyuic6', ui_path, '-o', py_file],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stderr:
            logger.warning(f"Warnings while building {ui_file}:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building {ui_file}:\n{e.stderr}")
        return False


def build_resources():
    """
    Build the resources file if it exists
    
    Returns:
        bool: True if build was successful or no resource file, False on error
    """
    if not RESOURCE_FILE.exists():
        logger.info("No resource file found, skipping")
        return True
    
    py_file = RESOURCE_FILE.with_name(f"{RESOURCE_FILE.stem}_rc.py")
    
    logger.info(f"Building resources {RESOURCE_FILE} -> {py_file}")
    try:
        result = subprocess.run(
            ['pyrcc6', RESOURCE_FILE, '-o', py_file],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stderr:
            logger.warning(f"Warnings while building resources:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building resources:\n{e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("pyrcc6 not found. Make sure it's installed and in your PATH.")
        return False


def main():
    """Main entry point"""
    args = parse_args()
    
    # Create the designer directory if it doesn't exist
    os.makedirs(DESIGNER_DIR, exist_ok=True)
    
    # Find and build UI files
    ui_files = find_ui_files()
    success_count = 0
    for ui_file in ui_files:
        if build_ui_file(ui_file, args.force):
            success_count += 1
    
    # Build resources file
    build_resources()
    
    # Report results
    logger.info(f"Successfully built {success_count}/{len(ui_files)} UI files")
    return 0 if success_count == len(ui_files) else 1


if __name__ == "__main__":
    sys.exit(main()) 