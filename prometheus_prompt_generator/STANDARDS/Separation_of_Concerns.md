# Separation of Concerns

## Overview

Separation of Concerns (SoC) is a design principle that divides a software system into distinct sections, each addressing a separate concern. A "concern" is a set of information or functionality that affects the code of a computer program. This principle helps create more modular, maintainable, and scalable applications.

In the context of the Prometheus AI Prompt Generator, SoC ensures that different aspects of the application are properly isolated, making the codebase easier to develop, test, and maintain.

## Core Benefits

- **Maintainability**: Changes to one component don't affect others
- **Reusability**: Components can be reused in different contexts
- **Testability**: Isolated components are easier to test
- **Scalability**: Well-separated components can be scaled independently
- **Collaboration**: Team members can work on different concerns simultaneously

## Application Architecture Layers

The Prometheus AI Prompt Generator follows a layered architecture with clear separation of concerns:

### 1. Presentation Layer (UI)

**Responsibility**: User interface and user interaction

**Components**:
- Qt widgets and views
- Forms and dialogs
- UI controllers
- View models for data binding

**Should NOT contain**:
- Business logic
- Direct database access
- Complex data transformations

Example:
```python
class PromptListView(QWidget):
    def __init__(self, prompt_service, parent=None):
        super().__init__(parent)
        self.prompt_service = prompt_service
        self._setup_ui()
        
    def _setup_ui(self):
        # UI components only (labels, lists, buttons)
        self.layout = QVBoxLayout(self)
        self.prompt_list = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        
        self.layout.addWidget(self.prompt_list)
        self.layout.addWidget(self.refresh_button)
        
        # Connect signals to slots
        self.refresh_button.clicked.connect(self.refresh_prompts)
        
    def refresh_prompts(self):
        # Delegate to service layer
        prompts = self.prompt_service.get_all_prompts()
        
        # Update UI with results
        self.prompt_list.clear()
        for prompt in prompts:
            self.prompt_list.addItem(prompt.title)
            
    def on_prompt_selected(self, item):
        # Handle UI interaction only
        prompt_title = item.text()
        self.selected_prompt.emit(prompt_title)
```

### 2. Application/Service Layer

**Responsibility**: Business logic, workflow, and orchestration

**Components**:
- Service classes
- Command handlers
- Workflow orchestrators
- Business rules and validation

**Should NOT contain**:
- UI logic
- Direct database queries
- Framework-specific code

Example:
```python
class PromptService:
    def __init__(self, prompt_repository, tag_repository):
        self.prompt_repository = prompt_repository
        self.tag_repository = tag_repository
        
    def get_all_prompts(self):
        # Business logic: Get all prompts with their tags
        prompts = self.prompt_repository.find_all()
        
        # Enrich with tags
        for prompt in prompts:
            prompt.tags = self.tag_repository.find_by_prompt_id(prompt.id)
            
        return prompts
        
    def create_prompt(self, prompt_data):
        # Business logic: Validate and create a prompt
        errors = self._validate_prompt_data(prompt_data)
        if errors:
            raise ValidationError(errors)
            
        prompt = Prompt(**prompt_data)
        
        # Save and return the result
        return self.prompt_repository.insert(prompt)
        
    def _validate_prompt_data(self, prompt_data):
        # Business logic: Validation rules
        errors = []
        
        if not prompt_data.get('title'):
            errors.append('Title is required')
            
        if not prompt_data.get('content'):
            errors.append('Content is required')
            
        return errors
```

### 3. Domain Layer

**Responsibility**: Core business entities and rules

**Components**:
- Domain models/entities
- Value objects
- Domain events
- Business constraints

**Should NOT contain**:
- UI logic
- Infrastructure concerns
- External service integrations

Example:
```python
class Prompt:
    def __init__(self, title, content, type, category_id=None, id=None, is_custom=False):
        self.id = id
        self.title = title
        self.content = content
        self.type = type
        self.category_id = category_id
        self.is_custom = is_custom
        self.created_date = datetime.now()
        self.tags = []
        
    def is_valid(self):
        """Domain rule: Check if the prompt is valid"""
        return bool(self.title and self.content and self.type)
        
    @property
    def is_system_prompt(self):
        """Domain rule: System prompts are non-custom prompts"""
        return not self.is_custom
        
    def add_tag(self, tag):
        """Domain operation: Add a tag if not already present"""
        if tag not in self.tags:
            self.tags.append(tag)
```

