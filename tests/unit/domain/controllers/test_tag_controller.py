"""
Unit tests for the TagController class.

This module contains tests for the TagController class, which
is responsible for managing tag operations and providing
a bridge between the UI and data layers.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

from prometheus_prompt_generator.domain.models.tag import Tag
from prometheus_prompt_generator.domain.controllers.tag_controller import TagController


class MockTagRepository:
    """Mock repository for testing."""

    def __init__(self):
        self.tags = {}
        self.get_all_called = False
        self.save_called = False
        self.delete_called = False
        self.filter_called = False
        self.error_on_get_all = False
        self.error_on_save = False
        self.error_on_delete = False
        self.error_on_filter = False

    def get_all(self):
        self.get_all_called = True
        if self.error_on_get_all:
            raise Exception("Failed to get tags")
        return list(self.tags.values())

    def get_by_id(self, tag_id):
        return self.tags.get(tag_id)

    def save(self, tag):
        self.save_called = True
        if self.error_on_save:
            raise Exception("Failed to save tag")
        
        # If tag has no ID, assign one
        if not tag.id:
            tag_id = max(self.tags.keys()) + 1 if self.tags else 1
            tag._id = tag_id
        
        self.tags[tag.id] = tag
        return tag

    def delete(self, tag_id):
        self.delete_called = True
        if self.error_on_delete:
            raise Exception("Database error")
        
        if tag_id in self.tags:
            del self.tags[tag_id]
            return True
        return False

    def filter(self, **kwargs):
        self.filter_called = True
        if self.error_on_filter:
            raise Exception("Failed to filter tags")
        
        if kwargs.get('name') == 'Test':
            # Return a tag with name 'Test' for testing
            filtered_tag = self.tags.get(1, None)
            return [filtered_tag] if filtered_tag else []
            
        return []


@pytest.fixture
def repository():
    """Fixture for creating a mock repository."""
    return MockTagRepository()


@pytest.fixture
def controller(repository):
    """Fixture for creating a controller with mock repository."""
    return TagController(repository)


@pytest.fixture
def sample_tag():
    """Fixture for creating a sample tag."""
    tag = Tag()
    tag._id = 1
    tag._name = "Test Tag"
    tag._color = "#FF5733"
    tag._description = "A test tag"
    return tag


class TestTagController:
    """Tests for the TagController class."""

    def test_init(self, controller, repository):
        """Test controller initialization."""
        assert controller.repository == repository
        assert controller.selected_tags == []
        assert controller.current_tag is None

    def test_load_tags_success(self, controller, repository, sample_tag):
        """Test successful loading of tags."""
        # Setup
        repository.tags[1] = sample_tag

        # Register signal spy
        tags_changed_received = False
        received_tags = None

        def on_tags_changed(tags):
            nonlocal tags_changed_received, received_tags
            tags_changed_received = True
            received_tags = tags

        controller.tagsChanged.connect(on_tags_changed)

        # Execute
        controller.load_tags()

        # Verify
        assert repository.get_all_called
        assert tags_changed_received
        assert len(received_tags) == 1
        assert received_tags[0].id == 1
        assert received_tags[0].name == "Test Tag"

    def test_load_tags_error(self, controller, repository):
        """Test loading tags with an error."""
        # Setup
        repository.error_on_get_all = True

        # Register signal spy
        error_signal_received = False
        error_message = None

        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message

        controller.operationError.connect(on_operation_error)

        # Execute
        controller.load_tags()

        # Verify
        assert repository.get_all_called
        assert error_signal_received
        assert "Failed to get tags" in error_message

    def test_select_tag(self, controller, repository, sample_tag):
        """Test selecting a tag."""
        # Setup
        repository.tags[1] = sample_tag

        # Register signal spies
        tag_selected_received = False
        selected_tag = None
        selection_changed_received = False
        selection = None

        def on_tag_selected(tag):
            nonlocal tag_selected_received, selected_tag
            tag_selected_received = True
            selected_tag = tag

        def on_selection_changed(tags):
            nonlocal selection_changed_received, selection
            selection_changed_received = True
            selection = tags

        controller.tagSelected.connect(on_tag_selected)
        controller.selectionChanged.connect(on_selection_changed)

        # Execute
        controller.select_tag(1)

        # Verify
        assert tag_selected_received
        assert selected_tag.id == 1
        assert selected_tag.name == "Test Tag"
        assert selection_changed_received
        assert len(selection) == 1
        assert selection[0].id == 1
        assert controller.current_tag.id == 1
        assert len(controller.selected_tags) == 1

    def test_save_tag_new(self, controller, repository):
        """Test saving a new tag."""
        # Setup
        tag = Tag()
        tag._name = "New Tag"
        tag._color = "#33FF57"

        # Register signal spy
        saved_signal_received = False
        saved_tag = None

        def on_tag_saved(tag):
            nonlocal saved_signal_received, saved_tag
            saved_signal_received = True
            saved_tag = tag

        controller.tagSaved.connect(on_tag_saved)

        # Execute
        controller.save_tag(tag)

        # Verify
        assert repository.save_called
        assert saved_signal_received
        assert saved_tag.name == "New Tag"
        assert saved_tag.color == "#33FF57"

    def test_save_tag_existing(self, controller, repository, sample_tag):
        """Test updating an existing tag."""
        # Setup
        repository.tags[1] = sample_tag
        updated_tag = Tag()
        updated_tag._id = 1
        updated_tag._name = "Updated Tag"
        updated_tag._color = "#5733FF"

        # Register signal spy
        saved_signal_received = False
        saved_tag = None

        def on_tag_saved(tag):
            nonlocal saved_signal_received, saved_tag
            saved_signal_received = True
            saved_tag = tag

        controller.tagSaved.connect(on_tag_saved)

        # Execute
        controller.save_tag(updated_tag)

        # Verify
        assert repository.save_called
        assert saved_signal_received
        assert saved_tag.name == "Updated Tag"
        assert saved_tag.color == "#5733FF"

    def test_save_tag_error(self, controller, repository):
        """Test saving a tag with an error."""
        # Setup
        tag = Tag()
        tag._name = "Error Tag"
        repository.error_on_save = True

        # Register signal spy
        error_signal_received = False
        error_message = None

        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message

        controller.operationError.connect(on_operation_error)

        # Execute
        controller.save_tag(tag)

        # Verify
        assert repository.save_called
        assert error_signal_received
        assert "Failed to save tag" in error_message

    def test_delete_tag(self, controller, repository, sample_tag):
        """Test deleting a tag."""
        # Setup
        repository.tags[1] = sample_tag

        # Register signal spy
        deleted_signal_received = False
        deleted_tag_id = None

        def on_tag_deleted(tag_id):
            nonlocal deleted_signal_received, deleted_tag_id
            deleted_signal_received = True
            deleted_tag_id = tag_id

        controller.tagDeleted.connect(on_tag_deleted)

        # Execute
        controller.delete_tag(1)

        # Verify
        assert repository.delete_called
        assert deleted_signal_received
        assert deleted_tag_id == "1"

    def test_delete_tag_error(self, controller, repository, sample_tag):
        """Test deleting a tag with an error."""
        # Setup
        repository.tags[1] = sample_tag
        repository.error_on_delete = True

        # Register signal spy
        error_signal_received = False
        error_message = None

        def on_operation_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message

        controller.operationError.connect(on_operation_error)

        # Execute
        controller.delete_tag(1)

        # Verify
        assert repository.delete_called
        assert error_signal_received
        assert "Database error" in error_message

    def test_filter_tags(self, controller, repository, sample_tag):
        """Test filtering tags."""
        # Setup
        repository.tags[1] = sample_tag

        # Register signal spy
        filtered_signal_received = False
        filtered_tags = None

        def on_tags_changed(tags):
            nonlocal filtered_signal_received, filtered_tags
            filtered_signal_received = True
            filtered_tags = tags

        controller.tagsChanged.connect(on_tags_changed)

        # Execute
        controller.filter_tags(name="Test")

        # Verify
        assert repository.filter_called
        assert filtered_signal_received
        assert len(filtered_tags) == 1

    def test_clear_selection(self, controller, repository, sample_tag):
        """Test clearing the selection."""
        # Setup
        repository.tags[1] = sample_tag
        controller.current_tag = sample_tag
        controller.selected_tags = [sample_tag]

        # Register signal spy
        selection_changed_received = False
        selection = None

        def on_selection_changed(tags):
            nonlocal selection_changed_received, selection
            selection_changed_received = True
            selection = tags

        controller.selectionChanged.connect(on_selection_changed)

        # Execute
        controller.clear_selection()

        # Verify
        assert selection_changed_received
        assert len(selection) == 0
        assert controller.current_tag is None
        assert len(controller.selected_tags) == 0

    def test_create_new_tag(self, controller):
        """Test creating a new tag."""
        # Execute
        new_tag = controller.create_new_tag()

        # Verify
        assert isinstance(new_tag, Tag)
        assert new_tag.id is None
        assert new_tag.name == "" 