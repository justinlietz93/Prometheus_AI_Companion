"""
Unit tests for the Category model in the Prometheus AI Prompt Generator.

This module contains tests for all Category model functionality including
CRUD operations, validation, hierarchy management, and circular reference prevention.
"""

import unittest

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import Category


class TestCategory(ModelTestBase):
    """Test case for the Category model."""
    
    def test_load_category(self):
        """Test loading an existing category from the database."""
        # Load a category that exists in test data
        category = Category(None, 1)
        
        # Verify loaded data
        self.assertEqual(category.id, 1)
        self.assertEqual(category.name, "AI Tools")
        self.assertEqual(category.description, "Prompts for various AI tools and platforms")
        self.assertIsNone(category.parent_id)  # Root category
    
    def test_load_nonexistent_category(self):
        """Test attempt to load a non-existent category."""
        # Trying to load a category that doesn't exist
        category = Category()
        result = category.load(999)  # Non-existent ID
        
        # Should return False
        self.assertFalse(result)
        
        # ID should still be None
        self.assertIsNone(category.id)
    
    def test_create_category(self):
        """Test creating a new category."""
        # Create a new category
        category = Category()
        category.name = "Test Category"
        category.description = "A test category"
        category.display_order = 5
        
        # Save to database
        result = category.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # ID should be set after save
        self.assertIsNotNone(category.id)
        
        # Verify the category was saved to the database
        self.assert_row_exists("Categories", "name = ?", ["Test Category"])
    
    def test_create_child_category(self):
        """Test creating a category with a parent."""
        # Create a child category under "AI Tools" (id=1)
        category = Category()
        category.name = "Child Category"
        category.description = "A child category"
        category.parent_id = 1
        
        # Save to database
        result = category.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # Verify parent relationship in database
        self.assert_row_exists("Categories", "name = ? AND parent_id = ?", 
                              ["Child Category", 1])
    
    def test_update_category(self):
        """Test updating an existing category."""
        # Load an existing category
        category = Category(None, 1)
        
        # Update fields
        category.name = "Updated Category"
        category.icon = "new_icon.png"
        
        # Save changes
        result = category.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # Verify changes in database
        self.assert_row_exists("Categories", "id = 1 AND name = ? AND icon = ?",
                              ["Updated Category", "new_icon.png"])
    
    def test_delete_category(self):
        """Test deleting a category that has no prompts or children."""
        # Create a new category that has no prompts
        category = Category()
        category.name = "Disposable Category"
        category.save()
        
        category_id = category.id
        
        # Delete it
        result = category.delete()
        
        # Should delete successfully
        self.assertTrue(result)
        
        # Verify it's gone from database
        query = self.execute_query("SELECT COUNT(*) FROM Categories WHERE id = ?", [category_id])
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_cant_delete_category_with_prompts(self):
        """Test that a category can't be deleted if it has prompts."""
        # Load a category that has prompts (id=1)
        category = Category(None, 1)
        
        # Try to delete it
        result = category.delete()
        
        # Should fail
        self.assertFalse(result)
        
        # Should still exist in database
        self.assert_row_exists("Categories", "id = 1")
    
    def test_cant_delete_category_with_children(self):
        """Test that a category can't be deleted if it has children."""
        # First create a parent and child
        parent = Category()
        parent.name = "Parent Category"
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Try to delete the parent
        result = parent.delete()
        
        # Should fail
        self.assertFalse(result)
        
        # Should still exist in database
        self.assert_row_exists("Categories", "id = ?", [parent.id])
    
    def test_validate_category_name(self):
        """Test validation of category name."""
        category = Category()
        
        # Empty name should fail validation
        category.name = ""
        self.assertFalse(category.validate())
        
        # Too long name should fail
        category.name = "A" * 101  # More than 100 chars
        self.assertFalse(category.validate())
        
        # Valid name should pass
        category.name = "Valid Category Name"
        self.assertTrue(category.validate())
    
    def test_validate_duplicate_name(self):
        """Test validation rejects duplicate category names within the same parent."""
        # "AI Tools" already exists as a root category
        category = Category()
        category.name = "AI Tools"  # Duplicate at root level
        
        # Should fail validation due to duplicate name
        self.assertFalse(category.validate())
        
        # Create a child with same name but different parent - this should be valid
        category = Category()
        category.name = "AI Tools"
        category.parent_id = 3  # Different parent
        
        # Should pass validation (unique within parent)
        self.assertTrue(category.validate())
    
    def test_validate_circular_reference(self):
        """Test validation prevents circular parent references."""
        # Create a parent category
        parent = Category()
        parent.name = "Parent Category"
        parent.save()
        
        # Create a child category
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Try to set child as parent's parent
        parent.parent_id = child.id
        
        # Should fail validation
        self.assertFalse(parent.validate())
    
    def test_deeper_circular_reference(self):
        """Test validation prevents deeper circular parent references."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent Category"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent Category"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Try to create a circular reference
        grandparent.parent_id = child.id
        
        # Should fail validation
        self.assertFalse(grandparent.validate())
    
    def test_get_children(self):
        """Test getting children of a category."""
        # Create a parent with multiple children
        parent = Category()
        parent.name = "Parent with Children"
        parent.save()
        
        child1 = Category()
        child1.name = "Child 1"
        child1.parent_id = parent.id
        child1.save()
        
        child2 = Category()
        child2.name = "Child 2"
        child2.parent_id = parent.id
        child2.save()
        
        # Get children
        children = parent.get_children()
        
        # Should have 2 children
        self.assertEqual(len(children), 2)
        
        # Check children's IDs
        child_ids = [c.id for c in children]
        self.assertIn(child1.id, child_ids)
        self.assertIn(child2.id, child_ids)
    
    def test_get_parent(self):
        """Test getting parent of a category."""
        # Create a parent and child
        parent = Category()
        parent.name = "Parent Category"
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Get parent of child
        retrieved_parent = child.get_parent()
        
        # Should be the correct parent
        self.assertIsNotNone(retrieved_parent)
        self.assertEqual(retrieved_parent.id, parent.id)
        self.assertEqual(retrieved_parent.name, "Parent Category")
    
    def test_get_ancestors(self):
        """Test getting all ancestors of a category."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent Category"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent Category"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Get ancestors of child
        ancestors = child.get_ancestors()
        
        # Should have 2 ancestors (parent and grandparent)
        self.assertEqual(len(ancestors), 2)
        
        # Check ancestors' IDs from nearest to furthest
        self.assertEqual(ancestors[0].id, parent.id)
        self.assertEqual(ancestors[1].id, grandparent.id)
    
    def test_get_descendants(self):
        """Test getting all descendants of a category."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent Category"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent Category"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Get descendants of grandparent
        descendants = grandparent.get_descendants()
        
        # Should have 2 descendants (parent and child)
        self.assertEqual(len(descendants), 2)
        
        # Check descendants include parent and child
        descendant_ids = [d.id for d in descendants]
        self.assertIn(parent.id, descendant_ids)
        self.assertIn(child.id, descendant_ids)
    
    def test_is_ancestor_of(self):
        """Test checking if a category is an ancestor of another."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent Category"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent Category"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Check if grandparent is ancestor of child
        self.assertTrue(grandparent.is_ancestor_of(child))
        
        # Parent should be ancestor of child
        self.assertTrue(parent.is_ancestor_of(child))
        
        # Child should not be ancestor of parent
        self.assertFalse(child.is_ancestor_of(parent))
        
        # Category should not be its own ancestor
        self.assertFalse(child.is_ancestor_of(child))
    
    def test_is_descendant_of(self):
        """Test checking if a category is a descendant of another."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent Category"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent Category"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child Category"
        child.parent_id = parent.id
        child.save()
        
        # Check if child is descendant of grandparent
        self.assertTrue(child.is_descendant_of(grandparent))
        
        # Child should be descendant of parent
        self.assertTrue(child.is_descendant_of(parent))
        
        # Parent should not be descendant of child
        self.assertFalse(parent.is_descendant_of(child))
        
        # Category should not be its own descendant
        self.assertFalse(child.is_descendant_of(child))
    
    def test_get_root_categories(self):
        """Test getting all root categories."""
        # Get root categories
        roots = Category.get_root_categories()
        
        # Should have at least the root categories from test data
        self.assertGreaterEqual(len(roots), 1)
        
        # All should have parent_id as None
        for root in roots:
            self.assertIsNone(root.parent_id)
    
    def test_get_full_path(self):
        """Test getting the full path of a category."""
        # Create a three-level hierarchy
        grandparent = Category()
        grandparent.name = "Grandparent"
        grandparent.save()
        
        parent = Category()
        parent.name = "Parent"
        parent.parent_id = grandparent.id
        parent.save()
        
        child = Category()
        child.name = "Child"
        child.parent_id = parent.id
        child.save()
        
        # Get full path of child
        path = child.get_full_path()
        
        # Path should be "Grandparent > Parent > Child"
        self.assertEqual(path, "Grandparent > Parent > Child")
        
        # Root category should just return its own name
        self.assertEqual(grandparent.get_full_path(), "Grandparent")


if __name__ == "__main__":
    unittest.main() 