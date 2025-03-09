"""
Pytest configuration for Prometheus AI Prompt Generator.

This module contains common fixtures and configuration for testing.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

# Add project root to the Python path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Import models
from prometheus_prompt_generator.domain.models.prompt import Prompt


@pytest.fixture
def sample_prompt():
    """Create a sample prompt for testing."""
    prompt = Prompt()
    prompt._id = 1
    prompt._title = "Test Prompt"
    prompt._content = "This is a test prompt content."
    prompt._description = "Sample prompt for testing purposes."
    prompt._is_public = True
    prompt._is_featured = False
    prompt._is_custom = True
    prompt._category_id = 2
    prompt._user_id = 1
    return prompt


class MockRepository:
    """Base mock repository for testing."""
    
    def __init__(self):
        self.items = {}
        self.save_called = False
        self.delete_called = False
        self.get_all_called = False
        self.get_by_id_called = False
        self.filter_called = False
        
    def save(self, item):
        self.save_called = True
        if item.id is None:
            # Simulate auto-increment ID
            item._id = max(self.items.keys()) + 1 if self.items else 1
        self.items[item.id] = item
        return item
        
    def delete(self, item_id):
        self.delete_called = True
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
        
    def get_all(self):
        self.get_all_called = True
        return list(self.items.values())
        
    def get_by_id(self, item_id):
        self.get_by_id_called = True
        return self.items.get(item_id)
        
    def filter(self, **kwargs):
        self.filter_called = True
        # Simple filtering, just return all for now
        return self.get_all()


@pytest.fixture
def mock_prompt_repository():
    """Create a mock prompt repository for testing."""
    return MockRepository()


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    mock = MagicMock()
    mock.transaction.return_value.__enter__.return_value = None
    mock.transaction.return_value.__exit__.return_value = None
    return mock 