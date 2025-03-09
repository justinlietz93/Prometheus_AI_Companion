"""
Services package for the Prometheus AI Prompt Generator.

This package contains service classes that provide various functionalities
to the application's controllers and models.
"""

from .template_engine import TemplateEngine

__all__ = [
    'TemplateEngine'
] 