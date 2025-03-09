"""
Prompt Model for the Prometheus AI Prompt Generator.

This module contains the Prompt class which represents a prompt entity
in the application along with its validation rules and CRUD operations.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QDateTime
from PyQt6.QtSql import QSqlQuery, QSqlError

class Prompt(QObject):
    """
    Represents an AI prompt in the Prometheus system.
    
    The Prompt class encapsulates all data and operations related to prompts,
    including validation, database operations, and signal notifications.
    """
    
    # Define signals for change notifications
    changed = pyqtSignal()
    error = pyqtSignal(str)
    saved = pyqtSignal()
    
    def __init__(self, parent=None, prompt_id=None):
        """
        Initialize a Prompt object.
        
        Args:
            parent: The parent QObject
            prompt_id: Optional prompt ID to load from database
        """
        super().__init__(parent)
        
        # Initialize properties
        self._id = None
        self._title = ""
        self._content = ""
        self._description = ""
        self._is_public = False
        self._is_featured = False
        self._is_custom = False
        self._category_id = None
        self._user_id = None
        self._created_date = QDateTime.currentDateTime()
        self._modified_date = QDateTime.currentDateTime()
        self._tags = []
        
        # Load prompt if ID provided
        if prompt_id is not None:
            self.load(prompt_id)
    
    # Property getters and setters
    @pyqtProperty(int)
    def id(self):
        return self._id
    
    @pyqtProperty(str)
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        if value != self._title:
            self._title = value
            self.changed.emit()
    
    @pyqtProperty(str)
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        if value != self._content:
            self._content = value
            self.changed.emit()
    
    @pyqtProperty(str)
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if value != self._description:
            self._description = value
            self.changed.emit()
    
    @pyqtProperty(bool)
    def is_public(self):
        return self._is_public
    
    @is_public.setter
    def is_public(self, value):
        if value != self._is_public:
            self._is_public = value
            self.changed.emit()
    
    @pyqtProperty(bool)
    def is_featured(self):
        return self._is_featured
    
    @is_featured.setter
    def is_featured(self, value):
        if value != self._is_featured:
            self._is_featured = value
            self.changed.emit()
    
    @pyqtProperty(bool)
    def is_custom(self):
        return self._is_custom
    
    @is_custom.setter
    def is_custom(self, value):
        if value != self._is_custom:
            self._is_custom = value
            self.changed.emit()
    
    @pyqtProperty(int)
    def category_id(self):
        return self._category_id
    
    @category_id.setter
    def category_id(self, value):
        if value != self._category_id:
            self._category_id = value
            self.changed.emit()
    
    @pyqtProperty(QDateTime)
    def created_date(self):
        return self._created_date
    
    @pyqtProperty(QDateTime)
    def modified_date(self):
        return self._modified_date
    
    @pyqtSlot(result=bool)
    def validate(self):
        """
        Validate the prompt data.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Title is required and must be between 3 and 100 characters
        if not self._title or len(self._title) < 3 or len(self._title) > 100:
            self.error.emit(self.tr("Title must be between 3 and 100 characters"))
            return False
        
        # Content is required
        if not self._content:
            self.error.emit(self.tr("Content is required"))
            return False
        
        # Description should not exceed 500 characters
        if self._description and len(self._description) > 500:
            self.error.emit(self.tr("Description cannot exceed 500 characters"))
            return False
        
        return True
    
    @pyqtSlot(int, result=bool)
    def load(self, prompt_id):
        """
        Load a prompt from the database by ID.
        
        Args:
            prompt_id: The ID of the prompt to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT p.id, p.title, p.content, p.description, p.is_public, 
                   p.is_featured, p.is_custom, p.category_id, p.user_id,
                   p.created_date, p.modified_date
            FROM Prompts p
            WHERE p.id = ?
        """)
        query.addBindValue(prompt_id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load prompt: ") + query.lastError().text())
            return False
        
        if query.next():
            self._id = query.value(0)
            self._title = query.value(1)
            self._content = query.value(2)
            self._description = query.value(3)
            self._is_public = query.value(4)
            self._is_featured = query.value(5)
            self._is_custom = query.value(6)
            self._category_id = query.value(7)
            self._user_id = query.value(8)
            self._created_date = query.value(9)
            self._modified_date = query.value(10)
            
            # Load tags for this prompt
            self._load_tags()
            
            self.changed.emit()
            return True
        else:
            self.error.emit(self.tr("Prompt not found"))
            return False
    
    @pyqtSlot(result=bool)
    def save(self):
        """
        Save the prompt to the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.validate():
            return False
        
        query = QSqlQuery()
        
        # Update the modified date
        self._modified_date = QDateTime.currentDateTime()
        
        if self._id is None:
            # Insert new prompt
            query.prepare("""
                INSERT INTO Prompts (title, content, description, is_public, 
                                    is_featured, is_custom, category_id, user_id,
                                    created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
            query.addBindValue(self._title)
            query.addBindValue(self._content)
            query.addBindValue(self._description)
            query.addBindValue(self._is_public)
            query.addBindValue(self._is_featured)
            query.addBindValue(self._is_custom)
            query.addBindValue(self._category_id)
            query.addBindValue(self._user_id)
            query.addBindValue(self._created_date)
            query.addBindValue(self._modified_date)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to create prompt: ") + query.lastError().text())
                return False
            
            # Get the new ID
            self._id = query.lastInsertId()
        else:
            # Update existing prompt
            query.prepare("""
                UPDATE Prompts
                SET title = ?, content = ?, description = ?, is_public = ?,
                    is_featured = ?, is_custom = ?, category_id = ?, user_id = ?,
                    modified_date = ?
                WHERE id = ?
            """)
            query.addBindValue(self._title)
            query.addBindValue(self._content)
            query.addBindValue(self._description)
            query.addBindValue(self._is_public)
            query.addBindValue(self._is_featured)
            query.addBindValue(self._is_custom)
            query.addBindValue(self._category_id)
            query.addBindValue(self._user_id)
            query.addBindValue(self._modified_date)
            query.addBindValue(self._id)
            
            if not query.exec():
                self.error.emit(self.tr("Failed to update prompt: ") + query.lastError().text())
                return False
        
        # Save tags
        if not self._save_tags():
            return False
        
        self.saved.emit()
        return True
    
    @pyqtSlot(result=bool)
    def delete(self):
        """
        Delete the prompt from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._id is None:
            self.error.emit(self.tr("Cannot delete unsaved prompt"))
            return False
        
        # Begin transaction
        query = QSqlQuery()
        if not query.exec("BEGIN TRANSACTION"):
            self.error.emit(self.tr("Failed to begin transaction: ") + query.lastError().text())
            return False
        
        # Delete prompt-tag associations
        query.prepare("DELETE FROM PromptTags WHERE prompt_id = ?")
        query.addBindValue(self._id)
        if not query.exec():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to delete prompt tags: ") + query.lastError().text())
            return False
        
        # Delete the prompt
        query.prepare("DELETE FROM Prompts WHERE id = ?")
        query.addBindValue(self._id)
        if not query.exec():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to delete prompt: ") + query.lastError().text())
            return False
        
        # Commit transaction
        if not query.exec("COMMIT"):
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to commit transaction: ") + query.lastError().text())
            return False
        
        # Reset the object
        self._id = None
        self._title = ""
        self._content = ""
        self._description = ""
        self._is_public = False
        self._is_featured = False
        self._is_custom = False
        self._category_id = None
        self._user_id = None
        self._created_date = QDateTime.currentDateTime()
        self._modified_date = QDateTime.currentDateTime()
        self._tags = []
        
        self.changed.emit()
        return True
    
    def _load_tags(self):
        """
        Load tags associated with this prompt.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._id is None:
            return True
        
        self._tags = []
        
        query = QSqlQuery()
        query.prepare("""
            SELECT t.id, t.name
            FROM Tags t
            JOIN PromptTags pt ON pt.tag_id = t.id
            WHERE pt.prompt_id = ?
        """)
        query.addBindValue(self._id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load tags: ") + query.lastError().text())
            return False
        
        while query.next():
            self._tags.append({
                'id': query.value(0),
                'name': query.value(1)
            })
        
        return True
    
    def _save_tags(self):
        """
        Save the tags associated with this prompt.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._id is None:
            return True
        
        # Begin transaction
        query = QSqlQuery()
        if not query.exec("BEGIN TRANSACTION"):
            self.error.emit(self.tr("Failed to begin transaction: ") + query.lastError().text())
            return False
        
        # Delete existing tag associations
        query.prepare("DELETE FROM PromptTags WHERE prompt_id = ?")
        query.addBindValue(self._id)
        if not query.exec():
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to delete tag associations: ") + query.lastError().text())
            return False
        
        # Insert new tag associations
        for tag in self._tags:
            query.prepare("INSERT INTO PromptTags (prompt_id, tag_id) VALUES (?, ?)")
            query.addBindValue(self._id)
            query.addBindValue(tag['id'])
            if not query.exec():
                query.exec("ROLLBACK")
                self.error.emit(self.tr("Failed to add tag association: ") + query.lastError().text())
                return False
        
        # Commit transaction
        if not query.exec("COMMIT"):
            query.exec("ROLLBACK")
            self.error.emit(self.tr("Failed to commit transaction: ") + query.lastError().text())
            return False
        
        return True
    
    @pyqtSlot(list)
    def set_tags(self, tags):
        """
        Set the tags for this prompt.
        
        Args:
            tags: List of tag objects with 'id' and 'name' keys
        """
        self._tags = tags
        self.changed.emit()
    
    @pyqtProperty(list)
    def tags(self):
        """Get the tags associated with this prompt."""
        return self._tags
    
    @pyqtSlot(int)
    def add_tag(self, tag_id):
        """
        Add a tag to this prompt.
        
        Args:
            tag_id: The ID of the tag to add
        """
        # Check if tag is already added
        for tag in self._tags:
            if tag['id'] == tag_id:
                return
        
        # Get tag name from database
        query = QSqlQuery()
        query.prepare("SELECT name FROM Tags WHERE id = ?")
        query.addBindValue(tag_id)
        
        if query.exec() and query.next():
            tag_name = query.value(0)
            self._tags.append({
                'id': tag_id,
                'name': tag_name
            })
            self.changed.emit()
    
    @pyqtSlot(int)
    def remove_tag(self, tag_id):
        """
        Remove a tag from this prompt.
        
        Args:
            tag_id: The ID of the tag to remove
        """
        self._tags = [tag for tag in self._tags if tag['id'] != tag_id]
        self.changed.emit()


class PromptMapper:
    """
    Maps a Prompt model to UI form widgets.
    
    This class provides an interface between the Prompt model and the UI,
    handling two-way data binding and validation.
    """
    
    def __init__(self, prompt, form_widgets):
        """
        Initialize the mapper.
        
        Args:
            prompt: The Prompt model to map
            form_widgets: Dictionary of form widgets keyed by field name
        """
        self.prompt = prompt
        self.widgets = form_widgets
        self.connections = []
        
        # Connect prompt signals
        self.prompt.changed.connect(self.update_widgets)
        self.prompt.error.connect(self.show_error)
        
        # Connect widget signals
        self._connect_widgets()
        
        # Initial update
        self.update_widgets()
    
    def _connect_widgets(self):
        """Connect widget signals to update the model."""
        if 'title' in self.widgets:
            self.connections.append(
                self.widgets['title'].textChanged.connect(
                    lambda text: setattr(self.prompt, 'title', text)
                )
            )
        
        if 'content' in self.widgets:
            self.connections.append(
                self.widgets['content'].textChanged.connect(
                    lambda: setattr(self.prompt, 'content', self.widgets['content'].toPlainText())
                )
            )
        
        if 'description' in self.widgets:
            self.connections.append(
                self.widgets['description'].textChanged.connect(
                    lambda: setattr(self.prompt, 'description', self.widgets['description'].toPlainText())
                )
            )
        
        if 'is_public' in self.widgets:
            self.connections.append(
                self.widgets['is_public'].toggled.connect(
                    lambda checked: setattr(self.prompt, 'is_public', checked)
                )
            )
        
        if 'is_featured' in self.widgets:
            self.connections.append(
                self.widgets['is_featured'].toggled.connect(
                    lambda checked: setattr(self.prompt, 'is_featured', checked)
                )
            )
        
        if 'is_custom' in self.widgets:
            self.connections.append(
                self.widgets['is_custom'].toggled.connect(
                    lambda checked: setattr(self.prompt, 'is_custom', checked)
                )
            )
        
        if 'category' in self.widgets:
            self.connections.append(
                self.widgets['category'].currentIndexChanged.connect(
                    lambda index: setattr(self.prompt, 'category_id', 
                                          self.widgets['category'].itemData(index))
                )
            )
    
    def update_widgets(self):
        """Update widget values from the model."""
        if 'title' in self.widgets:
            self.widgets['title'].setText(self.prompt.title)
        
        if 'content' in self.widgets:
            self.widgets['content'].setPlainText(self.prompt.content)
        
        if 'description' in self.widgets:
            self.widgets['description'].setPlainText(self.prompt.description)
        
        if 'is_public' in self.widgets:
            self.widgets['is_public'].setChecked(self.prompt.is_public)
        
        if 'is_featured' in self.widgets:
            self.widgets['is_featured'].setChecked(self.prompt.is_featured)
        
        if 'is_custom' in self.widgets:
            self.widgets['is_custom'].setChecked(self.prompt.is_custom)
        
        if 'category' in self.widgets and self.prompt.category_id is not None:
            for i in range(self.widgets['category'].count()):
                if self.widgets['category'].itemData(i) == self.prompt.category_id:
                    self.widgets['category'].setCurrentIndex(i)
                    break
        
        if 'created_date' in self.widgets:
            self.widgets['created_date'].setText(
                self.prompt.created_date.toString('yyyy-MM-dd hh:mm:ss')
            )
        
        if 'modified_date' in self.widgets:
            self.widgets['modified_date'].setText(
                self.prompt.modified_date.toString('yyyy-MM-dd hh:mm:ss')
            )
        
        if 'tags' in self.widgets:
            # Assuming this is a custom tag widget that can be updated with a list
            self.widgets['tags'].set_tags(self.prompt.tags)
    
    def show_error(self, error_message):
        """Show error message in the appropriate widget."""
        if 'error_label' in self.widgets:
            self.widgets['error_label'].setText(error_message)
            self.widgets['error_label'].setVisible(True)
    
    def submit(self):
        """
        Submit form data to the model and save.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.prompt.save()
    
    def reset(self):
        """Reset form to model values."""
        self.update_widgets()
        
        if 'error_label' in self.widgets:
            self.widgets['error_label'].setVisible(False)
    
    def disconnect(self):
        """Disconnect all signal connections."""
        for connection in self.connections:
            try:
                connection.disconnect()
            except:
                pass
        
        self.connections = []
        
        try:
            self.prompt.changed.disconnect(self.update_widgets)
            self.prompt.error.disconnect(self.show_error)
        except:
            pass 