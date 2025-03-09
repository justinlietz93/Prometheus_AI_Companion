"""
Data modules for the Prometheus AI Prompt Generator

This package contains modules for loading and managing prompt data.
"""

# Import classes to make them accessible at the package level
try:
    from .prompt_loader import PromptLoader
except ImportError:
    # Fallback for when prompt_loader hasn't been migrated yet
    PromptLoader = None

try:
    from .prompt_manager import PromptManager
except ImportError:
    # Fallback for when prompt_manager hasn't been migrated yet
    PromptManager = None
