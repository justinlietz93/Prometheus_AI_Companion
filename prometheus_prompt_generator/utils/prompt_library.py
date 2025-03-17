"""
Prometheus AI Prompt Library

A module for managing AI prompts of different types.
"""

import os
import json
from .constants import (DEFAULT_AUTHOR, DEFAULT_VERSION, 
                      DEFAULT_CREATED_DATE, DEFAULT_UPDATED_DATE, DEFAULT_TAGS)

class PromptLibrary:
    """A library for managing AI prompts of different types.
    
    This class provides functionality to load, retrieve, save, and delete prompts.
    It includes a fallback set of sample prompts if no external prompts are available.
    """
    
    def __init__(self):
        """Initialize the prompt library with sample prompts."""
        self.prompts = {}
        self.library_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "prompt_library", "prompts")
        
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
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
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
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
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
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
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
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
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
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["network", "technical", "configuration"]
                }
            },
            "Motivation": {
                "title": "Motivation Prompt",
                "description": "An inspiring prompt for motivation and encouragement",
                "template": "Create a motivational message for someone facing {challenge}. Your message should:\n\n1. Acknowledge the difficulty of the situation\n2. Provide genuine encouragement\n3. Offer practical steps forward\n4. Include relevant inspirational examples or quotes\n5. End with a powerful call to action\n\nThe tone should be supportive but not patronizing, and realistic without being pessimistic.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["motivation", "inspiration", "encouragement"]
                }
            },
            "api": {
                "title": "API Design Prompt",
                "description": "A technical prompt for designing and implementing APIs",
                "template": "Design a RESTful API for {service_description}. Your API design should include:\n\n1. Endpoint definitions with paths and HTTP methods\n2. Request and response formats (JSON schema)\n3. Authentication and authorization mechanisms\n4. Error handling and status codes\n5. Rate limiting and versioning strategy\n\nProvide example requests and responses for common operations, and documentation for integrating with the API.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE, 
                    "tags": ["api", "backend", "web development"]
                }
            },
            "auth": {
                "title": "Authentication System Prompt",
                "description": "A technical prompt for designing authentication systems",
                "template": "Design an authentication system for {application_type}. Your design should:\n\n1. Choose appropriate authentication methods (username/password, OAuth, JWT, etc.)\n2. Include secure password handling and storage\n3. Implement MFA or 2FA where appropriate\n4. Consider session management and timeout policies\n5. Address security considerations to prevent common attacks\n\nProvide a detailed overview of the system architecture and implementation steps.",
                "metadata": {
                    "author": DEFAULT_AUTHOR, 
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["security", "authentication", "system design"]
                }
            },
            "best_practices": {
                "title": "Best Practices Prompt",
                "description": "A guide for implementing best practices in a specific domain",
                "template": "Outline the best practices for {practice_area} in {industry}. Include:\n\n1. Industry standards and guidelines\n2. Common pitfalls and how to avoid them\n3. Tools and frameworks that support these best practices\n4. Metrics for measuring adherence to these practices\n5. Examples of successful implementations\n\nEnsure the advice is practical, actionable, and aligned with current industry trends.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["best practices", "guidelines", "standards"]
                }
            },
            "build": {
                "title": "Build System Prompt",
                "description": "A technical prompt for designing and configuring build systems",
                "template": "Design a build system for a {project_type} using {technology_stack}. Your solution should:\n\n1. Automate compilation and packaging processes\n2. Include dependency management\n3. Implement testing and validation steps\n4. Support different environments (dev, test, prod)\n5. Optimize for build speed and reliability\n\nProvide configuration examples and explain the rationale behind key decisions.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["build", "ci/cd", "devops"]
                }
            },
            "code_review": {
                "title": "Code Review Prompt",
                "description": "A guide for conducting thorough code reviews",
                "template": "Perform a comprehensive code review of the following {language} code:\n\n```\n{code_snippet}\n```\n\nYour review should address:\n\n1. Code quality and readability\n2. Potential bugs or edge cases\n3. Performance optimizations\n4. Security vulnerabilities\n5. Adherence to language conventions and best practices\n\nProvide specific, actionable feedback with examples of how to improve the code.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["code review", "quality assurance", "programming"]
                }
            },
            "continue": {
                "title": "Continuation Prompt",
                "description": "A prompt to continue from previous content",
                "template": "Continue the following {content_type} based on what has been provided so far:\n\n{initial_content}\n\nYour continuation should:\n\n1. Maintain the same style, tone, and format\n2. Build logically on the ideas presented\n3. Add new valuable information or development\n4. Ensure coherence with the existing content\n5. Bring the piece to a satisfying conclusion if appropriate\n\nThe continuation should feel seamless as if written by the same author.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["continuation", "writing", "content generation"]
                }
            },
            "database": {
                "title": "Database Design Prompt",
                "description": "A technical prompt for database design and implementation",
                "template": "Design a database schema for {application_purpose}. Your design should:\n\n1. Include entity-relationship diagrams\n2. Define tables, columns, and data types\n3. Specify primary and foreign keys\n4. Consider normalization and performance\n5. Include indexing strategy\n\nProvide SQL DDL statements for creating the schema and explain your design decisions.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["database", "schema design", "SQL"]
                }
            },
            "data_pipeline": {
                "title": "Data Pipeline Prompt",
                "description": "A guide for designing efficient data pipelines",
                "template": "Design a data pipeline for {data_source} to {data_destination} that handles {data_volume} of data. Your solution should include:\n\n1. Data extraction methods from the source\n2. Transformation and processing steps\n3. Loading process into the destination\n4. Error handling and data validation\n5. Monitoring and maintenance strategy\n\nConsider scalability, reliability, and latency requirements in your design.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["data engineering", "ETL", "data processing"]
                }
            },
            "debugging": {
                "title": "Debugging Prompt",
                "description": "A systematic approach to debugging technical issues",
                "template": "Help me debug the following issue in my {language} application:\n\n{issue_description}\n\nError message: {error_message}\n\nCode snippet:\n```\n{code_snippet}\n```\n\nPlease provide:\n\n1. Analysis of the potential causes\n2. Systematic steps to isolate the issue\n3. Possible solutions with examples\n4. Prevention strategies for similar issues\n5. Debugging tools or techniques that could help\n\nFocus on practical advice that I can apply immediately.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["debugging", "troubleshooting", "error handling"]
                }
            },
            "deductive_reasoning": {
                "title": "Deductive Reasoning Prompt",
                "description": "A prompt for solving problems through logical deduction",
                "template": "Using deductive reasoning, analyze the following situation or problem:\n\n{situation_or_problem}\n\nYour analysis should:\n\n1. Identify the given facts and premises\n2. Apply logical rules and principles\n3. Draw step-by-step inferences\n4. Arrive at a logical conclusion\n5. Identify any assumptions made in your reasoning\n\nPresent your reasoning in a clear, structured format showing how each conclusion follows from the premises.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["logic", "reasoning", "problem-solving"]
                }
            },
            "deployment": {
                "title": "Deployment Strategy Prompt",
                "description": "A guide for planning and executing deployments",
                "template": "Design a deployment strategy for {application_type} to {environment}. Your strategy should include:\n\n1. Deployment process and steps\n2. Required infrastructure and resources\n3. Rollback plan and disaster recovery\n4. Testing and validation procedures\n5. Monitoring and post-deployment support\n\nAddress potential risks and how they will be mitigated, and include a timeline for the deployment.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["deployment", "devops", "operations"]
                }
            },
            "example": {
                "title": "Example Creation Prompt",
                "description": "A prompt for generating clear, instructive examples",
                "template": "Create {number} practical examples demonstrating {concept} in {context}. For each example:\n\n1. Provide a realistic scenario or use case\n2. Include step-by-step implementation details\n3. Explain why this is an effective implementation\n4. Highlight potential variations or adaptations\n5. Note common mistakes to avoid\n\nEnsure the examples range from simple to complex and cover different aspects of the concept.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION, 
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["examples", "learning", "explanation"]
                }
            },
            "fix_immediate_problem": {
                "title": "Emergency Fix Prompt",
                "description": "A guide for implementing quick fixes to critical issues",
                "template": "Provide an immediate solution to fix the following critical issue in my {system_or_application}:\n\n{issue_description}\n\nYour solution should:\n\n1. Address the immediate problem to restore functionality\n2. Require minimal changes to implement quickly\n3. Consider potential side effects of the fix\n4. Include clear implementation instructions\n5. Suggest follow-up actions for a more permanent solution\n\nThis is an urgent situation, so prioritize speed and reliability in your approach.",
                "metadata": {
                    "author": DEFAULT_AUTHOR,
                    "version": DEFAULT_VERSION,
                    "created": DEFAULT_CREATED_DATE,
                    "updated": DEFAULT_UPDATED_DATE,
                    "tags": ["hotfix", "emergency", "troubleshooting"]
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
        """Get a prompt by type.
        
        Args:
            prompt_type (str): The type of prompt to retrieve
            default (dict, optional): Default value if prompt not found. Defaults to None.
            
        Returns:
            dict: The prompt data or default value
        """
        result = None
        
        # First try exact match
        if prompt_type in self.prompts:
            result = self.prompts[prompt_type]
        else:
            # If not found, try case-insensitive search
            for key in self.prompts:
                if key.lower() == prompt_type.lower():
                    result = self.prompts[key]
                    break
        
        # If still not found, return default
        if result is None:
            return default or {}
            
        # Check if we need to convert from old format to new format
        if "template" not in result and "prompts" in result:
            # This is the old format with urgency levels
            # Convert to new format by using the highest urgency level (10) as template
            level_10 = "10"
            if level_10 in result["prompts"]:
                template = result["prompts"][level_10]
            else:
                # Use the highest available level
                available_levels = list(result["prompts"].keys())
                if available_levels:
                    highest_level = max(available_levels, key=lambda x: int(x) if x.isdigit() else 0)
                    template = result["prompts"][highest_level]
                else:
                    template = ""
                    
            # Create a new format prompt with the extracted template
            new_format = {
                "title": result.get("name", prompt_type).title() + " Prompt",
                "description": result.get("description", ""),
                "template": template,
                "metadata": result.get("metadata", {})
            }
            
            # Update in-memory cache for future calls
            self.prompts[prompt_type] = new_format
            
            return new_format
                
        return result
    
    def get_types(self):
        """Return all prompt types.
        
        Returns:
            list: List of prompt type names
        """
        return list(self.prompts.keys())
    
    def save_prompt(self, prompt_type, prompt_data):
        """Save a prompt to the library.
        
        Args:
            prompt_type (str): The type identifier for the prompt
            prompt_data (dict): The prompt data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
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
        """Delete a prompt from the library.
        
        Args:
            prompt_type (str): The type identifier for the prompt to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
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