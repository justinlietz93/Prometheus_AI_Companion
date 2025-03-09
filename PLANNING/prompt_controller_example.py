"""
Prompt Controller Example for SQLite-based MVC Architecture

This file provides an example implementation of the Prompt controller class
that would bridge the UI and data model in the SQLite MVC architecture.
"""

from typing import List, Dict, Optional, Any, Callable
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

# Import the model (from the example)
from prompt_model_example import Prompt, PromptRepository


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
    
    def __init__(self, repository: PromptRepository):
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
    
    @pyqtSlot()
    def load_prompts(self) -> None:
        """Load all prompts from the repository."""
        try:
            self._all_prompts = self.repository.get_all()
            self.promptsChanged.emit(self._all_prompts)
        except Exception as e:
            self.operationError.emit(f"Failed to load prompts: {str(e)}")
    
    @pyqtSlot(str)
    def toggle_prompt_selection(self, prompt_type: str) -> None:
        """Toggle selection state of a prompt.
        
        Args:
            prompt_type: The type identifier of the prompt
        """
        if prompt_type in self.selected_prompts:
            self.selected_prompts.remove(prompt_type)
        else:
            self.selected_prompts.append(prompt_type)
        
        # Notify UI that selection has changed
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot()
    def select_all_prompts(self) -> None:
        """Select all available prompts."""
        self.selected_prompts = [p.type for p in self._all_prompts]
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot()
    def deselect_all_prompts(self) -> None:
        """Deselect all prompts."""
        self.selected_prompts = []
        self.selectionChanged.emit(self.selected_prompts)
    
    @pyqtSlot(str)
    def load_prompt_details(self, prompt_type: str) -> None:
        """Load detailed information for a prompt.
        
        Args:
            prompt_type: The type identifier of the prompt
        """
        try:
            prompt = self.repository.get_by_type(prompt_type)
            if prompt:
                self.current_prompt = prompt
                self.promptSelected.emit(prompt)
            else:
                self.operationError.emit(f"Prompt '{prompt_type}' not found")
        except Exception as e:
            self.operationError.emit(f"Failed to load prompt details: {str(e)}")
    
    @pyqtSlot(dict)
    def save_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """Save a prompt to the repository.
        
        Args:
            prompt_data: Dictionary containing prompt data
        """
        try:
            # Convert dict to Prompt object
            prompt = Prompt.from_dict(prompt_data)
            
            # Save to repository
            saved_prompt = self.repository.save(prompt)
            
            # Update cache and notify UI
            self._update_prompt_in_cache(saved_prompt)
            self.promptSaved.emit(saved_prompt)
            self.operationSuccess.emit(f"Prompt '{saved_prompt.title}' saved successfully")
            
        except ValueError as e:
            # Validation error
            self.operationError.emit(str(e))
        except Exception as e:
            # Other errors
            self.operationError.emit(f"Failed to save prompt: {str(e)}")
    
    @pyqtSlot(str)
    def delete_prompt(self, prompt_type: str) -> None:
        """Delete a prompt from the repository.
        
        Args:
            prompt_type: The type identifier of the prompt
        """
        try:
            # Find prompt ID by type
            prompt = next((p for p in self._all_prompts if p.type == prompt_type), None)
            if not prompt:
                self.operationError.emit(f"Prompt '{prompt_type}' not found")
                return
                
            # Delete from repository
            success = self.repository.delete(prompt.id)
            
            if success:
                # Remove from cache and notify UI
                self._all_prompts = [p for p in self._all_prompts if p.type != prompt_type]
                
                # Also remove from selection if selected
                if prompt_type in self.selected_prompts:
                    self.selected_prompts.remove(prompt_type)
                    self.selectionChanged.emit(self.selected_prompts)
                
                self.promptDeleted.emit(prompt_type)
                self.promptsChanged.emit(self._all_prompts)
                self.operationSuccess.emit(f"Prompt '{prompt_type}' deleted successfully")
            else:
                self.operationError.emit(f"Failed to delete prompt '{prompt_type}'")
                
        except Exception as e:
            self.operationError.emit(f"Failed to delete prompt: {str(e)}")
    
    @pyqtSlot(list, int)
    def generate_prompts(self, prompt_types: List[str], urgency_level: int) -> Dict[str, str]:
        """Generate prompts for selected types with specified urgency level.
        
        Args:
            prompt_types: List of prompt type identifiers
            urgency_level: Urgency level (1-10)
            
        Returns:
            Dictionary mapping prompt types to generated text
        """
        results = {}
        errors = []
        
        for prompt_type in prompt_types:
            try:
                # Get prompt from repository
                prompt = self.repository.get_by_type(prompt_type)
                if not prompt:
                    errors.append(f"Prompt '{prompt_type}' not found")
                    continue
                    
                if not prompt.template:
                    errors.append(f"Template for '{prompt_type}' is empty")
                    continue
                
                # In a real implementation, this would use the template engine
                # For this example, we'll just simulate it
                template = prompt.template
                generated_text = self._apply_urgency_to_template(template, urgency_level)
                
                # Store result
                results[prompt_type] = generated_text
                
            except Exception as e:
                errors.append(f"Error generating '{prompt_type}': {str(e)}")
        
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
            self.promptsChanged.emit(self._all_prompts)
            return
            
        # Perform search (case-insensitive)
        query = query.lower()
        results = []
        
        for prompt in self._all_prompts:
            # Search in type, title, and description
            if (query in prompt.type.lower() or
                query in prompt.title.lower() or
                query in prompt.description.lower() or
                any(query in tag.lower() for tag in prompt.tags)):
                results.append(prompt)
        
        # Update UI with results
        self.promptsChanged.emit(results)
    
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
        
        # Notify UI that prompts have changed
        self.promptsChanged.emit(self._all_prompts)
    
    def _apply_urgency_to_template(self, template: str, urgency_level: int) -> str:
        """Apply urgency level to a template.
        
        Args:
            template: The prompt template
            urgency_level: Urgency level (1-10)
            
        Returns:
            Template with urgency applied
        """
        # Define urgency modifiers based on level
        urgency_modifiers = {
            1: {"intro": "Whenever you have free time, please consider"},
            2: {"intro": "When you have time, please"},
            3: {"intro": "I would appreciate if you could"},
            4: {"intro": "Please"},
            5: {"intro": "I would like you to"},
            6: {"intro": "I need you to"},
            7: {"intro": "I strongly need you to"},
            8: {"intro": "I urgently need you to"},
            9: {"intro": "URGENT: I require you to"},
            10: {"intro": "CRITICAL URGENT ACTION REQUIRED:"}
        }
        
        # Get modifier for level (default to level 5 if invalid)
        modifier = urgency_modifiers.get(urgency_level, urgency_modifiers[5])
        
        # Apply urgency to template
        return f"{modifier['intro']} {template.lstrip()}"


