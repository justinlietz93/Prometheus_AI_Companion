"""
Unit tests for the AdvancedFilterProxyModel class.

This module contains tests for the AdvancedFilterProxyModel, which provides
enhanced filtering capabilities over the standard QSortFilterProxyModel.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, Qt, QAbstractItemModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from prometheus_prompt_generator.domain.controllers.advanced_filter_proxy_model import AdvancedFilterProxyModel


@pytest.fixture
def source_model():
    """Fixture to create a standard item model with test data."""
    model = QStandardItemModel()
    
    # Add column headers
    model.setHorizontalHeaderLabels(["Title", "Category", "Tags", "Date"])
    
    # Add some test data
    items = [
        ["ChatGPT Prompt", "General", "AI, GPT", "2025-03-01"],
        ["DALL-E Image Generation", "Visual", "AI, Image", "2025-03-02"],
        ["Text Summarization", "General", "NLP, Text", "2025-03-03"],
        ["Code Review Assistant", "Development", "Code, AI", "2025-03-04"],
        ["Customer Support Bot", "Business", "Support, AI", "2025-03-05"],
    ]
    
    for row_data in items:
        row_items = []
        for col_data in row_data:
            item = QStandardItem(col_data)
            row_items.append(item)
        model.appendRow(row_items)
    
    return model


@pytest.fixture
def filter_model(source_model):
    """Fixture to create an AdvancedFilterProxyModel with the source model."""
    proxy_model = AdvancedFilterProxyModel()
    proxy_model.setSourceModel(source_model)
    return proxy_model


class TestAdvancedFilterProxyModel:
    """Tests for the AdvancedFilterProxyModel class."""
    
    def test_init(self, filter_model):
        """Test initialization."""
        assert filter_model.filterCaseSensitivity() == Qt.CaseSensitivity.CaseInsensitive
        assert filter_model.sourceModel() is not None
    
    def test_column_mapping(self, filter_model):
        """Test setting column mappings."""
        column_maps = {
            "title": 0,
            "category": 1,
            "tags": 2,
            "date": 3
        }
        filter_model.set_column_mapping(column_maps)
        
        # Internal test - using private attribute for verification purposes
        assert filter_model._column_mappings == column_maps
    
    def test_simple_string_filter(self, filter_model):
        """Test filtering by a simple string."""
        filter_model.add_filter(0, "GPT")
        
        # Should only show rows containing "GPT" in the first column
        assert filter_model.rowCount() == 1
        assert filter_model.data(filter_model.index(0, 0)) == "ChatGPT Prompt"
    
    def test_regex_filter(self, filter_model):
        """Test filtering with regex."""
        # Filter for rows with titles that start with 'C'
        filter_model.add_filter(0, "^C", regex=True)
        
        # Should show "ChatGPT Prompt", "Code Review Assistant", "Customer Support Bot"
        assert filter_model.rowCount() == 3
        
        titles = [filter_model.data(filter_model.index(i, 0)) for i in range(filter_model.rowCount())]
        assert "ChatGPT Prompt" in titles
        assert "Code Review Assistant" in titles
        assert "Customer Support Bot" in titles
        assert "DALL-E Image Generation" not in titles
        assert "Text Summarization" not in titles
    
    def test_multi_column_filter(self, filter_model):
        """Test filtering on multiple columns."""
        # Filter for rows with "AI" in the Tags column and "General" in the Category column
        filter_model.add_filter(2, "AI")
        filter_model.add_filter(1, "General")
        
        # Should show only "ChatGPT Prompt"
        assert filter_model.rowCount() == 1
        assert filter_model.data(filter_model.index(0, 0)) == "ChatGPT Prompt"
    
    def test_remove_filter(self, filter_model):
        """Test removing a filter."""
        # Add filter and verify it works
        filter_model.add_filter(0, "GPT")
        assert filter_model.rowCount() == 1
        
        # Remove filter and verify all rows are visible again
        filter_model.remove_filter(0)
        assert filter_model.rowCount() == 5
    
    def test_clear_filters(self, filter_model):
        """Test clearing all filters."""
        # Add multiple filters
        filter_model.add_filter(0, "GPT")
        filter_model.add_filter(1, "General")
        assert filter_model.rowCount() == 1
        
        # Clear filters and verify all rows are visible
        filter_model.clear_filters()
        assert filter_model.rowCount() == 5
    
    def test_case_sensitivity(self, filter_model):
        """Test case-sensitive filtering."""
        # Case insensitive (default)
        filter_model.add_filter(0, "gpt")
        assert filter_model.rowCount() == 1  # Should find "ChatGPT Prompt"
        
        # Change to case sensitive
        filter_model.clear_filters()
        filter_model.set_case_sensitivity(True)
        filter_model.add_filter(0, "gpt")
        assert filter_model.rowCount() == 0  # Should not find "ChatGPT Prompt"
        
        # Try with correct case
        filter_model.clear_filters()
        filter_model.add_filter(0, "GPT")
        assert filter_model.rowCount() == 1  # Should find "ChatGPT Prompt"
    
    def test_filter_role(self, filter_model, source_model):
        """Test filtering with different roles."""
        # Set user role data
        for row in range(source_model.rowCount()):
            index = source_model.index(row, 0)
            source_model.setData(index, f"UserRole{row}", Qt.ItemDataRole.UserRole)
        
        # Filter using user role
        filter_model.set_filter_role(Qt.ItemDataRole.UserRole)
        filter_model.add_filter(0, "UserRole0")
        
        # Should only match the first row
        assert filter_model.rowCount() == 1
    
    def test_custom_filter_function(self, filter_model):
        """Test adding a custom filter function."""
        # Custom filter to show only rows with "AI" in the tags column
        def ai_filter(index):
            # Get the source model index for the tags column (column 2)
            tags_index = index.model().index(index.row(), 2, index.parent())
            tags_text = index.model().data(tags_index)
            return "AI" in tags_text
        
        filter_model.add_custom_filter(ai_filter)
        
        # Should show rows with "AI" in tags
        assert filter_model.rowCount() == 4
        
        titles = [filter_model.data(filter_model.index(i, 0)) for i in range(filter_model.rowCount())]
        assert "ChatGPT Prompt" in titles
        assert "DALL-E Image Generation" in titles
        assert "Code Review Assistant" in titles
        assert "Customer Support Bot" in titles
        assert "Text Summarization" not in titles
    
    def test_column_name_resolution(self, filter_model):
        """Test column name resolution with mappings."""
        # Set column mappings
        filter_model.set_column_mapping({
            "title": 0,
            "category": 1,
            "tags": 2,
            "date": 3
        })
        
        # Filter using column name
        filter_model.add_filter("category", "General")
        
        # Should show rows with General category
        assert filter_model.rowCount() == 2
        
        categories = [filter_model.data(filter_model.index(i, 1)) for i in range(filter_model.rowCount())]
        assert all(category == "General" for category in categories)
    
    def test_unknown_column_name(self, filter_model):
        """Test behavior with unknown column name."""
        # Set column mappings
        filter_model.set_column_mapping({
            "title": 0,
            "category": 1,
            "tags": 2,
            "date": 3
        })
        
        # Use an unknown column name (should default to column 0)
        filter_model.add_filter("unknown_column", "ChatGPT")
        
        # Should use column 0 (title) and filter for "ChatGPT"
        assert filter_model.rowCount() == 1
        assert filter_model.data(filter_model.index(0, 0)) == "ChatGPT Prompt" 