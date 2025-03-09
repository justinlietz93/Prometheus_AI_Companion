"""
Prometheus AI Prompt Generator

A professional desktop application for generating AI prompts with different
urgency levels using a prompt library, built with PyQt6 with dark mode support.
"""

__version__ = "1.0.0"

# Import main classes to make them available at package level
from .ui.main_window import PrometheusPromptGenerator
from .utils.prompt_library import PromptLibrary

# Import sub-packages to make them accessible
from . import ui
from . import utils
from . import data 