#!/usr/bin/env python3
"""
Prompt Generator Application

This script launches a GUI application that allows users to generate
prompts with different urgency levels from the various prompt types
available in the codebase.
"""

import sys
import os
import tkinter as tk

# Ensure we can find the prompt_library module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Check if tkinter is available
try:
    import tkinter
except ImportError:
    print("Error: Tkinter is not available. This application requires Tkinter.")
    print("Please install Tkinter or use a Python distribution that includes it.")
    sys.exit(1)

try:
    from prompt_generator_gui import PromptGeneratorApp
except ImportError:
    # If we can't import directly, try to fix the paths
    try:
        from prometheus_prompt_generator.data.fix_imports import fix_import_paths
        fix_import_paths()
        from prompt_generator_gui import PromptGeneratorApp
    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("Please make sure all required files are present and in the correct location.")
        sys.exit(1)

def main():
    """Launch the Prompt Generator application"""
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 