### 4. Data/Repository Layer

**Responsibility**: Data access and persistence

**Components**:
- Repository classes
- Data mappers/converters
- Query objects
- Database connection management

**Should NOT contain**:
- UI logic
- Business rules
- Application workflows

Example:
```python
class PromptRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        
    def find_all(self):
        """Data access only: Get all prompts from the database"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Prompts ORDER BY title")
        rows = cursor.fetchall()
        return [self._row_to_prompt(row) for row in rows]
        
    def find_by_id(self, prompt_id):
        """Data access only: Get a prompt by ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_prompt(row)
        
    def insert(self, prompt):
        """Data access only: Insert a prompt into the database"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO Prompts (title, content, type, category_id, is_custom, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                prompt.title,
                prompt.content,
                prompt.type,
                prompt.category_id,
                prompt.is_custom,
                prompt.created_date
            )
        )
        self.connection.commit()
        prompt.id = cursor.lastrowid
        return prompt
        
    def _row_to_prompt(self, row):
        """Data conversion only: Convert a database row to a Prompt object"""
        return Prompt(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            type=row['type'],
            category_id=row['category_id'],
            is_custom=row['is_custom']
        )
```

### 5. Infrastructure/Cross-Cutting Layer

**Responsibility**: Technical services and infrastructure

**Components**:
- Logging
- Configuration
- Security
- Caching
- Dependency injection

**Should NOT contain**:
- Business logic
- UI concerns
- Domain rules

Example:
```python
class Logger:
    """Infrastructure concern: Logging"""
    @staticmethod
    def info(message):
        print(f"[INFO] {datetime.now()} - {message}")
        
    @staticmethod
    def error(message, exception=None):
        error_text = f"[ERROR] {datetime.now()} - {message}"
        if exception:
            error_text += f": {str(exception)}"
        print(error_text)
        
class AppConfig:
    """Infrastructure concern: Configuration"""
    @staticmethod
    def load_config(config_file):
        # Load configuration from file
        pass
        
    @staticmethod
    def get_db_path():
        return "data/prometheus.db"
```

## Vertical Slices

In addition to horizontal layers, our application is organized into vertical slices by feature:

### Prompt Management Slice

- UI: Prompt editor views and widgets
- Service: PromptService
- Domain: Prompt entity
- Repository: PromptRepository
- Cross-cutting: Prompt-specific logging and configuration

### Tag Management Slice

- UI: Tag management views and widgets
- Service: TagService
- Domain: Tag entity
- Repository: TagRepository
- Cross-cutting: Tag-specific logging and configuration

### Analytics Slice

- UI: Analytics dashboards and reports
- Service: AnalyticsService
- Domain: Usage and score entities
- Repository: Usage and score repositories
- Cross-cutting: Analytics-specific caching and performance optimizations

## Implementation Guidelines

### Folder Structure

Our project structure reflects the separation of concerns:

```
prometheus_prompt_generator/
  ├── ui/                   # Presentation layer
  │   ├── widgets/          # Reusable UI components
  │   ├── views/            # Screen/page views
  │   ├── dialogs/          # Modal dialogs
  │   └── viewmodels/       # View data binding
  │
  ├── services/             # Application/Service layer
  │   ├── prompt_service.py
  │   ├── tag_service.py
  │   └── analytics_service.py
  │
  ├── domain/               # Domain layer
  │   ├── models/           # Domain entities
  │   ├── values/           # Value objects
  │   └── events/           # Domain events
  │
  ├── data/                 # Data/Repository layer
  │   ├── repositories/     # Data access repositories
  │   ├── migrations/       # Schema migrations
  │   └── db_manager.py     # Database connection management
  │
  └── infrastructure/       # Infrastructure/Cross-cutting layer
      ├── logging/          # Logging utilities
      ├── config/           # Configuration management
      └── security/         # Security utilities
```

