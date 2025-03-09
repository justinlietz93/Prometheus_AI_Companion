# Architecture Patterns

## Overview

This document outlines the architectural patterns used in the Prometheus AI Prompt Generator. These patterns establish a consistent approach to structuring the application, ensuring maintainability, testability, and scalability.

## Core Architecture: Layered Architecture

The Prometheus AI Prompt Generator follows a layered architecture pattern that separates the application into distinct layers, each with a specific responsibility.

### Layer Structure

1. **Presentation Layer (UI)**
   - Implements the user interface
   - Handles user input and display of information
   - Uses Qt framework for desktop UI components

2. **Application/Service Layer**
   - Implements business workflows and use cases
   - Coordinates activities between the UI and data layers
   - Manages the application's behavior

3. **Domain Layer**
   - Contains business entities and business rules
   - Represents the core concepts of the application
   - Independent of UI and persistence concerns

4. **Data/Repository Layer**
   - Handles data access and persistence
   - Abstracts database operations
   - Provides a domain-friendly interface for data operations

5. **Infrastructure Layer**
   - Provides cross-cutting concerns
   - Includes configuration, logging, security
   - Supports operations across all other layers

### Layer Communication

```
┌───────────────────┐
│  Presentation     │
│  (UI Layer)       │
└─────────┬─────────┘
          │ 
          ▼
┌───────────────────┐
│  Application      │
│  (Service Layer)  │
└─────────┬─────────┘
          │ 
    ┌─────┴─────┐
    │           │ 
    ▼           ▼
┌─────────┐ ┌─────────┐
│ Domain  │ │  Data   │
│ Layer   │ │  Layer  │
└─────────┘ └─────────┘
    ▲           ▲
    │           │
    └─────┬─────┘
          │ 
          ▼
┌───────────────────┐
│  Infrastructure   │
│  Layer            │
└───────────────────┘
```

- Each layer should only depend on the layer directly below it
- The domain layer should not depend on any other layers
- Infrastructure may be accessed by any layer

## Key Supporting Patterns

### Repository Pattern

The Repository pattern provides an abstraction of data persistence, allowing the application to work with domain objects without being concerned with how they are saved or retrieved.

#### Implementation

```python
# Domain model (independent of persistence)
class Prompt:
    def __init__(self, id, title, content, type, category_id, is_custom):
        self.id = id
        self.title = title
        self.content = content
        self.type = type
        self.category_id = category_id
        self.is_custom = is_custom

# Repository interface in domain
class PromptRepository(ABC):
    @abstractmethod
    def find_by_id(self, id):
        pass
    
    @abstractmethod
    def find_all(self):
        pass
    
    @abstractmethod
    def insert(self, prompt):
        pass
    
    @abstractmethod
    def update(self, prompt):
        pass
    
    @abstractmethod
    def delete(self, id):
        pass

# Concrete repository implementation in data layer
class SQLitePromptRepository(PromptRepository):
    def __init__(self, connection):
        self.connection = connection
    
    def find_by_id(self, id):
        # Implementation using SQLite
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Prompts WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_prompt(row)
    
    # Other methods implemented as well
```

#### Benefits

- Decouples the domain model from data persistence details
- Simplifies unit testing through the ability to mock repositories
- Centralizes data access logic for maintainability
- Provides a clean API for data access operations

### Service Pattern

The Service pattern encapsulates business logic that doesn't naturally fit within a domain entity, operating on multiple entities, or managing workflows.

#### Implementation

```python
class PromptService:
    def __init__(self, prompt_repository, tag_repository):
        self.prompt_repository = prompt_repository
        self.tag_repository = tag_repository
    
    def create_prompt_with_tags(self, prompt_data, tags):
        # Business logic spanning multiple repositories
        prompt = Prompt(**prompt_data)
        saved_prompt = self.prompt_repository.insert(prompt)
        
        for tag_name in tags:
            tag = self.tag_repository.find_by_name(tag_name)
            if not tag:
                tag = Tag(name=tag_name)
                tag = self.tag_repository.insert(tag)
            
            self.tag_repository.associate_with_prompt(tag.id, saved_prompt.id)
        
        return saved_prompt
```

#### Benefits

- Encapsulates complex business logic
- Orchestrates operations across multiple repositories
- Provides a clear API for application features
- Simplifies testing of business workflows

### Dependency Injection

Dependency Injection is a technique for achieving Inversion of Control (IoC) between classes and their dependencies.

#### Implementation

