"""
Unit tests for the FilterController class.

This module contains tests for the FilterController class, which
is responsible for managing filtering and sorting operations for
data collections in the Prometheus AI Prompt Generator.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QStandardItemModel

from prometheus_prompt_generator.domain.models.prompt import Prompt


class MockPromptRepository:
    """Mock repository for testing filtering capabilities."""
    
    def __init__(self):
        self.prompts = {}
        self.filter_called = False
        self.error_on_filter = False
    
    def get_all(self):
        return list(self.prompts.values())
    
    def get_by_id(self, prompt_id):
        return self.prompts.get(prompt_id)
    
    def filter(self, **kwargs):
        self.filter_called = True
        if self.error_on_filter:
            raise Exception("Error filtering prompts")
        
        if not kwargs:
            return self.get_all()
        
        filtered_prompts = []
        for prompt in self.prompts.values():
            matched = True
            for key, value in kwargs.items():
                if key == 'title' and value and value.lower() not in prompt.title.lower():
                    matched = False
                    break
                elif key == 'tags' and value:
                    # Assume prompt.tags is a list of tag ids
                    if not set(value).issubset(set(prompt.tags)):
                        matched = False
                        break
                elif key == 'category_id' and value and prompt.category_id != value:
                    matched = False
                    break
            
            if matched:
                filtered_prompts.append(prompt)
        
        return filtered_prompts


class MockPrompt:
    """Mock prompt class for testing."""
    
    def __init__(self, prompt_id, title, content="", tags=None, category_id=None, created_date=None):
        self.id = prompt_id
        self.title = title
        self.content = content
        self.tags = tags or []
        self.category_id = category_id
        self.created_date = created_date


@pytest.fixture
def repository():
    """Fixture for creating a mock repository."""
    repo = MockPromptRepository()
    
    # Add some sample prompts
    repo.prompts[1] = MockPrompt(1, "ChatGPT Prompt", tags=[1, 2], category_id=1)
    repo.prompts[2] = MockPrompt(2, "DALL-E Image Generation", tags=[2, 3], category_id=2)
    repo.prompts[3] = MockPrompt(3, "Text Summarization", tags=[1, 3], category_id=1)
    repo.prompts[4] = MockPrompt(4, "Code Review Assistant", tags=[4], category_id=3)
    repo.prompts[5] = MockPrompt(5, "Customer Support Bot", tags=[2, 5], category_id=2)
    
    return repo


@pytest.fixture
def filter_controller(repository):
    """Fixture for creating a filter controller with mock repository."""
    from prometheus_prompt_generator.domain.controllers.filter_controller import FilterController
    return FilterController(repository)


class TestFilterController:
    """Tests for the FilterController class."""
    
    def test_init(self, filter_controller, repository):
        """Test controller initialization."""
        assert filter_controller.repository == repository
        assert isinstance(filter_controller.proxy_model, QSortFilterProxyModel)
    
    def test_set_source_model(self, filter_controller):
        """Test setting a source model for filtering."""
        # Create a real model instead of a mock for better compatibility
        mock_model = QStandardItemModel()
        filter_controller.set_source_model(mock_model)
        assert filter_controller.proxy_model.sourceModel() == mock_model
    
    def test_filter_by_title(self, filter_controller, repository):
        """Test filtering prompts by title."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_title("ChatGPT")
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 1
        assert filtered_prompts[0].title == "ChatGPT Prompt"
    
    def test_filter_by_tags(self, filter_controller, repository):
        """Test filtering prompts by tags."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_tags([2])
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 3
        assert any(p.title == "ChatGPT Prompt" for p in filtered_prompts)
        assert any(p.title == "DALL-E Image Generation" for p in filtered_prompts)
        assert any(p.title == "Customer Support Bot" for p in filtered_prompts)
    
    def test_filter_by_category(self, filter_controller, repository):
        """Test filtering prompts by category."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_category(1)
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 2
        assert any(p.title == "ChatGPT Prompt" for p in filtered_prompts)
        assert any(p.title == "Text Summarization" for p in filtered_prompts)
    
    def test_apply_multiple_filters(self, filter_controller, repository):
        """Test applying multiple filters simultaneously."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute - filter by category 1 and tag 1
        filter_controller.apply_filters(category_id=1, tags=[1])
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 2
        assert filtered_prompts[0].title == "ChatGPT Prompt"
        assert filtered_prompts[1].title == "Text Summarization"
    
    def test_clear_filters(self, filter_controller, repository):
        """Test clearing all filters."""
        # Setup
        filter_controller.apply_filters(title="ChatGPT")  # Apply a filter first
        
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.clear_filters()
        
        # Verify
        assert filter_signal_received
        assert len(filtered_prompts) == 5  # All prompts
    
    def test_sort_by_title_ascending(self, filter_controller):
        """Test sorting prompts by title in ascending order."""
        # Setup
        sort_signal_received = False
        
        def on_sorted():
            nonlocal sort_signal_received
            sort_signal_received = True
        
        filter_controller.sorted.connect(on_sorted)
        
        # Execute
        filter_controller.sort_by_column(0, Qt.SortOrder.AscendingOrder)  # Assuming column 0 is title
        
        # Verify
        assert sort_signal_received
        assert filter_controller.proxy_model.sortColumn() == 0
        assert filter_controller.proxy_model.sortOrder() == Qt.SortOrder.AscendingOrder
    
    def test_sort_by_title_descending(self, filter_controller):
        """Test sorting prompts by title in descending order."""
        # Setup
        sort_signal_received = False
        
        def on_sorted():
            nonlocal sort_signal_received
            sort_signal_received = True
        
        filter_controller.sorted.connect(on_sorted)
        
        # Execute
        filter_controller.sort_by_column(0, Qt.SortOrder.DescendingOrder)  # Assuming column 0 is title
        
        # Verify
        assert sort_signal_received
        assert filter_controller.proxy_model.sortColumn() == 0
        assert filter_controller.proxy_model.sortOrder() == Qt.SortOrder.DescendingOrder
    
    def test_filter_error_handling(self, filter_controller, repository):
        """Test error handling during filtering."""
        # Setup
        repository.error_on_filter = True
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.filter_by_title("Test")
        
        # Verify
        assert error_signal_received
        assert "Error filtering prompts" in error_message
    
    def test_get_filtered_data(self, filter_controller):
        """Test retrieving filtered data from the controller."""
        # Setup - apply a filter
        filter_controller.filter_by_title("ChatGPT")
        
        # Execute
        filtered_data = filter_controller.get_filtered_data()
        
        # Verify
        assert len(filtered_data) == 1
        assert filtered_data[0].title == "ChatGPT Prompt"
    
    def test_custom_filter_function(self, filter_controller):
        """Test applying a custom filter function."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Custom filter function to find prompts with 'Assistant' in the title
        def custom_filter(prompt):
            return "Assistant" in prompt.title
        
        # Execute
        filter_controller.apply_custom_filter(custom_filter)
        
        # Verify
        assert filter_signal_received
        assert len(filtered_prompts) == 1
        assert filtered_prompts[0].title == "Code Review Assistant"
    
    def test_filter_by_title_empty(self, filter_controller, repository):
        """Test filtering by empty title text."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Apply a filter first, then clear it with empty string
        filter_controller.filter_by_title("ChatGPT")
        filter_controller.filter_by_title("")
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 5  # All prompts should be returned
    
    def test_filter_by_title_error(self, filter_controller, repository):
        """Test error handling when filtering by title."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Filter by title error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.filter_by_title("test")
        
        # Verify
        assert error_signal_received
        assert "Error applying repository filters: Filter by title error" in error_message
    
    def test_filter_by_tags_empty(self, filter_controller, repository):
        """Test filtering by empty tags list."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Apply a filter first, then clear it with empty list
        filter_controller.filter_by_tags([1])
        filter_controller.filter_by_tags([])
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 5  # All prompts should be returned
    
    def test_filter_by_tags_error(self, filter_controller, repository):
        """Test error handling when filtering by tags."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Filter by tags error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.filter_by_tags([1, 2])
        
        # Verify
        assert error_signal_received
        assert "Error applying repository filters: Filter by tags error" in error_message
    
    def test_filter_by_category_error(self, filter_controller, repository):
        """Test error handling when filtering by category."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Filter by category error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.filter_by_category(1)
        
        # Verify
        assert error_signal_received
        assert "Error applying repository filters: Filter by category error" in error_message
    
    def test_filter_by_category_empty(self, filter_controller, repository):
        """Test filtering by empty category."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Apply a filter first, then clear it with None
        filter_controller.filter_by_category(1)
        filter_controller.filter_by_category(None)
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 5  # All prompts should be returned
    
    def test_apply_filters_error(self, filter_controller, repository):
        """Test error handling when applying multiple filters."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Apply filters error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.apply_filters(title="test", category_id=1)
        
        # Verify
        assert error_signal_received
        assert "Error applying repository filters: Apply filters error" in error_message
    
    def test_apply_filters_empty(self, filter_controller, repository):
        """Test applying empty filters."""
        # Setup
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.apply_filters()
        
        # Verify
        assert repository.filter_called
        assert filter_signal_received
        assert len(filtered_prompts) == 5  # All prompts should be returned
    
    def test_clear_filters_error(self, filter_controller, repository):
        """Test error handling when clearing filters."""
        # Setup
        repository.get_all = MagicMock(side_effect=Exception("Clear filters error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.clear_filters()
        
        # Verify
        assert error_signal_received
        assert "Error clearing filters:" in error_message
    
    def test_sort_by_column_error(self, filter_controller):
        """Test error handling when sorting by column."""
        # Setup
        # Create a mock proxy model that will raise an exception when sort is called
        mock_proxy = MagicMock()
        mock_proxy.sort = MagicMock(side_effect=Exception("Sort error"))
        filter_controller.proxy_model = mock_proxy
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.sort_by_column(0, Qt.SortOrder.AscendingOrder)
        
        # Verify
        assert error_signal_received
        assert "Error sorting data:" in error_message
    
    def test_apply_custom_filter_error(self, filter_controller, repository):
        """Test error handling when applying custom filter."""
        # Setup
        repository.get_all = MagicMock(side_effect=Exception("Custom filter error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller.apply_custom_filter(lambda x: True)
        
        # Verify
        assert error_signal_received
        assert "Error applying custom filter:" in error_message
    
    def test_get_filtered_data_with_custom_filter(self, filter_controller, repository):
        """Test getting filtered data with custom filter function."""
        # Setup
        # Custom filter function to find prompts with 'Assistant' in the title
        def custom_filter(prompt):
            return "Assistant" in prompt.title
            
        filter_controller.custom_filter_func = custom_filter
        
        # Execute
        filtered_data = filter_controller.get_filtered_data()
        
        # Verify
        assert len(filtered_data) == 1
        assert filtered_data[0].title == "Code Review Assistant"
    
    def test_get_filtered_data_with_proxy_model(self, filter_controller):
        """Test getting filtered data from proxy model."""
        # Setup
        # Create a model with data
        from PyQt6.QtGui import QStandardItemModel, QStandardItem
        source_model = QStandardItemModel()
        
        # Create a sample item and add to model
        item = QStandardItem("Sample Item")
        # Create a mock prompt
        mock_prompt = MockPrompt(1, "Sample Prompt")
        item.setData(mock_prompt, Qt.ItemDataRole.UserRole)
        source_model.appendRow(item)
        
        filter_controller.set_source_model(source_model)
        
        # Execute
        filtered_data = filter_controller.get_filtered_data()
        
        # Verify
        assert len(filtered_data) > 0
        assert hasattr(filtered_data[0], 'title')  # Verify we got a prompt object
    
    def test_get_filtered_data_error(self, filter_controller, repository):
        """Test error handling when getting filtered data."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Get filtered data error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Add a filter to trigger repository.filter call
        filter_controller.current_filters = {'title': 'test'}
        
        # Execute
        result = filter_controller.get_filtered_data()
        
        # Verify
        assert error_signal_received
        assert "Error getting filtered data:" in error_message
        assert result == []  # Should return empty list on error
    
    def test_apply_repository_filters_error(self, filter_controller, repository):
        """Test error handling when applying repository filters."""
        # Setup
        repository.filter = MagicMock(side_effect=Exception("Apply repository filters error"))
        
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Execute
        filter_controller._apply_repository_filters()
        
        # Verify
        assert error_signal_received
        assert "Error applying repository filters:" in error_message
    
    def test_filter_by_title_no_proxy_model(self, filter_controller):
        """Test filtering by title without proxy model."""
        # Setup - explicitly set proxy_model to None
        filter_controller.proxy_model = None
        
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_title("ChatGPT")
        
        # Verify
        assert filter_signal_received
        assert len(filtered_prompts) == 1
        assert filtered_prompts[0].title == "ChatGPT Prompt"
    
    def test_filter_by_tags_no_proxy_model(self, filter_controller):
        """Test filtering by tags without proxy model."""
        # Setup - explicitly set proxy_model to None
        filter_controller.proxy_model = None
        
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_tags([2])
        
        # Verify
        assert filter_signal_received
        assert len(filtered_prompts) == 3
    
    def test_filter_by_category_no_proxy_model(self, filter_controller):
        """Test filtering by category without proxy model."""
        # Setup - explicitly set proxy_model to None
        filter_controller.proxy_model = None
        
        filter_signal_received = False
        filtered_prompts = None
        
        def on_filtered(prompts):
            nonlocal filter_signal_received, filtered_prompts
            filter_signal_received = True
            filtered_prompts = prompts
        
        filter_controller.filtered.connect(on_filtered)
        
        # Execute
        filter_controller.filter_by_category(1)
        
        # Verify
        assert filter_signal_received
        assert len(filtered_prompts) == 2
    
    def test_get_filtered_data_empty_results(self, filter_controller, repository):
        """Test getting filtered data with empty results."""
        # Setup
        # Override the repository's filter method to return empty list
        repository.filter = MagicMock(return_value=[])
        filter_controller.current_filters = {'title': 'nonexistent'}
        
        # Execute
        filtered_data = filter_controller.get_filtered_data()
        
        # Verify
        assert len(filtered_data) == 0
        assert filtered_data == []
    
    def test_error_paths_with_patching(self, filter_controller, repository):
        """Test error handling paths by patching the methods directly."""
        from unittest.mock import patch

        error_signal_received = False
        error_message = ""
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        filter_controller.error.connect(on_error)
        
        # Test error in filter_by_title
        with patch.object(filter_controller, '_apply_repository_filters', 
                         side_effect=Exception("Direct error in filter_by_title")):
            # Reset tracking variables
            error_signal_received = False
            error_message = ""
            
            # Execute
            filter_controller.filter_by_title("test")
            
            # Verify
            assert error_signal_received
            assert "Error filtering by title:" in error_message
        
        # Test error in filter_by_tags
        with patch.object(filter_controller, '_apply_repository_filters', 
                         side_effect=Exception("Direct error in filter_by_tags")):
            # Reset tracking variables
            error_signal_received = False
            error_message = ""
            
            # Execute
            filter_controller.filter_by_tags([1, 2])
            
            # Verify
            assert error_signal_received
            assert "Error filtering by tags:" in error_message
        
        # Test error in filter_by_category
        with patch.object(filter_controller, '_apply_repository_filters', 
                         side_effect=Exception("Direct error in filter_by_category")):
            # Reset tracking variables
            error_signal_received = False
            error_message = ""
            
            # Execute
            filter_controller.filter_by_category(1)
            
            # Verify
            assert error_signal_received
            assert "Error filtering by category:" in error_message
        
        # Test error in apply_filters
        with patch.object(filter_controller, '_apply_repository_filters', 
                         side_effect=Exception("Direct error in apply_filters")):
            # Reset tracking variables
            error_signal_received = False
            error_message = ""
            
            # Execute
            filter_controller.apply_filters(title="test")
            
            # Verify
            assert error_signal_received
            assert "Error applying filters:" in error_message
    
    def test_get_filtered_data_direct_error(self, filter_controller, repository):
        """Test error handling in get_filtered_data with a direct exception."""
        # Setup
        # Create a repository that raises an exception when get_all is called
        repository.get_all = MagicMock(side_effect=Exception("Direct error in get_filtered_data"))
        
        error_signal_received = False
        error_message = ""
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        filter_controller.error.connect(on_error)
        
        # Execute - with no filters, this will call repository.get_all()
        filter_controller.current_filters = {}
        filter_controller.custom_filter_func = None
        result = filter_controller.get_filtered_data()
        
        # Verify
        assert error_signal_received
        assert "Error getting filtered data:" in error_message
        assert result == []  # Should return empty list on error 