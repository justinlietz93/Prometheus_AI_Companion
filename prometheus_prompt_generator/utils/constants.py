"""
Constants for the Prometheus AI Prompt Generator

This module contains constants used throughout the application.
"""

from PyQt6.QtGui import QColor

# Default theme colors - more vibrant yet coordinated
PROMETHEUS_BLUE = QColor(41, 128, 185)      # Vibrant blue
PROMETHEUS_LIGHT_BLUE = QColor(52, 152, 219) # Lighter blue for UI elements
PROMETHEUS_DARK = QColor(33, 37, 43)        # Rich dark background
PROMETHEUS_LIGHT = QColor(240, 240, 245)    # Clean light background
PROMETHEUS_ACCENT = QColor(52, 152, 219)    # Vibrant blue accent (default)

# Default fonts
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 10
DEFAULT_HEADING_SIZE = 14

# Available themes from qt-material
AVAILABLE_THEMES = {
    "Dark Blue": "dark_blue.xml",
    "Dark Teal": "dark_teal.xml",
    "Dark Amber": "dark_amber.xml", 
    "Dark Purple": "dark_purple.xml",
    "Dark Pink": "dark_pink.xml",
    "Dark Red": "dark_red.xml",
    "Dark Yellow": "dark_yellow.xml",
    "Light Blue": "light_blue.xml",
    "Light Teal": "light_teal.xml",
    "Light Amber": "light_amber.xml",
    "Light Purple": "light_purple.xml",
    "Light Pink": "light_pink.xml",
    "Light Red": "light_red.xml",
    "Light Yellow": "light_yellow.xml",
}

# Default metadata values
DEFAULT_AUTHOR = "Prometheus AI"
DEFAULT_VERSION = "1.0.0"
DEFAULT_CREATED_DATE = "2025-03-09"
DEFAULT_UPDATED_DATE = "2025-03-09"
DEFAULT_TAGS = ["ai", "prompt"]

# Urgency level definitions
URGENCY_LEVELS = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "Normal",
    5: "Medium",
    6: "Significant",
    7: "High",
    8: "Very High",
    9: "Urgent",
    10: "Critical"
}

# Theme settings
DEFAULT_THEMES = ["Light", "Dark Blue", "Dark Gray"]

DEFAULT_THEME_COLORS = {
    "Light": {
        "background": "#f5f5f5",
        "text": "#333333",
        "menu_bg": "#e0e0e0",
        "menu_text": "#333333",
        "input_bg": "#ffffff",
        "input_text": "#333333",
        "button_bg": "#2980b9",
        "button_text": "#ffffff",
        "button_hover": "#3498db",
        "button_pressed": "#1c5c8e",
        "list_bg": "#ffffff",
        "list_text": "#333333",
        "list_alt_bg": "#f0f0f0",
        "accent": "#2980b9",
        "accent_text": "#ffffff",
        "border": "#cccccc",
        "slider_bg": "#cdcdcd",
        "header_text": "#333333",
        "statusbar_bg": "#e0e0e0",
        "statusbar_text": "#333333"
    },
    "Dark Blue": {
        "background": "#2c2c2c",
        "text": "#ffffff",
        "menu_bg": "#333333",
        "menu_text": "#ffffff",
        "input_bg": "#3c3c3c",
        "input_text": "#ffffff",
        "button_bg": "#2980b9",
        "button_text": "#ffffff",
        "button_hover": "#3498db",
        "button_pressed": "#1c5c8e",
        "list_bg": "#3c3c3c",
        "list_text": "#ffffff",
        "list_alt_bg": "#444444",
        "accent": "#2980b9",
        "accent_text": "#ffffff",
        "border": "#555555",
        "slider_bg": "#555555",
        "header_text": "#ffffff",
        "statusbar_bg": "#333333",
        "statusbar_text": "#ffffff"
    },
    "Dark Gray": {
        "background": "#2c2c2c",
        "text": "#ffffff",
        "menu_bg": "#333333",
        "menu_text": "#ffffff",
        "input_bg": "#3c3c3c",
        "input_text": "#ffffff",
        "button_bg": "#505050",
        "button_text": "#ffffff",
        "button_hover": "#606060",
        "button_pressed": "#404040",
        "list_bg": "#3c3c3c",
        "list_text": "#ffffff",
        "list_alt_bg": "#444444",
        "accent": "#707070",
        "accent_text": "#ffffff",
        "border": "#555555",
        "slider_bg": "#555555",
        "header_text": "#ffffff",
        "statusbar_bg": "#333333",
        "statusbar_text": "#ffffff"
    }
} 