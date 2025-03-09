# Prometheus AI Prompt Generator - Standards Summary

This document provides a quick overview of all the standards documentation available for the Prometheus AI Prompt Generator project.

## Available Standards Documentation

| Document | Description | Key Points |
|----------|-------------|------------|
| [README.md](./README.md) | Main standards documentation entry point | Overview, usage guidelines, and core principles |
| [Architecture_Patterns.md](./Architecture_Patterns.md) | Architectural patterns used in the project | Layered architecture, repository pattern, MVVM, dependency injection |
| [SOLID_Principles.md](./SOLID_Principles.md) | SOLID design principles and application | Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion |
| [CRUD_Standards.md](./CRUD_Standards.md) | Guidelines for data operations | Create, read, update, delete operations, error handling, validation |
| [DRY_Principle.md](./DRY_Principle.md) | Don't Repeat Yourself practices | Code reuse, abstraction, utility classes, avoiding over-abstraction |
| [Separation_of_Concerns.md](./Separation_of_Concerns.md) | Maintaining clear boundaries | UI layer, service layer, domain layer, data layer, infrastructure layer |
| [Code_Style_Guide.md](./Code_Style_Guide.md) | Coding conventions | Naming, formatting, documentation, error handling, testing |
| [Database_Standards.md](./Database_Standards.md) | Database design and access | Schema design, migrations, queries, repositories, security |

## Standards Quick Reference

### Architecture

- **Layered Architecture**: UI → Service → Domain/Data → Infrastructure
- **Communication Flow**: Dependencies flow downward, data flows upward
- **Repository Pattern**: Abstracts data access behind domain-focused interfaces
- **MVVM Pattern**: Separates UI (View) from presentation logic (ViewModel) and data (Model)
- **Dependency Injection**: Components receive dependencies rather than creating them

### Code Organization

- **Package Structure**: Organized by layer, then by feature within each layer
- **Module Structure**: Docstring → Imports → Constants → Classes → Functions → Main
- **Import Order**: Standard library → Third-party libraries → Local modules
- **Method Order**: Special methods → Public methods → Protected methods → Private methods

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `PromptService`)
- **Functions/Methods**: `snake_case` (e.g., `get_prompt_by_id`)
- **Variables**: `snake_case` (e.g., `user_prompt`)
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES` (e.g., `MAX_PROMPT_LENGTH`)
- **Protected Members**: Prefix with `_` (e.g., `_validate_data`)
- **Private Members**: Prefix with `__` (e.g., `__apply_business_rules`)
- **Database Tables**: `PascalCase` for tables, `snake_case` for columns

### Documentation Requirements

- **Module Level**: Purpose and content overview
- **Class Level**: Responsibility and behavior
- **Method Level**: Purpose, parameters, return values, exceptions
- **Complex Logic**: Comments explaining "why", not "what"
- **API Changes**: Comprehensive documentation of changes

### Database Best Practices

- **Schema Changes**: Only through migration scripts (never direct modification)
- **Queries**: Always use parameterized queries to prevent SQL injection
- **Transactions**: Use transactions for multi-step operations
- **Error Handling**: Proper exception handling and rollback on errors
- **Security**: Encrypt sensitive data, implement access controls

### Testing Guidelines

- **Test Coverage**: All business logic and data access code
- **Naming**: `test_<function>_<scenario>_<expected_result>`
- **Structure**: Arrange-Act-Assert pattern
- **Isolation**: Mock external dependencies

## Applying Standards to New Code

When adding new code to the project, follow these steps:

1. **Identify Responsibilities**: Determine which layer(s) your code belongs to
2. **Follow Patterns**: Apply the appropriate architectural patterns
3. **Adhere to Style**: Follow naming and formatting conventions
4. **Document**: Add proper documentation at all levels
5. **Test**: Write comprehensive tests for your code
6. **Review**: Have your code reviewed against these standards

## Version History

| Date | Changes |
|------|---------|
| 2025-03-09 | Initial creation of all standards documentation |

Last updated: March 9, 2025 