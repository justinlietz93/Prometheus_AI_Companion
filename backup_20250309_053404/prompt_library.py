#!/usr/bin/env python3
"""
Prometheus AI Prompt Library

A module for managing AI prompts of different types.
"""

import os
import json
from constants import DEFAULT_AUTHOR, DEFAULT_VERSION, DEFAULT_TAGS

class PromptLibrary:
    """A library for managing AI prompts of different types."""
    
    def __init__(self):
        """Initialize the prompt library with sample prompts."""
        self.prompts = {}
        self.library_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt_library/prompts")
        
        # Create directory if it doesn't exist
        os.makedirs(self.library_dir, exist_ok=True)
        
        # Load sample prompts as fallback
        self._load_sample_prompts()
        
        # Try to load prompts from disk if available
        self._load_from_disk()
    
    def _load_sample_prompts(self):
        """Load sample prompts to ensure the application runs without external dependencies."""
        self.prompts = {
            "Research": {
                "title": "Research Prompt",
                "description": "A detailed prompt for conducting research on a given topic",
                "template": "Conduct a comprehensive research on {topic}. Include the following sections:\n\n1. Historical background\n2. Current state\n3. Future trends\n4. Key figures\n5. Major debates\n\nProvide specific details, examples, and cite reliable sources.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["research", "academic", "information gathering"]
                }
            },
            "Development": {
                "title": "Development Prompt",
                "description": "A structured prompt for software development tasks",
                "template": "Develop a {language} solution for {problem}. Your solution should:\n\n1. Be efficient and scalable\n2. Include error handling\n3. Be well-documented\n4. Follow best practices for {language}\n5. Include tests\n\nProvide the complete code with explanations for key sections.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["development", "coding", "programming"]
                }
            },
            "Design": {
                "title": "Design Prompt",
                "description": "A creative prompt for design tasks",
                "template": "Design a {design_type} for {purpose}. Your design should:\n\n1. Be visually appealing and original\n2. Communicate the intended message clearly\n3. Be suitable for the target audience\n4. Be adaptable to different formats\n5. Follow current design trends while remaining timeless\n\nProvide a detailed description of your design, including color scheme, typography, and key elements.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["design", "creative", "visual"]
                }
            },
            "Performance Analysis": {
                "title": "Performance Analysis Prompt",
                "description": "A analytical prompt for evaluating system or process performance",
                "template": "Conduct a thorough performance analysis of {system_or_process}. Your analysis should:\n\n1. Identify performance bottlenecks\n2. Measure key performance indicators\n3. Compare against industry benchmarks\n4. Recommend optimization strategies\n5. Prioritize improvements by impact and effort\n\nProvide quantitative data where possible and justify your recommendations.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["analysis", "performance", "optimization"]
                }
            },
            "Network": {
                "title": "Network Configuration Prompt",
                "description": "A technical prompt for network setup and troubleshooting",
                "template": "Provide a detailed plan for {network_task} in a {environment_type} environment. Include:\n\n1. Required hardware and software\n2. Step-by-step configuration instructions\n3. Security considerations\n4. Testing procedures\n5. Common issues and solutions\n\nEnsure the solution is robust, secure, and follows industry best practices.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["network", "technical", "configuration"]
                }
            },
            "Motivate": {
                "title": "Motivation Prompt",
                "description": "An inspiring prompt for motivation and encouragement",
                "template": "Create a motivational message for someone facing {challenge}. Your message should:\n\n1. Acknowledge the difficulty of the situation\n2. Provide genuine encouragement\n3. Offer practical steps forward\n4. Include relevant inspirational examples or quotes\n5. End with a powerful call to action\n\nThe tone should be supportive but not patronizing, and realistic without being pessimistic.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": "2025-03-09",
                    "updated": "2025-03-09",
                    "tags": ["motivation", "inspiration", "encouragement"]
                }
            }
        }
    
    def _load_from_disk(self):
        """Load prompts from disk if available."""
        try:
            if os.path.exists(self.library_dir):
                for filename in os.listdir(self.library_dir):
                    if filename.endswith(".json"):
                        prompt_type = os.path.splitext(filename)[0]
                        with open(os.path.join(self.library_dir, filename), 'r', encoding='utf-8') as f:
                            self.prompts[prompt_type] = json.load(f)
        except Exception as e:
            print(f"Error loading prompts from disk: {e}")
    
    def get(self, prompt_type, default=None):
        """Get a prompt by type."""
        return self.prompts.get(prompt_type, default or {})
    
    def get_types(self):
        """Return all prompt types."""
        return list(self.prompts.keys())
    
    def save_prompt(self, prompt_type, prompt_data):
        """Save a prompt to the library."""
        self.prompts[prompt_type] = prompt_data
        
        # Save to file
        try:
            file_path = os.path.join(self.library_dir, f"{prompt_type}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving prompt: {e}")
            return False
            
    def delete_prompt(self, prompt_type):
        """Delete a prompt from the library."""
        if prompt_type in self.prompts:
            del self.prompts[prompt_type]
            
            # Delete the file
            try:
                file_path = os.path.join(self.library_dir, f"{prompt_type}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error deleting prompt file: {e}")
        return False 