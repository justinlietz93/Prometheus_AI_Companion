"""
Prompt Controller for the Prometheus AI Prompt Generator.

This module contains the PromptController class which implements the business logic
for prompt operations and mediates between the UI and data layers using Qt's signal/slot mechanism.
"""

from typing import List, Dict, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QDateTime
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlError

from ..models.prompt import Prompt


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
    promptDeleted = pyqtSignal(int)  # Emitted when a prompt is deleted
    operationError = pyqtSignal(str)  # Emitted when an operation fails
    operationSuccess = pyqtSignal(str)  # Emitted when an operation succeeds
    filterChanged = pyqtSignal(dict)  # Emitted when filter criteria change
    
    def __init__(self, parent=None):
        """Initialize the controller.
        
        Args:
            parent: The parent QObject
        """
        super().__init__(parent)
        self.selected_prompts = []  # List of selected prompt IDs
        self.current_prompt = None  # Currently focused prompt
        self._all_prompts = []  # Cache of all prompts
        self._filter_criteria = {}  # Current filter criteria
        
        # Load prompts on initialization
        QTimer.singleShot(0, self.load_prompts)
    
    @pyqtSlot()
    def load_prompts(self) -> None:
        """Load all prompts from the database."""
        try:
            # Clear existing cache
            self._all_prompts = []
            
            # Create query to get all prompts
            query = QSqlQuery()
            query.prepare("""
                SELECT id FROM prompts
                ORDER BY title
            """)
            
            if not query.exec():
                raise Exception(f"Database error: {query.lastError().text()}")
            
            # Load each prompt
            while query.next():
                prompt_id = query.value(0)
                prompt = Prompt(parent=self, prompt_id=prompt_id)
                self._all_prompts.append(prompt)
            
            # Notify UI that prompts have changed
            self.promptsChanged.emit(self._all_prompts)
            
        except Exception as e:
            self.operationError.emit(f"Failed to load prompts: {str(e)}")
    
    @pyqtSlot(dict)
    def apply_filter(self, criteria: Dict[str, Any]) -> None:
        """Apply filter criteria to the prompt list.
        
        Args:
            criteria: Dictionary of filter criteria
        """
        self._filter_criteria = criteria
        self.filterChanged.emit(criteria)
        
        try:
            # Build query based on filter criteria
            query_parts = ["SELECT id FROM prompts WHERE 1=1"]
            params = []
            
            # Title filter
            if 'title' in criteria and criteria['title']:
                query_parts.append("AND title LIKE ?")
                params.append(f"%{criteria['title']}%")
            
            # Category filter
            if 'category_id' in criteria and criteria['category_id']:
                query_parts.append("AND category_id = ?")
                params.append(criteria['category_id'])
            
            # Public/private filter
            if 'is_public' in criteria:
                query_parts.append("AND is_public = ?")
                params.append(1 if criteria['is_public'] else 0)
            
            # Featured filter
            if 'is_featured' in criteria:
                query_parts.append("AND is_featured = ?")
                params.append(1 if criteria['is_featured'] else 0)
            
            # Custom filter
            if 'is_custom' in criteria:
                query_parts.append("AND is_custom = ?")
                params.append(1 if criteria['is_custom'] else 0)
            
            # Date range filter
            if 'date_from' in criteria and criteria['date_from']:
                query_parts.append("AND created_date >= ?")
                params.append(criteria['date_from'].toString("yyyy-MM-dd"))
            
            if 'date_to' in criteria and criteria['date_to']:
                query_parts.append("AND created_date <= ?")
                params.append(criteria['date_to'].toString("yyyy-MM-dd"))
            
            # Tag filter
            if 'tag_id' in criteria and criteria['tag_id']:
                query_parts.append("""
                    AND id IN (
                        SELECT prompt_id FROM prompt_tags 
                        WHERE tag_id = ?
                    )
                """)
                params.append(criteria['tag_id'])
            
            # Add ordering
            query_parts.append("ORDER BY title")
            
            # Execute query
            query = QSqlQuery()
            query.prepare(" ".join(query_parts))
            
            # Bind parameters
            for param in params:
                query.addBindValue(param)
            
            if not query.exec():
                raise Exception(f"Database error: {query.lastError().text()}")
            
            # Load filtered prompts
            filtered_prompts = []
            while query.next():
                prompt_id = query.value(0)
                # Check if prompt is already in cache
                prompt = next((p for p in self._all_prompts if p.id == prompt_id), None)
                if not prompt:
                    prompt = Prompt(parent=self, prompt_id=prompt_id)
                filtered_prompts.append(prompt)
            
            # Notify UI that prompts have changed
            self.promptsChanged.emit(filtered_prompts)
            
        except Exception as e:
            self.operationError.emit(f"Failed to apply filter: {str(e)}")
    
    @pyqtSlot(int)
    def toggle_prompt_selection(self, prompt_id: int) -> None:
        """Toggle selection state of a prompt.
        
        Args:
            prompt_id: The ID of the prompt
        """
        if prompt_id in self.selected_prompts:
            self.selected_prompts.remove(prompt_id)
        else:
            self.selected_prompts.append(prompt_id)
        
        # Notify UI that selection has changed
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot()
    def select_all_prompts(self) -> None:
        """Select all available prompts."""
        self.selected_prompts = [p.id for p in self._all_prompts]
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot()
    def deselect_all_prompts(self) -> None:
        """Deselect all prompts."""
        self.selected_prompts = []
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot(int)
    def load_prompt_details(self, prompt_id: int) -> None:
        """Load detailed information for a prompt.
        
        Args:
            prompt_id: The ID of the prompt
        """
        try:
            # Check if prompt is in cache
            prompt = next((p for p in self._all_prompts if p.id == prompt_id), None)
            
            if not prompt:
                # Create new prompt object and load from database
                prompt = Prompt(parent=self, prompt_id=prompt_id)
            
            if prompt.id is not None:
                self.current_prompt = prompt
                self.promptSelected.emit(prompt)
            else:
                self.operationError.emit(f"Prompt with ID {prompt_id} not found")
                
        except Exception as e:
            self.operationError.emit(f"Failed to load prompt details: {str(e)}")
    
    @pyqtSlot(object)
    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to the database.
        
        Args:
            prompt: The prompt to save
        """
        try:
            # Validate prompt
            if not prompt.validate():
                # Validation errors are emitted by the prompt object
                return
            
            # Save prompt
            if prompt.save():
                # Update cache
                self._update_prompt_in_cache(prompt)
                
                # Notify UI
                self.promptSaved.emit(prompt)
                self.operationSuccess.emit(f"Prompt '{prompt.title}' saved successfully")
            else:
                self.operationError.emit("Failed to save prompt")
                
        except Exception as e:
            self.operationError.emit(f"Failed to save prompt: {str(e)}")
    
    @pyqtSlot()
    def create_new_prompt(self) -> Prompt:
        """Create a new prompt object.
        
        Returns:
            A new Prompt object
        """
        prompt = Prompt(parent=self)
        self.current_prompt = prompt
        self.promptSelected.emit(prompt)
        return prompt
    
    @pyqtSlot(int)
    def delete_prompt(self, prompt_id: int) -> None:
        """Delete a prompt from the database.
        
        Args:
            prompt_id: The ID of the prompt to delete
        """
        try:
            # Find prompt in cache
            prompt = next((p for p in self._all_prompts if p.id == prompt_id), None)
            
            if not prompt:
                # Create temporary prompt object for deletion
                prompt = Prompt(parent=self, prompt_id=prompt_id)
            
            # Delete prompt
            if prompt.delete():
                # Remove from cache
                self._all_prompts = [p for p in self._all_prompts if p.id != prompt_id]
                
                # Remove from selection if selected
                if prompt_id in self.selected_prompts:
                    self.selected_prompts.remove(prompt_id)
                    self.selectionChanged.emit(self.selected_prompts)
                
                # Notify UI
                self.promptDeleted.emit(prompt_id)
                self.operationSuccess.emit(f"Prompt '{prompt.title}' deleted successfully")
                
                # Refresh prompt list
                self.load_prompts()
            else:
                self.operationError.emit(f"Failed to delete prompt with ID {prompt_id}")
                
        except Exception as e:
            self.operationError.emit(f"Failed to delete prompt: {str(e)}")
    
    @pyqtSlot(list, int, result=dict)
    def generate_prompts(self, prompt_ids: List[int], urgency_level: int) -> Dict[int, str]:
        """Generate prompts for selected IDs with specified urgency level.
        
        Args:
            prompt_ids: List of prompt IDs
            urgency_level: Urgency level (1-10)
            
        Returns:
            Dictionary mapping prompt IDs to generated text
        """
        results = {}
        errors = []
        
        for prompt_id in prompt_ids:
            try:
                # Find prompt in cache
                prompt = next((p for p in self._all_prompts if p.id == prompt_id), None)
                
                if not prompt:
                    # Load prompt from database
                    prompt = Prompt(parent=self, prompt_id=prompt_id)
                
                if not prompt.id:
                    errors.append(f"Prompt with ID {prompt_id} not found")
                    continue
                    
                if not prompt.content:
                    errors.append(f"Content for prompt '{prompt.title}' is empty")
                    continue
                
                # In a real implementation, this would use a template engine
                # For this example, we'll just simulate it
                template = prompt.content
                generated_text = self._apply_urgency_to_template(template, urgency_level)
                
                # Store result
                results[prompt_id] = generated_text
                
            except Exception as e:
                errors.append(f"Error generating prompt ID {prompt_id}: {str(e)}")
        
        # Report any errors
        if errors:
            error_message = "The following errors occurred:\n" + "\n".join(f"• {error}" for error in errors)
            self.operationError.emit(error_message)
        
        return results
    
    @pyqtSlot(str)
    def search_prompts(self, query: str) -> None:
        """Search prompts by text.
        
        Args:
            query: Search query text
        """
        if not query:
            # Empty query, show all prompts
            self.load_prompts()
            return
            
        try:
            # Create query to search prompts
            sql_query = QSqlQuery()
            sql_query.prepare("""
                SELECT id FROM prompts
                WHERE title LIKE ? OR description LIKE ? OR content LIKE ?
                ORDER BY title
            """)
            
            # Bind parameters
            search_term = f"%{query}%"
            sql_query.addBindValue(search_term)
            sql_query.addBindValue(search_term)
            sql_query.addBindValue(search_term)
            
            if not sql_query.exec():
                raise Exception(f"Database error: {sql_query.lastError().text()}")
            
            # Load search results
            search_results = []
            while sql_query.next():
                prompt_id = sql_query.value(0)
                # Check if prompt is already in cache
                prompt = next((p for p in self._all_prompts if p.id == prompt_id), None)
                if not prompt:
                    prompt = Prompt(parent=self, prompt_id=prompt_id)
                search_results.append(prompt)
            
            # Notify UI that prompts have changed
            self.promptsChanged.emit(search_results)
            
        except Exception as e:
            self.operationError.emit(f"Failed to search prompts: {str(e)}")
    
    def _update_prompt_in_cache(self, prompt: Prompt) -> None:
        """Update a prompt in the cache.
        
        Args:
            prompt: The updated prompt
        """
        # Check if prompt exists in cache
        for i, p in enumerate(self._all_prompts):
            if p.id == prompt.id:
                # Update existing prompt
                self._all_prompts[i] = prompt
                return
                
        # If not found, add to cache
        self._all_prompts.append(prompt)
    
    def _apply_urgency_to_template(self, template: str, urgency_level: int) -> str:
        """Apply urgency level to a template.
        
        Args:
            template: The template text
            urgency_level: Urgency level (1-10)
            
        Returns:
            The processed template text
        """
        # In a real implementation, this would use a proper template engine
        # For this example, we'll just add some urgency indicators
        
        urgency_indicators = [
            "Please",
            "Kindly",
            "I'd appreciate if you could",
            "I need you to",
            "It's important that you",
            "It's very important that you",
            "It's crucial that you",
            "It's extremely urgent that you",
            "Drop everything and",
            "This is an emergency:"
        ]
        
        # Clamp urgency level to valid range
        urgency_level = max(1, min(10, urgency_level))
        
        # Get appropriate indicator for urgency level
        indicator = urgency_indicators[urgency_level - 1]
        
        # Apply to template
        if "{urgency}" in template:
            return template.replace("{urgency}", indicator)
        else:
            return f"{indicator} {template}" 