import os
import importlib.util
import inspect
import sys
import re

class PromptManager:
    """Manager for handling all prompt types in the system"""
    
    def __init__(self):
        self.prompts = {}
        self.prompt_files = []
        
    def discover_prompt_files(self):
        """Scan the root directory for prompt Python files"""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompt_files = []
        
        # Find all potential prompt files in the root directory
        for file in os.listdir(root_dir):
            if file.endswith("_prompt.py") and file != "base_prompt.py":
                self.prompt_files.append(os.path.join(root_dir, file))
                
        return self.prompt_files
    
    def load_prompt_file(self, file_path):
        """Load a prompt file directly using its generate_*_prompt function"""
        prompt_name = os.path.basename(file_path).replace(".py", "")
        scenario = prompt_name.replace("_prompt", "")
        
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(prompt_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for the generate_*_prompt function
        function_name = f"generate_{scenario}_prompt"
        if hasattr(module, function_name):
            return {
                "name": scenario,
                "file": file_path,
                "function": getattr(module, function_name)
            }
        return None
    
    def load_all_prompts(self):
        """Load all discovered prompt files"""
        self.discover_prompt_files()
        self.prompts = {}
        
        for file_path in self.prompt_files:
            prompt_info = self.load_prompt_file(file_path)
            if prompt_info:
                self.prompts[prompt_info["name"]] = prompt_info
                
        return self.prompts
    
    def get_prompt(self, prompt_type, level):
        """Get a specific prompt by type and urgency level"""
        if prompt_type not in self.prompts:
            return f"Error: Prompt type '{prompt_type}' not found."
            
        try:
            level = int(level)
            prompt_function = self.prompts[prompt_type]["function"]
            return prompt_function(level)
        except ValueError:
            return "Error: Level must be an integer between 1 and 10."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_available_prompt_types(self):
        """Get a list of all available prompt types"""
        return list(self.prompts.keys()) 