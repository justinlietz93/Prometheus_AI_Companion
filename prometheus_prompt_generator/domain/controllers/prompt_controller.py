"""
Prompt Controller for the Prometheus AI Prompt Generator.

This module contains the PromptController class which handles the business logic
for prompt operations and bridges the UI layer with the data model.
"""

from typing import List, Dict, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QDateTime
import logging

from ..models.prompt import Prompt

logger = logging.getLogger(__name__)


class PromptController(QObject):
    """Controller class for prompt operations.
    
    This class handles the business logic for prompt operations and bridges
    the UI layer with the data model. It provides signals to notify the UI
    of data changes and slots to handle UI actions.
    """
    
    # Signals to notify the UI of changes
    promptsChanged = pyqtSignal(list)  # Emitted when the list of prompts changes
    promptSelected = pyqtSignal(object)  # Emitted when a prompt is selected
    selectionChanged = pyqtSignal(list)  # Emitted when selection changes
    promptSaved = pyqtSignal(object)  # Emitted when a prompt is saved
    promptDeleted = pyqtSignal(str)  # Emitted when a prompt is deleted
    operationError = pyqtSignal(str)  # Emitted when an operation fails
    operationSuccess = pyqtSignal(str)  # Emitted when an operation succeeds
    
    def __init__(self, repository):
        """Initialize the controller with a repository.
        
        Args:
            repository: The prompt repository
        """
        super().__init__()
        self.repository = repository
        self.selected_prompts = []  # List of selected prompt types
        self.current_prompt = None  # Currently focused prompt
        self._all_prompts = []  # Cache of all prompts
        
        # Load prompts on initialization
        QTimer.singleShot(0, self.load_prompts)
        
        logger.info("PromptController initialized with repository")
    
    @pyqtSlot()
    def load_prompts(self) -> None:
        """Load all prompts from the repository."""
        try:
            logger.debug("Loading all prompts from repository")
            prompts = self.repository.get_all()
            self._all_prompts = prompts
            self.promptsChanged.emit(prompts)
            self.operationSuccess.emit(self.tr("Successfully loaded %d prompts") % len(prompts))
            logger.info(f"Successfully loaded {len(prompts)} prompts")
        except Exception as e:
            error_msg = self.tr("Failed to load prompts: %s") % str(e)
            logger.error(f"Error loading prompts: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(int)
    def select_prompt(self, prompt_id: int) -> None:
        """Select a prompt by ID.
        
        Args:
            prompt_id: The ID of the prompt to select
        """
        try:
            logger.debug(f"Selecting prompt with ID: {prompt_id}")
            prompt = self.repository.get_by_id(prompt_id)
            if prompt:
                self.current_prompt = prompt
                self.selected_prompts = [prompt]
                self.selectionChanged.emit(self.selected_prompts)
                self.promptSelected.emit(prompt)
                logger.info(f"Selected prompt: {prompt.title} (ID: {prompt_id})")
            else:
                error_msg = self.tr("Prompt with ID %d not found") % prompt_id
                logger.warning(f"Prompt with ID {prompt_id} not found")
                self.operationError.emit(error_msg)
        except Exception as e:
            error_msg = self.tr("Failed to select prompt: %s") % str(e)
            logger.error(f"Error selecting prompt {prompt_id}: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot()
    def clear_selection(self) -> None:
        """Clear the current prompt selection."""
        logger.debug("Clearing prompt selection")
        self.selected_prompts = []
        self.current_prompt = None
        self.selectionChanged.emit(self.selected_prompts)
        logger.info("Prompt selection cleared")
    
    @pyqtSlot(object)
    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to the repository.
        
        Args:
            prompt: The prompt to save
        """
        try:
            logger.debug(f"Saving prompt: {prompt.title} (ID: {prompt.id if prompt.id else 'New'})")
            
            # Perform validation
            validation_errors = self._validate_prompt(prompt)
            if validation_errors:
                error_msg = self.tr("Validation errors: %s") % ", ".join(validation_errors)
                logger.warning(f"Validation errors when saving prompt: {error_msg}")
                self.operationError.emit(error_msg)
                return
                
            # Update modified date for existing prompts
            if prompt.id is not None:
                prompt._modified_date = QDateTime.currentDateTime()
            
            saved_prompt = self.repository.save(prompt)
            self.promptSaved.emit(saved_prompt)
            
            # Refresh prompts list to include the new/updated prompt
            self.load_prompts()
            
            success_msg = self.tr("Prompt saved successfully")
            self.operationSuccess.emit(success_msg)
            logger.info(f"Prompt saved successfully: {prompt.title} (ID: {prompt.id})")
        except Exception as e:
            error_msg = self.tr("Failed to save prompt: %s") % str(e)
            logger.error(f"Error saving prompt: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(int)
    def delete_prompt(self, prompt_id: int) -> None:
        """Delete a prompt from the repository.
        
        Args:
            prompt_id: The ID of the prompt to delete
        """
        try:
            logger.debug(f"Deleting prompt with ID: {prompt_id}")
            
            # Check if the prompt exists
            prompt = self.repository.get_by_id(prompt_id)
            if not prompt:
                error_msg = self.tr("Prompt with ID %d not found") % prompt_id
                logger.warning(f"Attempt to delete non-existent prompt with ID {prompt_id}")
                self.operationError.emit(error_msg)
                return
                
            # If the prompt is currently selected, clear the selection
            if self.current_prompt and self.current_prompt.id == prompt_id:
                self.clear_selection()
            
            result = self.repository.delete(prompt_id)
            if result:
                self.promptDeleted.emit(str(prompt_id))
                
                # Refresh prompts list to reflect the deletion
                self.load_prompts()
                
                success_msg = self.tr("Prompt deleted successfully")
                self.operationSuccess.emit(success_msg)
                logger.info(f"Prompt deleted successfully: ID {prompt_id}")
            else:
                error_msg = self.tr("Failed to delete prompt with ID %d") % prompt_id
                logger.warning(f"Failed to delete prompt with ID {prompt_id}")
                self.operationError.emit(error_msg)
        except Exception as e:
            error_msg = self.tr("Failed to delete prompt: %s") % str(e)
            logger.error(f"Error deleting prompt {prompt_id}: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(dict)
    @pyqtSlot(str)
    def filter_prompts(self, **kwargs) -> None:
        """Filter prompts based on criteria.
        
        Args:
            **kwargs: Filter criteria (e.g., title="test", is_public=True)
        """
        try:
            logger.debug(f"Filtering prompts with criteria: {kwargs}")
            filtered_prompts = self.repository.filter(**kwargs)
            self.promptsChanged.emit(filtered_prompts)
            logger.info(f"Filtered prompts: {len(filtered_prompts)} results")
        except Exception as e:
            error_msg = self.tr("Failed to filter prompts: %s") % str(e)
            logger.error(f"Error filtering prompts: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(list)
    def batch_delete_prompts(self, prompt_ids: List[int]) -> None:
        """Delete multiple prompts in a batch operation.
        
        Args:
            prompt_ids: List of prompt IDs to delete
        """
        try:
            logger.debug(f"Batch deleting {len(prompt_ids)} prompts")
            success_count = 0
            failed_ids = []
            
            for prompt_id in prompt_ids:
                try:
                    result = self.repository.delete(prompt_id)
                    if result:
                        self.promptDeleted.emit(str(prompt_id))
                        success_count += 1
                    else:
                        failed_ids.append(prompt_id)
                except Exception as e:
                    logger.error(f"Error deleting prompt {prompt_id}: {str(e)}")
                    failed_ids.append(prompt_id)
            
            # Refresh the prompts list
            self.load_prompts()
            
            if success_count == len(prompt_ids):
                success_msg = self.tr("Successfully deleted %d prompts") % success_count
                self.operationSuccess.emit(success_msg)
                logger.info(f"Batch delete successful: {success_count} prompts deleted")
            elif success_count > 0:
                partial_msg = self.tr("Partially successful: %d of %d prompts deleted") % (success_count, len(prompt_ids))
                self.operationError.emit(partial_msg)
                logger.warning(f"Batch delete partially successful: {success_count} of {len(prompt_ids)} deleted. Failed IDs: {failed_ids}")
            else:
                error_msg = self.tr("Failed to delete any prompts")
                self.operationError.emit(error_msg)
                logger.error(f"Batch delete failed: No prompts deleted. Failed IDs: {failed_ids}")
        except Exception as e:
            error_msg = self.tr("Failed to perform batch delete: %s") % str(e)
            logger.error(f"Error in batch delete operation: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot(list)
    def multi_select_prompts(self, prompt_ids: List[int]) -> None:
        """Select multiple prompts.
        
        Args:
            prompt_ids: List of prompt IDs to select
        """
        try:
            logger.debug(f"Selecting multiple prompts: {prompt_ids}")
            selected = []
            
            for prompt_id in prompt_ids:
                prompt = self.repository.get_by_id(prompt_id)
                if prompt:
                    selected.append(prompt)
            
            self.selected_prompts = selected
            
            # Set current prompt to the first selected prompt if any
            if selected:
                self.current_prompt = selected[0]
                logger.info(f"Selected {len(selected)} prompts, current prompt: {self.current_prompt.title}")
            else:
                self.current_prompt = None
                logger.info("No prompts selected")
            
            self.selectionChanged.emit(self.selected_prompts)
        except Exception as e:
            error_msg = self.tr("Failed to select prompts: %s") % str(e)
            logger.error(f"Error selecting multiple prompts: {str(e)}", exc_info=True)
            self.operationError.emit(error_msg)
    
    @pyqtSlot()
    def create_new_prompt(self) -> Prompt:
        """Create a new empty prompt.
        
        Returns:
            A new Prompt instance
        """
        logger.debug("Creating new prompt")
        new_prompt = Prompt()
        return new_prompt
    
    def _validate_prompt(self, prompt: Prompt) -> List[str]:
        """Validate a prompt before saving.
        
        Args:
            prompt: The prompt to validate
            
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        if not prompt.title.strip():
            errors.append(self.tr("Title cannot be empty"))
        
        if not prompt.content.strip():
            errors.append(self.tr("Content cannot be empty"))
        
        # Check title length
        if len(prompt.title) > 255:
            errors.append(self.tr("Title cannot exceed 255 characters"))
        
        logger.debug(f"Validation for prompt: {len(errors)} errors found")
        return errors 