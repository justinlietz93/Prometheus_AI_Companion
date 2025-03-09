"""
Tag Controller for the Prometheus AI Prompt Generator.

This module contains the TagController class which handles the business logic
for tag operations and bridges the UI layer with the data model.
"""

from typing import List, Dict, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
import logging

from ..models.tag import Tag

logger = logging.getLogger(__name__)


class TagController(QObject):
    """Controller class for tag operations.
    
    This class handles the business logic for tag operations and bridges
    the UI layer with the data model. It provides signals to notify the UI
    of data changes and slots to handle UI actions.
    """
    
    # Signals to notify the UI of changes
    tagsChanged = pyqtSignal(list)  # Emitted when the list of tags changes
    tagSelected = pyqtSignal(object)  # Emitted when a tag is selected
    selectionChanged = pyqtSignal(list)  # Emitted when selection changes
    tagSaved = pyqtSignal(object)  # Emitted when a tag is saved
    tagDeleted = pyqtSignal(str)  # Emitted when a tag is deleted
    operationError = pyqtSignal(str)  # Emitted when an operation fails
    operationSuccess = pyqtSignal(str)  # Emitted when an operation succeeds
    
    def __init__(self, repository):
        """Initialize the controller with a repository.
        
        Args:
            repository: The tag repository
        """
        super().__init__()
        self.repository = repository
        self.selected_tags = []  # List of selected tags
        self.current_tag = None  # Currently focused tag
        self._all_tags = []  # Cache of all tags
        
        # Load tags on initialization
        QTimer.singleShot(0, self.load_tags)
        
        logger.info("TagController initialized with repository")
    
    @pyqtSlot()
    def load_tags(self) -> None:
        """Load all tags from the repository."""
        try:
            logger.debug("Loading all tags from repository")
            tags = self.repository.get_all()
            self._all_tags = tags
            self.tagsChanged.emit(tags)
            self.operationSuccess.emit(self.tr("Successfully loaded %d tags") % len(tags))
            logger.info(f"Successfully loaded {len(tags)} tags")
        except Exception as e:
            error_msg = self.tr("Failed to load tags: %s") % str(e)
            logger.error(f"Error loading tags: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(int)
    def select_tag(self, tag_id: int) -> None:
        """Select a tag by ID.
        
        Args:
            tag_id: The ID of the tag to select
        """
        try:
            logger.debug(f"Selecting tag with ID: {tag_id}")
            tag = self.repository.get_by_id(tag_id)
            if tag:
                self.current_tag = tag
                self.selected_tags = [tag]
                self.selectionChanged.emit(self.selected_tags)
                self.tagSelected.emit(tag)
                logger.info(f"Selected tag: {tag.name} (ID: {tag_id})")
            else:
                error_msg = self.tr("Tag with ID %d not found") % tag_id
                logger.warning(f"Tag with ID {tag_id} not found")
                self.operationError.emit(error_msg)
        except Exception as e:
            error_msg = self.tr("Failed to select tag: %s") % str(e)
            logger.error(f"Error selecting tag {tag_id}: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot()
    def clear_selection(self) -> None:
        """Clear the current tag selection."""
        logger.debug("Clearing tag selection")
        self.selected_tags = []
        self.current_tag = None
        self.selectionChanged.emit(self.selected_tags)
        logger.info("Tag selection cleared")
    
    @pyqtSlot(object)
    def save_tag(self, tag: Tag) -> None:
        """Save a tag to the repository.
        
        Args:
            tag: The tag to save
        """
        try:
            logger.debug(f"Saving tag: {tag.name} (ID: {tag.id if tag.id else 'New'})")
            
            # Validate the tag before saving
            if not tag.name or not tag.name.strip():
                error_msg = self.tr("Tag name cannot be empty")
                logger.warning("Attempted to save tag with empty name")
                self.operationError.emit(error_msg)
                return
                
            # Save the tag using the repository
            saved_tag = self.repository.save(tag)
            
            # Emit signals to notify the UI
            self.tagSaved.emit(saved_tag)
            
            # Refresh tags list to include the new/updated tag
            self.load_tags()
            
            success_msg = self.tr("Tag saved successfully")
            self.operationSuccess.emit(success_msg)
            logger.info(f"Tag saved successfully: {tag.name} (ID: {tag.id})")
        except Exception as e:
            error_msg = self.tr("Failed to save tag: %s") % str(e)
            logger.error(f"Error saving tag: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(int)
    def delete_tag(self, tag_id: int) -> None:
        """Delete a tag from the repository.
        
        Args:
            tag_id: The ID of the tag to delete
        """
        try:
            logger.debug(f"Deleting tag with ID: {tag_id}")
            
            # Check if the tag exists
            tag = self.repository.get_by_id(tag_id)
            if not tag:
                error_msg = self.tr("Tag with ID %d not found") % tag_id
                logger.warning(f"Attempt to delete non-existent tag with ID {tag_id}")
                self.operationError.emit(error_msg)
                return
                
            # If the tag is currently selected, clear the selection
            if self.current_tag and self.current_tag.id == tag_id:
                self.clear_selection()
            
            # Delete the tag
            result = self.repository.delete(tag_id)
            if result:
                self.tagDeleted.emit(str(tag_id))
                
                # Refresh tags list to reflect the deletion
                self.load_tags()
                
                success_msg = self.tr("Tag deleted successfully")
                self.operationSuccess.emit(success_msg)
                logger.info(f"Tag deleted successfully: ID {tag_id}")
            else:
                error_msg = self.tr("Failed to delete tag with ID %d") % tag_id
                logger.warning(f"Failed to delete tag with ID {tag_id}")
                self.operationError.emit(error_msg)
        except Exception as e:
            error_msg = self.tr("Failed to delete tag: %s") % str(e)
            logger.error(f"Error deleting tag {tag_id}: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(dict)
    def filter_tags(self, **kwargs):
        """Filter tags based on criteria.
        
        Args:
            **kwargs: Filter criteria (e.g., name="test", color="#FF5733")
        """
        try:
            logger.debug(f"Filtering tags with criteria: {kwargs}")
            filtered_tags = self.repository.filter(**kwargs)
            self.tagsChanged.emit(filtered_tags)
            logger.info(f"Filtered tags: {len(filtered_tags)} results")
        except Exception as e:
            error_msg = self.tr("Failed to filter tags: %s") % str(e)
            logger.error(f"Error filtering tags: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(list)
    def multi_select_tags(self, tag_ids: List[int]) -> None:
        """Select multiple tags.
        
        Args:
            tag_ids: List of tag IDs to select
        """
        try:
            logger.debug(f"Selecting multiple tags: {tag_ids}")
            selected = []
            
            for tag_id in tag_ids:
                tag = self.repository.get_by_id(tag_id)
                if tag:
                    selected.append(tag)
            
            self.selected_tags = selected
            
            # Set current tag to the first selected tag if any
            if selected:
                self.current_tag = selected[0]
                logger.info(f"Selected {len(selected)} tags, current tag: {self.current_tag.name}")
            else:
                self.current_tag = None
                logger.info("No tags selected")
            
            self.selectionChanged.emit(self.selected_tags)
        except Exception as e:
            error_msg = self.tr("Failed to select tags: %s") % str(e)
            logger.error(f"Error selecting multiple tags: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot()
    def create_new_tag(self) -> Tag:
        """Create a new empty tag.
        
        Returns:
            A new Tag instance
        """
        logger.debug("Creating new tag")
        new_tag = Tag()
        return new_tag
    
    @pyqtSlot(str, result=list)
    def search_tags(self, search_term: str) -> List[Tag]:
        """Search for tags by name.
        
        Args:
            search_term: The search term to look for in tag names
            
        Returns:
            A list of matching tags
        """
        try:
            logger.debug(f"Searching tags with term: {search_term}")
            
            if not search_term.strip():
                # Empty search term, return all tags
                return self._all_tags
            
            matching_tags = []
            for tag in self._all_tags:
                if search_term.lower() in tag.name.lower():
                    matching_tags.append(tag)
            
            logger.info(f"Tag search results: {len(matching_tags)} matches")
            return matching_tags
        except Exception as e:
            error_msg = self.tr("Failed to search tags: %s") % str(e)
            logger.error(f"Error searching tags: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
            return [] 