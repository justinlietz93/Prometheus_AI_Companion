"""
Model Factory for the Prometheus AI Prompt Generator.

This module contains factory methods for creating and configuring Qt model classes
that work with the application's database for use in UI data binding.
"""

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlTableModel, QSqlDatabase, QSqlQuery


class ModelFactory(QObject):
    """
    Factory class for creating and configuring Qt model classes.
    
    The ModelFactory provides methods to create properly configured 
    QSqlRelationalTableModel and other model classes for use in UI 
    components while maintaining relationships between data entities.
    """
    
    # Define signals for notifications
    error = pyqtSignal(str)
    
    def __init__(self, db=None, parent=None):
        """
        Initialize the ModelFactory.
        
        Args:
            db: QSqlDatabase instance to use (or None to use the default connection)
            parent: The parent QObject
        """
        super().__init__(parent)
        self.db = db if db is not None else QSqlDatabase.database()
    
    def create_tag_model(self):
        """
        Create a model for Tag data suitable for UI components.
        
        Returns:
            QSqlTableModel: Configured model for Tag data
        """
        model = QSqlTableModel(self, self.db)
        model.setTable("Tags")
        
        # Set field headers
        model.setHeaderData(0, Qt.Orientation.Horizontal, self.tr("ID"))
        model.setHeaderData(1, Qt.Orientation.Horizontal, self.tr("Name"))
        model.setHeaderData(2, Qt.Orientation.Horizontal, self.tr("Color"))
        model.setHeaderData(3, Qt.Orientation.Horizontal, self.tr("Description"))
        
        # Set edit strategy - changes are cached in the model until submitAll() is called
        model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        
        # Initial sort order
        model.setSort(1, Qt.SortOrder.AscendingOrder)  # Sort by name
        
        # Load data
        if not model.select():
            self.error.emit(self.tr("Failed to load tag data: ") + model.lastError().text())
        
        return model
    
    def create_category_model(self, include_parent_relation=True):
        """
        Create a model for Category data suitable for UI components.
        
        Args:
            include_parent_relation: Whether to include parent category relation
            
        Returns:
            QSqlRelationalTableModel: Configured model for Category data with relations
        """
        model = QSqlRelationalTableModel(self, self.db)
        model.setTable("Categories")
        
        # Set field headers
        model.setHeaderData(0, Qt.Orientation.Horizontal, self.tr("ID"))
        model.setHeaderData(1, Qt.Orientation.Horizontal, self.tr("Name"))
        model.setHeaderData(2, Qt.Orientation.Horizontal, self.tr("Description"))
        model.setHeaderData(3, Qt.Orientation.Horizontal, self.tr("Parent"))
        model.setHeaderData(4, Qt.Orientation.Horizontal, self.tr("Display Order"))
        model.setHeaderData(5, Qt.Orientation.Horizontal, self.tr("Icon"))
        
        # Setup relations
        if include_parent_relation:
            # Relate parent_id to Categories table to show parent name instead of ID
            model.setRelation(3, QSqlRelation("Categories", "id", "name"))
        
        # Set edit strategy - changes are cached in the model until submitAll() is called
        model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        
        # Initial sort order
        model.setSort(4, Qt.SortOrder.AscendingOrder)  # Sort by display_order
        model.setSort(1, Qt.SortOrder.AscendingOrder)  # Then by name
        
        # Load data
        if not model.select():
            self.error.emit(self.tr("Failed to load category data: ") + model.lastError().text())
        
        return model
    
    def create_prompt_category_model(self):
        """
        Create a model for Categories specifically for use in prompt editing.
        
        This provides a hierarchical view of categories focused on selection rather
        than editing.
        
        Returns:
            QSqlTableModel: Configured model for Category selection
        """
        model = QSqlTableModel(self, self.db)
        model.setTable("Categories")
        
        # Only show id and name columns for selection
        for i in range(model.columnCount()):
            # Hide all columns except id and name
            if i not in [0, 1]:
                model.removeColumn(i)
        
        # Initial sort order
        model.setSort(1, Qt.SortOrder.AscendingOrder)  # Sort by name
        
        # Load data
        if not model.select():
            self.error.emit(self.tr("Failed to load category data: ") + model.lastError().text())
        
        return model
    
    def create_tag_selection_model(self):
        """
        Create a model for Tags specifically for use in tag selection.
        
        Returns:
            QSqlTableModel: Configured model for Tag selection
        """
        model = QSqlTableModel(self, self.db)
        model.setTable("Tags")
        
        # Show only relevant columns for selection
        for i in range(model.columnCount()):
            # Hide all columns except id, name, and color
            if i not in [0, 1, 2]:
                model.removeColumn(i)
        
        # Initial sort order
        model.setSort(1, Qt.SortOrder.AscendingOrder)  # Sort by name
        
        # Load data
        if not model.select():
            self.error.emit(self.tr("Failed to load tag data: ") + model.lastError().text())
        
        return model
    
    def create_prompt_tags_model(self, prompt_id):
        """
        Create a model showing tags associated with a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt to show tags for
            
        Returns:
            QSqlTableModel: Configured model for prompt tags
        """
        model = QSqlTableModel(self, self.db)
        
        # Use a custom query to get tags for a specific prompt
        query = QSqlQuery(self.db)
        query.prepare("""
            SELECT t.id, t.name, t.color, t.description
            FROM Tags t
            JOIN PromptTags pt ON pt.tag_id = t.id
            WHERE pt.prompt_id = ?
            ORDER BY t.name
        """)
        query.addBindValue(prompt_id)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load prompt tags: ") + query.lastError().text())
            return None
        
        model.setQuery(query)
        
        # Set field headers
        model.setHeaderData(0, Qt.Orientation.Horizontal, self.tr("ID"))
        model.setHeaderData(1, Qt.Orientation.Horizontal, self.tr("Name"))
        model.setHeaderData(2, Qt.Orientation.Horizontal, self.tr("Color"))
        model.setHeaderData(3, Qt.Orientation.Horizontal, self.tr("Description"))
        
        return model
    
    def create_category_tree_model(self):
        """
        Create a specialized model for displaying the category tree.
        
        This uses a QSqlQueryModel with a custom query to enable
        hierarchical display in tree views.
        
        Returns:
            QSqlQueryModel: Model configured for hierarchical category display
        """
        from PyQt6.QtSql import QSqlQueryModel
        
        model = QSqlQueryModel(self)
        
        # Get all categories ordered by hierarchy
        query = QSqlQuery(self.db)
        query.prepare("""
            WITH RECURSIVE CategoryHierarchy AS (
                -- Base case: select all root categories
                SELECT id, name, description, parent_id, display_order, icon, 0 AS level, 
                       CAST(display_order AS TEXT) AS sort_path
                FROM Categories
                WHERE parent_id IS NULL
                
                UNION ALL
                
                -- Recursive case: select children and link to parents
                SELECT c.id, c.name, c.description, c.parent_id, c.display_order, c.icon,
                       h.level + 1,
                       h.sort_path || '.' || CAST(c.display_order AS TEXT) AS sort_path
                FROM Categories c
                JOIN CategoryHierarchy h ON c.parent_id = h.id
            )
            SELECT id, name, description, parent_id, display_order, icon, level,
                   (SELECT COUNT(*) FROM Categories WHERE parent_id = CategoryHierarchy.id) AS has_children
            FROM CategoryHierarchy
            ORDER BY sort_path, name
        """)
        
        if not query.exec():
            self.error.emit(self.tr("Failed to load category hierarchy: ") + query.lastError().text())
            return None
        
        model.setQuery(query)
        
        # Set field headers
        model.setHeaderData(0, Qt.Orientation.Horizontal, self.tr("ID"))
        model.setHeaderData(1, Qt.Orientation.Horizontal, self.tr("Name"))
        model.setHeaderData(2, Qt.Orientation.Horizontal, self.tr("Description"))
        model.setHeaderData(3, Qt.Orientation.Horizontal, self.tr("Parent ID"))
        model.setHeaderData(4, Qt.Orientation.Horizontal, self.tr("Display Order"))
        model.setHeaderData(5, Qt.Orientation.Horizontal, self.tr("Icon"))
        model.setHeaderData(6, Qt.Orientation.Horizontal, self.tr("Level"))
        model.setHeaderData(7, Qt.Orientation.Horizontal, self.tr("Has Children"))
        
        return model 