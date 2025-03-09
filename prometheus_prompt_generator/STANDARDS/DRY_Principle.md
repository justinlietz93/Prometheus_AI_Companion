# DRY Principle - Don't Repeat Yourself

## Overview

The DRY (Don't Repeat Yourself) principle states that:

> "Every piece of knowledge or logic must have a single, unambiguous representation within a system."

This principle helps reduce duplication, improve maintainability, and decrease the likelihood of bugs and inconsistencies. This document outlines how to apply DRY principles throughout the Prometheus AI Prompt Generator project.

## Key Concepts

### Knowledge Duplication vs. Code Duplication

- **Knowledge duplication** is the real target of DRY, not just identical code
- Knowledge includes business rules, algorithms, configurations, and domain concepts
- Sometimes similar code represents different knowledge and should not be combined
- Sometimes different code represents the same knowledge and should be unified

### When to Apply DRY

1. When the same business rule or logic appears in multiple places
2. When the same calculation is performed repeatedly
3. When the same data transformation occurs in multiple locations
4. When UI patterns and components are reproduced across views

### When NOT to Apply DRY

1. When forcing commonality between unrelated concepts
2. When abstraction would make the code less readable or maintainable
3. When the cost of the abstraction exceeds the benefit
4. When premature abstraction might limit future flexibility

## DRY Implementation Techniques

### Code Reuse Through Functions and Classes

Extract common logic into reusable functions:

```python
# Bad: Repetitive code
def validate_prompt_title(title):
    if not title:
        raise ValidationError("Title is required")
    if len(title) > 100:
        raise ValidationError("Title cannot exceed 100 characters")
        
def validate_category_name(name):
    if not name:
        raise ValidationError("Name is required")
    if len(name) > 100:
        raise ValidationError("Name cannot exceed 100 characters")

# Good: DRY approach
def validate_text_field(value, field_name, max_length=100):
    if not value:
        raise ValidationError(f"{field_name} is required")
    if len(value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
        
def validate_prompt_title(title):
    validate_text_field(title, "Title")
    
def validate_category_name(name):
    validate_text_field(name, "Name")
```

### Template Method Pattern

Use inheritance to share common behavior while allowing specialization:

```python
class BaseRepository:
    def __init__(self, connection):
        self.connection = connection
        
    def find_by_id(self, id):
        """Generic implementation for finding by ID"""
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_entity(row)
        
    def _row_to_entity(self, row):
        """Convert a database row to an entity - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement this method")
        
class PromptRepository(BaseRepository):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = "Prompts"
        
    def _row_to_entity(self, row):
        """Convert a prompt row to a Prompt entity"""
        return Prompt(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            type=row["type"],
            category_id=row["category_id"]
        )
```

### Utility Classes and Modules

Create dedicated utilities for common operations:

```python
# validators.py
class Validators:
    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def is_valid_url(url):
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, url))
        
# Usage elsewhere
if not Validators.is_valid_email(user_email):
    raise ValidationError("Invalid email address")
```

### Configuration over Code

Define configurations in a single place:

```python
# config.py
class AppConfig:
    # Database settings
    DB_PATH = "data/prometheus.db"
    
    # Validation rules
    MAX_PROMPT_TITLE_LENGTH = 100
    MAX_PROMPT_CONTENT_LENGTH = 10000
    MAX_TAG_LENGTH = 50
    
    # API settings
    API_TIMEOUT_SECONDS = 30
    API_RETRY_ATTEMPTS = 3
    
# Usage elsewhere in the code
def validate_prompt_title(title):
    if len(title) > AppConfig.MAX_PROMPT_TITLE_LENGTH:
        raise ValidationError(f"Title cannot exceed {AppConfig.MAX_PROMPT_TITLE_LENGTH} characters")
```

### Common UI Components

Build reusable UI components with consistent behavior:

```python
class LabeledTextField(QWidget):
    def __init__(self, parent=None, label="", max_length=None, required=False):
        super().__init__(parent)
        self.label = QLabel(label)
        self.textField = QLineEdit()
        self.required = required
        self.max_length = max_length
        
        if max_length:
            self.textField.setMaxLength(max_length)
            
        # Layout setup code
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.textField)
        self.setLayout(layout)
        
    def text(self):
        return self.textField.text()
        
    def setText(self, text):
        self.textField.setText(text)
        
    def validate(self):
        if self.required and not self.text():
            return False
        return True

# Usage in forms
class PromptForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title_field = LabeledTextField(
            label="Title",
            max_length=AppConfig.MAX_PROMPT_TITLE_LENGTH,
            required=True
        )
        
        self.description_field = LabeledTextField(
            label="Description",
            max_length=AppConfig.MAX_PROMPT_DESCRIPTION_LENGTH,
            required=False
        )
        
        # More form setup...
```

### Database Access Patterns

Use a consistent pattern for database access:

```python
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
        
    def get_connection(self):
        """Get the current connection or create a new one"""
        if self.conn is None:
            return self.connect()
        return self.conn
        
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def execute_query(self, query, params=()):
        """Execute a query and return the cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor
        
    def execute_many(self, query, params_list):
        """Execute many queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor
        
    def commit(self):
        """Commit changes to the database"""
        if self.conn:
            self.conn.commit()
            
    def rollback(self):
        """Rollback changes"""
        if self.conn:
            self.conn.rollback()
```

## Avoiding Over-Abstraction

While eliminating duplication is beneficial, it can be taken too far. Signs of over-application of DRY include:

1. **Excessive indirection**: Too many layers of abstraction making code hard to follow
2. **Premature generalization**: Creating complex abstractions before understanding all use cases
3. **Forced commonality**: Combining things that appear similar but have different semantics
4. **Abstraction complexity**: When the abstraction becomes more complex than the duplicated code

### Finding the Right Balance

1. **Rule of Three**: Wait until you've seen something repeated three times before abstracting
2. **Context Matters**: Consider if separate instances might evolve differently
3. **Readability First**: Only abstract if it makes the code more readable, not less
4. **YAGNI**: "You Aren't Gonna Need It" - don't build abstractions for anticipated future needs

## DRY in Different Project Aspects

### DRY in Models and Data Access

- Create base repository classes for common CRUD operations
- Implement shared validation logic
- Use ORM patterns consistently
- Create reusable data transformation utilities

### DRY in Business Logic

- Extract business rules into dedicated rules or service classes
- Create a consistent service pattern across the application
- Use strategy pattern for variant algorithms
- Implement chain of responsibility for multi-step processing

### DRY in User Interface

- Create a component library of reusable UI elements
- Use templates or layout managers consistently
- Standardize styles and appearance
- Implement shared input validation

### DRY in Testing

- Create test fixtures and factories
- Use parameterized tests for similar test cases
- Implement shared assertion helpers
- Create base test classes for common testing patterns

## Examples from Our Project

### Example 1: Validation Logic

```python
# validator.py - Central validation module
class PromptValidator:
    @staticmethod
    def validate_prompt(prompt_data):
        """Validate all prompt attributes"""
        errors = []
        
        # Title validation
        if not prompt_data.get('title'):
            errors.append('Title is required')
        elif len(prompt_data.get('title', '')) > 100:
            errors.append('Title cannot exceed 100 characters')
        
        # Content validation
        if not prompt_data.get('content'):
            errors.append('Content is required')
        elif len(prompt_data.get('content', '')) > 10000:
            errors.append('Content cannot exceed 10000 characters')
        
        # Type validation
        valid_types = ['instruction', 'character', 'scenario']
        if prompt_data.get('type') not in valid_types:
            errors.append(f'Type must be one of: {", ".join(valid_types)}')
        
        return errors
```

### Example 2: Database Connections

```python
# db_manager.py - Single place to manage database connections
class DBManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get a database connection"""
        if self.connection is None:
            db_path = AppConfig.DB_PATH
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
```

### Example 3: UI Components

```python
# ui_components.py - Reusable UI components
class FormField(QWidget):
    """Base form field component with label and validation"""
    valueChanged = pyqtSignal(object)
    
    def __init__(self, label, required=False, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.required = required
        self._setup_ui()
    
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Create label with required indicator if needed
        label_text = self.label_text
        if self.required:
            label_text += " *"
        self.label = QLabel(label_text)
        
        self.layout.addWidget(self.label)
        self._setup_input()
        
        # Error label for validation messages
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setVisible(False)
        self.layout.addWidget(self.error_label)
    
    def _setup_input(self):
        """Override in subclasses to add specific input widgets"""
        pass
    
    def set_error(self, error_message):
        """Display error message"""
        if error_message:
            self.error_label.setText(error_message)
            self.error_label.setVisible(True)
        else:
            self.error_label.setVisible(False)
    
    def value(self):
        """Get field value - override in subclasses"""
        raise NotImplementedError
    
    def set_value(self, value):
        """Set field value - override in subclasses"""
        raise NotImplementedError
    
    def is_valid(self):
        """Validate field value"""
        if self.required and not self.value():
            self.set_error("This field is required")
            return False
        self.set_error("")
        return True

# Derived text field component
class TextField(FormField):
    def _setup_input(self):
        self.input = QLineEdit()
        self.input.textChanged.connect(lambda: self.valueChanged.emit(self.value()))
        self.layout.addWidget(self.input)
    
    def value(self):
        return self.input.text()
    
    def set_value(self, value):
        self.input.setText(value)

# Derived component for larger text areas
class TextAreaField(FormField):
    def _setup_input(self):
        self.input = QTextEdit()
        self.input.textChanged.connect(lambda: self.valueChanged.emit(self.value()))
        self.layout.addWidget(self.input)
    
    def value(self):
        return self.input.toPlainText()
    
    def set_value(self, value):
        self.input.setPlainText(value)
```

## Conclusion

Applying the DRY principle effectively leads to more maintainable, understandable, and less error-prone code. By consolidating knowledge and logic in single locations, we reduce the effort required for changes and enhancements. However, it's important to apply DRY with consideration for readability, maintainability, and the natural boundaries in the domain.

In the Prometheus AI Prompt Generator project, we strive to:
- Identify and eliminate knowledge duplication
- Create reusable components at appropriate levels of abstraction
- Balance DRY considerations with clarity and simplicity
- Refactor toward DRY as patterns emerge rather than prematurely abstracting

Last updated: March 9, 2025 