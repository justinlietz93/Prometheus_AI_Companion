"""
Tag Model for the Prometheus AI Prompt Generator.

This module contains the Tag class which represents a tag entity in the application.
Tags are used to categorize and organize prompts.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt6.QtSql import QSqlQuery, QSqlError

class Tag(QObject):
    """
    Represents a tag in the Prometheus system.
    
    The Tag class encapsulates all data and operations related to tags,
    including validation, database operations, and signal notifications.
    """
    
    # Define signals for change notifications
    changed = pyqtSignal()
    error = pyqtSignal(str)
    saved = pyqtSignal()
    
    def __init__(self, parent=None, tag_id=None):
        """
        Initialize a Tag object.
        
        Args:
            parent: The parent QObject
            tag_id: Optional tag ID to load from database
        """
        super().__init__(parent)
        
        # Initialize properties
        self._id = None
        self._name = ""
        self._color = "#6c757d"  # Default gray color
        self._description = ""
        self._original_name = ""  # For duplicate name checking
        
        # Load tag if ID provided
        if tag_id is not None:
            self.load(tag_id)
    
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
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        if value != self._color:
            self._color = value
            self.changed.emit()
    
    @pyqtProperty(str)
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if value != self._description:
            self._description = value
            self.changed.emit()
    
    @pyqtSlot(result=bool)
    def validate(self):
        """
        Validate the tag data.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Name is required and must be between 1 and 50 characters
        if not self._name or len(self._name) > 50:
            self.error.emit(self.tr("Tag name must be between 1 and 50 characters"))
            return False
        
        # Check for duplicate name
        if self._id is None or self._name != self._original_name:
            query = QSqlQuery()
            query.prepare("SELECT COUNT(*) FROM Tags WHERE name = ? AND id != ?")
            query.addBindValue(self._name)
            query.addBindValue(self._id if self._id is not None else -1)
            
            if not query.exec() or not query.next():
                self.error.emit(self.tr("Failed to check for duplicate tag names"))
                return False
            
            if query.value(0) > 0:
                self.error.emit(self.tr("A tag with this name already exists"))
                return False
        
        # Description should not exceed 255 characters
        if self._description and len(self._description) > 255:
            self.error.emit(self.tr("Description cannot exceed 255 characters"))
            return False
        
        return True
    
    @pyqtSlot(int, result=bool)
    def load(self, tag_id):
        """
        Load a tag from the database by ID.
        
        Args:
            tag_id: The ID of the tag to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT id, name, color, description
            FROM Tags
            WHERE id = ?
        """)
        query.addBindValue(tag_id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load tag: ") + query.lastError().text())
            return False
        
        if query.next():
            self._id = query.value(0)
            self._name = query.value(1)
            self._original_name = self._name  # Store for duplicate check
            self._color = query.value(2) if query.value(2) else "#6c757d"
            self._description = query.value(3) if query.value(3) else ""
            
            self.changed.emit()
            return True
        else:
            self.error.emit(self.tr("Tag not found"))
            return False
    
    @pyqtSlot(result=bool)
    def save(self):
        """
        Save the tag to the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.validate():
            return False
        
        query = QSqlQuery()
        
        if self._id is None:
            # Insert new tag
            query.prepare("""
                INSERT INTO Tags (name, color, description)
                VALUES (?, ?, ?)
            """)
            query.addBindValue(self._name)
            query.addBindValue(self._color)
            query.addBindValue(self._description)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to create tag: ") + query.lastError().text())
                return False
            
            # Get the new ID
            self._id = query.lastInsertId()
        else:
            # Update existing tag
            query.prepare("""
                UPDATE Tags
                SET name = ?, color = ?, description = ?
                WHERE id = ?
            """)
            query.addBindValue(self._name)
            query.addBindValue(self._color)
            query.addBindValue(self._description)
            query.addBindValue(self._id)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to update tag: ") + query.lastError().text())
                return False
        
        # Update the original name after successful save
        self._original_name = self._name
        
        self.saved.emit()
        return True
    
    @pyqtSlot(result=bool)
    def delete(self):
        """
        Delete the tag from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._id is None:
            self.error.emit(self.tr("Cannot delete unsaved tag"))
            return False
        
        # Begin transaction
        query = QSqlQuery()
        if not query.exec("BEGIN TRANSACTION"):
            self.error.emit(self.tr("Failed to begin transaction: ") + query.lastError().text())
            return False
        
        # Check if tag is in use
        query.prepare("SELECT COUNT(*) FROM PromptTags WHERE tag_id = ?")
        query.addBindValue(self._id)
        
        if not query.exec() or not query.next():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to check if tag is in use: ") + query.lastError().text())
            return False
        
        if query.value(0) > 0:
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Cannot delete tag because it is associated with prompts"))
            return False
        
        # Delete the tag
        query.prepare("DELETE FROM Tags WHERE id = ?")
        query.addBindValue(self._id)
        
        if not query.exec():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to delete tag: ") + query.lastError().text())
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
        self._color = "#6c757d"
        self._description = ""
        
        self.changed.emit()
        return True
    
    @pyqtSlot(result=list)
    def get_associated_prompts(self):
        """
        Get the list of prompts associated with this tag.
        
        Returns:
            list: List of prompt IDs associated with this tag
        """
        if self._id is None:
            return []
        
        prompt_ids = []
        query = QSqlQuery()
        query.prepare("""
            SELECT prompt_id
            FROM PromptTags
            WHERE tag_id = ?
        """)
        query.addBindValue(self._id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to get associated prompts: ") + query.lastError().text())
            return []
        
        while query.next():
            prompt_ids.append(query.value(0))
        
        return prompt_ids
    
    @staticmethod
    def get_all_tags():
        """
        Get all tags from the database.
        
        Returns:
            list: List of dictionaries with tag data
        """
        tags = []
        query = QSqlQuery("SELECT id, name, color, description FROM Tags ORDER BY name")
        
        if not query.exec():
            return []
        
        while query.next():
            tags.append({
                'id': query.value(0),
                'name': query.value(1),
                'color': query.value(2) if query.value(2) else "#6c757d",
                'description': query.value(3) if query.value(3) else ""
            })
        
        return tags
    
    @staticmethod
    def search_tags(search_term):
        """
        Search for tags by name.
        
        Args:
            search_term: The search term to look for in tag names
            
        Returns:
            list: List of dictionaries with tag data
        """
        tags = []
        query = QSqlQuery()
        query.prepare("SELECT id, name, color, description FROM Tags WHERE name LIKE ? ORDER BY name")
        query.addBindValue(f"%{search_term}%")
        
        if not query.exec():
            return []
        
        while query.next():
            tags.append({
                'id': query.value(0),
                'name': query.value(1),
                'color': query.value(2) if query.value(2) else "#6c757d",
                'description': query.value(3) if query.value(3) else ""
            })
        
        return tags 