### Dependency Flow

Dependencies should flow from outer layers to inner layers:

1. Presentation depends on Application/Service
2. Application/Service depends on Domain and Repository
3. Repository depends on Domain
4. All layers may depend on Infrastructure

This creates a dependency structure that isolates the core business logic from external concerns.

### Communication Between Layers

- **Presentation → Application**: Direct method calls
- **Application → Domain**: Creating and manipulating domain objects
- **Application → Repository**: Method calls for data access
- **Repository → Domain**: Creating domain objects from data

## Examples of Proper Separation

### Example 1: Prompt Creation

```python
# UI Layer
class PromptCreationView(QWidget):
    def __init__(self, prompt_service, parent=None):
        super().__init__(parent)
        self.prompt_service = prompt_service
        self._setup_ui()
        
    def _setup_ui(self):
        # UI components and layout
        pass
        
    def on_save_clicked(self):
        # Gather data from UI
        prompt_data = {
            'title': self.title_input.text(),
            'content': self.content_input.toPlainText(),
            'type': self.type_combo.currentText(),
            'category_id': self.category_combo.itemData(self.category_combo.currentIndex()),
            'is_custom': True
        }
        
        try:
            # Delegate to service layer
            prompt = self.prompt_service.create_prompt(prompt_data)
            
            # Update UI with result
            self.show_success_message(f"Prompt '{prompt.title}' created successfully")
            self.clear_form()
            
        except ValidationError as e:
            # Handle UI-specific error display
            self.show_validation_errors(e.errors)

# Service Layer
class PromptService:
    def __init__(self, prompt_repository, tag_repository):
        self.prompt_repository = prompt_repository
        self.tag_repository = tag_repository
        
    def create_prompt(self, prompt_data):
        # Business validation
        errors = self._validate_prompt_data(prompt_data)
        if errors:
            raise ValidationError(errors)
            
        # Create domain object
        prompt = Prompt(**prompt_data)
        
        # Persist through repository
        saved_prompt = self.prompt_repository.insert(prompt)
        
        # Return domain object
        return saved_prompt
        
    def _validate_prompt_data(self, prompt_data):
        # Business validation logic
        pass

# Domain Layer
class Prompt:
    def __init__(self, title, content, type, category_id=None, id=None, is_custom=False):
        # Entity properties and domain logic
        pass

# Repository Layer
class PromptRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        
    def insert(self, prompt):
        # Data access code
        pass
```

### Example 2: Analytics Dashboard

```python
# UI Layer
class AnalyticsDashboardView(QWidget):
    def __init__(self, analytics_service, parent=None):
        super().__init__(parent)
        self.analytics_service = analytics_service
        self._setup_ui()
        
    def _setup_ui(self):
        # UI components and layout
        pass
        
    def load_dashboard(self):
        # Show loading indicator
        self.loading_indicator.setVisible(True)
        
        try:
            # Delegate to service layer
            usage_stats = self.analytics_service.get_usage_statistics()
            score_stats = self.analytics_service.get_score_statistics()
            
            # Update UI with results
            self._update_charts(usage_stats, score_stats)
            
        except Exception as e:
            # Handle UI-specific error display
            self.show_error_message(f"Failed to load analytics data: {str(e)}")
        finally:
            # Hide loading indicator
            self.loading_indicator.setVisible(False)

# Service Layer
class AnalyticsService:
    def __init__(self, usage_repository, score_repository):
        self.usage_repository = usage_repository
        self.score_repository = score_repository
        
    def get_usage_statistics(self):
        # Business logic: Aggregate usage data
        raw_data = self.usage_repository.get_usage_by_prompt_type()
        
        # Transform data for visualization
        usage_stats = self._transform_usage_data(raw_data)
        
        return usage_stats
        
    def get_score_statistics(self):
        # Business logic: Aggregate score data
        raw_data = self.score_repository.get_average_scores_by_prompt()
        
        # Transform data for visualization
        score_stats = self._transform_score_data(raw_data)
        
        return score_stats
        
    def _transform_usage_data(self, raw_data):
        # Data transformation logic
        pass
        
    def _transform_score_data(self, raw_data):
        # Data transformation logic
        pass

# Repository Layer
class UsageRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        
    def get_usage_by_prompt_type(self):
        # Data access: Retrieve usage statistics from database
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.type, COUNT(pu.id) as count
            FROM PromptUsage pu
            JOIN Prompts p ON pu.prompt_id = p.id
            GROUP BY p.type
        """)
        return cursor.fetchall()
```

