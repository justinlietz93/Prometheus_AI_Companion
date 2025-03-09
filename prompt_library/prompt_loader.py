#!/usr/bin/env python3
"""
Prompt Loader

This module provides functionality to load prompt data from JSON files
in the prompt library directory.
"""

import os
import json
import glob

class PromptLibrary:
    """A class for loading and accessing prompts from the prompt library"""
    
    def __init__(self, library_dir="prompt_library/prompts"):
        """Initialize the prompt library with the directory containing prompt files"""
        self.library_dir = library_dir
        self.prompts = {}
        self.load_all_prompts()
        
    def load_all_prompts(self):
        """Load all prompt JSON files from the library directory"""
        # Clear existing prompts
        self.prompts = {}
        
        # Find all JSON files in the library directory
        json_pattern = os.path.join(self.library_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        # Load each file
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)
                    
                # Store the prompt data by name
                if "name" in prompt_data and "prompts" in prompt_data:
                    self.prompts[prompt_data["name"]] = prompt_data
            except Exception as e:
                print(f"Error loading prompt file {json_file}: {str(e)}")
                
        return self.prompts
    
    def get_prompt_types(self):
        """Get a list of all available prompt types"""
        return list(self.prompts.keys())
    
    def get_prompt(self, prompt_type, level):
        """Get a specific prompt by type and urgency level"""
        if prompt_type not in self.prompts:
            return f"Error: Prompt type '{prompt_type}' not found"
            
        try:
            level = int(level)
            level_str = str(level)
            
            # Check if the level exists in the prompts
            if level_str in self.prompts[prompt_type]["prompts"]:
                return self.prompts[prompt_type]["prompts"][level_str]
            elif level in self.prompts[prompt_type]["prompts"]:
                return self.prompts[prompt_type]["prompts"][level]
            else:
                return f"Error: Level {level} not found for prompt type '{prompt_type}'"
        except ValueError:
            return "Error: Level must be an integer between 1 and 10"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_prompt_description(self, prompt_type):
        """Get the description of a prompt type"""
        if prompt_type not in self.prompts:
            return ""
            
        return self.prompts[prompt_type].get("description", "")
        
    def get_prompt_metadata(self, prompt_type):
        """Get metadata for a prompt type
        
        Returns a dictionary with metadata or empty dict if no metadata exists
        """
        if prompt_type not in self.prompts:
            return {}
            
        return self.prompts[prompt_type].get("metadata", {})
        
    def get_prompt_tags(self, prompt_type):
        """Get tags for a prompt type
        
        Returns a list of tags or empty list if no tags exist
        """
        metadata = self.get_prompt_metadata(prompt_type)
        return metadata.get("tags", [])
        
    def add_custom_prompt(self, prompt_type, description, prompts=None):
        """Add a custom prompt to the library
        
        Args:
            prompt_type (str): The type/name of the prompt
            description (str): The description of the prompt
            prompts (dict, optional): Dictionary of prompts by level. Defaults to a basic template.
            
        Returns:
            bool: True if prompt was added successfully, False otherwise
        """
        # Create basic template if no prompts provided
        if prompts is None:
            prompts = {
                "1": f"Standard {prompt_type} prompt.",
                "5": f"Enhanced {prompt_type} prompt with more detail.",
                "10": f"Comprehensive {prompt_type} prompt with maximum detail and urgency."
            }
            
        # Create the prompt data structure
        prompt_data = {
            "name": prompt_type,
            "description": description,
            "prompts": prompts,
            "metadata": {
                "custom": True,
                "tags": ["custom"]
            }
        }
        
        # Add to in-memory prompts
        self.prompts[prompt_type] = prompt_data
        
        # Save to file
        try:
            file_path = os.path.join(self.library_dir, f"{prompt_type}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving custom prompt: {str(e)}")
            return False 