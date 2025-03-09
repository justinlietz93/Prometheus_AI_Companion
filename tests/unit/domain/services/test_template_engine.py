"""
Test suite for TemplateEngine.

This module contains tests for the TemplateEngine class, which handles
template rendering with variable substitution for the Prometheus AI Prompt Generator.
Following TDD principles, these tests define the expected behavior before implementation.
"""

import pytest
import sys
from unittest.mock import MagicMock, patch
import re

# Add project root to the Python path to enable imports
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the service classes
from prometheus_prompt_generator.domain.services.template_engine import TemplateEngine


class TestTemplateEngine:
    """Tests for the TemplateEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Provides a template engine instance for testing."""
        return TemplateEngine()
    
    def test_render_simple_variables(self, engine):
        """Test rendering a template with simple variable substitution."""
        # Setup
        template = "Hello {{ name }}, welcome to {{ location }}!"
        variables = {"name": "John", "location": "Prometheus AI"}
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify
        assert result == "Hello John, welcome to Prometheus AI!"
    
    def test_render_missing_variables(self, engine):
        """Test rendering with missing variables."""
        # Setup
        template = "Hello {{ name }}, welcome to {{ location }}!"
        variables = {"name": "John"}  # location is missing
        
        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            engine.render(template, variables)
        
        assert "Missing required variable" in str(exc_info.value)
        assert "location" in str(exc_info.value)
    
    def test_render_with_default_values(self, engine):
        """Test rendering with default values for variables."""
        # Setup
        template = "Hello {{ name | default('Guest') }}, welcome to {{ location | default('our platform') }}!"
        variables = {"name": "John"}  # location will use default
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify
        assert result == "Hello John, welcome to our platform!"
    
    def test_render_with_filters(self, engine):
        """Test rendering with filters applied to variables."""
        # Setup
        template = "Hello {{ name | upper }}, welcome to {{ location | lower }}!"
        variables = {"name": "John", "location": "Prometheus AI"}
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify
        assert result == "Hello JOHN, welcome to prometheus ai!"
    
    def test_render_with_conditional_logic(self, engine):
        """Test rendering with conditional logic."""
        # Setup
        template = """
        {% if urgency_level > 5 %}
        URGENT: {{ message }}
        {% else %}
        {{ message }}
        {% endif %}
        """
        variables = {"urgency_level": 7, "message": "This is an important message."}
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify
        expected = "\n        URGENT: This is an important message.\n        "
        assert result.strip() == expected.strip()
    
    def test_render_with_loops(self, engine):
        """Test rendering with loops."""
        # Setup
        template = """
        Items:
        {% for item in items %}
        - {{ item }}
        {% endfor %}
        """
        variables = {"items": ["Apple", "Banana", "Cherry"]}
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify - normalize whitespace for comparison
        # Remove all whitespace between lines and compare the content
        def normalize_whitespace(text):
            # Replace all whitespace with a single space
            text = re.sub(r'\s+', ' ', text)
            # Remove leading/trailing whitespace
            return text.strip()
        
        expected_content = "Items: - Apple - Banana - Cherry"
        assert normalize_whitespace(result) == normalize_whitespace(expected_content)
    
    def test_render_with_nested_variables(self, engine):
        """Test rendering with nested variable structures."""
        # Setup
        template = "User {{ user.name }} from {{ user.location.city }}, {{ user.location.country }}"
        variables = {
            "user": {
                "name": "John",
                "location": {
                    "city": "New York",
                    "country": "USA"
                }
            }
        }
        
        # Execute
        result = engine.render(template, variables)
        
        # Verify
        assert result == "User John from New York, USA"
    
    def test_extract_variables_simple(self, engine):
        """Test extracting variables from a simple template."""
        # Setup
        template = "Hello {{ name }}, welcome to {{ location }}!"
        
        # Execute
        variables = engine.extract_variables(template)
        
        # Verify
        assert sorted(variables) == sorted(["name", "location"])
    
    def test_extract_variables_with_filters(self, engine):
        """Test extracting variables from a template with filters."""
        # Setup
        template = "Hello {{ name | upper }}, welcome to {{ location | lower }}!"
        
        # Execute
        variables = engine.extract_variables(template)
        
        # Verify
        assert sorted(variables) == sorted(["name", "location"])
    
    def test_extract_variables_with_defaults(self, engine):
        """Test extracting variables from a template with default values."""
        # Setup
        template = "Hello {{ name | default('Guest') }}, welcome to {{ location | default('our platform') }}!"
        
        # Execute
        variables = engine.extract_variables(template)
        
        # Verify
        assert sorted(variables) == sorted(["name", "location"])
    
    def test_extract_variables_with_conditionals(self, engine):
        """Test extracting variables from a template with conditional logic."""
        # Setup
        template = """
        {% if urgency_level > 5 %}
        URGENT: {{ message }}
        {% else %}
        {{ message }}
        {% endif %}
        """
        
        # Execute
        variables = engine.extract_variables(template)
        
        # Verify
        assert sorted(variables) == sorted(["urgency_level", "message"])
    
    def test_extract_variables_with_loops(self, engine):
        """Test extracting variables from a template with loops."""
        # Setup
        template = """
        Items:
        {% for item in items %}
        - {{ item }}
        {% endfor %}
        """
        
        # Execute
        variables = engine.extract_variables(template)
        
        # Verify - both the loop variable (item) and the iterable (items) should be detected
        assert sorted(variables) == sorted(["item", "items"])
    
    def test_find_loop_variables(self, engine):
        """Test finding loop variables in a template."""
        # Setup
        template = """
        {% for item in items %}
        - {{ item }}
        {% endfor %}
        
        {% for user in users %}
        * {{ user.name }}
        {% endfor %}
        """
        
        # Execute
        loop_vars = engine._find_loop_variables(template)
        
        # Verify
        assert sorted(loop_vars) == sorted(["item", "user"])
    
    def test_render_with_error_handling(self, engine):
        """Test error handling during template rendering."""
        # Setup
        template = "{{ undefined_variable + 5 }}"
        variables = {}
        
        # Execute & Verify
        with pytest.raises(ValueError) as exc_info:
            engine.render(template, variables)
        
        assert "Error rendering template" in str(exc_info.value) 