```python
# Explicit constructor injection
class PromptService:
    def __init__(self, prompt_repository, tag_repository, validator):
        self.prompt_repository = prompt_repository
        self.tag_repository = tag_repository
        self.validator = validator

# Application setup with manual dependency injection
def setup_application():
    db_connection = create_database_connection()
    
    # Create repositories
    prompt_repo = SQLitePromptRepository(db_connection)
    tag_repo = SQLiteTagRepository(db_connection)
    
    # Create services with dependencies
    prompt_validator = PromptValidator()
    prompt_service = PromptService(prompt_repo, tag_repo, prompt_validator)
    
    # Create UI components with dependencies
    main_window = MainWindow(prompt_service)
    return main_window
```

#### Benefits

- Reduces tight coupling between components
- Enables easier unit testing through dependency substitution
- Makes component dependencies explicit
- Facilitates reuse of components in different contexts

### Factory Pattern

The Factory pattern creates objects without specifying the exact class of object that will be created, providing a way to encapsulate object creation logic.

#### Implementation

```python
class RepositoryFactory:
    def __init__(self, db_connection):
        self.connection = db_connection
    
    def create_prompt_repository(self):
        return SQLitePromptRepository(self.connection)
    
    def create_tag_repository(self):
        return SQLiteTagRepository(self.connection)
    
    def create_category_repository(self):
        return SQLiteCategoryRepository(self.connection)

# Usage
def setup_services():
    db_connection = create_database_connection()
    repo_factory = RepositoryFactory(db_connection)
    
    prompt_repository = repo_factory.create_prompt_repository()
    tag_repository = repo_factory.create_tag_repository()
    
    return PromptService(prompt_repository, tag_repository)
```

#### Benefits

- Centralizes object creation logic
- Simplifies switching implementations
- Encapsulates initialization complexity
- Promotes consistency in object creation

### Observer Pattern (Signal/Slot in Qt)

The Observer pattern (implemented as Signals/Slots in Qt) allows objects to be notified of changes to other objects without being tightly coupled.

#### Implementation

```python
class PromptListViewModel(QObject):
    promptsChanged = pyqtSignal(list)  # Signal that will be emitted when prompts change
    
    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.prompts = []
    
    def load_prompts(self):
        self.prompts = self.prompt_service.get_all_prompts()
        self.promptsChanged.emit(self.prompts)  # Emit signal with new data

class PromptListView(QWidget):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self._setup_ui()
        
        # Connect signal to slot
        self.view_model.promptsChanged.connect(self.update_prompt_list)
    
    def update_prompt_list(self, prompts):
        # Update UI with new prompts
        self.prompt_list.clear()
        for prompt in prompts:
            self.prompt_list.addItem(prompt.title)
```

#### Benefits

- Decouples objects that interact with each other
- Allows for one-to-many notification
- Facilitates event-driven architecture
- Improves modularity and reusability

### Model-View-ViewModel (MVVM)

The MVVM pattern separates UI logic from business logic, using a ViewModel to act as an intermediary between the View and the Model.

#### Implementation

```python
# Model (Domain object)
class Prompt:
    def __init__(self, id, title, content, type):
        self.id = id
        self.title = title
        self.content = content
        self.type = type

# ViewModel (Adapts Model for View)
class PromptEditorViewModel(QObject):
    titleChanged = pyqtSignal(str)
    contentChanged = pyqtSignal(str)
    typeChanged = pyqtSignal(str)
    
    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        self._prompt_id = None
        self._title = ""
        self._content = ""
        self._type = ""
    
    def load_prompt(self, prompt_id):
        prompt = self.prompt_service.get_prompt(prompt_id)
        if prompt:
            self._prompt_id = prompt.id
            self.set_title(prompt.title)
            self.set_content(prompt.content)
            self.set_type(prompt.type)
    
    def set_title(self, title):
        if self._title != title:
            self._title = title
            self.titleChanged.emit(title)
    
    def set_content(self, content):
        if self._content != content:
            self._content = content
            self.contentChanged.emit(content)
    
    def set_type(self, type):
        if self._type != type:
            self._type = type
            self.typeChanged.emit(type)
    
    def save(self):
        prompt_data = {
            'id': self._prompt_id,
            'title': self._title,
            'content': self._content,
            'type': self._type
        }
        
        if self._prompt_id:
            return self.prompt_service.update_prompt(self._prompt_id, prompt_data)
        else:
            return self.prompt_service.create_prompt(prompt_data)

# View (UI)
class PromptEditorView(QWidget):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self._setup_ui()
        
        # Connect ViewModel signals to View updates
        self.view_model.titleChanged.connect(self.title_input.setText)
        self.view_model.contentChanged.connect(self.content_input.setPlainText)
        self.view_model.typeChanged.connect(self.update_type_selection)
        
        # Connect View events to ViewModel
        self.title_input.textChanged.connect(self.view_model.set_title)
        self.content_input.textChanged.connect(self.view_model.set_content)
        self.type_combo.currentTextChanged.connect(self.view_model.set_type)
        self.save_button.clicked.connect(self.save_prompt)
    
    def save_prompt(self):
        try:
            prompt = self.view_model.save()
            self.show_success_message(f"Prompt '{prompt.title}' saved successfully")
        except Exception as e:
            self.show_error_message(str(e))
```

