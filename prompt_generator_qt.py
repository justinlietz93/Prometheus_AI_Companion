#!/usr/bin/env python3
"""
Prometheus AI Prompt Generator

This is a compatibility module that imports from the modularized structure.
For new code, import directly from the prometheus_prompt_generator package.
"""

# Import main classes to make them available at the module level
from prometheus_prompt_generator import PrometheusPromptGenerator
from prometheus_prompt_generator.utils.prompt_library import PromptLibrary
from prometheus_prompt_generator.ui.prompt_list_item import PromptListItem
from prometheus_prompt_generator.ui.metadata_dialog import MetadataDialog

# Import constants
from prometheus_prompt_generator.utils.constants import (
    PROMETHEUS_BLUE, PROMETHEUS_LIGHT_BLUE, PROMETHEUS_DARK, PROMETHEUS_LIGHT, PROMETHEUS_ACCENT,
    DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, DEFAULT_HEADING_SIZE,
    AVAILABLE_THEMES, URGENCY_LEVELS
)

# Re-export the main function
from main import main

# This allows the file to be run directly
if __name__ == "__main__":
    main() 