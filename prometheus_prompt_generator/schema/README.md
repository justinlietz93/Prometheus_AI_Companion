# Prometheus AI Prompt Generator - Database Schema

## Overview

This directory contains the SQLite database schema for the Prometheus AI Prompt Generator application. The database is designed to support all required features, including prompt management, versioning, scoring, usage tracking, benchmarking, and reporting.

## Files

- **db_schema.sql**: Complete database schema definition
- **er_diagram.md**: Entity-relationship diagram in Mermaid format
- **sqlite_validator.py**: Script to validate the database schema for common issues
- **db_init.py**: Script to initialize the database and apply migrations

### Migrations

The `migrations` directory contains migration scripts to create and update the database schema in a versioned manner. Each migration is numbered and applied in sequence:

1. **001_initial_schema.sql**: Core tables for prompts, tags, and categories
2. **002_analytics_tables.sql**: Tables for prompt scoring and usage tracking
3. **003_benchmarking_tables.sql**: Tables for LLM benchmarking and documentation context

## Database Structure

The database follows a properly normalized structure with the following core entities:

- **Prompts**: Stores prompt templates with unique identifiers
- **Tags**: Categorization labels for prompts
- **Categories**: Hierarchical organization for prompts
- **PromptVersions**: Historical versions of prompts
- **PromptScores**: Quality metrics for prompts
- **PromptUsage**: Usage tracking for prompts
- **Models**: Registry of available LLMs
- **Benchmarks**: Test definitions for LLM evaluation
- **Documentation**: Context information for prompts

## Relationship Diagram

See `er_diagram.md` for a complete entity-relationship diagram in Mermaid format.

## Usage

### Initializing the Database

To initialize the database:

```bash
python -m prometheus_prompt_generator.schema.db_init [path_to_database]
```

If no path is provided, the default location will be used:

```
prometheus_prompt_generator/data/prometheus.db
```

### Validating the Database

To validate the database schema for common issues:

```bash
python -m prometheus_prompt_generator.schema.sqlite_validator [path_to_database]
```

### Adding New Migrations

To add a new migration:

1. Create a new SQL file in the `migrations` directory with a sequentially numbered name
2. Add the migration SQL statements, including version tracking
3. Run the `db_init.py` script to apply the new migration

## Design Principles

The database schema follows these design principles:

1. **Proper Normalization**: Tables are properly normalized to prevent data duplication
2. **Referential Integrity**: Foreign key constraints ensure data integrity
3. **Performance Optimization**: Indices are added for frequently queried columns
4. **Versioning**: All changes are tracked through migrations
5. **Analytics Support**: The schema includes tables for comprehensive analytics and reporting

## Migration from JSON

The initialization script includes functionality to migrate existing JSON prompt files to the SQLite database. This ensures backward compatibility with the previous storage format.

## Testing

The database schema should be thoroughly tested with representative data to ensure it supports all required features and performs adequately under load. 