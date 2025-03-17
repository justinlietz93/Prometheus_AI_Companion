"""
Prompt Editor Dialog for the Prometheus AI Prompt Generator.

This module contains the PromptEditorDialog class which implements the UI for editing
prompts with form validation.
"""

from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSlot, QTimer

from ..domain.models.prompt import Prompt
from ..domain.controllers.prompt_controller import PromptController
from .designer.ui_prompt_editor_dialog import Ui_PromptEditorDialog


class PromptEditorDialog(QDialog):
    """
    Dialog for creating and editing prompts with form validation.
    
    This dialog provides a user interface for creating and editing prompts with
    form validation, ensuring that data entered by the user is valid before saving.
    """
    
    def __init__(self, parent=None, prompt_controller=None, prompt_id=None):
        """
        Initialize the prompt editor dialog.
        
        Args:
            parent: The parent widget
            prompt_controller: The prompt controller
            prompt_id: Optional ID of the prompt to edit
        """
        super().__init__(parent)
        self.ui = Ui_PromptEditorDialog()
        self.ui.setupUi(self)
        
        self.prompt_controller = prompt_controller
        self.prompt = None
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.setInterval(500)  # Validate after 500ms of inactivity
        
        # Connect signals
        self.ui.titleLineEdit.textChanged.connect(self._on_title_changed)
        self.ui.descriptionTextEdit.textChanged.connect(self._on_description_changed)
        self.ui.contentTextEdit.textChanged.connect(self._on_content_changed)
        self.validation_timer.timeout.connect(self._validate_form)
        
        # Connect buttons
        self.ui.buttonBox.accepted.connect(self._on_accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        reset_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Reset)
        help_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Help)
        if reset_button:
            reset_button.clicked.connect(self._on_reset)
        if help_button:
            help_button.clicked.connect(self._on_help)
            
        # Initialize prompt
        if prompt_id is not None and prompt_controller is not None:
            QTimer.singleShot(0, lambda: self._load_prompt(prompt_id))
        else:
            self._create_new_prompt()
            
    def _create_new_prompt(self):
        """Create a new prompt for editing."""
        self.prompt = Prompt(self)
        self.prompt.error.connect(self._show_error)
        self.setWindowTitle(self.tr("Create New Prompt"))
        
    def _load_prompt(self, prompt_id):
        """Load an existing prompt for editing.
        
        Args:
            prompt_id: The ID of the prompt to load
        """
        if not self.prompt_controller:
            self._show_error(self.tr("No prompt controller available"))
            return
            
        try:
            self.prompt_controller.select_prompt(prompt_id)
            self.prompt = self.prompt_controller.current_prompt
            if not self.prompt:
                self._show_error(self.tr("Prompt not found"))
                return
                
            self.prompt.error.connect(self._show_error)
            self._update_ui_from_prompt()
            self.setWindowTitle(self.tr("Edit Prompt: {}").format(self.prompt.title))
        except Exception as e:
            self._show_error(self.tr("Error loading prompt: {}").format(str(e)))
            
    def _update_ui_from_prompt(self):
        """Update the UI with data from the current prompt."""
        if not self.prompt:
            return
            
        # Block signals to prevent validation during loading
        old_block = self.blockSignals(True)
        
        self.ui.titleLineEdit.setText(self.prompt.title)
        self.ui.descriptionTextEdit.setText(self.prompt.description)
        self.ui.contentTextEdit.setText(self.prompt.content)
        self.ui.isPublicCheckBox.setChecked(self.prompt.is_public)
        self.ui.isFeaturedCheckBox.setChecked(self.prompt.is_featured)
        self.ui.isCustomCheckBox.setChecked(self.prompt.is_custom)
        
        if self.prompt.id is not None:
            self.ui.createdDateValue.setText(self.prompt.created_date.toString(Qt.DateFormat.ISODate))
            self.ui.modifiedDateValue.setText(self.prompt.modified_date.toString(Qt.DateFormat.ISODate))
            # Usage count would be loaded from the controller
            
        # Restore signal blocking
        self.blockSignals(old_block)
        
    def _update_prompt_from_ui(self):
        """Update the prompt with data from the UI."""
        if not self.prompt:
            return
            
        self.prompt.title = self.ui.titleLineEdit.text()
        self.prompt.description = self.ui.descriptionTextEdit.toPlainText()
        self.prompt.content = self.ui.contentTextEdit.toPlainText()
        self.prompt.is_public = self.ui.isPublicCheckBox.isChecked()
        self.prompt.is_featured = self.ui.isFeaturedCheckBox.isChecked()
        self.prompt.is_custom = self.ui.isCustomCheckBox.isChecked()
        
        # Category would be added here
        # Tags would be updated here
        
    def _on_title_changed(self):
        """Handle title changes and trigger validation."""
        if self.prompt:
            self.prompt.title = self.ui.titleLineEdit.text()
            self.validation_timer.start()
            
    def _on_description_changed(self):
        """Handle description changes and trigger validation."""
        if self.prompt:
            self.prompt.description = self.ui.descriptionTextEdit.toPlainText()
            self.validation_timer.start()
            
    def _on_content_changed(self):
        """Handle content changes and trigger validation."""
        if self.prompt:
            self.prompt.content = self.ui.contentTextEdit.toPlainText()
            self.validation_timer.start()
            
    def _validate_form(self):
        """Validate the form data."""
        if not self.prompt:
            return False
            
        # Reset error displays
        self.ui.errorFrame.setVisible(False)
        self.ui.titleErrorLabel.setVisible(False)
        self.ui.descriptionErrorLabel.setVisible(False)
        self.ui.contentErrorLabel.setVisible(False)
        
        # Validate title
        if not self.prompt.title.strip():
            self.ui.titleErrorLabel.setText(self.tr("Title cannot be empty"))
            self.ui.titleErrorLabel.setVisible(True)
            self.ui.titleLineEdit.setFocus()
            return False
        
        if len(self.prompt.title) < 3:
            self.ui.titleErrorLabel.setText(self.tr("Title must be at least 3 characters"))
            self.ui.titleErrorLabel.setVisible(True)
            self.ui.titleLineEdit.setFocus()
            return False
            
        if len(self.prompt.title) > 100:
            self.ui.titleErrorLabel.setText(self.tr("Title cannot exceed 100 characters"))
            self.ui.titleErrorLabel.setVisible(True)
            self.ui.titleLineEdit.setFocus()
            return False
            
        # Validate description
        if len(self.prompt.description) > 500:
            self.ui.descriptionErrorLabel.setText(self.tr("Description cannot exceed 500 characters"))
            self.ui.descriptionErrorLabel.setVisible(True)
            self.ui.descriptionTextEdit.setFocus()
            return False
            
        # Validate content
        if not self.prompt.content.strip():
            self.ui.contentErrorLabel.setText(self.tr("Content cannot be empty"))
            self.ui.contentErrorLabel.setVisible(True)
            self.ui.contentTextEdit.setFocus()
            return False
            
        return True
        
    def _show_error(self, message):
        """Display an error message in the error frame.
        
        Args:
            message: The error message to display
        """
        self.ui.errorMessage.setText(message)
        self.ui.errorFrame.setVisible(True)
        
    def _on_accept(self):
        """Handle dialog acceptance (Save button)."""
        if self._validate_form():
            self._update_prompt_from_ui()
            
            if self.prompt_controller:
                try:
                    self.prompt_controller.save_prompt(self.prompt)
                    self.accept()
                except Exception as e:
                    self._show_error(str(e))
            else:
                # If no controller, just validate and accept
                if self.prompt.validate():
                    self.accept()
                else:
                    # Validation failed with an error
                    pass  # Error message handled by the error signal
        
    def _on_reset(self):
        """Handle Reset button click."""
        if self.prompt and self.prompt.id:
            # For existing prompts, reload from database
            self._load_prompt(self.prompt.id)
        else:
            # For new prompts, clear the form
            self.ui.titleLineEdit.clear()
            self.ui.descriptionTextEdit.clear()
            self.ui.contentTextEdit.clear()
            self.ui.isPublicCheckBox.setChecked(False)
            self.ui.isFeaturedCheckBox.setChecked(False)
            self.ui.isCustomCheckBox.setChecked(False)
            
    def _on_help(self):
        """Handle Help button click."""
        QMessageBox.information(
            self,
            self.tr("Prompt Editor Help"),
            self.tr(
                "This dialog allows you to create or edit prompts.\n\n"
                "Required fields are marked with an asterisk (*).\n\n"
                "- Title: Must be 3-100 characters\n"
                "- Description: Optional, maximum 500 characters\n"
                "- Content: The template for your prompt\n"
                "- Variables: Use {{variable_name}} syntax in your content\n\n"
                "See the user manual for more information on prompt templates."
            )
        )
        
    @staticmethod
    def edit_prompt(parent, prompt_controller, prompt_id=None):
        """Static convenience method for editing a prompt.
        
        Args:
            parent: The parent widget
            prompt_controller: The prompt controller
            prompt_id: Optional ID of the prompt to edit
            
        Returns:
            bool: True if the dialog was accepted, False otherwise
        """
        dialog = PromptEditorDialog(parent, prompt_controller, prompt_id)
        return dialog.exec() == QDialog.DialogCode.Accepted 