from abc import ABC, abstractmethod

class BasePrompt(ABC):
    """Base class for all prompt types"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.prompts = {}
        
    @abstractmethod
    def load_prompts(self):
        """Load prompts from source (to be implemented by subclasses)"""
        pass
        
    def get_prompt(self, level):
        """Get a prompt based on urgency level (1-10)"""
        if not isinstance(level, int) or not 1 <= level <= 10:
            return "Error: Please provide an integer between 1 and 10 for urgency level."
        
        return self.prompts.get(level, "Invalid level selected.")
    
    def get_name(self):
        """Get the prompt type name"""
        return self.name
        
    def get_description(self):
        """Get the prompt type description"""
        return self.description 