#### Benefits

- Separates UI logic from business logic
- Provides a clean way to implement data binding
- Supports unit testing of UI logic
- Promotes separation of concerns in the UI layer

## Application-Specific Patterns

### Domain-Driven Design (DDD) Concepts

While not implementing full DDD, we borrow key concepts to structure our domain:

#### Entities

Entities are objects with a distinct identity that runs through time and different states.

```python
class Prompt:
    def __init__(self, id, title, content, type):
        self.id = id  # Identity attribute
        self.title = title
        self.content = content
        self.type = type
    
    def __eq__(self, other):
        if not isinstance(other, Prompt):
            return False
        return self.id == other.id  # Equality based on identity, not attributes
```

#### Value Objects

Value objects describe characteristics of a thing and are immutable.

```python
class PromptScore:
    def __init__(self, accuracy, relevance, creativity):
        self._accuracy = accuracy
        self._relevance = relevance
        self._creativity = creativity
    
    @property
    def accuracy(self):
        return self._accuracy
    
    @property
    def relevance(self):
        return self._relevance
    
    @property
    def creativity(self):
        return self._creativity
    
    @property
    def average_score(self):
        return (self._accuracy + self._relevance + self._creativity) / 3
    
    def __eq__(self, other):
        if not isinstance(other, PromptScore):
            return False
        # Equality based on all attributes
        return (self._accuracy == other._accuracy and 
                self._relevance == other._relevance and 
                self._creativity == other._creativity)
```

#### Aggregates

Aggregates group related entities and value objects, with one entity serving as the root.

```python
class PromptAggregate:
    def __init__(self, prompt):
        self.prompt = prompt  # Root entity
        self.versions = []    # Child entities
        self.tags = []        # Related entities
        self.scores = []      # Value objects
    
    def add_version(self, version):
        """Add a new version to the prompt aggregate"""
        version.prompt_id = self.prompt.id
        self.versions.append(version)
    
    def add_tag(self, tag):
        """Associate a tag with the prompt"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_score(self, score):
        """Add a new score to the prompt"""
        self.scores.append(score)
    
    @property
    def average_score(self):
        """Calculate the average score across all scores"""
        if not self.scores:
            return None
        return sum(score.average_score for score in self.scores) / len(self.scores)
```

### Plugin Architecture

To support extensibility, we implement a plugin architecture for adding new prompt types, LLM providers, and integrations.

#### Implementation

```python
# Plugin interface
class PromptProviderPlugin(ABC):
    @abstractmethod
    def get_name(self):
        """Get the name of the provider"""
        pass
    
    @abstractmethod
    def get_supported_models(self):
        """Get a list of supported models"""
        pass
    
    @abstractmethod
    def generate_completion(self, prompt, model, options=None):
        """Generate a completion for the prompt"""
        pass

# Concrete implementation
class OpenAIProvider(PromptProviderPlugin):
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_name(self):
        return "OpenAI"
    
    def get_supported_models(self):
        return ["gpt-4-turbo", "gpt-3.5-turbo"]
    
    def generate_completion(self, prompt, model, options=None):
        # Implementation using OpenAI API
        pass

# Plugin registry
class PluginRegistry:
    def __init__(self):
        self.providers = {}
    
    def register_provider(self, provider):
        self.providers[provider.get_name()] = provider
    
    def get_provider(self, name):
        return self.providers.get(name)
    
    def get_all_providers(self):
        return list(self.providers.values())
```

#### Benefits

- Allows for extensibility without modifying core code
- Enables third-party integrations
- Supports feature toggling
- Facilitates testing with mock implementations

## Persistence Patterns

### Unit of Work

The Unit of Work pattern keeps track of everything you do during a business transaction and coordinates the writing out of changes.

#### Implementation

