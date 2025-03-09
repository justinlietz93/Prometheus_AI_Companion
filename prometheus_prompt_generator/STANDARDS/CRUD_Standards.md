# CRUD Operations Standards

## Overview

CRUD (Create, Read, Update, Delete) represents the four basic operations for persistent storage. This document establishes standards for implementing CRUD operations in the Prometheus AI Prompt Generator to ensure consistency, security, and maintainability.

## General CRUD Guidelines

### Naming Conventions

All CRUD operations should follow consistent naming patterns:

| Operation | Method Name | Repository Method | SQL Action |
|-----------|-------------|-------------------|------------|
| Create | `create_*` | `insert_*` or `save_*` | `INSERT INTO` |
| Read | `get_*`, `find_*`, `list_*` | `select_*` or `find_*` | `SELECT` |
| Update | `update_*`, `modify_*` | `update_*` | `UPDATE` |
| Delete | `delete_*`, `remove_*` | `delete_*` | `DELETE` |

Example:
```python
# Service/Model level
def create_prompt(prompt_data):
    pass

def get_prompt(prompt_id):
    pass

# Repository level
def insert_prompt(prompt_obj):
    pass

def select_prompt_by_id(prompt_id):
    pass
```

### Return Values

CRUD operations should have consistent return values:

- **Create**: Return the newly created object with generated IDs
- **Read**: Return the requested object(s) or `None`/empty list if not found
- **Update**: Return the updated object or boolean indicating success
- **Delete**: Return boolean indicating success

### Error Handling

- Use appropriate exception classes for CRUD errors
- Provide meaningful error messages
- Handle database-specific errors and translate them to application-specific exceptions
- Log all CRUD errors with appropriate context

```python
class PromptNotFoundError(Exception):
    pass

class PromptCreateError(Exception):
    pass

def get_prompt(prompt_id):
    try:
        result = repository.select_prompt_by_id(prompt_id)
        if not result:
            raise PromptNotFoundError(f"Prompt with ID {prompt_id} not found")
        return result
    except DatabaseError as e:
        logger.error(f"Database error when retrieving prompt {prompt_id}: {e}")
        raise PromptNotFoundError(f"Error retrieving prompt: {e}")
```

## Implementation Guidelines

### Repository Layer

Each entity (Prompt, Tag, etc.) should have a dedicated repository class that implements CRUD operations:

```python
class PromptRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        
    def insert(self, prompt):
        """Create a new prompt record"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Prompts (title, content, type, category_id, is_custom) VALUES (?, ?, ?, ?, ?)",
                (prompt.title, prompt.content, prompt.type, prompt.category_id, prompt.is_custom)
            )
            self.connection.commit()
            prompt.id = cursor.lastrowid
            return prompt
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RepositoryError(f"Failed to insert prompt: {e}")
            
    def find_by_id(self, prompt_id):
        """Read a prompt by its ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM Prompts WHERE id = ?",
                (prompt_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_prompt(row)
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to find prompt: {e}")
            
    def update(self, prompt):
        """Update an existing prompt"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Prompts SET title = ?, content = ?, type = ?, category_id = ?, is_custom = ? WHERE id = ?",
                (prompt.title, prompt.content, prompt.type, prompt.category_id, prompt.is_custom, prompt.id)
            )
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RepositoryError(f"Failed to update prompt: {e}")
            
    def delete(self, prompt_id):
        """Delete a prompt by its ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Prompts WHERE id = ?",
                (prompt_id,)
            )
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RepositoryError(f"Failed to delete prompt: {e}")
```

### Service Layer

The service layer should wrap repository calls with business logic:

```python
class PromptService:
    def __init__(self, prompt_repository, tag_repository):
        self.prompt_repository = prompt_repository
        self.tag_repository = tag_repository
        
    def create_prompt(self, prompt_data):
        """Create a new prompt with validation"""
        # Validate input
        self._validate_prompt_data(prompt_data)
        
        # Create prompt object
        prompt = Prompt(**prompt_data)
        
        # Save to database
        saved_prompt = self.prompt_repository.insert(prompt)
        
        # Handle tags if provided
        if 'tags' in prompt_data:
            self._associate_tags(saved_prompt.id, prompt_data['tags'])
            
        return saved_prompt
        
    def get_prompt(self, prompt_id):
        """Get a prompt by ID with its associated tags"""
        prompt = self.prompt_repository.find_by_id(prompt_id)
        if not prompt:
            return None
            
        # Get associated tags
        tags = self.tag_repository.find_by_prompt_id(prompt_id)
        prompt.tags = tags
        
        return prompt
        
    def update_prompt(self, prompt_id, prompt_data):
        """Update an existing prompt"""
        # Verify existence
        existing_prompt = self.prompt_repository.find_by_id(prompt_id)
        if not existing_prompt:
            raise PromptNotFoundError(f"Prompt with ID {prompt_id} not found")
            
        # Validate input
        self._validate_prompt_data(prompt_data)
        
        # Update prompt object
        for key, value in prompt_data.items():
            if key != 'tags' and hasattr(existing_prompt, key):
                setattr(existing_prompt, key, value)
                
        # Save to database
        success = self.prompt_repository.update(existing_prompt)
        
        # Update tags if provided
        if 'tags' in prompt_data:
            self._update_tags(prompt_id, prompt_data['tags'])
            
        return existing_prompt if success else None
        
    def delete_prompt(self, prompt_id):
        """Delete a prompt and its associations"""
        # Delete associated tags first
        self.tag_repository.delete_by_prompt_id(prompt_id)
        
        # Delete the prompt
        return self.prompt_repository.delete(prompt_id)
        
    def _validate_prompt_data(self, prompt_data):
        """Validate prompt data against business rules"""
        if not prompt_data.get('title'):
            raise ValidationError("Prompt title is required")
        if not prompt_data.get('content'):
            raise ValidationError("Prompt content is required")
        if len(prompt_data.get('title', '')) > 100:
            raise ValidationError("Prompt title cannot exceed 100 characters")
```