## Common Violations and How to Fix Them

### Violation 1: UI Layer Accessing Database Directly

```python
# VIOLATION: UI directly accessing database
class PromptListView(QWidget):
    def refresh_prompts(self):
        # Direct database access in UI - BAD!
        db = sqlite3.connect("data/prometheus.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Prompts")
        prompts = cursor.fetchall()
        
        self.prompt_list.clear()
        for prompt in prompts:
            self.prompt_list.addItem(prompt[1])  # title is at index 1
```

**Fix**:
```python
# CORRECT: UI delegating to service layer
class PromptListView(QWidget):
    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        
    def refresh_prompts(self):
        # Delegate to service layer
        prompts = self.prompt_service.get_all_prompts()
        
        # UI only handles presentation
        self.prompt_list.clear()
        for prompt in prompts:
            self.prompt_list.addItem(prompt.title)
```

### Violation 2: Business Logic in Repository Layer

```python
# VIOLATION: Business logic in repository
class PromptRepository:
    def create_prompt(self, title, content, type):
        # Business validation in repository - BAD!
        if not title or len(title) > 100:
            raise ValueError("Title is required and cannot exceed 100 characters")
            
        if not content:
            raise ValueError("Content is required")
            
        # Database operations...
```

**Fix**:
```python
# CORRECT: Repository only handles data access
class PromptRepository:
    def insert(self, prompt):
        # Only data access logic in repository
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO Prompts (title, content, type) VALUES (?, ?, ?)",
            (prompt.title, prompt.content, prompt.type)
        )
        self.connection.commit()
        prompt.id = cursor.lastrowid
        return prompt

# Business logic belongs in service layer
class PromptService:
    def create_prompt(self, prompt_data):
        # Business validation
        self._validate_prompt_data(prompt_data)
        
        # Create entity
        prompt = Prompt(**prompt_data)
        
        # Use repository for data access
        return self.prompt_repository.insert(prompt)
```

### Violation 3: UI-Specific Code in Domain Layer

```python
# VIOLATION: UI concerns in domain model
class Prompt:
    def __init__(self, title, content, type):
        self.title = title
        self.content = content
        self.type = type
        
    def display_on_list_widget(self, list_widget):
        # UI logic in domain model - BAD!
        item = QListWidgetItem(self.title)
        item.setData(Qt.UserRole, self.id)
        list_widget.addItem(item)
```

**Fix**:
```python
# CORRECT: Domain model with no UI dependencies
class Prompt:
    def __init__(self, title, content, type):
        self.title = title
        self.content = content
        self.type = type
        
    def is_valid(self):
        # Only domain logic in the model
        return bool(self.title and self.content and self.type)

# UI logic belongs in UI layer
class PromptListView(QWidget):
    def display_prompts(self, prompts):
        self.list_widget.clear()
        for prompt in prompts:
            item = QListWidgetItem(prompt.title)
            item.setData(Qt.UserRole, prompt.id)
            self.list_widget.addItem(item)
```

## Conclusion

Proper separation of concerns is essential for building a maintainable, testable, and scalable application. In the Prometheus AI Prompt Generator, we enforce a clear separation between:

1. **Presentation Layer**: UI components and user interaction
2. **Application/Service Layer**: Business logic and workflow orchestration
3. **Domain Layer**: Core business entities and rules
4. **Data/Repository Layer**: Data access and persistence
5. **Infrastructure/Cross-Cutting Layer**: Technical services

By following these guidelines, we ensure that our codebase remains:
- Easy to understand and navigate
- Simple to modify and extend
- Efficient to test
- Suitable for collaboration

Each team member should strive to maintain these separation boundaries and refactor code that violates these principles.

Last updated: March 9, 2025 