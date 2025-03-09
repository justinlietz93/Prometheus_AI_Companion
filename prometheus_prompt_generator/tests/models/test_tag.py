"""
Unit tests for the Tag model in the Prometheus AI Prompt Generator.

This module contains tests for all Tag model functionality including
CRUD operations, validation, and relationship verification.
"""

import unittest

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import Tag


class TestTag(ModelTestBase):
    """Test case for the Tag model."""
    
    def test_load_tag(self):
        """Test loading an existing tag from the database."""
        # Load a tag that exists in test data
        tag = Tag(None, 1)
        
        # Verify loaded data
        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.name, "python")
        self.assertEqual(tag.color, "#3776AB")
        self.assertEqual(tag.description, "Python programming language")
    
    def test_load_nonexistent_tag(self):
        """Test attempt to load a non-existent tag."""
        # Trying to load a tag that doesn't exist
        tag = Tag()
        result = tag.load(999)  # Non-existent ID
        
        # Should return False and emit error signal
        self.assertFalse(result)
        
        # ID should still be None
        self.assertIsNone(tag.id)
    
    def test_create_tag(self):
        """Test creating a new tag."""
        # Create a new tag
        tag = Tag()
        tag.name = "new_tag"
        tag.color = "#FF5500"
        tag.description = "A new test tag"
        
        # Save to database
        result = tag.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # ID should be set after save
        self.assertIsNotNone(tag.id)
        
        # Verify the tag was saved to the database
        self.assert_row_exists("Tags", "name = ?", ["new_tag"])
    
    def test_update_tag(self):
        """Test updating an existing tag."""
        # Load an existing tag
        tag = Tag(None, 1)
        
        # Update fields
        tag.name = "python_updated"
        tag.color = "#4B8BBE"
        
        # Save changes
        result = tag.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # Verify changes in database
        self.assert_row_exists("Tags", "id = 1 AND name = ? AND color = ?",
                              ["python_updated", "#4B8BBE"])
    
    def test_delete_tag(self):
        """Test deleting a tag that isn't associated with prompts."""
        # We first need to create a new tag that isn't used by prompts
        tag = Tag()
        tag.name = "disposable_tag"
        tag.save()
        
        tag_id = tag.id
        
        # Delete it
        result = tag.delete()
        
        # Should delete successfully
        self.assertTrue(result)
        
        # Verify it's gone from database
        query = self.execute_query("SELECT COUNT(*) FROM Tags WHERE id = ?", [tag_id])
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_cant_delete_tag_with_prompts(self):
        """Test that a tag can't be deleted if it's associated with prompts."""
        # Load a tag that's used by prompts (python tag, id=1)
        tag = Tag(None, 1)
        
        # Delete should fail
        result = tag.delete()
        
        # Should return false
        self.assertFalse(result)
        
        # Tag should still exist in database
        self.assert_row_exists("Tags", "id = 1")
    
    def test_validate_tag_name(self):
        """Test validation of tag name."""
        tag = Tag()
        
        # Empty name should fail validation
        tag.name = ""
        self.assertFalse(tag.validate())
        
        # Too long name should fail
        tag.name = "A" * 51  # More than 50 chars
        self.assertFalse(tag.validate())
        
        # Valid name should pass
        tag.name = "valid_tag_name"
        self.assertTrue(tag.validate())
    
    def test_validate_duplicate_name(self):
        """Test validation rejects duplicate tag names."""
        # First tag with name "python" already exists in test data
        tag = Tag()
        tag.name = "python"
        
        # Should fail validation due to duplicate name
        self.assertFalse(tag.validate())
        
        # Different name should pass
        tag.name = "unique_tag_name"
        self.assertTrue(tag.validate())
    
    def test_validate_description_length(self):
        """Test validation of description length."""
        tag = Tag()
        tag.name = "valid_tag_name"
        
        # Empty description should pass (it's optional)
        tag.description = ""
        self.assertTrue(tag.validate())
        
        # Valid description should pass
        tag.description = "This is a valid description"
        self.assertTrue(tag.validate())
        
        # Too long description should fail
        tag.description = "A" * 256  # More than 255 chars
        self.assertFalse(tag.validate())
    
    def test_get_associated_prompts(self):
        """Test getting prompts associated with a tag."""
        # Load a tag used by prompts (python tag, id=1)
        tag = Tag(None, 1)
        
        # Get associated prompts
        prompt_ids = tag.get_associated_prompts()
        
        # Should return at least one prompt
        self.assertGreater(len(prompt_ids), 0)
        
        # First prompt should be associated
        self.assertIn(1, prompt_ids)
    
    def test_get_all_tags(self):
        """Test getting all tags."""
        # Get all tags
        tags = Tag.get_all_tags()
        
        # Should have at least the tags from test data
        self.assertGreaterEqual(len(tags), 4)
        
        # Check structure of returned data
        first_tag = tags[0]
        self.assertIn('id', first_tag)
        self.assertIn('name', first_tag)
        self.assertIn('color', first_tag)
        self.assertIn('description', first_tag)
    
    def test_search_tags(self):
        """Test searching for tags."""
        # Search for python tag
        tags = Tag.search_tags("python")
        
        # Should find at least one tag
        self.assertGreater(len(tags), 0)
        
        # First result should be the python tag
        self.assertEqual(tags[0]['name'], "python")
        
        # Search for non-existent tag
        tags = Tag.search_tags("nonexistent_tag_name")
        
        # Should return empty list
        self.assertEqual(len(tags), 0)


if __name__ == "__main__":
    unittest.main() 