# Example usage in a Qt application
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QMessageBox
    
    class ExampleWindow(QMainWindow):
        def __init__(self, controller):
            super().__init__()
            self.controller = controller
            
            # Set up UI
            self.setWindowTitle("Prompt Controller Example")
            self.setGeometry(100, 100, 600, 400)
            
            # Create central widget
            central = QWidget()
            self.setCentralWidget(central)
            
            # Create layout
            layout = QVBoxLayout(central)
            
            # Create list widget for prompts
            self.prompt_list = QListWidget()
            layout.addWidget(self.prompt_list)
            
            # Create buttons
            self.select_all_btn = QPushButton("Select All")
            self.deselect_all_btn = QPushButton("Deselect All")
            self.generate_btn = QPushButton("Generate Selected")
            
            layout.addWidget(self.select_all_btn)
            layout.addWidget(self.deselect_all_btn)
            layout.addWidget(self.generate_btn)
            
            # Connect signals and slots
            self.connect_signals()
            
        def connect_signals(self):
            # Connect controller signals
            self.controller.promptsChanged.connect(self.update_prompt_list)
            self.controller.operationError.connect(self.show_error)
            self.controller.operationSuccess.connect(self.show_success)
            
            # Connect UI signals to controller slots
            self.prompt_list.itemClicked.connect(
                lambda item: self.controller.toggle_prompt_selection(item.data(0))
            )
            self.select_all_btn.clicked.connect(self.controller.select_all_prompts)
            self.deselect_all_btn.clicked.connect(self.controller.deselect_all_prompts)
            self.generate_btn.clicked.connect(self.generate_prompts)
            
        def update_prompt_list(self, prompts):
            self.prompt_list.clear()
            for prompt in prompts:
                item = QListWidget.QListWidgetItem(f"{prompt.title} ({prompt.type})")
                item.setData(0, prompt.type)  # Store prompt_type as data
                self.prompt_list.addItem(item)
                
        def generate_prompts(self):
            if not self.controller.selected_prompts:
                self.show_error("No prompts selected")
                return
                
            results = self.controller.generate_prompts(
                self.controller.selected_prompts, 
                5  # Default urgency level
            )
            
            if results:
                # Show first result in a message box
                prompt_type = list(results.keys())[0]
                text = results[prompt_type]
                QMessageBox.information(self, "Generated Prompt", text)
                
        def show_error(self, message):
            QMessageBox.critical(self, "Error", message)
            
        def show_success(self, message):
            QMessageBox.information(self, "Success", message)
    
    # Sample application
    app = QApplication(sys.argv)
    
    # Create repository and controller
    repo = PromptRepository("prompts.db")
    controller = PromptController(repo)
    
    # Create and show window
    window = ExampleWindow(controller)
    window.show()
    
    sys.exit(app.exec()) 