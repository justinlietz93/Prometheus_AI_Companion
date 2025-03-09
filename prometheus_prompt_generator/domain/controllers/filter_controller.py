"""
Filter Controller for the Prometheus AI Prompt Generator.

This module contains the FilterController class which handles filtering and sorting
operations for data collections in the application.
"""

from typing import List, Dict, Optional, Any, Callable, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QSortFilterProxyModel, Qt, QModelIndex
import logging

logger = logging.getLogger(__name__)


class FilterController(QObject):
    """Controller class for filtering and sorting operations.
    
    This class provides a unified interface for filtering and sorting data
    in the application, regardless of the data source (model or repository).
    It uses Qt's QSortFilterProxyModel for efficient filtering and sorting.
    """
    
    # Signals to notify the UI of changes
    filtered = pyqtSignal(list)  # Emitted when data is filtered
    sorted = pyqtSignal()  # Emitted when data is sorted
    error = pyqtSignal(str)  # Emitted when an operation fails
    
    def __init__(self, repository):
        """Initialize the controller with a repository.
        
        Args:
            repository: The repository to use for data operations
        """
        super().__init__()
        self.repository = repository
        self.proxy_model = QSortFilterProxyModel()
        self.current_filters = {}
        self.custom_filter_func = None
        
        # Configure proxy model for case-insensitive filtering
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        logger.info("FilterController initialized with repository")
    
    @pyqtSlot(object)
    def set_source_model(self, model):
        """Set the source model for the proxy model.
        
        Args:
            model: The source model to filter and sort
        """
        logger.debug(f"Setting source model: {type(model).__name__}")
        self.proxy_model.setSourceModel(model)
    
    @pyqtSlot(str)
    def filter_by_title(self, title: str):
        """Filter data by title.
        
        Args:
            title: The title text to filter by
        """
        logger.debug(f"Filtering by title: {title}")
        try:
            if title and title.strip():
                self.current_filters['title'] = title
            else:
                if 'title' in self.current_filters:
                    del self.current_filters['title']
            
            # Apply the filters
            self._apply_repository_filters()
        except Exception as e:
            error_msg = f"Error filtering by title: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    @pyqtSlot(list)
    def filter_by_tags(self, tags: List[int]):
        """Filter data by tags.
        
        Args:
            tags: List of tag IDs to filter by
        """
        logger.debug(f"Filtering by tags: {tags}")
        try:
            if tags:
                self.current_filters['tags'] = tags
            else:
                if 'tags' in self.current_filters:
                    del self.current_filters['tags']
            
            # Apply the filters
            self._apply_repository_filters()
        except Exception as e:
            error_msg = f"Error filtering by tags: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    @pyqtSlot(int)
    def filter_by_category(self, category_id: int):
        """Filter data by category.
        
        Args:
            category_id: The category ID to filter by
        """
        logger.debug(f"Filtering by category ID: {category_id}")
        try:
            if category_id:
                self.current_filters['category_id'] = category_id
            else:
                if 'category_id' in self.current_filters:
                    del self.current_filters['category_id']
            
            # Apply the filters
            self._apply_repository_filters()
        except Exception as e:
            error_msg = f"Error filtering by category: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    @pyqtSlot(dict)
    def apply_filters(self, **kwargs):
        """Apply multiple filters at once.
        
        Args:
            **kwargs: Key-value pairs of filter criteria
        """
        logger.debug(f"Applying multiple filters: {kwargs}")
        try:
            # Update current filters with the provided filters
            for key, value in kwargs.items():
                if value:
                    self.current_filters[key] = value
                elif key in self.current_filters:
                    del self.current_filters[key]
            
            # Apply the filters
            self._apply_repository_filters()
        except Exception as e:
            error_msg = f"Error applying filters: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    @pyqtSlot()
    def clear_filters(self):
        """Clear all filters and return to unfiltered state."""
        logger.debug("Clearing all filters")
        try:
            # Clear all filters
            self.current_filters = {}
            self.custom_filter_func = None
            
            # Reset the proxy model's filter
            self.proxy_model.setFilterFixedString("")
            
            # Get all data from repository
            all_data = self.repository.get_all()
            
            # Emit signal with all data
            self.filtered.emit(all_data)
            
            logger.info("All filters cleared")
        except Exception as e:
            error_msg = f"Error clearing filters: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    @pyqtSlot(int, object)
    def sort_by_column(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """Sort data by a specific column.
        
        Args:
            column: The column index to sort by
            order: The sort order (ascending or descending)
        """
        logger.debug(f"Sorting by column {column}, order: {order}")
        try:
            # Apply the sort
            self.proxy_model.sort(column, order)
            
            # Emit signal to indicate sorting has changed
            self.sorted.emit()
            
            logger.info(f"Data sorted by column {column}, order: {order}")
        except Exception as e:
            error_msg = f"Error sorting data: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    def apply_custom_filter(self, filter_func: Callable[[Any], bool]):
        """Apply a custom filter function.
        
        Args:
            filter_func: A function that takes an item and returns True if it should be included
        """
        logger.debug("Applying custom filter function")
        try:
            # Store the custom filter function
            self.custom_filter_func = filter_func
            
            # Apply custom filter to repository data
            all_data = self.repository.get_all()
            filtered_data = [item for item in all_data if filter_func(item)]
            
            # Emit signal with filtered data
            self.filtered.emit(filtered_data)
            
            logger.info(f"Custom filter applied, {len(filtered_data)} items matched")
        except Exception as e:
            error_msg = f"Error applying custom filter: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    def get_filtered_data(self) -> List[Any]:
        """Get the currently filtered data.
        
        Returns:
            A list of items that match the current filters
        """
        try:
            # If we're using repository filtering, return filtered data from repository
            if self.current_filters or self.custom_filter_func:
                if self.custom_filter_func:
                    # Apply custom filter to repository data
                    all_data = self.repository.get_all()
                    return [item for item in all_data if self.custom_filter_func(item)]
                else:
                    # Apply repository filters
                    return self.repository.filter(**self.current_filters)
            
            # If we're using proxy model filtering, extract data from proxy model
            if self.proxy_model.sourceModel():
                filtered_data = []
                for row in range(self.proxy_model.rowCount()):
                    index = self.proxy_model.index(row, 0)
                    source_index = self.proxy_model.mapToSource(index)
                    item = self.proxy_model.sourceModel().data(source_index, Qt.ItemDataRole.UserRole)
                    filtered_data.append(item)
                return filtered_data
            
            # If no filtering is applied, return all data
            return self.repository.get_all()
        except Exception as e:
            error_msg = f"Error getting filtered data: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            return []
    
    def _apply_repository_filters(self):
        """Internal method to apply filters using the repository."""
        try:
            # Get filtered data from repository
            filtered_data = self.repository.filter(**self.current_filters)
            
            # Emit signal with filtered data
            self.filtered.emit(filtered_data)
            
            logger.info(f"Filters applied, {len(filtered_data)} items matched")
        except Exception as e:
            error_msg = f"Error applying repository filters: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg) 