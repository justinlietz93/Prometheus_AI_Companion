# Prometheus AI Database Schema Diagram

## Entity Relationship Diagram (Mermaid Format)

```mermaid
erDiagram
    Prompts ||--o{ PromptTagAssociation : has
    Prompts ||--o{ PromptVersions : tracks
    Prompts }o--|| Categories : belongs_to
    Tags ||--o{ PromptTagAssociation : used_in
    Categories ||--o{ CategoryHierarchy : parent_in
    Categories ||--o{ CategoryHierarchy : child_in
    Prompts ||--o{ PromptScores : rated_as
    Prompts ||--o{ PromptUsage : tracked_by
    Prompts ||--o{ BenchmarkResults : evaluated_in
    Models ||--o{ BenchmarkResults : used_in
    Benchmarks ||--o{ BenchmarkResults : contains
    PromptUsage ||--o{ UsageContext : used_in
    Documentation ||--o{ PromptDocContext : provides_context_to
    Prompts ||--o{ PromptDocContext : receives_context_from

    Prompts {
        int id PK
        string type UK
        string title
        string template
        string description
        string author
        string version
        string created_date
        string updated_date
        int category_id FK
        float avg_score
        int usage_count
        string last_used
    }

    Tags {
        int id PK
        string name UK
        string description
        string color
    }

    Categories {
        int id PK 
        string name UK
        string description
        int display_order
        int prompt_count
        float avg_category_score
    }

    PromptTagAssociation {
        int id PK
        int prompt_id FK
        int tag_id FK
    }

    PromptVersions {
        int id PK
        int prompt_id FK
        int version_num
        string template
        string changes
        string author
        string created_date
        float version_score
    }

    CategoryHierarchy {
        int id PK
        int parent_id FK
        int child_id FK
    }

    PromptScores {
        int id PK
        int prompt_id FK
        float clarity_score
        float specificity_score
        float effectiveness_score
        float overall_score
        string scorer
        string timestamp
        string feedback
    }

    PromptUsage {
        int id PK
        int prompt_id FK
        string timestamp
        int context_id FK
        string user_id
        boolean successful
        int response_time_ms
        string result_summary
    }

    UsageContext {
        int id PK
        string context_type
        string context_name
        string description
    }

    Models {
        int id PK
        string name UK
        string provider
        string version
        string description
        boolean is_local
    }

    Benchmarks {
        int id PK
        string name
        string description
        string prompt_text
        string created_date
        string user_id
        string metrics
    }

    BenchmarkResults {
        int id PK
        int benchmark_id FK
        int model_id FK
        int prompt_id FK
        float accuracy_score
        float coherence_score
        float speed_score
        float relevance_score
        string response_text
        int response_time_ms
        string timestamp
    }

    Documentation {
        int id PK
        string title
        string content
        string file_path
        string doc_type
        string tags
        string created_date
        string updated_date
    }

    PromptDocContext {
        int id PK
        int prompt_id FK
        int doc_id FK
        float relevance_score
        boolean is_active
        string inserted_at
    }

    ReportingMetrics {
        int id PK
        string metric_type
        string metric_name
        string timestamp
        float value
        string dimension
        string dimension_value
    }
```

## Notes on Database Schema

This diagram represents the complete database schema for the Prometheus AI Prompt Generator application. The schema includes:

1. **Core Entities:**
   - `Prompts`: Stores prompt templates with unique identifiers
   - `Tags`: Categorization labels for prompts
   - `Categories`: Hierarchical organization for prompts

2. **Relationships:**
   - Many-to-many between Prompts and Tags (via PromptTagAssociation)
   - One-to-many between Categories and Prompts
   - Self-referential relationship in Categories for hierarchical structure

3. **Versioning and History:**
   - `PromptVersions`: Tracks historical versions of prompts
   - `PromptUsage`: Records when and how prompts are used

4. **Analytics:**
   - `PromptScores`: Quality metrics for prompts
   - `ReportingMetrics`: Denormalized metrics for efficient reporting

5. **Benchmarking:**
   - `Models`: Registry of available LLMs
   - `Benchmarks`: Test definitions
   - `BenchmarkResults`: Performance metrics

6. **Documentation:**
   - `Documentation`: Stores context documents
   - `PromptDocContext`: Maps relevance between prompts and documentation

The schema is designed to support all requirements of the Prometheus AI application with a focus on performance, scalability, and analytical capabilities. 