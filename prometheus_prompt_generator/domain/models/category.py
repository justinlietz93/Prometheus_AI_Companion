"""
Category Model for the Prometheus AI Prompt Generator.

This module contains the Category class which represents a category entity 
in the application with hierarchical structure support.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt6.QtSql import QSqlQuery, QSqlError

class Category(QObject):
    """
    Represents a category in the Prometheus system with hierarchical structure.
    
    The Category class encapsulates all data and operations related to categories,
    including validation, database operations, signal notifications, and hierarchy
    management (parent-child relationships).
    """
    
    # Define signals for change notifications
    changed = pyqtSignal()
    error = pyqtSignal(str)
    saved = pyqtSignal()
    
    def __init__(self, parent=None, category_id=None):
        """
        Initialize a Category object.
        
        Args:
            parent: The parent QObject
            category_id: Optional category ID to load from database
        """
        super().__init__(parent)
        
        # Initialize properties
        self._id = None
        self._name = ""
        self._description = ""
        self._parent_id = None
        self._display_order = 0
        self._icon = ""
        self._original_name = ""  # For duplicate name checking
        
        # Load category if ID provided
        if category_id is not None:
            self.load(category_id)
    
    # Property getters and setters
    @pyqtProperty(int)
    def id(self):
        return self._id
    
    @pyqtProperty(str)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if value != self._name:
            self._name = value
            self.changed.emit()
    
    @pyqtProperty(str)
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if value != self._description:
            self._description = value
            self.changed.emit()
    
    @pyqtProperty(int)
    def parent_id(self):
        return self._parent_id
    
    @parent_id.setter
    def parent_id(self, value):
        if value != self._parent_id:
            self._parent_id = value
            self.changed.emit()
    
    @pyqtProperty(int)
    def display_order(self):
        return self._display_order
    
    @display_order.setter
    def display_order(self, value):
        if value != self._display_order:
            self._display_order = value
            self.changed.emit()
    
    @pyqtProperty(str)
    def icon(self):
        return self._icon
    
    @icon.setter
    def icon(self, value):
        if value != self._icon:
            self._icon = value
            self.changed.emit()
    
    @pyqtSlot(result=bool)
    def validate(self):
        """
        Validate the category data.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Name is required and must be between 1 and 100 characters
        if not self._name or len(self._name) > 100:
            self.error.emit(self.tr("Category name must be between 1 and 100 characters"))
            return False
        
        # Check for duplicate name within the same parent
        if self._id is None or self._name != self._original_name:
            query = QSqlQuery()
            query.prepare("""
                SELECT COUNT(*) FROM Categories 
                WHERE name = ? AND parent_id IS ? AND id != ?
            """)
            query.addBindValue(self._name)
            query.addBindValue(self._parent_id)  # This correctly handles NULL values
            query.addBindValue(self._id if self._id is not None else -1)
            
            if not query.exec() or not query.next():
                self.error.emit(self.tr("Failed to check for duplicate category names"))
                return False
            
            if query.value(0) > 0:
                self.error.emit(self.tr("A category with this name already exists at this level"))
                return False
        
        # Description should not exceed 500 characters
        if self._description and len(self._description) > 500:
            self.error.emit(self.tr("Description cannot exceed 500 characters"))
            return False
        
        # Check for circular references in hierarchy
        if self._parent_id is not None and self._id is not None:
            if self._parent_id == self._id:
                self.error.emit(self.tr("A category cannot be its own parent"))
                return False
            
            # Check if any of this category's descendants is set as its parent
            descendants = self.get_descendants()
            if self._parent_id in descendants:
                self.error.emit(self.tr("Cannot set a descendant as the parent (circular reference)"))
                return False
        
        return True
    
    @pyqtSlot(int, result=bool)
    def load(self, category_id):
        """
        Load a category from the database by ID.
        
        Args:
            category_id: The ID of the category to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            WHERE id = ?
        """)
        query.addBindValue(category_id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load category: ") + query.lastError().text())
            return False
        
        if query.next():
            self._id = query.value(0)
            self._name = query.value(1)
            self._original_name = self._name  # Store for duplicate check
            self._description = query.value(2) if query.value(2) else ""
            self._parent_id = query.value(3)  # This will be None if the database value is NULL
            self._display_order = query.value(4)
            self._icon = query.value(5) if query.value(5) else ""
            
            self.changed.emit()
            return True
        else:
            self.error.emit(self.tr("Category not found"))
            return False
    
    @pyqtSlot(result=bool)
    def save(self):
        """
        Save the category to the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.validate():
            return False
        
        query = QSqlQuery()
        
        if self._id is None:
            # Insert new category
            query.prepare("""
                INSERT INTO Categories (name, description, parent_id, display_order, icon)
                VALUES (?, ?, ?, ?, ?)
            """)
            query.addBindValue(self._name)
            query.addBindValue(self._description)
            query.addBindValue(self._parent_id)  # This correctly handles NULL values
            query.addBindValue(self._display_order)
            query.addBindValue(self._icon)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to create category: ") + query.lastError().text())
                return False
            
            # Get the new ID
            self._id = query.lastInsertId()
        else:
            # Update existing category
            query.prepare("""
                UPDATE Categories
                SET name = ?, description = ?, parent_id = ?, display_order = ?, icon = ?
                WHERE id = ?
            """)
            query.addBindValue(self._name)
            query.addBindValue(self._description)
            query.addBindValue(self._parent_id)  # This correctly handles NULL values
            query.addBindValue(self._display_order)
            query.addBindValue(self._icon)
            query.addBindValue(self._id)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to update category: ") + query.lastError().text())
                return False
        
        # Update the original name after successful save
        self._original_name = self._name
        
        self.saved.emit()
        return True
    
    @pyqtSlot(result=bool)
    def delete(self):
        """
        Delete the category from the database.
        
        This operation will only succeed if the category has no children
        and is not associated with any prompts.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._id is None:
            self.error.emit(self.tr("Cannot delete unsaved category"))
            return False
        
        # Begin transaction
        query = QSqlQuery()
        if not query.exec("BEGIN TRANSACTION"):
            self.error.emit(self.tr("Failed to begin transaction: ") + query.lastError().text())
            return False
        
        # Check if category has children
        query.prepare("SELECT COUNT(*) FROM Categories WHERE parent_id = ?")
        query.addBindValue(self._id)
        
        if not query.exec() or not query.next():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to check for child categories: ") + query.lastError().text())
            return False
        
        if query.value(0) > 0:
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Cannot delete category because it has child categories"))
            return False
        
        # Check if category is associated with prompts
        query.prepare("SELECT COUNT(*) FROM Prompts WHERE category_id = ?")
        query.addBindValue(self._id)
        
        if not query.exec() or not query.next():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to check if category has prompts: ") + query.lastError().text())
            return False
        
        if query.value(0) > 0:
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Cannot delete category because it is associated with prompts"))
            return False
        
        # Delete the category
        query.prepare("DELETE FROM Categories WHERE id = ?")
        query.addBindValue(self._id)
        
        if not query.exec():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to delete category: ") + query.lastError().text())
            return False
        
        # Commit transaction
        if not query.exec("COMMIT"):
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to commit transaction: ") + query.lastError().text())
            return False
        
        # Reset the object
        self._id = None
        self._name = ""
        self._original_name = ""
        self._description = ""
        self._parent_id = None
        self._display_order = 0
        self._icon = ""
        
        self.changed.emit()
        return True
    
    @pyqtSlot(result=list)
    def get_children(self):
        """
        Get the direct child categories of this category.
        
        Returns:
            list: List of dictionaries with child category data
        """
        if self._id is None:
            return []
        
        children = []
        query = QSqlQuery()
        query.prepare("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            WHERE parent_id = ?
            ORDER BY display_order, name
        """)
        query.addBindValue(self._id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to get child categories: ") + query.lastError().text())
            return []
        
        while query.next():
            children.append({
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            })
        
        return children
    
    @pyqtSlot(result=object)
    def get_parent(self):
        """
        Get the parent category of this category.
        
        Returns:
            dict: Dictionary with parent category data or None if no parent
        """
        if self._id is None or self._parent_id is None:
            return None
        
        query = QSqlQuery()
        query.prepare("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            WHERE id = ?
        """)
        query.addBindValue(self._parent_id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to get parent category: ") + query.lastError().text())
            return None
        
        if query.next():
            return {
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            }
        
        return None
    
    @pyqtSlot(result=list)
    def get_ancestors(self):
        """
        Get all ancestor categories in order from parent to root.
        
        Returns:
            list: List of dictionaries with ancestor category data
        """
        if self._id is None or self._parent_id is None:
            return []
        
        ancestors = []
        current_parent_id = self._parent_id
        
        # Prevent infinite loops by limiting to a reasonable number of iterations
        max_iterations = 100
        iterations = 0
        
        query = QSqlQuery()
        
        while current_parent_id is not None and iterations < max_iterations:
            query.prepare("""
                SELECT id, name, description, parent_id, display_order, icon
                FROM Categories
                WHERE id = ?
            """)
            query.addBindValue(current_parent_id)
            
            if not query.exec() or not query.next():
                break
            
            ancestor = {
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            }
            
            ancestors.append(ancestor)
            current_parent_id = query.value(3)  # Next parent_id
            iterations += 1
        
        return ancestors
    
    @pyqtSlot(result=list)
    def get_descendants(self):
        """
        Get all descendant category IDs.
        
        Returns:
            list: List of descendant category IDs
        """
        if self._id is None:
            return []
        
        # Start with direct children
        descendants = []
        to_process = [self._id]
        processed = set()
        
        query = QSqlQuery()
        
        while to_process:
            current_id = to_process.pop(0)
            
            if current_id in processed:
                continue
            
            processed.add(current_id)
            
            # Skip the root category itself
            if current_id != self._id:
                descendants.append(current_id)
            
            # Get children of current category
            query.prepare("SELECT id FROM Categories WHERE parent_id = ?")
            query.addBindValue(current_id)
            
            if not query.exec():
                continue
            
            while query.next():
                child_id = query.value(0)
                if child_id not in processed:
                    to_process.append(child_id)
        
        return descendants
    
    @pyqtSlot(result=list)
    def get_associated_prompts(self):
        """
        Get the list of prompts associated with this category.
        
        Returns:
            list: List of prompt IDs associated with this category
        """
        if self._id is None:
            return []
        
        prompt_ids = []
        query = QSqlQuery()
        query.prepare("SELECT id FROM Prompts WHERE category_id = ?")
        query.addBindValue(self._id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to get associated prompts: ") + query.lastError().text())
            return []
        
        while query.next():
            prompt_ids.append(query.value(0))
        
        return prompt_ids
    
    @staticmethod
    def get_root_categories():
        """
        Get all top-level (root) categories.
        
        Returns:
            list: List of dictionaries with root category data
        """
        categories = []
        query = QSqlQuery("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            WHERE parent_id IS NULL
            ORDER BY display_order, name
        """)
        
        if not query.exec():
            return []
        
        while query.next():
            categories.append({
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            })
        
        return categories
    
    @staticmethod
    def get_category_path(category_id):
        """
        Get the full path of a category (all ancestors + the category itself).
        
        Args:
            category_id: The ID of the category
            
        Returns:
            list: List of dictionaries with category data in path order (root to leaf)
        """
        if category_id is None:
            return []
        
        path = []
        current_id = category_id
        
        # Prevent infinite loops
        max_iterations = 100
        iterations = 0
        
        query = QSqlQuery()
        
        while current_id is not None and iterations < max_iterations:
            query.prepare("""
                SELECT id, name, description, parent_id, display_order, icon
                FROM Categories
                WHERE id = ?
            """)
            query.addBindValue(current_id)
            
            if not query.exec() or not query.next():
                break
            
            category = {
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            }
            
            path.insert(0, category)  # Insert at beginning to maintain root->leaf order
            current_id = query.value(3)  # Next parent_id
            iterations += 1
        
        return path
    
    @staticmethod
    def search_categories(search_term):
        """
        Search for categories by name.
        
        Args:
            search_term: The search term to look for in category names
            
        Returns:
            list: List of dictionaries with category data
        """
        categories = []
        query = QSqlQuery()
        query.prepare("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            WHERE name LIKE ?
            ORDER BY name
        """)
        query.addBindValue(f"%{search_term}%")
        
        if not query.exec():
            return []
        
        while query.next():
            categories.append({
                'id': query.value(0),
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else ""
            })
        
        return categories
    
    @staticmethod
    def get_full_category_tree():
        """
        Get the complete category hierarchy as a nested dictionary structure.
        
        Returns:
            list: List of dictionaries with category data and children
        """
        # Get all categories
        query = QSqlQuery("""
            SELECT id, name, description, parent_id, display_order, icon
            FROM Categories
            ORDER BY display_order, name
        """)
        
        if not query.exec():
            return []
        
        # Build flat dictionary of all categories
        all_categories = {}
        while query.next():
            category_id = query.value(0)
            all_categories[category_id] = {
                'id': category_id,
                'name': query.value(1),
                'description': query.value(2) if query.value(2) else "",
                'parent_id': query.value(3),
                'display_order': query.value(4),
                'icon': query.value(5) if query.value(5) else "",
                'children': []
            }
        
        # Build tree structure
        root_categories = []
        for category_id, category in all_categories.items():
            parent_id = category['parent_id']
            if parent_id is None:
                # This is a root category
                root_categories.append(category)
            elif parent_id in all_categories:
                # Add to parent's children
                all_categories[parent_id]['children'].append(category)
        
        # Sort children by display_order and name
        def sort_children(categories):
            categories.sort(key=lambda x: (x['display_order'], x['name']))
            for category in categories:
                sort_children(category['children'])
        
        sort_children(root_categories)
        
        return root_categories 