from PyQt6.QtGui import QColor

# Colors
PROMETHEUS_BLUE = QColor(41, 128, 185)      # Vibrant blue
PROMETHEUS_LIGHT_BLUE = QColor(52, 152, 219) # Lighter blue for UI elements
PROMETHEUS_DARK = QColor(33, 37, 43)        # Rich dark background
PROMETHEUS_LIGHT = QColor(240, 240, 245)    # Clean light background
PROMETHEUS_ACCENT = QColor(52, 152, 219)    # Vibrant blue accent (default)

# Fonts
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 11
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

# Default metadata
DEFAULT_AUTHOR = "Prometheus AI"
DEFAULT_VERSION = "1.0.0"
DEFAULT_TAGS = ["ai", "prompt"] 