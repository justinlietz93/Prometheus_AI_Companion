"""
Advanced Filter Proxy Model for the Prometheus AI Prompt Generator.

This module provides an enhanced QSortFilterProxyModel implementation that supports
complex filtering criteria including multi-column filtering, regular expressions,
and custom filter functions.
"""

from typing import Dict, Any, Callable, List, Optional
from PyQt6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt
import logging

logger = logging.getLogger(__name__)


class AdvancedFilterProxyModel(QSortFilterProxyModel):
    """An enhanced filter proxy model with advanced filtering capabilities.
    
    This class extends QSortFilterProxyModel to provide more sophisticated filtering
    options, including multi-column filtering, custom filter functions, and
    optimized performance for large datasets.
    """
    
    def __init__(self, parent=None):
        """Initialize the advanced filter proxy model.
        
        Args:
            parent: The parent QObject (optional)
        """
        super().__init__(parent)
        
        self._filter_criteria = {}  # {column_index: (filter_string, filter_regex)}
        self._column_mappings = {}  # {column_name: column_index}
        self._custom_filters = []  # List of custom filter functions
        self._filter_role = Qt.ItemDataRole.DisplayRole
        self._case_sensitive = False
        
        # Set default filtering behavior
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        logger.debug("AdvancedFilterProxyModel initialized")
    
    def set_column_mapping(self, column_mappings: Dict[str, int]):
        """Set column name to index mappings for named column access.
        
        Args:
            column_mappings: Dict mapping column names to column indices
        """
        self._column_mappings = column_mappings
        logger.debug(f"Column mappings set: {column_mappings}")
    
    def add_filter(self, column: Any, filter_string: str, regex: bool = False):
        """Add a filter for a specific column.
        
        Args:
            column: Column index (int) or name (str) to filter
            filter_string: String to filter by
            regex: Whether to treat filter_string as a regular expression
        """
        # Resolve column index if name was provided
        column_index = self._resolve_column(column)
        
        # Create regex if requested
        if regex:
            pattern = QRegularExpression(filter_string)
            if not self._case_sensitive:
                pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
            self._filter_criteria[column_index] = (filter_string, pattern)
        else:
            self._filter_criteria[column_index] = (filter_string, None)
        
        # Trigger re-filtering
        self.invalidateFilter()
        
        logger.debug(f"Filter added for column {column_index}: '{filter_string}', regex={regex}")
    
    def remove_filter(self, column: Any):
        """Remove a filter for a specific column.
        
        Args:
            column: Column index (int) or name (str) to remove filter from
        """
        column_index = self._resolve_column(column)
        
        if column_index in self._filter_criteria:
            del self._filter_criteria[column_index]
            self.invalidateFilter()
            logger.debug(f"Filter removed for column {column_index}")
        else:
            logger.debug(f"No filter found for column {column_index}")
    
    def clear_filters(self):
        """Clear all filters."""
        self._filter_criteria.clear()
        self._custom_filters.clear()
        self.invalidateFilter()
        logger.debug("All filters cleared")
    
    def add_custom_filter(self, filter_function: Callable[[QModelIndex], bool]):
        """Add a custom filter function.
        
        Args:
            filter_function: Function that takes a source model index and returns
                            True if the item should be included, False otherwise
        """
        self._custom_filters.append(filter_function)
        self.invalidateFilter()
        logger.debug("Custom filter function added")
    
    def set_filter_role(self, role: Qt.ItemDataRole):
        """Set the data role to use for filtering.
        
        Args:
            role: Qt.ItemDataRole to use for filtering
        """
        self._filter_role = role
        self.invalidateFilter()
        logger.debug(f"Filter role set to {role}")
    
    def set_case_sensitivity(self, case_sensitive: bool):
        """Set case sensitivity for filtering.
        
        Args:
            case_sensitive: Whether filtering should be case sensitive
        """
        self._case_sensitive = case_sensitive
        sensitivity = Qt.CaseSensitivity.CaseSensitive if case_sensitive else Qt.CaseSensitivity.CaseInsensitive
        self.setFilterCaseSensitivity(sensitivity)
        
        # Update regex patterns if they exist
        for column, (filter_string, pattern) in self._filter_criteria.items():
            if pattern:
                new_pattern = QRegularExpression(filter_string)
                if not case_sensitive:
                    new_pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
                self._filter_criteria[column] = (filter_string, new_pattern)
        
        self.invalidateFilter()
        logger.debug(f"Case sensitivity set to {case_sensitive}")
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Determine if a row should be included in the filtered view.
        
        This method is called by Qt for each row in the source model to determine
        if it should be included in the filtered view.
        
        Args:
            source_row: Row index in the source model
            source_parent: Parent index in the source model
            
        Returns:
            True if the row should be included, False otherwise
        """
        # If no filters are applied, include all rows
        if not self._filter_criteria and not self._custom_filters:
            return True
        
        # Check column filters
        if self._filter_criteria:
            for column, (filter_string, pattern) in self._filter_criteria.items():
                index = self.sourceModel().index(source_row, column, source_parent)
                data = self.sourceModel().data(index, self._filter_role)
                
                if data is None:
                    return False
                
                # Convert to string for filtering
                text = str(data)
                
                # Apply filter
                if pattern:
                    # Regex filtering
                    match = pattern.match(text)
                    if not match.hasMatch():
                        return False
                else:
                    # Simple string filtering
                    if self._case_sensitive:
                        if filter_string not in text:
                            return False
                    else:
                        if filter_string.lower() not in text.lower():
                            return False
        
        # Check custom filters
        if self._custom_filters:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            for custom_filter in self._custom_filters:
                if not custom_filter(source_index):
                    return False
        
        # If we got here, the row passed all filters
        return True
    
    def _resolve_column(self, column: Any) -> int:
        """Resolve column name to index if needed.
        
        Args:
            column: Column index (int) or name (str)
            
        Returns:
            Column index as integer
        """
        if isinstance(column, str):
            if column in self._column_mappings:
                return self._column_mappings[column]
            else:
                logger.warning(f"Column name '{column}' not found in mappings, using 0")
                return 0
        else:
            return column 