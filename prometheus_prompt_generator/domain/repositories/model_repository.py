"""
Model Repository for the Prometheus AI Prompt Generator.

This module provides database access for managing language models.
"""

from typing import List, Optional, Dict, Any

from PySide6.QtSql import QSqlQuery, QSqlError, QSqlDatabase

from prometheus_prompt_generator.domain.models.model import Model


class ModelRepository:
    """
    Repository for managing language models.
    
    This class provides methods for storing, retrieving, and managing
    language models used for benchmarking.
    """
    
    def __init__(self, db=None):
        """
        Initialize the ModelRepository.
        
        Args:
            db: QSqlDatabase instance to use (or None to use the default connection)
        """
        self.db = db if db is not None else QSqlDatabase.database()
    
    def save(self, model: Model) -> Model:
        """
        Save a model to the database.
        
        Args:
            model: The model to save
            
        Returns:
            The saved model with updated ID if it was a new record
            
        Raises:
            Exception: If the save operation fails
        """
        # Call the save method on the model object
        if not model.save():
            raise Exception(f"Failed to save model: {model.name}")
        
        return model
    
    def get_by_id(self, model_id: int) -> Optional[Model]:
        """
        Get a model by its ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            The retrieved model, or None if not found
            
        Raises:
            Exception: If the retrieval operation fails
        """
        model = Model(model_id)
        if model.id is None:
            return None
        
        return model
    
    def get_all(self) -> List[Model]:
        """
        Get all models.
        
        Returns:
            List of all models
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return Model.get_all_models()
    
    def delete(self, model_id: int) -> bool:
        """
        Delete a model.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            True if the model was deleted, False otherwise
            
        Raises:
            Exception: If the delete operation fails
        """
        model = self.get_by_id(model_id)
        if model is None:
            return False
        
        return model.delete()
    
    def get_by_provider(self, provider: str) -> List[Model]:
        """
        Get all models from a specific provider.
        
        Args:
            provider: Name of the provider
            
        Returns:
            List of models from the provider
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return Model.get_models_by_provider(provider) 