## UI/Client Layer

UI components should:

- Use service layer methods for CRUD operations
- Handle loading states during CRUD operations
- Display appropriate success/error messages
- Implement optimistic updates where appropriate
- Ensure proper validation before submitting

```python
class PromptEditorWidget(QWidget):
    def __init__(self, parent=None, prompt_service=None):
        super().__init__(parent)
        self.prompt_service = prompt_service
        # UI initialization code...
        
    def save_prompt(self):
        # Gather data from form
        prompt_data = {
            'title': self.title_field.text(),
            'content': self.content_field.toPlainText(),
            'type': self.type_combo.currentText(),
            'category_id': self.category_combo.itemData(self.category_combo.currentIndex()),
            'is_custom': True,
            'tags': [tag.text() for tag in self.tag_list.selectedItems()]
        }
        
        try:
            # Validate form data client-side
            self._validate_form()
            
            # Show loading state
            self.save_button.setEnabled(False)
            self.status_label.setText("Saving...")
            
            # Create or update prompt
            if self.editing_prompt_id:
                prompt = self.prompt_service.update_prompt(self.editing_prompt_id, prompt_data)
                self.status_label.setText("Prompt updated successfully")
            else:
                prompt = self.prompt_service.create_prompt(prompt_data)
                self.editing_prompt_id = prompt.id
                self.status_label.setText("Prompt created successfully")
                
            # Update UI with saved data
            self._update_ui_with_prompt(prompt)
            
        except ValidationError as e:
            self.status_label.setText(f"Validation error: {e}")
        except PromptNotFoundError:
            self.status_label.setText("Error: Prompt not found")
        except Exception as e:
            self.status_label.setText(f"Error saving prompt: {e}")
        finally:
            self.save_button.setEnabled(True)
```

## Testing CRUD Operations

Each CRUD operation should have comprehensive test coverage:

- Test successful operations
- Test error handling
- Test validation
- Test edge cases (empty values, large values, etc.)
- Test with mock repositories for service layer tests
- Test with in-memory database for integration tests

```python
def test_create_prompt_success():
    # Arrange
    mock_repository = MockPromptRepository()
    service = PromptService(mock_repository, MockTagRepository())
    prompt_data = {
        'title': 'Test Prompt',
        'content': 'This is a test prompt',
        'type': 'instruction',
        'category_id': 1,
        'is_custom': True
    }
    
    # Act
    result = service.create_prompt(prompt_data)
    
    # Assert
    assert result is not None
    assert result.id is not None
    assert result.title == prompt_data['title']
    assert mock_repository.insert.called_once_with(ANY)

def test_create_prompt_validation_error():
    # Arrange
    service = PromptService(MockPromptRepository(), MockTagRepository())
    prompt_data = {
        'title': '',  # Empty title should fail validation
        'content': 'This is a test prompt',
        'type': 'instruction',
        'category_id': 1
    }
    
    # Act/Assert
    with pytest.raises(ValidationError) as exc:
        service.create_prompt(prompt_data)
    assert "Prompt title is required" in str(exc.value)
```

## Specific Guidelines for Each Entity

### Prompts

- Create unique versions for each major update (using PromptVersions table)
- Track creation and update timestamps
- Validate content against prompt type-specific rules
- Ensure category links are valid

### Tags

- Prevent duplicate tags (case-insensitive)
- Normalize tag names (lowercase, trim whitespace)
- Restrict tag length (max 50 characters)
- Handle tag associations in separate operations

### Categories

- Maintain hierarchy relationships
- Prevent circular references in hierarchies
- Validate category names

### API Keys

- Encrypt key values in storage
- Validate against provider-specific patterns
- Track usage against limits
- Implement soft delete (deactivation) instead of hard delete

## Security Considerations

- Implement parameterized queries for all CRUD operations
- Validate input data before processing
- Implement appropriate access controls
- Audit log sensitive CRUD operations
- Handle personally identifiable information (PII) according to regulations

## Performance Considerations

- Use database transactions for multi-step CRUD operations
- Implement appropriate indexing for frequently queried fields
- Consider pagination for large result sets
- Optimize queries for specific use cases
- Use prepared statements for repeated operations

## Conclusion

Following these CRUD standards will ensure a consistent, maintainable, and secure implementation across the Prometheus AI Prompt Generator application. Each team member should adhere to these guidelines when implementing CRUD operations for any entity in the system.

Last updated: March 9, 2025 