```python
class UnitOfWork:
    def __init__(self, connection):
        self.connection = connection
        self.prompt_repository = None
        self.tag_repository = None
    
    def __enter__(self):
        # Begin transaction
        self.connection.execute("BEGIN TRANSACTION")
        
        # Create repositories
        self.prompt_repository = SQLitePromptRepository(self.connection)
        self.tag_repository = SQLiteTagRepository(self.connection)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Commit or rollback transaction
        if exc_type is not None:
            print(f"Rolling back transaction due to: {exc_val}")
            self.connection.execute("ROLLBACK")
        else:
            self.connection.execute("COMMIT")
    
    def commit(self):
        """Explicitly commit the transaction"""
        self.connection.execute("COMMIT")
        self.connection.execute("BEGIN TRANSACTION")

# Usage
def create_prompt_with_tags(prompt_data, tags, db_connection):
    with UnitOfWork(db_connection) as uow:
        # Create the prompt
        prompt = Prompt(**prompt_data)
        prompt = uow.prompt_repository.insert(prompt)
        
        # Create and associate tags
        for tag_name in tags:
            tag = uow.tag_repository.find_by_name(tag_name)
            if not tag:
                tag = Tag(name=tag_name)
                tag = uow.tag_repository.insert(tag)
            
            uow.tag_repository.associate_with_prompt(tag.id, prompt.id)
        
        # Transaction will be automatically committed unless an exception is raised
        return prompt
```

#### Benefits

- Ensures database consistency through transactions
- Centralizes transaction management
- Simplifies transaction handling in services
- Reduces the chance of partial updates

### Data Mapper

The Data Mapper pattern moves data between objects and a database while keeping them independent of each other.

#### Implementation

```python
class PromptMapper:
    def __init__(self, connection):
        self.connection = connection
    
    def to_entity(self, row):
        """Convert a database row to a domain entity"""
        return Prompt(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            type=row['type'],
            category_id=row['category_id'],
            is_custom=row['is_custom']
        )
    
    def to_row(self, prompt):
        """Convert a domain entity to a database row"""
        return {
            'id': prompt.id,
            'title': prompt.title,
            'content': prompt.content,
            'type': prompt.type,
            'category_id': prompt.category_id,
            'is_custom': prompt.is_custom
        }
    
    def insert(self, prompt):
        """Insert a prompt into the database"""
        cursor = self.connection.cursor()
        row = self.to_row(prompt)
        
        # Remove ID for insertion if it's None
        if row['id'] is None:
            del row['id']
            
        columns = ', '.join(row.keys())
        placeholders = ', '.join(['?' for _ in row])
        
        sql = f"INSERT INTO Prompts ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, list(row.values()))
        
        if prompt.id is None:
            prompt.id = cursor.lastrowid
            
        return prompt
```

#### Benefits

- Clear separation between domain objects and database structure
- Simplifies database schema changes
- Centralizes mapping logic
- Keeps domain objects clean of persistence concerns

## Putting It All Together

Our architecture combines these patterns to create a maintainable, testable, and extensible application:

```
┌───────────────────────────────────────────────────────┐
│                     UI Layer                          │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │    Views    │  │  ViewModels │  │   Widgets   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────────────┬───────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────┐
│                   Service Layer                       │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Services   │  │  Validators │  │ Orchestrators│   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────┬─────────────────┬─────────────────┘
                    │                 │
┌───────────────────▼─────┐ ┌─────────▼───────────────┐
│     Domain Layer        │ │    Repository Layer     │
│                         │ │                         │
│  ┌─────────┐ ┌────────┐ │ │ ┌─────────┐ ┌────────┐ │
│  │ Entities │ │ Values │ │ │ │Repository│ │Mappers │ │
│  └─────────┘ └────────┘ │ │ └─────────┘ └────────┘ │
└─────────────────────────┘ └─────────────────────────┘
                   ▲                   ▲
                   │                   │
┌──────────────────┴───────────────────┴──────────────┐
│                Infrastructure Layer                  │
│                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Logging │  │ Config  │  │ Security│  │ Database│ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
└──────────────────────────────────────────────────────┘
```

### Example Flow

Here's how a typical prompt creation flow works through our architecture:

1. **User** enters prompt data in the **UI** (Presentation Layer)
2. **ViewModel** collects and validates the input (Presentation Layer)
3. **PromptService** is called to create a prompt (Service Layer)
4. **Validator** validates the input data (Service Layer)
5. **Prompt** entity is created with business rules (Domain Layer)
6. **UnitOfWork** begins a transaction (Infrastructure Layer)
7. **PromptRepository** stores the prompt (Repository Layer)
8. Data is mapped to the database format (Repository Layer)
9. Transaction is committed (Infrastructure Layer)
10. Result is returned to the UI (Presentation Layer)

## Conclusion

By following these architectural patterns consistently, we create a codebase that is:

- **Maintainable**: Changes can be made to one part without affecting others
- **Testable**: Components can be tested in isolation
- **Extensible**: New features can be added without changing existing code
- **Understandable**: Clear organization makes code easier to comprehend

All team members should adhere to these patterns when contributing to the Prometheus AI Prompt Generator project.

Last updated: March 9, 2025 