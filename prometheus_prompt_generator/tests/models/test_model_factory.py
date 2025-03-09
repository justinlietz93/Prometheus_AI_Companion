"""
Unit tests for the ModelFactory class in the Prometheus AI Prompt Generator.

This module tests the ModelFactory class's ability to create various SQL models
for Tags, Categories, and Prompts, as well as its error handling and hierarchical view creation.
"""

import unittest
from unittest.mock import patch, MagicMock

from PySide6.QtSql import QSqlRelationalTableModel, QSqlTableModel, QSqlDatabase

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import ModelFactory


class TestModelFactory(ModelTestBase):
    """Test case for the ModelFactory class."""
    
    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        self.factory = ModelFactory()
    
    def test_create_tag_model(self):
        """Test creating a tag model."""
        # Create tag model
        model = self.factory.create_tag_model()
        
        # Should be a QSqlTableModel
        self.assertIsInstance(model, QSqlTableModel)
        
        # Should have the correct table name
        self.assertEqual(model.tableName(), "Tags")
        
        # Should have records
        self.assertGreater(model.rowCount(), 0)
        
        # Should have the correct header data for columns
        self.assertEqual(model.headerData(1, 1), "Name")
        self.assertEqual(model.headerData(2, 1), "Description")
        self.assertEqual(model.headerData(3, 1), "Color")
    
    def test_create_category_model(self):
        """Test creating a category model."""
        # Create category model
        model = self.factory.create_category_model()
        
        # Should be a QSqlRelationalTableModel
        self.assertIsInstance(model, QSqlRelationalTableModel)
        
        # Should have the correct table name
        self.assertEqual(model.tableName(), "Categories")
        
        # Should have records
        self.assertGreater(model.rowCount(), 0)
        
        # Should have the correct header data for columns
        self.assertEqual(model.headerData(1, 1), "Name")
        self.assertEqual(model.headerData(2, 1), "Description")
        self.assertEqual(model.headerData(3, 1), "Parent")
    
    def test_create_prompt_model(self):
        """Test creating a prompt model."""
        # Create prompt model
        model = self.factory.create_prompt_model()
        
        # Should be a QSqlRelationalTableModel
        self.assertIsInstance(model, QSqlRelationalTableModel)
        
        # Should have the correct table name
        self.assertEqual(model.tableName(), "Prompts")
        
        # Should have records
        self.assertGreater(model.rowCount(), 0)
        
        # Should have the correct header data for columns
        self.assertEqual(model.headerData(1, 1), "Title")
        self.assertEqual(model.headerData(2, 1), "Content")
        self.assertEqual(model.headerData(3, 1), "Description")
        self.assertEqual(model.headerData(4, 1), "Category")
    
    def test_create_prompt_tag_model(self):
        """Test creating a prompt-tag relationship model."""
        # Create prompt-tag model
        model = self.factory.create_prompt_tag_model()
        
        # Should be a QSqlRelationalTableModel
        self.assertIsInstance(model, QSqlRelationalTableModel)
        
        # Should have the correct table name
        self.assertEqual(model.tableName(), "PromptTags")
        
        # Should have records (from test data)
        self.assertGreater(model.rowCount(), 0)
        
        # Should have the correct header data for columns
        self.assertEqual(model.headerData(1, 1), "Prompt")
        self.assertEqual(model.headerData(2, 1), "Tag")
    
    def test_create_filtered_model(self):
        """Test creating a filtered model."""
        # Create a tag model with filter
        model = self.factory.create_filtered_model("Tags", "name LIKE '%python%'")
        
        # Should be a QSqlTableModel
        self.assertIsInstance(model, QSqlTableModel)
        
        # Should have the correct table name
        self.assertEqual(model.tableName(), "Tags")
        
        # Should have a filter applied
        self.assertEqual(model.filter(), "name LIKE '%python%'")
        
        # Should only include matching records
        self.assertEqual(model.rowCount(), 1)  # Only the python tag
    
    def test_create_hierarchical_category_model(self):
        """Test creating a hierarchical category model."""
        # First create some test categories with hierarchy
        parent = self.factory.create_category_model()
        parent.insertRow(parent.rowCount())
        parent.setData(parent.index(parent.rowCount() - 1, 1), "Parent Category")
        parent.setData(parent.index(parent.rowCount() - 1, 2), "A parent category")
        parent.submitAll()
        
        # Get the ID of the new parent
        parent_id = parent.data(parent.index(parent.rowCount() - 1, 0))
        
        # Add a child
        child = self.factory.create_category_model()
        child.insertRow(child.rowCount())
        child.setData(child.index(child.rowCount() - 1, 1), "Child Category")
        child.setData(child.index(child.rowCount() - 1, 2), "A child category")
        child.setData(child.index(child.rowCount() - 1, 3), parent_id)
        child.submitAll()
        
        # Create hierarchical model
        model = self.factory.create_hierarchical_category_model()
        
        # Should have a stacked structure
        # Model should have items - at minimum the ones we created plus existing test data
        self.assertGreaterEqual(model.rowCount(), 2)
        
        # Setting up a way to verify hierarchy would require more complex testing
        # involving traversing the model's items - this would be implementation-specific
    
    @patch('PySide6.QtSql.QSqlRelationalTableModel.setRelation')
    def test_relation_setup_error_handling(self, mock_set_relation):
        """Test error handling during relation setup."""
        # Make setRelation raise an exception
        mock_set_relation.side_effect = Exception("Test error")
        
        # Should not crash but return None and emit error signal
        with patch.object(self.factory, 'error_occurred') as mock_signal:
            model = self.factory.create_category_model()
            
            # Model should be None
            self.assertIsNone(model)
            
            # Error signal should be emitted
            mock_signal.emit.assert_called_once()
            self.assertIn("Error setting up relations", mock_signal.emit.call_args[0][0])
    
    @patch('PySide6.QtSql.QSqlTableModel.select')
    def test_select_error_handling(self, mock_select):
        """Test error handling when selecting data."""
        # Make select return False (error)
        mock_select.return_value = False
        
        # Should not crash but return None and emit error signal
        with patch.object(self.factory, 'error_occurred') as mock_signal:
            model = self.factory.create_tag_model()
            
            # Model should be None
            self.assertIsNone(model)
            
            # Error signal should be emitted
            mock_signal.emit.assert_called_once()
            self.assertIn("Error loading data", mock_signal.emit.call_args[0][0])
    
    def test_nonexistent_table(self):
        """Test creating a model for a non-existent table."""
        # Should return None and emit error signal
        with patch.object(self.factory, 'error_occurred') as mock_signal:
            model = self.factory.create_filtered_model("NonExistentTable", "")
            
            # Model should be None
            self.assertIsNone(model)
            
            # Error signal should be emitted
            mock_signal.emit.assert_called_once()
            self.assertIn("Error creating model", mock_signal.emit.call_args[0][0])


if __name__ == "__main__":
    unittest.main() 