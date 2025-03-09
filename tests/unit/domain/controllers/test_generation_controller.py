"""
Test suite for GenerationController.

This module contains tests for the GenerationController class, which handles
the business logic for prompt generation in the Prometheus AI Prompt Generator.
Following TDD principles, these tests define the expected behavior before implementation.
"""

import pytest
import sys
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

# Add project root to the Python path to enable imports
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the controller and related classes
from prometheus_prompt_generator.domain.models.prompt import Prompt
from prometheus_prompt_generator.domain.controllers.generation_controller import GenerationController


class MockPromptRepository:
    """Mock repository for testing the GenerationController."""
    
    def __init__(self):
        self.prompts = {}
        self.get_by_id_called = False
        
    def get_by_id(self, prompt_id):
        self.get_by_id_called = True
        return self.prompts.get(prompt_id)
        
    def get_all(self):
        return list(self.prompts.values())


class MockTemplateEngine:
    """Mock template engine for testing the GenerationController."""
    
    def __init__(self):
        self.render_called = False
        self.extract_variables_called = False
        self.last_template = None
        self.last_variables = None
        self.return_value = "Rendered template"
        self.variables_to_return = []
        
    def render(self, template, variables=None):
        self.render_called = True
        self.last_template = template
        self.last_variables = variables or {}
        return self.return_value
        
    def extract_variables(self, template):
        self.extract_variables_called = True
        self.last_template = template
        
        # Return the predefined list of variables
        return self.variables_to_return


class TestGenerationController:
    """Tests for the GenerationController class."""
    
    @pytest.fixture
    def repository(self):
        """Provides a mock repository for testing."""
        return MockPromptRepository()
    
    @pytest.fixture
    def template_engine(self):
        """Provides a mock template engine for testing."""
        return MockTemplateEngine()
    
    @pytest.fixture
    def controller(self, repository, template_engine):
        """Provides a controller instance for testing."""
        return GenerationController(repository, template_engine)
    
    @pytest.fixture
    def sample_prompt(self):
        """Provides a sample prompt for testing."""
        prompt = Prompt()
        prompt._id = 1
        prompt._title = "Test Prompt"
        prompt._content = "This is a {{ urgency_level }} test prompt with {{ variable }}."
        prompt._description = "Test description"
        prompt._metadata = {"variables": ["urgency_level", "variable"]}
        return prompt
    
    def test_init(self, controller, repository, template_engine):
        """Test controller initialization."""
        assert controller.repository == repository
        assert controller.template_engine == template_engine
    
    def test_generate_from_prompt_id(self, controller, repository, template_engine, sample_prompt):
        """Test generating a prompt from a prompt ID."""
        # Setup
        repository.prompts[1] = sample_prompt
        variables = {"urgency_level": "high", "variable": "example"}
        
        # Register signal spy
        signal_received = False
        generated_prompt = None
        
        def on_prompt_generated(prompt_text, used_prompt_id):
            nonlocal signal_received, generated_prompt
            signal_received = True
            generated_prompt = prompt_text
            assert used_prompt_id == 1
        
        controller.promptGenerated.connect(on_prompt_generated)
        
        # Execute
        result = controller.generate_from_prompt_id(1, variables)
        
        # Verify
        assert result == "Rendered template"
        assert repository.get_by_id_called
        assert template_engine.render_called
        assert template_engine.last_template == sample_prompt._content
        assert template_engine.last_variables == variables
        assert signal_received
        assert generated_prompt == "Rendered template"
    
    def test_generate_from_prompt_id_not_found(self, controller, repository):
        """Test generating a prompt from a non-existent prompt ID."""
        # Register signal spy
        signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal signal_received, error_message
            signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute
        result = controller.generate_from_prompt_id(999, {})
        
        # Verify
        assert result is None
        assert repository.get_by_id_called
        assert signal_received
        assert "not found" in error_message
    
    def test_generate_from_prompt(self, controller, template_engine, sample_prompt):
        """Test generating a prompt directly from a Prompt object."""
        # Setup
        variables = {"urgency_level": "medium", "variable": "test case"}
        
        # Register signal spy
        signal_received = False
        generated_prompt = None
        
        def on_prompt_generated(prompt_text, used_prompt_id):
            nonlocal signal_received, generated_prompt
            signal_received = True
            generated_prompt = prompt_text
            assert used_prompt_id == 1
        
        controller.promptGenerated.connect(on_prompt_generated)
        
        # Execute
        result = controller.generate_from_prompt(sample_prompt, variables)
        
        # Verify
        assert result == "Rendered template"
        assert template_engine.render_called
        assert template_engine.last_template == sample_prompt._content
        assert template_engine.last_variables == variables
        assert signal_received
        assert generated_prompt == "Rendered template"
    
    def test_generate_from_template(self, controller, template_engine):
        """Test generating a prompt from a template string."""
        # Setup
        template = "This is a {{ level }} test template."
        variables = {"level": "critical"}
        
        # Register signal spy
        signal_received = False
        generated_prompt = None
        
        def on_prompt_generated(prompt_text, used_prompt_id):
            nonlocal signal_received, generated_prompt
            signal_received = True
            generated_prompt = prompt_text
            assert used_prompt_id is None
        
        controller.promptGenerated.connect(on_prompt_generated)
        
        # Execute
        result = controller.generate_from_template(template, variables)
        
        # Verify
        assert result == "Rendered template"
        assert template_engine.render_called
        assert template_engine.last_template == template
        assert template_engine.last_variables == variables
        assert signal_received
        assert generated_prompt == "Rendered template"
    
    def test_generate_with_error(self, controller, template_engine, sample_prompt):
        """Test error handling during prompt generation."""
        # Setup
        template_engine.render = MagicMock(side_effect=Exception("Template error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute
        result = controller.generate_from_prompt(sample_prompt, {})
        
        # Verify
        assert result is None
        assert error_signal_received
        assert "Template error" in error_message
    
    def test_get_available_variables(self, controller, repository, sample_prompt):
        """Test retrieving available variables for a prompt."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Execute
        variables = controller.get_available_variables(1)
        
        # Verify
        assert variables == ["urgency_level", "variable"]
        assert repository.get_by_id_called
    
    def test_get_available_variables_no_metadata(self, controller, repository):
        """Test retrieving variables when prompt has no metadata."""
        # Setup
        prompt = Prompt()
        prompt._id = 2
        prompt._title = "No Metadata"
        prompt._content = "Plain content"
        prompt._metadata = {}  # No metadata
        repository.prompts[2] = prompt
        
        # Set up the mock to return variables
        controller.template_engine.variables_to_return = ["content", "variable"]
        
        # Execute
        variables = controller.get_available_variables(2)
        
        # Verify
        assert variables == ["content", "variable"]
        assert repository.get_by_id_called
        assert controller.template_engine.extract_variables_called
        
        # Reset the mock for the next test
        controller.template_engine.variables_to_return = []
    
    def test_extract_variables_from_template(self, controller):
        """Test extracting variables from a template string."""
        # Setup
        template = "Hello {{ name }}, welcome to {{ location }}!"
        controller.template_engine.variables_to_return = ["name", "location"]
        
        # Execute
        variables = controller.extract_variables_from_template(template)
        
        # Verify
        assert sorted(variables) == sorted(["name", "location"])
        assert controller.template_engine.extract_variables_called
        assert controller.template_engine.last_template == template 