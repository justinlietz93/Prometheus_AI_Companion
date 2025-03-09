"""
Generation Controller for the Prometheus AI Prompt Generator.

This module contains the GenerationController class which handles the business logic
for prompt generation and bridges the UI layer with the data model and template engine.
"""

from typing import List, Dict, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import logging
import re

from ..models.prompt import Prompt
from ..services.template_engine import TemplateEngine

logger = logging.getLogger(__name__)


class GenerationController(QObject):
    """Controller class for prompt generation operations.
    
    This class handles the business logic for prompt generation and bridges
    the UI layer with the data model and template engine. It provides signals to notify
    the UI of generation results and slots to handle UI actions.
    """
    
    # Signals to notify the UI of generation results
    promptGenerated = pyqtSignal(str, object)  # Emitted when a prompt is generated (text, prompt_id)
    error = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, repository, template_engine=None):
        """Initialize the controller with a repository and template engine.
        
        Args:
            repository: The prompt repository
            template_engine (TemplateEngine, optional): The template engine to use
        """
        super().__init__()
        self.repository = repository
        self.template_engine = template_engine or TemplateEngine()
        
        logger.info("GenerationController initialized with repository and template engine")
    
    @pyqtSlot(int, dict)
    def generate_from_prompt_id(self, prompt_id: int, variables: Dict[str, Any]) -> Optional[str]:
        """Generate a prompt from a prompt ID with variable substitution.
        
        Args:
            prompt_id (int): The ID of the prompt to generate
            variables (dict): Variables to substitute in the prompt template
            
        Returns:
            str: The generated prompt text, or None if an error occurred
        """
        try:
            logger.debug(f"Generating prompt from ID: {prompt_id}")
            prompt = self.repository.get_by_id(prompt_id)
            
            if not prompt:
                error_msg = f"Prompt with ID {prompt_id} not found"
                logger.warning(error_msg)
                self.error.emit(error_msg)
                return None
                
            return self.generate_from_prompt(prompt, variables)
            
        except Exception as e:
            error_msg = f"Error generating prompt from ID {prompt_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            return None
    
    @pyqtSlot(object, dict)
    def generate_from_prompt(self, prompt: Prompt, variables: Dict[str, Any]) -> Optional[str]:
        """Generate a prompt from a Prompt object with variable substitution.
        
        Args:
            prompt (Prompt): The prompt object to generate from
            variables (dict): Variables to substitute in the prompt template
            
        Returns:
            str: The generated prompt text, or None if an error occurred
        """
        try:
            logger.debug(f"Generating prompt from Prompt object: {prompt._title}")
            
            # Get the template from the prompt content
            template = prompt._content
            
            # Render the template with the variables
            result = self.template_engine.render(template, variables)
            
            # Emit the generated prompt
            self.promptGenerated.emit(result, prompt._id)
            
            logger.info(f"Successfully generated prompt from {prompt._title}")
            return result
            
        except Exception as e:
            error_msg = f"Error generating prompt: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            return None
    
    @pyqtSlot(str, dict)
    def generate_from_template(self, template: str, variables: Dict[str, Any]) -> Optional[str]:
        """Generate a prompt from a template string with variable substitution.
        
        Args:
            template (str): The template string to generate from
            variables (dict): Variables to substitute in the template
            
        Returns:
            str: The generated prompt text, or None if an error occurred
        """
        try:
            logger.debug("Generating prompt from template string")
            
            # Render the template with the variables
            result = self.template_engine.render(template, variables)
            
            # Emit the generated prompt (with None as prompt_id since it's a custom template)
            self.promptGenerated.emit(result, None)
            
            logger.info("Successfully generated prompt from template string")
            return result
            
        except Exception as e:
            error_msg = f"Error generating prompt from template: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            return None
    
    @pyqtSlot(int)
    def get_available_variables(self, prompt_id: int) -> List[str]:
        """Get the available variables for a prompt.
        
        Args:
            prompt_id (int): The ID of the prompt
            
        Returns:
            list: A list of variable names available for the prompt
        """
        try:
            logger.debug(f"Getting available variables for prompt ID: {prompt_id}")
            prompt = self.repository.get_by_id(prompt_id)
            
            if not prompt:
                logger.warning(f"Prompt with ID {prompt_id} not found")
                return []
                
            # Check if the prompt has predefined variables in metadata
            if prompt._metadata and "variables" in prompt._metadata:
                return prompt._metadata["variables"]
                
            # Otherwise, extract variables from the template
            return self.extract_variables_from_template(prompt._content)
            
        except Exception as e:
            logger.error(f"Error getting variables for prompt ID {prompt_id}: {str(e)}", exc_info=True)
            return []
    
    def extract_variables_from_template(self, template: str) -> List[str]:
        """Extract variables from a template string.
        
        Args:
            template (str): The template string to extract variables from
            
        Returns:
            list: A list of variable names found in the template
        """
        try:
            logger.debug("Extracting variables from template string")
            return self.template_engine.extract_variables(template)
            
        except Exception as e:
            logger.error(f"Error extracting variables from template: {str(e)}", exc_info=True)
            return [] 