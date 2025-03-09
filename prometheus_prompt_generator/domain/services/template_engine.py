"""
Template Engine for the Prometheus AI Prompt Generator.

This module provides a template engine for rendering templates with variable substitution,
conditional logic, and filters. It is used by the GenerationController to generate
prompts from templates.
"""

import re
import logging
import jinja2

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Template engine for rendering templates with variable substitution.
    
    This class uses Jinja2 for template rendering and provides additional functionality
    for variable extraction and error handling.
    """
    
    def __init__(self):
        """Initialize the template engine with a Jinja2 environment."""
        self.env = jinja2.Environment(
            # Add autoescape for security
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            # Keep whitespace and newlines
            trim_blocks=False,
            lstrip_blocks=False,
            # Custom filters can be added here
            extensions=['jinja2.ext.loopcontrols']
        )
        logger.info("TemplateEngine initialized with Jinja2 environment")
    
    def render(self, template, variables=None):
        """
        Render a template with the given variables.
        
        Args:
            template (str): The template to render
            variables (dict, optional): Variables to substitute in the template
            
        Returns:
            str: The rendered template
            
        Raises:
            ValueError: If the template contains syntax errors or required variables are missing
        """
        if variables is None:
            variables = {}
            
        try:
            # Create a Jinja2 template from the string
            jinja_template = self.env.from_string(template)
            
            # Check for missing variables (excluding loop variables)
            template_variables = self.extract_variables(template)
            
            # Filter out loop variables (those used in for loops)
            loop_vars = self._find_loop_variables(template)
            required_vars = [var for var in template_variables if var not in loop_vars]
            
            for var in required_vars:
                # Skip variables that have defaults in the template
                if f"{var} | default" not in template and var not in variables:
                    raise ValueError(f"Missing required variable: {var}")
            
            # Render the template with the variables
            result = jinja_template.render(**variables)
            return result
            
        except jinja2.exceptions.UndefinedError as e:
            # This occurs when a required variable is missing
            logger.error(f"Missing variable in template: {str(e)}")
            raise ValueError(f"Missing required variable: {str(e)}")
            
        except jinja2.exceptions.TemplateSyntaxError as e:
            # This occurs when the template has syntax errors
            logger.error(f"Template syntax error: {str(e)}")
            raise ValueError(f"Template syntax error: {str(e)}")
            
        except Exception as e:
            # Catch any other errors
            logger.error(f"Error rendering template: {str(e)}", exc_info=True)
            raise ValueError(f"Error rendering template: {str(e)}")
    
    def extract_variables(self, template):
        """
        Extract variables from a template.
        
        Args:
            template (str): The template to extract variables from
            
        Returns:
            list: A list of variable names found in the template
        """
        try:
            # Parse the template using Jinja's parser
            parsed_content = self.env.parse(template)
            
            # Find all variable nodes in the syntax tree
            variables = set()
            self._find_variables_in_node(parsed_content, variables)
            
            return list(variables)
        except Exception as e:
            logger.error(f"Error extracting variables from template: {str(e)}", exc_info=True)
            return []
    
    def _find_variables_in_node(self, node, variables):
        """
        Recursively find all variables in a Jinja2 syntax tree node.
        
        Args:
            node: A Jinja2 AST node
            variables (set): A set to collect variable names
        """
        # Process different types of nodes
        if hasattr(node, 'find_all'):
            # Find all name nodes
            for name_node in node.find_all(jinja2.nodes.Name):
                if name_node.name not in jinja2.defaults.DEFAULT_NAMESPACE:
                    variables.add(name_node.name)
            
            # Find all filter nodes (they may use variables)
            for filter_node in node.find_all(jinja2.nodes.Filter):
                if hasattr(filter_node, 'node') and isinstance(filter_node.node, jinja2.nodes.Name):
                    variables.add(filter_node.node.name)
            
            # Find all get attribute nodes for nested variables
            for getattr_node in node.find_all(jinja2.nodes.Getattr):
                if hasattr(getattr_node, 'node') and isinstance(getattr_node.node, jinja2.nodes.Name):
                    variables.add(getattr_node.node.name)
        
        # Process children recursively
        if hasattr(node, 'iter_child_nodes'):
            for child in node.iter_child_nodes():
                self._find_variables_in_node(child, variables)
    
    def _find_loop_variables(self, template):
        """
        Find variables used in for loops.
        
        Args:
            template (str): The template to analyze
            
        Returns:
            set: A set of variable names used as loop variables
        """
        try:
            # Use regex to find for loop constructs
            loop_vars = set()
            
            # Match {% for x in y %} pattern
            for_pattern = r'{%\s*for\s+([a-zA-Z0-9_]+)\s+in\s+([a-zA-Z0-9_]+)\s*%}'
            for match in re.finditer(for_pattern, template):
                loop_vars.add(match.group(1))  # Add the loop variable (x)
            
            return loop_vars
        except Exception as e:
            logger.error(f"Error finding loop variables: {str(e)}", exc_info=True)
            return set() 