"""
Prompt Generator Controller for Prometheus AI Prompt Generator

This module handles the logic for generating prompts based on templates
and user-provided variables.
"""

@pyqtSlot(str, int, dict, result=str)
def generate_from_type(self, prompt_type, urgency_level=10, variables=None):
    """
    Generate a prompt from a prompt type using a specific urgency level.
    
    Args:
        prompt_type (str): The type of prompt to generate
        urgency_level (int): Urgency level (1-10), defaults to 10
        variables (dict): Dictionary of variables for the template
        
    Returns:
        str: The generated prompt text or error message
    """
    if variables is None:
        variables = {}
        
    try:
        # First try to get the prompt from the repository
        prompt = self.repository.get_by_type(prompt_type)
        if not prompt:
            return f"Error: Prompt type '{prompt_type}' not found"
            
        # If this prompt uses urgency levels, get the appropriate level content
        if prompt.get("uses_urgency_levels"):
            prompt = self.repository.get_prompt_with_urgency_level(prompt["id"], urgency_level)
            if not prompt:
                return f"Error: Failed to get urgency level {urgency_level} for prompt type '{prompt_type}'"
        
        # Now generate using the template
        template = prompt["template"]
        return self.template_engine.render(template, variables)
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
        self.generationError.emit(str(e))
        return f"Error generating prompt: {str(e)}" 