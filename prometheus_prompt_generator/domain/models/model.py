"""
Prometheus AI Prompt Generator - Model Entity

This module defines the Model class, which represents a language model that can be used
for benchmarking and comparison in the system.
"""

from typing import Dict, List, Optional, Union
import json

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlQuery, QSqlError


class Model(QObject):
    """
    Model entity representing a language model in the system.
    
    This class encapsulates a language model that can be used for benchmarking,
    including its provider, version, and other metadata.
    
    Signals:
        changed: Emitted when any property of the model changes
        error: Emitted when an error occurs during model operations
        saved: Emitted when the model is successfully saved
    """
    
    # Define signals
    changed = Signal()
    error = Signal(str)
    saved = Signal()
    
    def __init__(self, model_id: Optional[int] = None):
        """
        Initialize a Model instance.
        
        Args:
            model_id: Optional ID of an existing model to load from the database
        """
        super().__init__()
        
        # Initialize properties
        self._id: Optional[int] = None
        self._name: str = ""
        self._provider: str = ""
        self._version: str = ""
        self._description: str = ""
        self._is_local: bool = False
        
        # Load the model if an ID is provided
        if model_id is not None:
            self.load(model_id)
    
    @property
    def id(self) -> Optional[int]:
        """Get the model ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get the model name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the model name."""
        if not value:
            self.error.emit("Model name cannot be empty")
            return
        
        self._name = value
        self.changed.emit()
    
    @property
    def provider(self) -> str:
        """Get the model provider."""
        return self._provider
    
    @provider.setter
    def provider(self, value: str):
        """Set the model provider."""
        self._provider = value
        self.changed.emit()
    
    @property
    def version(self) -> str:
        """Get the model version."""
        return self._version
    
    @version.setter
    def version(self, value: str):
        """Set the model version."""
        self._version = value
        self.changed.emit()
    
    @property
    def description(self) -> str:
        """Get the model description."""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """Set the model description."""
        self._description = value
        self.changed.emit()
    
    @property
    def is_local(self) -> bool:
        """Get whether the model is local or cloud-based."""
        return self._is_local
    
    @is_local.setter
    def is_local(self, value: bool):
        """Set whether the model is local or cloud-based."""
        self._is_local = value
        self.changed.emit()
    
    def validate(self) -> bool:
        """
        Validate the model data.
        
        Returns:
            True if the model data is valid, False otherwise
        """
        if not self._name:
            self.error.emit("Model name cannot be empty")
            return False
        
        # Additional validation can be added here
        
        return True
    
    def load(self, model_id: int) -> bool:
        """
        Load a model from the database.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            True if the model was loaded successfully, False otherwise
        """
        try:
            query = QSqlQuery()
            query.prepare("""
                SELECT id, name, provider, version, description, is_local
                FROM Models
                WHERE id = ?
            """)
            query.addBindValue(model_id)
            
            if not query.exec() or not query.first():
                self.error.emit(f"Failed to load model: {query.lastError().text()}")
                return False
            
            # Populate properties
            self._id = query.value(0)
            self._name = query.value(1)
            self._provider = query.value(2)
            self._version = query.value(3)
            self._description = query.value(4)
            self._is_local = bool(query.value(5))
            
            return True
            
        except Exception as e:
            self.error.emit(f"Error loading model: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save the model to the database.
        
        Returns:
            True if the model was saved successfully, False otherwise
        """
        try:
            # Validate model data
            if not self.validate():
                return False
            
            query = QSqlQuery()
            
            # Update existing or insert new
            if self._id is not None:
                query.prepare("""
                    UPDATE Models
                    SET name = ?, provider = ?, version = ?, description = ?, is_local = ?
                    WHERE id = ?
                """)
                query.addBindValue(self._name)
                query.addBindValue(self._provider)
                query.addBindValue(self._version)
                query.addBindValue(self._description)
                query.addBindValue(1 if self._is_local else 0)
                query.addBindValue(self._id)
                
                if not query.exec():
                    self.error.emit(f"Failed to update model: {query.lastError().text()}")
                    return False
                    
            else:
                # Insert new model
                query.prepare("""
                    INSERT INTO Models (name, provider, version, description, is_local)
                    VALUES (?, ?, ?, ?, ?)
                """)
                query.addBindValue(self._name)
                query.addBindValue(self._provider)
                query.addBindValue(self._version)
                query.addBindValue(self._description)
                query.addBindValue(1 if self._is_local else 0)
                
                if not query.exec():
                    self.error.emit(f"Failed to create model: {query.lastError().text()}")
                    return False
                
                # Get the new ID
                self._id = query.lastInsertId()
            
            self.saved.emit()
            return True
            
        except Exception as e:
            self.error.emit(f"Error saving model: {str(e)}")
            return False
    
    def delete(self) -> bool:
        """
        Delete the model from the database.
        
        Returns:
            True if the model was deleted successfully, False otherwise
        """
        try:
            if self._id is None:
                self.error.emit("Cannot delete model: no ID specified")
                return False
            
            query = QSqlQuery()
            query.prepare("DELETE FROM Models WHERE id = ?")
            query.addBindValue(self._id)
            
            if not query.exec():
                self.error.emit(f"Failed to delete model: {query.lastError().text()}")
                return False
            
            # Reset properties
            self._id = None
            
            return True
            
        except Exception as e:
            self.error.emit(f"Error deleting model: {str(e)}")
            return False
    
    @staticmethod
    def get_all_models() -> List['Model']:
        """
        Get all models from the database.
        
        Returns:
            List of Model objects
        """
        models = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM Models ORDER BY name")
            
            if not query.exec():
                raise Exception(f"Failed to query models: {query.lastError().text()}")
            
            while query.next():
                model_id = query.value(0)
                model = Model(model_id)
                models.append(model)
            
        except Exception as e:
            print(f"Error retrieving models: {str(e)}")
        
        return models
    
    @staticmethod
    def get_models_by_provider(provider: str) -> List['Model']:
        """
        Get all models from a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of Model objects
        """
        models = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM Models WHERE provider = ? ORDER BY name")
            query.addBindValue(provider)
            
            if not query.exec():
                raise Exception(f"Failed to query models: {query.lastError().text()}")
            
            while query.next():
                model_id = query.value(0)
                model = Model(model_id)
                models.append(model)
            
        except Exception as e:
            print(f"Error retrieving models: {str(e)}")
        
        return models 