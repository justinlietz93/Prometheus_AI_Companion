"""
Models package for the Prometheus AI Prompt Generator.

This package contains model classes that represent the domain entities
of the application and handle data validation and persistence.
"""

from .prompt import Prompt, PromptMapper
from .tag import Tag

__all__ = ['Prompt', 'PromptMapper', 'Tag'] 