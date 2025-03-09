# Prometheus AI Prompt Generator - Domain Models

This directory contains the domain model classes for the Prometheus AI Prompt Generator. These models encapsulate the business logic and data structures used throughout the application.

## Model Classes

### Prompt

The `Prompt` class represents an AI prompt in the system. It includes the following key features:

- CRUD operations for prompts
- Rich metadata (title, description, creation date, etc.)
- Category assignment
- Tag management
- Full validation
- Signal-based error notification

**Usage Example:**
```python
# Create a new prompt
prompt = Prompt()
prompt.title = "Python Code Assistant"
prompt.content = "Write a Python function that..."
prompt.description = "Helps with Python coding tasks"
prompt.category_id = 1
prompt.save()

# Add tags to the prompt
prompt.add_tag(1)  # Add tag with ID 1
```

### Tag

The `Tag` class represents a label that can be applied to prompts for organization and filtering. It includes:

- CRUD operations for tags
- Name, color, and description properties
- Association with prompts
- Validation to prevent duplicates
- Referential integrity checking

**Usage Example:**
```python
# Create a new tag
tag = Tag()
tag.name = "python"
tag.color = "#3776AB"
tag.description = "Python programming language"
tag.save()

# Get prompts associated with this tag
prompt_ids = tag.get_associated_prompts()
```

### Category

The `Category` class represents a hierarchical organization structure for prompts. It includes:

- CRUD operations for categories
- Hierarchical structure (parent-child relationships)
- Navigation methods (get_parent, get_children)
- Path management (ancestors, descendants)
- Circular reference prevention
- Display ordering

**Usage Example:**
```python
# Create a parent category
parent = Category()
parent.name = "Programming"
parent.description = "Programming related prompts"
parent.save()

# Create a child category
child = Category()
child.name = "Python"
child.description = "Python programming prompts"
child.parent_id = parent.id
child.save()

# Get full path
path = child.get_full_path()  # Returns "Programming > Python"
```

### ModelFactory

The `ModelFactory` class provides an abstraction layer for creating Qt SQL models that can be directly bound to UI components. It includes:

- Methods to create QSqlTableModel and QSqlRelationalTableModel instances
- Support for various tables (Prompts, Tags, Categories, etc.)
- Automatic relation setup
- Filtering capabilities
- Hierarchical view creation for categories
- Error handling with signal emission

**Usage Example:**
```python
# Create a factory
factory = ModelFactory()

# Get a model for tags that can be bound to a view
tag_model = factory.create_tag_model()

# Get a filtered model
filtered_model = factory.create_filtered_model("Tags", "name LIKE '%python%'")

# Create a hierarchical category model for a tree view
category_model = factory.create_hierarchical_category_model()
```

### PromptScore

The `PromptScore` class is an analytics model that tracks and analyzes prompt performance metrics. It includes:

- Usage tracking (total, success, failure counts)
- Performance metrics (success rate, token usage, cost)
- User satisfaction ratings
- Temporal analysis (trends over time)
- Comparative ranking
- Aggregation methods for analytics dashboards

**Usage Example:**
```python
# Load a prompt's score metrics
score = PromptScore(prompt_id=123)

# Record a new usage
score.record_usage(
    success=True,
    tokens_used=500,
    cost=0.05,
    satisfaction=4.5
)

# Get usage trend for last 30 days
trend_data = score.get_usage_trend(days=30)

# Get comparative ranking
rank_info = score.get_comparative_rank()
print(f"This prompt ranks #{rank_info['usage_rank']} in usage")

# Get top prompts by satisfaction
top_prompts = PromptScore.get_top_prompts(limit=5, metric="satisfaction")
```

## Implementation Details

All models follow a consistent architecture:

- Qt signals for error notification
- Private attributes with property accessors
- Full validation
- Database operations through QSqlQuery
- Clear separation of concerns
- Comprehensive error handling

Database connections are managed externally and injected where needed. 