"""
Unit tests for the Prompt model in the Prometheus AI Prompt Generator.

This module contains tests for all Prompt model functionality including
CRUD operations, validation, and tag relationship management.
"""

import unittest
from datetime import datetime

from PyQt6.QtCore import QDateTime

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import Prompt


class TestPrompt(ModelTestBase):
    """Test case for the Prompt model."""
    
    def test_load_prompt(self):
        """Test loading an existing prompt from the database."""
        # Load a prompt that exists in test data
        prompt = Prompt(None, 1)
        
        # Verify loaded data
        self.assertEqual(prompt.id, 1)
        self.assertEqual(prompt.title, "Test Prompt 1")
        self.assertEqual(prompt.content, "Content for test prompt 1")
        self.assertEqual(prompt.description, "A test prompt")
        self.assertTrue(prompt.is_public)
        self.assertFalse(prompt.is_featured)
        self.assertFalse(prompt.is_custom)
        self.assertEqual(prompt.category_id, 1)
        
        # Check tags were loaded
        self.assertEqual(len(prompt.tags), 2)
        tag_ids = [tag['id'] for tag in prompt.tags]
        self.assertIn(1, tag_ids)  # python tag
        self.assertIn(2, tag_ids)  # database tag
    
    def test_load_nonexistent_prompt(self):
        """Test attempt to load a non-existent prompt."""
        # Trying to load a prompt that doesn't exist
        prompt = Prompt()
        result = prompt.load(999)  # Non-existent ID
        
        # Should return False and emit error signal
        self.assertFalse(result)
        
        # ID should still be None
        self.assertIsNone(prompt.id)
    
    def test_create_prompt(self):
        """Test creating a new prompt."""
        # Create a new prompt
        prompt = Prompt()
        prompt.title = "New Test Prompt"
        prompt.content = "This is content for a new test prompt"
        prompt.description = "New prompt description"
        prompt.is_public = True
        prompt.is_featured = True
        prompt.is_custom = False
        prompt.category_id = 2
        
        # Save to database
        result = prompt.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # ID should be set after save
        self.assertIsNotNone(prompt.id)
        
        # Verify the prompt was saved to the database
        self.assert_row_exists("Prompts", "title = ?", ["New Test Prompt"])
    
    def test_update_prompt(self):
        """Test updating an existing prompt."""
        # Load an existing prompt
        prompt = Prompt(None, 1)
        
        # Update fields
        prompt.title = "Updated Title"
        prompt.content = "Updated content"
        prompt.is_featured = True
        
        # Save changes
        result = prompt.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # Verify changes in database
        self.assert_row_exists("Prompts", "id = 1 AND title = ? AND content = ? AND is_featured = 1",
                              ["Updated Title", "Updated content"])
    
    def test_delete_prompt(self):
        """Test deleting a prompt."""
        # Load a prompt to delete
        prompt = Prompt(None, 2)
        
        # Initial tag count for this prompt
        initial_tag_count = self.assert_row_exists("PromptTags", "prompt_id = 2")
        
        # Delete it
        result = prompt.delete()
        
        # Should delete successfully
        self.assertTrue(result)
        
        # Verify it's gone from database
        query = self.execute_query("SELECT COUNT(*) FROM Prompts WHERE id = 2")
        query.next()
        self.assertEqual(query.value(0), 0)
        
        # Verify prompt tags were also deleted
        query = self.execute_query("SELECT COUNT(*) FROM PromptTags WHERE prompt_id = 2")
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_validate_prompt_title(self):
        """Test validation of prompt title."""
        prompt = Prompt()
        
        # Empty title should fail validation
        prompt.title = ""
        prompt.content = "Valid content"
        self.assertFalse(prompt.validate())
        
        # Too short title should fail
        prompt.title = "AB"  # Less than 3 chars
        self.assertFalse(prompt.validate())
        
        # Too long title should fail
        prompt.title = "A" * 101  # More than 100 chars
        self.assertFalse(prompt.validate())
        
        # Valid title should pass
        prompt.title = "Valid Title"
        self.assertTrue(prompt.validate())
    
    def test_validate_prompt_content(self):
        """Test validation of prompt content."""
        prompt = Prompt()
        prompt.title = "Valid Title"
        
        # Empty content should fail validation
        prompt.content = ""
        self.assertFalse(prompt.validate())
        
        # Valid content should pass
        prompt.content = "This is valid content"
        self.assertTrue(prompt.validate())
    
    def test_validate_prompt_description(self):
        """Test validation of prompt description."""
        prompt = Prompt()
        prompt.title = "Valid Title"
        prompt.content = "Valid Content"
        
        # Empty description should pass (it's optional)
        prompt.description = ""
        self.assertTrue(prompt.validate())
        
        # Valid description should pass
        prompt.description = "This is a valid description"
        self.assertTrue(prompt.validate())
        
        # Too long description should fail
        prompt.description = "A" * 501  # More than 500 chars
        self.assertFalse(prompt.validate())
    
    def test_add_remove_tags(self):
        """Test adding and removing tags from a prompt."""
        # Load a prompt
        prompt = Prompt(None, 1)
        initial_tag_count = len(prompt.tags)
        
        # Add a new tag
        prompt.add_tag(3)  # AI tag
        
        # Tag count should increase
        self.assertEqual(len(prompt.tags), initial_tag_count + 1)
        
        # Tag should be in the list
        tag_ids = [tag['id'] for tag in prompt.tags]
        self.assertIn(3, tag_ids)
        
        # Save changes
        result = prompt.save()
        self.assertTrue(result)
        
        # Verify in database
        self.assert_row_exists("PromptTags", "prompt_id = 1 AND tag_id = 3")
        
        # Remove a tag
        prompt.remove_tag(1)  # Remove Python tag
        
        # Tag count should decrease
        self.assertEqual(len(prompt.tags), initial_tag_count)
        
        # Tag should not be in the list
        tag_ids = [tag['id'] for tag in prompt.tags]
        self.assertNotIn(1, tag_ids)
        
        # Save changes
        result = prompt.save()
        self.assertTrue(result)
        
        # Verify in database
        query = self.execute_query("SELECT COUNT(*) FROM PromptTags WHERE prompt_id = 1 AND tag_id = 1")
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_set_tags(self):
        """Test setting all tags at once."""
        # Load a prompt
        prompt = Prompt(None, 1)
        
        # Set completely new tags
        new_tags = [
            {'id': 3, 'name': 'ai'},
            {'id': 4, 'name': 'beginner'}
        ]
        prompt.set_tags(new_tags)
        
        # Tag count should match new tags
        self.assertEqual(len(prompt.tags), len(new_tags))
        
        # Tags should match new set
        tag_ids = [tag['id'] for tag in prompt.tags]
        self.assertIn(3, tag_ids)
        self.assertIn(4, tag_ids)
        self.assertNotIn(1, tag_ids)  # Old tag should be gone
        
        # Save changes
        result = prompt.save()
        self.assertTrue(result)
        
        # Verify in database
        self.assert_row_exists("PromptTags", "prompt_id = 1 AND tag_id = 3")
        self.assert_row_exists("PromptTags", "prompt_id = 1 AND tag_id = 4")
        
        # Old tags should be gone
        query = self.execute_query("SELECT COUNT(*) FROM PromptTags WHERE prompt_id = 1 AND tag_id = 1")
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_dates(self):
        """Test created_date and modified_date functionality."""
        # Create a new prompt
        prompt = Prompt()
        prompt.title = "Date Test Prompt"
        prompt.content = "Testing dates"
        
        # Dates should be set automatically
        self.assertIsInstance(prompt.created_date, QDateTime)
        self.assertIsInstance(prompt.modified_date, QDateTime)
        
        # Convert to Python datetime for easier comparison
        created_dt = prompt.created_date.toPython()
        self.assertIsInstance(created_dt, datetime)
        
        # Make sure the date is recent (within last minute)
        now = datetime.now()
        diff = now - created_dt
        self.assertLess(diff.total_seconds(), 60)
        
        # Save prompt
        prompt.save()
        
        # Get the creation timestamp
        original_modified = prompt.modified_date
        
        # Wait a moment to ensure timestamp would change
        import time
        time.sleep(0.1)
        
        # Update the prompt
        prompt.content = "Updated content for date test"
        prompt.save()
        
        # Modified date should have changed
        self.assertNotEqual(original_modified, prompt.modified_date)


if __name__ == "__main__":
    unittest.main() 