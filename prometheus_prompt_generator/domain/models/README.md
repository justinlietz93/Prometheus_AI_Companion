# Prometheus AI Prompt Generator - Data Models

This directory contains the model classes that represent the domain entities of the Prometheus AI Prompt Generator. These models are implemented as PyQt6 QObject subclasses to support two-way data binding with the UI components.

## Key Models

### Prompt

The `Prompt` class represents an AI prompt in the system. It includes:

- Core prompt data (title, content, description)
- Status flags (`is_public`, `is_featured`, `is_custom`)
- Metadata (creation date, modification date)
- Tag associations
- CRUD operations with database integration
- Data validation

**Basic Usage:**

```python
# Create a new prompt
prompt = Prompt()
prompt.title = "My Test Prompt"
prompt.content = "This is a test prompt for {{context}}"
prompt.description = "A simple test prompt"
prompt.is_public = True
prompt.save()  # Saves to database

# Load an existing prompt
prompt = Prompt(prompt_id=123)

# Modify a prompt
prompt.title = "Updated Title"
prompt.save()

# Delete a prompt
prompt.delete()

# Working with tags
tag_ids = [1, 2, 3]
for tag_id in tag_ids:
    prompt.add_tag(tag_id)
prompt.save()
```

### PromptMapper

The `PromptMapper` class connects `Prompt` models to UI form widgets, handling two-way data binding and validation. It:

- Automatically updates the model when UI controls change
- Updates UI controls when model data changes
- Handles error display
- Manages form submission and reset

**Basic Usage:**

```python
# Create a form mapper (assuming an existing UI form with widgets)
form_widgets = {
    'title': self.titleLineEdit,
    'content': self.contentTextEdit,
    'description': self.descriptionTextEdit,
    'is_public': self.isPublicCheckBox,
    'is_featured': self.isFeaturedCheckBox,
    'is_custom': self.isCustomCheckBox,
    'category': self.categoryComboBox,
    'created_date': self.createdDateLabel,
    'modified_date': self.modifiedDateLabel,
    'tags': self.tagsWidget,
    'error_label': self.errorLabel
}
mapper = PromptMapper(prompt, form_widgets)

# Submit the form (saves to database)
if mapper.submit():
    self.accept()
else:
    # Validation failed, error will be displayed in error_label

# Reset the form to original values
mapper.reset()

# Clean up connections when done
mapper.disconnect()
```

### Tag

The `Tag` class represents a tag used to categorize prompts. It includes:

- Basic tag data (name, color, description)
- CRUD operations with database integration
- Duplicate name validation
- Referential integrity checking

**Basic Usage:**

```python
# Create a new tag
tag = Tag()
tag.name = "Python"
tag.color = "#3776AB"  # Python blue
tag.description = "Code examples in Python"
tag.save()

# Load an existing tag
tag = Tag(tag_id=5)

# Modify a tag
tag.color = "#4B8BBE"  # Different shade of Python blue
tag.save()

# Delete a tag (if not in use)
tag.delete()

# Get all tags as a list
all_tags = Tag.get_all_tags()

# Search for tags
python_tags = Tag.search_tags("python")
```

## Design Principles

These models follow several key design principles:

1. **Data Validation**: All models include comprehensive validation to ensure data integrity.
2. **Signals and Slots**: Models use Qt's signal/slot mechanism for change notification.
3. **Separation of Concerns**: Models handle business logic and persistence separately from UI.
4. **Internationalization**: All user-facing messages use the `tr()` function for translation.
5. **ACID Compliance**: All database operations use transactions to ensure consistency.
6. **Error Handling**: Comprehensive error handling with meaningful messages.

## Implementation Notes

- All database access uses parameterized queries to prevent SQL injection.
- Models use transactions for operations that affect multiple tables.
- Changes to model properties emit the `changed` signal to notify observers.
- Validation errors emit the `error` signal with a descriptive message.
- Successful save operations emit the `saved` signal.

## Creating New Models

When creating new model classes, follow these guidelines:

1. Inherit from `QObject` to support signals and properties
2. Use `pyqtProperty`, `pyqtSignal`, and `pyqtSlot` decorators
3. Implement validation in a `validate()` method
4. Use transactions for complex operations
5. Emit appropriate signals for state changes
6. Include proper documentation 