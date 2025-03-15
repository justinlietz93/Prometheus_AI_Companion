"""
Test suite for PromptController.

This module contains tests for the PromptController class, which handles
the business logic for prompt operations in the Prometheus AI Prompt Generator.
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
from prometheus_prompt_generator.domain.controllers.prompt_controller import PromptController
from prometheus_prompt_generator.domain.models.prompt import Prompt


class MockPromptRepository:
    """Mock repository for testing the PromptController."""
    
    def __init__(self):
        self.prompts = {}
        self.save_called = False
        self.delete_called = False
        self.get_all_called = False
        self.get_by_id_called = False
        self.filter_called = False
        
    def save(self, prompt):
        self.save_called = True
        self.prompts[prompt.id] = prompt
        return prompt
        
    def delete(self, prompt_id):
        self.delete_called = True
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
            return True
        return False
        
    def get_all(self):
        self.get_all_called = True
        return list(self.prompts.values())
        
    def get_by_id(self, prompt_id):
        self.get_by_id_called = True
        return self.prompts.get(prompt_id)
        
    def filter(self, **kwargs):
        self.filter_called = True
        # Simple filtering, just return all for now
        return self.get_all()


class TestPromptController:
    """Tests for the PromptController class."""
    
    @pytest.fixture
    def repository(self):
        """Provides a mock repository for testing."""
        return MockPromptRepository()
        
    @pytest.fixture
    def controller(self, repository):
        """Provides a controller instance for testing."""
        return PromptController(repository)
        
    @pytest.fixture
    def sample_prompt(self):
        """Provides a sample prompt for testing."""
        prompt = Prompt()
        prompt._id = 1
        prompt._title = "Test Prompt"
        prompt._content = "This is a test prompt content."
        prompt._description = "Test description"
        prompt._is_public = True
        return prompt
    
    def test_init(self, controller, repository):
        """Test controller initialization."""
        assert controller.repository == repository
        assert controller.selected_prompts == []
        assert controller.current_prompt is None
    
    def test_load_prompts_success(self, controller, repository, sample_prompt):
        """Test loading prompts successfully."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Register a signal spy
        signal_received = False
        prompt_list = None
        
        def on_prompts_changed(prompts):
            nonlocal signal_received, prompt_list
            signal_received = True
            prompt_list = prompts
            
        controller.promptsChanged.connect(on_prompts_changed)
        
        # Execute
        controller.load_prompts()
        
        # Verify
        assert repository.get_all_called
        assert signal_received
        assert len(prompt_list) == 1
        assert prompt_list[0].id == 1
        assert prompt_list[0].title == "Test Prompt"
    
    def test_load_prompts_error(self, controller, repository):
        """Test loading prompts with an error."""
        # Setup
        repository.get_all = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.load_prompts()
        
        # Verify
        assert error_signal_received
        assert "Database error" in error_message
    
    def test_select_prompt(self, controller, repository, sample_prompt):
        """Test selecting a prompt."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Register signal spies
        selection_changed = False
        prompt_selected = False
        selected_list = None
        selected_prompt = None
        
        def on_selection_changed(prompts):
            nonlocal selection_changed, selected_list
            selection_changed = True
            selected_list = prompts
            
        def on_prompt_selected(prompt):
            nonlocal prompt_selected, selected_prompt
            prompt_selected = True
            selected_prompt = prompt
            
        controller.selectionChanged.connect(on_selection_changed)
        controller.promptSelected.connect(on_prompt_selected)
        
        # Execute
        controller.select_prompt(1)
        
        # Verify
        assert repository.get_by_id_called
        assert selection_changed
        assert prompt_selected
        assert len(selected_list) == 1
        assert selected_list[0].id == 1
        assert selected_prompt.id == 1
        assert controller.current_prompt.id == 1
    
    def test_save_prompt_new(self, controller, repository):
        """Test saving a new prompt."""
        # Setup
        prompt = Prompt()
        prompt._title = "New Prompt"
        prompt._content = "New content"
        
        # Register signal spy
        saved_signal_received = False
        saved_prompt = None
        
        def on_prompt_saved(prompt):
            nonlocal saved_signal_received, saved_prompt
            saved_signal_received = True
            saved_prompt = prompt
            
        controller.promptSaved.connect(on_prompt_saved)
        
        # Execute
        controller.save_prompt(prompt)
        
        # Verify
        assert repository.save_called
        assert saved_signal_received
        assert saved_prompt.title == "New Prompt"
    
    def test_save_prompt_existing(self, controller, repository, sample_prompt):
        """Test updating an existing prompt."""
        # Setup
        repository.prompts[1] = sample_prompt
        updated_prompt = Prompt()
        updated_prompt._id = 1
        updated_prompt._title = "Updated Title"
        updated_prompt._content = "Updated content"
        
        # Register signal spy
        saved_signal_received = False
        saved_prompt = None
        
        def on_prompt_saved(prompt):
            nonlocal saved_signal_received, saved_prompt
            saved_signal_received = True
            saved_prompt = prompt
            
        controller.promptSaved.connect(on_prompt_saved)
        
        # Execute
        controller.save_prompt(updated_prompt)
        
        # Verify
        assert repository.save_called
        assert saved_signal_received
        assert saved_prompt.title == "Updated Title"
        assert repository.prompts[1].title == "Updated Title"
    
    def test_save_prompt_error(self, controller, repository):
        """Test saving a prompt with an error."""
        # Setup
        prompt = Prompt()
        prompt._title = "Error Prompt"
        # Add content to avoid validation error
        prompt._content = "Test content"
        repository.save = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.save_prompt(prompt)
        
        # Verify
        assert error_signal_received
        assert "Failed to save prompt: Database error" in error_message
    
    def test_delete_prompt(self, controller, repository, sample_prompt):
        """Test deleting a prompt."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Register signal spy
        deleted_signal_received = False
        deleted_id = None
        
        def on_prompt_deleted(prompt_id):
            nonlocal deleted_signal_received, deleted_id
            deleted_signal_received = True
            deleted_id = prompt_id
            
        controller.promptDeleted.connect(on_prompt_deleted)
        
        # Execute
        controller.delete_prompt(1)
        
        # Verify
        assert repository.delete_called
        assert deleted_signal_received
        assert deleted_id == "1"
        assert 1 not in repository.prompts
    
    def test_delete_prompt_error(self, controller, repository):
        """Test deleting a prompt with an error."""
        # Setup
        # Add a mock prompt to the repository so it passes the existence check
        mock_prompt = MagicMock()
        repository.get_by_id = MagicMock(return_value=mock_prompt)
        repository.delete = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.delete_prompt(1)
        
        # Verify
        assert error_signal_received
        assert "Failed to delete prompt: Database error" in error_message
    
    def test_filter_prompts(self, controller, repository, sample_prompt):
        """Test filtering prompts."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Register signal spy
        filtered_signal_received = False
        filtered_prompts = None
        
        def on_prompts_changed(prompts):
            nonlocal filtered_signal_received, filtered_prompts
            filtered_signal_received = True
            filtered_prompts = prompts
            
        controller.promptsChanged.connect(on_prompts_changed)
        
        # Execute
        controller.filter_prompts(title="Test")
        
        # Verify
        assert repository.filter_called
        assert filtered_signal_received
        assert len(filtered_prompts) == 1
        
    def test_clear_selection(self, controller, repository, sample_prompt):
        """Test clearing the selection."""
        # Setup
        repository.prompts[1] = sample_prompt
        controller.selected_prompts = [sample_prompt]
        controller.current_prompt = sample_prompt
        
        # Register signal spy
        selection_changed = False
        selected_list = None
        
        def on_selection_changed(prompts):
            nonlocal selection_changed, selected_list
            selection_changed = True
            selected_list = prompts
            
        controller.selectionChanged.connect(on_selection_changed)
        
        # Execute
        controller.clear_selection()
        
        # Verify
        assert selection_changed
        assert len(selected_list) == 0
        assert controller.selected_prompts == []
        assert controller.current_prompt is None
        
    def test_create_new_prompt(self, controller):
        """Test creating a new prompt."""
        # Execute
        new_prompt = controller.create_new_prompt()
        
        # Verify
        assert isinstance(new_prompt, Prompt)
        assert new_prompt.id is None
        assert new_prompt.title == ""
        assert new_prompt.content == ""
        
    def test_validate_prompt_empty_title(self, controller):
        """Test prompt validation with empty title."""
        # Setup
        prompt = Prompt()
        prompt._content = "Content"
        prompt._title = ""
        
        # Execute
        errors = controller._validate_prompt(prompt)
        
        # Verify
        assert len(errors) == 1
        assert "Title cannot be empty" in errors[0]
        
    def test_validate_prompt_empty_content(self, controller):
        """Test prompt validation with empty content."""
        # Setup
        prompt = Prompt()
        prompt._content = ""
        prompt._title = "Title"
        
        # Execute
        errors = controller._validate_prompt(prompt)
        
        # Verify
        assert len(errors) == 1
        assert "Content cannot be empty" in errors[0]
        
    def test_validate_prompt_title_too_long(self, controller):
        """Test prompt validation with title exceeding max length."""
        # Setup
        prompt = Prompt()
        prompt._content = "Content"
        prompt._title = "X" * 256  # Create a title > 255 chars
        
        # Execute
        errors = controller._validate_prompt(prompt)
        
        # Verify
        assert len(errors) == 1
        assert "Title cannot exceed 255 characters" in errors[0]
        
    def test_validate_prompt_multiple_errors(self, controller):
        """Test prompt validation with multiple errors."""
        # Setup
        prompt = Prompt()
        prompt._content = ""
        prompt._title = "X" * 256  # Create a title > 255 chars
        
        # Execute
        errors = controller._validate_prompt(prompt)
        
        # Verify
        assert len(errors) == 2
        assert any("Title cannot exceed 255 characters" in error for error in errors)
        assert any("Content cannot be empty" in error for error in errors)
        
    def test_save_prompt_validation_error(self, controller):
        """Test saving a prompt with validation errors."""
        # Setup
        prompt = Prompt()
        prompt._title = ""  # Empty title to trigger validation error
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        saved_signal_received = False
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        def on_prompt_saved(prompt):
            nonlocal saved_signal_received
            saved_signal_received = True
            
        controller.operationError.connect(on_operation_error)
        controller.promptSaved.connect(on_prompt_saved)
        
        # Execute
        controller.save_prompt(prompt)
        
        # Verify
        assert error_signal_received
        assert "Validation errors" in error_message
        assert "Title cannot be empty" in error_message
        assert not saved_signal_received
        
    def test_select_prompt_not_found(self, controller, repository):
        """Test selecting a prompt that doesn't exist."""
        # Setup
        repository.get_by_id = MagicMock(return_value=None)
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.select_prompt(999)  # Non-existent ID
        
        # Verify
        assert error_signal_received
        assert "not found" in error_message

    def test_select_prompt_error(self, controller, repository):
        """Test selecting a prompt with an error."""
        # Setup
        repository.get_by_id = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.select_prompt(1)
        
        # Verify
        assert error_signal_received
        assert "Failed to select prompt" in error_message
        
    def test_multi_select_prompts(self, controller, repository, sample_prompt):
        """Test selecting multiple prompts."""
        # Setup
        prompt1 = sample_prompt
        prompt2 = Prompt()
        prompt2._id = 2
        prompt2._title = "Second Prompt"
        prompt2._content = "Second content"
        
        repository.prompts[1] = prompt1
        repository.prompts[2] = prompt2
        
        # Register signal spy
        selection_changed = False
        selected_prompts = None
        
        def on_selection_changed(prompts):
            nonlocal selection_changed, selected_prompts
            selection_changed = True
            selected_prompts = prompts
            
        controller.selectionChanged.connect(on_selection_changed)
        
        # Execute
        controller.multi_select_prompts([1, 2])
        
        # Verify
        assert selection_changed
        assert len(selected_prompts) == 2
        assert controller.current_prompt.id == 1  # First prompt is current
        assert controller.selected_prompts[0].id == 1
        assert controller.selected_prompts[1].id == 2
        
    def test_multi_select_prompts_none_found(self, controller, repository):
        """Test selecting multiple prompts when none exist."""
        # Setup
        repository.get_by_id = MagicMock(return_value=None)
        
        # Register signal spy
        selection_changed = False
        selected_prompts = None
        
        def on_selection_changed(prompts):
            nonlocal selection_changed, selected_prompts
            selection_changed = True
            selected_prompts = prompts
            
        controller.selectionChanged.connect(on_selection_changed)
        
        # Execute
        controller.multi_select_prompts([1, 2])
        
        # Verify
        assert selection_changed
        assert len(selected_prompts) == 0
        assert controller.current_prompt is None
        
    def test_multi_select_prompts_error(self, controller, repository):
        """Test selecting multiple prompts with an error."""
        # Setup
        repository.get_by_id = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.multi_select_prompts([1, 2])
        
        # Verify
        assert error_signal_received
        assert "Failed to select prompts" in error_message
        
    def test_batch_delete_prompts_success(self, controller, repository, sample_prompt):
        """Test batch deleting prompts successfully."""
        # Setup
        prompt1 = sample_prompt
        prompt2 = Prompt()
        prompt2._id = 2
        prompt2._title = "Second Prompt"
        prompt2._content = "Second content"
        
        repository.prompts[1] = prompt1
        repository.prompts[2] = prompt2
        
        # Register signal spies
        delete_signals = []
        success_signal_received = False
        success_message = None
        
        def on_prompt_deleted(prompt_id):
            delete_signals.append(prompt_id)
            
        def on_operation_success(message):
            nonlocal success_signal_received, success_message
            success_signal_received = True
            success_message = message
            
        controller.promptDeleted.connect(on_prompt_deleted)
        controller.operationSuccess.connect(on_operation_success)
        
        # Execute
        controller.batch_delete_prompts([1, 2])
        
        # Verify
        assert repository.delete_called
        assert len(delete_signals) == 2
        assert "1" in delete_signals
        assert "2" in delete_signals
        assert success_signal_received
        assert "Successfully deleted" in success_message
        assert len(repository.prompts) == 0
        
    def test_batch_delete_prompts_partial_success(self, controller, repository, sample_prompt):
        """Test batch deleting prompts with partial success."""
        # Setup
        repository.prompts[1] = sample_prompt
        
        # Make delete fail for ID 2 by returning False
        original_delete = repository.delete
        def mock_delete(prompt_id):
            if prompt_id == 1:
                del repository.prompts[prompt_id]
                return True
            return False
        repository.delete = mock_delete
        
        # Register signal spies
        delete_signals = []
        error_signal_received = False
        error_message = None
        
        def on_prompt_deleted(prompt_id):
            delete_signals.append(prompt_id)
            
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.promptDeleted.connect(on_prompt_deleted)
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.batch_delete_prompts([1, 2])
        
        # Verify
        assert len(delete_signals) == 1
        assert "1" in delete_signals
        assert error_signal_received
        assert "Partially successful" in error_message
        assert len(repository.prompts) == 0
        
    def test_batch_delete_prompts_complete_failure(self, controller, repository):
        """Test batch deleting prompts with complete failure."""
        # Setup
        # Make delete fail for all IDs
        repository.delete = MagicMock(return_value=False)
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.batch_delete_prompts([1, 2])
        
        # Verify
        assert error_signal_received
        assert "Failed to delete any prompts" in error_message
        
    def test_batch_delete_prompts_error(self, controller, repository):
        """Test batch deleting prompts with an exception."""
        # Setup
        repository.delete = MagicMock(side_effect=Exception("Database error"))
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.operationError.connect(on_operation_error)
        
        # Execute
        controller.batch_delete_prompts([1, 2])
        
        # Verify
        assert error_signal_received
        assert "Failed to delete any prompts" in error_message 