# Code Style Guide

## Overview

This document outlines coding style conventions for the Prometheus AI Prompt Generator project. Following these guidelines ensures code consistency, readability, and maintainability across the codebase.

## Python Style Guidelines

### General Python Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for general Python style
- Use [PEP 484](https://www.python.org/dev/peps/pep-0484/) type hints for function signatures
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use docstrings following [PEP 257](https://www.python.org/dev/peps/pep-0257/)

### Naming Conventions

#### Variables and Functions

- Use `snake_case` for variables and functions
- Names should be descriptive and clear about purpose
- Avoid single-letter variable names except for counters and coordinates

```python
# Good
user_id = get_user_id_from_request(request)
filtered_prompts = filter_prompts_by_type(prompts, prompt_type)

# Bad
uid = get_uid(req)
fps = filter(ps, pt)
```

#### Classes

- Use `PascalCase` for class names
- Class names should be nouns or noun phrases
- Use singular form for class names

```python
# Good
class PromptRepository:
    pass

class UserService:
    pass

# Bad
class handle_prompts:
    pass

class Prompts:  # Plural
    pass
```

#### Constants

- Use `UPPER_CASE_WITH_UNDERSCORES` for constants
- Constants should be defined at the module level

```python
# Good
MAX_PROMPT_LENGTH = 1000
DEFAULT_TIMEOUT_SECONDS = 30

# Bad
MaxPromptLength = 1000
defaultTimeout = 30
```

#### Protected and Private Attributes

- Use a single underscore for protected attributes/methods (`_protected`)
- Use double underscore for private attributes/methods (`__private`)

```python
class User:
    def __init__(self, username, password):
        self.username = username  # Public
        self._last_login = None   # Protected
        self.__password = password  # Private
```

### Code Organization

#### Imports

- Imports should be grouped in this order:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports
- Each group should be separated by a blank line
- Imports within each group should be alphabetized

```python
# Standard library imports
import os
import sys
import time
from datetime import datetime

# Third-party imports
import numpy as np
import pytest
from PyQt5 import QtWidgets

# Local application imports
from prometheus_prompt_generator.data.repositories import PromptRepository
from prometheus_prompt_generator.domain.models import Prompt
```

#### Module Structure

A typical module should have the following structure:

1. Module docstring
2. Imports (as described above)
3. Module-level constants
4. Class definitions
5. Function definitions
6. Main execution code (if applicable)

```python
"""
Module for handling prompt operations.

This module provides classes and functions for creating, updating, 
and retrieving prompts from the database.
"""

# Imports
import sqlite3
from typing import List, Optional

# Constants
MAX_TITLE_LENGTH = 100
DEFAULT_PROMPT_TYPE = "instruction"

# Classes
class PromptService:
    """Service for handling prompt operations."""
    # Class implementation...

# Functions
def format_prompt_content(content: str) -> str:
    """Format the prompt content for display."""
    # Function implementation...

# Main execution (if applicable)
if __name__ == "__main__":
    service = PromptService()
    # ...
```

### Function and Method Guidelines

#### Function Definitions

- Keep functions focused on a single responsibility
- Use type hints for parameters and return values
- Include docstrings for all functions except simple ones
- Default parameter values should follow type hints

```python
def get_prompt_by_id(prompt_id: int, include_tags: bool = False) -> Optional[Prompt]:
    """
    Retrieve a prompt by its ID.
    
    Args:
        prompt_id: The ID of the prompt to retrieve
        include_tags: Whether to include associated tags
        
    Returns:
        The Prompt object if found, None otherwise
    """
    # Implementation...
```

#### Method Order in Classes

Methods in a class should be organized in the following order:

1. `__init__` and other special methods
2. Public methods
3. Protected methods (prefixed with `_`)
4. Private methods (prefixed with `__`)
5. Properties and static methods

### Comments and Documentation

#### Docstrings

- Use triple double quotes (`"""`) for docstrings
- Module docstrings should describe the purpose and contents of the module
- Class docstrings should describe the purpose and behavior of the class
- Function/method docstrings should describe:
  - What the function does
  - Parameters (with types and descriptions)
  - Return values (with types and descriptions)
  - Exceptions raised

```python
def validate_prompt(prompt_data: dict) -> List[str]:
    """
    Validate prompt data against business rules.
    
    Args:
        prompt_data: Dictionary containing prompt attributes
            Must include 'title' and 'content' keys
            
    Returns:
        List of validation error messages, empty if valid
        
    Raises:
        ValueError: If prompt_data is None
    """
    if prompt_data is None:
        raise ValueError("Prompt data cannot be None")
        
    errors = []
    # Validation logic...
    return errors
```

#### Comments

- Use comments sparingly and only when necessary to explain complex code
- Comments should explain "why" rather than "what" the code is doing
- Keep comments up to date when modifying code

```python
# Good comment - explains the rationale
# Using a threshold of 5 seconds based on user experience research
TIMEOUT_THRESHOLD = 5

# Bad comment - obvious from the code
# Set the user's name
user.name = input_name
```

### Error Handling

- Use specific exception types rather than catching all exceptions
- Handle exceptions at the appropriate level of abstraction
- Log exceptions with useful context
- Clean up resources in `finally` blocks or use context managers

```python
def get_prompt_from_database(prompt_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Prompt(**row)
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving prompt {prompt_id}: {e}")
        raise RepositoryError(f"Failed to retrieve prompt: {e}") from e
    finally:
        cursor.close()
```

## SQL Style Guidelines

- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Include appropriate comments for complex queries
- Format queries for readability with line breaks and indentation

```sql
-- Good
SELECT 
    p.id, 
    p.title, 
    p.content,
    COUNT(pu.id) AS usage_count
FROM 
    Prompts p
LEFT JOIN 
    PromptUsage pu ON p.id = pu.prompt_id
WHERE 
    p.type = 'instruction'
GROUP BY 
    p.id
ORDER BY 
    usage_count DESC;

-- Bad
select p.id,p.title,p.content,count(pu.id) as usage_count from Prompts p left join PromptUsage pu on p.id=pu.prompt_id where p.type='instruction' group by p.id order by usage_count desc;
```

## Qt/UI Style Guidelines

### Qt Class Naming

- Use `PascalCase` for Qt classes
- Suffix classes with their Qt base class (e.g., `PromptListWidget`, `MainWindow`)

```python
# Good
class PromptEditorDialog(QDialog):
    pass

class CategorySelectionWidget(QWidget):
    pass

# Bad
class promptEditor(QDialog):
    pass

class CategorySelection:  # Missing base class suffix
    pass
```

### UI Component Naming

- Use descriptive names for UI components that include their type
- Follow this format: `purpose_componentType`

```python
# Good
self.prompt_list = QListWidget()
self.save_button = QPushButton("Save")
self.title_label = QLabel("Title:")
self.content_text_edit = QTextEdit()

# Bad
self.list = QListWidget()  # Too generic
self.button = QPushButton("Save")  # What does this button do?
self.label = QLabel("Title:")  # Which label is this?
self.text = QTextEdit()  # Too generic
```

### Signal and Slot Naming

- Slots that handle signals should be named `on_*` or `handle_*`
- Custom signals should clearly describe the event they represent

```python
class PromptEditor(QWidget):
    # Signal naming
    promptSaved = pyqtSignal(Prompt)
    validationFailed = pyqtSignal(list)  # list of error messages
    
    def __init__(self):
        super().__init__()
        # Signal-slot connections
        self.save_button.clicked.connect(self.on_save_clicked)
        
    # Slot naming
    def on_save_clicked(self):
        # Handle save button click
        pass
        
    def on_validation_failed(self, errors):
        # Handle validation failures
        pass
```

## Testing Guidelines

### Test File Organization

- Place test files in a `tests` directory that mirrors the project structure
- Name test files `test_*.py` to be discovered by pytest
- One test file per module being tested

```
prometheus_prompt_generator/
  └── services/
      └── prompt_service.py
      
tests/
  └── services/
      └── test_prompt_service.py
```

### Test Function Naming

- Test function names should clearly describe what they're testing
- Format: `test_<function>_<scenario>_<expected_result>`

```python
# Good
def test_create_prompt_with_valid_data_returns_prompt_with_id():
    pass
    
def test_create_prompt_with_invalid_data_raises_validation_error():
    pass

# Bad
def test_create_prompt():  # Too vague
    pass
    
def test_prompt_creation_scenario_1():  # Not descriptive
    pass
```

### Test Structure

- Use the AAA (Arrange, Act, Assert) pattern for test structure
- Use pytest's built-in assert statements
- Create helper functions for common setup tasks

```python
def test_get_prompt_by_id_existing_prompt_returns_prompt():
    # Arrange
    prompt_id = 1
    expected_title = "Test Prompt"
    mock_repository = MockPromptRepository()
    mock_repository.add_prompt(Prompt(id=prompt_id, title=expected_title))
    service = PromptService(mock_repository)
    
    # Act
    result = service.get_prompt_by_id(prompt_id)
    
    # Assert
    assert result is not None
    assert result.id == prompt_id
    assert result.title == expected_title
```

## Version Control Guidelines

### Commit Messages

- Use clear, descriptive commit messages
- Follow the format: `<type>: <subject>`
- Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Keep subject line under 50 characters
- Use imperative mood ("Add feature" not "Added feature")

```
# Good
feat: add prompt scoring functionality
fix: correct SQL query in PromptRepository
docs: update installation instructions

# Bad
updated code
fixes
WIP
```

### Branching Strategy

- `main` branch should always be stable
- Create feature branches for new work
- Use the format `feature/<feature-name>` or `bugfix/<bug-description>`
- Merge via pull request after code review and testing

## Documentation Guidelines

### Code Documentation

- All modules, classes, methods, and functions should be documented with docstrings
- Include examples for complex functions
- Document parameters, return values, and exceptions

### Project Documentation

- Keep README up to date with current installation and usage instructions
- Document architectural decisions in appropriate documentation files
- Update API documentation when endpoints change
- Include diagrams for complex workflows

## Conclusion

This style guide aims to create a consistent, readable, and maintainable codebase. While it's comprehensive, the guiding principle is clarity and consistency. When in doubt, maintain the style of the surrounding code.

Tools like `pylint`, `flake8`, and `black` can help enforce many of these standards automatically. Consider setting up pre-commit hooks to check code style before commits.

Last updated: March 9, 2025 