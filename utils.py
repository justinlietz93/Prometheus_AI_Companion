#!/usr/bin/env python3
"""
Prometheus AI Utility Functions

Utility functions for the Prometheus AI Prompt Generator.
"""

import os
import sys
import random
from PyQt6.QtGui import QColor, QPalette

def random_color():
    """Generate a random, visually pleasing color.
    
    Returns:
        QColor: A randomly generated color.
    """
    # Generate pleasing colors (avoid too dark or too light)
    hue = random.randint(0, 359)
    saturation = random.randint(50, 80)
    value = random.randint(70, 90)
    
    return QColor.fromHsv(hue, saturation, value)

def format_display_name(prompt_type):
    """Format a prompt type for display (e.g., snake_case to Title Case).
    
    Args:
        prompt_type (str): The raw prompt type string.
        
    Returns:
        str: Formatted display name.
    """
    return prompt_type.replace("_", " ").title()

def ensure_directory_exists(directory_path):
    """Ensure that a directory exists, create it if it doesn't.
    
    Args:
        directory_path (str): Path to the directory.
    """
    os.makedirs(directory_path, exist_ok=True)

def get_application_path():
    """Get the path to the application directory.
    
    Returns:
        str: The absolute path to the application directory.
    """
    return os.path.dirname(os.path.abspath(__file__))

def is_dark_theme(theme_name):
    """Check if a theme is a dark theme.
    
    Args:
        theme_name (str): Name of the theme.
        
    Returns:
        bool: True if it's a dark theme, False otherwise.
    """
    return theme_name.startswith("Dark")

def set_palette_color(palette, role, color):
    """Set a color for a specific palette role.
    
    Args:
        palette (QPalette): The palette to modify
        role (QPalette.ColorRole): The color role to change
        color (QColor): The color to set
    """
    palette.setColor(role, color)

def generate_template_with_urgency(template, urgency_level):
    """Generate a prompt template with the specified urgency level applied.
    
    Args:
        template (str): The original prompt template.
        urgency_level (int): Urgency level from 1 to 5.
        
    Returns:
        str: The template with urgency applied.
    """
    # Define urgency modifiers based on urgency level
    urgency_modifiers = {
        1: {
            "intro": "When you have time, please",
            "deadline": "There is no rush.",
            "priority": "This is a low priority task.",
            "tone": "The tone should be casual and relaxed."
        },
        2: {
            "intro": "Please",
            "deadline": "This should be completed within a reasonable timeframe.",
            "priority": "This is a standard priority task.",
            "tone": "The tone should be professional but not urgent."
        },
        3: {
            "intro": "I need you to",
            "deadline": "This should be completed soon.",
            "priority": "This is an important task.",
            "tone": "The tone should be direct and focused."
        },
        4: {
            "intro": "I urgently need you to",
            "deadline": "This needs to be completed quickly.",
            "priority": "This is a high priority task.",
            "tone": "The tone should convey significant importance."
        },
        5: {
            "intro": "URGENT:",
            "deadline": "This needs immediate attention.",
            "priority": "This is a critical priority task.",
            "tone": "The tone should convey maximum urgency."
        }
    }
    
    # Get modifiers for the specified urgency level
    modifiers = urgency_modifiers.get(urgency_level, urgency_modifiers[3])
    
    # Add urgency to the template
    urgency_prefix = f"{modifiers['intro']} {template.lstrip()}\n\n"
    urgency_suffix = f"\n\n{modifiers['deadline']} {modifiers['priority']} {modifiers['tone']}"
    
    return urgency_prefix + urgency_suffix 