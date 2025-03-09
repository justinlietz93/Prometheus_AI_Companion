# Database Standards

## Overview

This document defines the standards for database design, implementation, and usage in the Prometheus AI Prompt Generator. Following these standards ensures data integrity, performance, and maintainability across the application.

## Database Technology

The Prometheus AI Prompt Generator uses SQLite as its primary database technology:

- **SQLite Version**: 3.36.0 or higher
- **Storage Format**: Single database file in `data/prometheus.db`
- **Foreign Key Support**: Enabled (`PRAGMA foreign_keys = ON;`)
- **Journal Mode**: WAL (Write-Ahead Logging) for improved concurrency
- **Access Method**: Python `sqlite3` module with custom wrapper classes

## Database Schema Standards

### Naming Conventions

#### Tables

- Use PascalCase for table names
- Use singular nouns for entity tables (e.g., `Prompt`, not `Prompts`)
- Use verbs for junction/association tables (e.g., `PromptTagAssociation`)
- Use descriptive names that clearly indicate the table's purpose

```sql
-- Good
CREATE TABLE Prompt (...)
CREATE TABLE PromptTagAssociation (...)

-- Bad
CREATE TABLE prompts (...)  -- Lowercase and plural
CREATE TABLE pt_assoc (...)  -- Unclear abbreviation
```

#### Columns

- Use snake_case for column names
- Primary key should be named `id` (simple tables) or `<table_name>_id` (for clarity in complex joins)
- Foreign keys should be named `<referenced_table_name>_id`
- Use descriptive names that clearly indicate the column's purpose
- Boolean columns should use `is_` or `has_` prefix

```sql
-- Good
id INTEGER PRIMARY KEY,
prompt_id INTEGER,
is_active INTEGER,  -- Boolean
created_date TEXT,  -- Date/time

-- Bad
ID INTEGER PRIMARY KEY,  -- Uppercase
pid INTEGER,  -- Unclear abbreviation
active INTEGER,  -- Unclear boolean
created TEXT,  -- Ambiguous name
```

#### Indexes

- Use `idx_<table_name>_<column(s)>` format for index names
- For multi-column indexes, include all columns in the name or the purpose of the index

```sql
-- Good
CREATE INDEX idx_prompt_type ON Prompt(type);
CREATE INDEX idx_prompt_category_title ON Prompt(category_id, title);

-- Bad
CREATE INDEX prompt_index ON Prompt(type);  -- Unclear purpose
CREATE INDEX idx1 ON Prompt(category_id);  -- Non-descriptive
```

### Data Types

SQLite has a dynamic type system, but we standardize types as follows:

- **INTEGER**: For integer values, booleans (0/1), and all ID fields
- **REAL**: For floating-point values
- **TEXT**: For strings, dates, and times (ISO format: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS)
- **BLOB**: For binary data (use sparingly)

```sql
CREATE TABLE Prompt (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    category_id INTEGER,
    is_custom INTEGER NOT NULL DEFAULT 0,  -- Boolean
    created_date TEXT NOT NULL,  -- Date in ISO format
    modified_date TEXT,  -- Date in ISO format
    version INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);
```

### Constraints

- All tables must have a primary key
- Use `NOT NULL` for required fields
- Define `DEFAULT` values where appropriate
- Use `FOREIGN KEY` constraints for all relationships
- Use `UNIQUE` constraints for fields that must be unique
- Use `CHECK` constraints to enforce data rules

```sql
CREATE TABLE ApiKey (
    id INTEGER PRIMARY KEY,
    provider TEXT NOT NULL,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_date TEXT NOT NULL,
    usage_limit REAL NOT NULL DEFAULT 0.0,
    usage_current REAL NOT NULL DEFAULT 0.0,
    UNIQUE(provider, key_name),
    CHECK(usage_limit >= 0),
    CHECK(usage_current >= 0)
);
```

### Relationships

- Define explicit foreign key constraints for all relationships
- Include `ON DELETE` and `ON UPDATE` clauses
- Use cascading deletes only when child records should not exist without parent

```sql
-- Parent-dependent relationship (cascade delete)
FOREIGN KEY (prompt_id) REFERENCES Prompt(id) ON DELETE CASCADE

-- Reference relationship (nullify on delete)
FOREIGN KEY (category_id) REFERENCES Category(id) ON DELETE SET NULL
```

## Database Migration Standards

### Migration Files

- Store migration scripts in the `schema/migrations` directory
- Name migration files with a sequential number prefix: `001_initial_schema.sql`, `002_analytics_tables.sql`
- Each migration file should include:
  - A header comment with migration number, date, and description
  - Statements to enable foreign keys
  - All schema changes (CREATE TABLE, ALTER TABLE, etc.)
  - Any required seed data
  - Schema version update

```sql
-- Migration: 001
-- Date: 2025-03-09
-- Description: Initial schema creation

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create tables
CREATE TABLE Category (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES Category(id)
);

-- ... more table definitions ...

-- Insert initial seed data
INSERT INTO Category (id, name) VALUES (1, 'General');

-- Update schema version
INSERT INTO SchemaVersion (version, migration_date, description) 
VALUES (1, '2025-03-09', 'Initial schema');
```

### Version Tracking

- All schema changes must be tracked in the `SchemaVersion` table
- Each migration updates the schema version
- The application should check schema version on startup

```sql
CREATE TABLE SchemaVersion (
    version INTEGER PRIMARY KEY,
    migration_date TEXT NOT NULL,
    description TEXT NOT NULL
);
```

### Migration Process

- Migrations must be applied in order
- Never modify existing migration files
- Create new migration files for schema changes
- Test migrations in a development environment before deployment
- Include rollback instructions where possible

## Query Standards

### Parameterized Queries

- Always use parameterized queries to prevent SQL injection
- Never concatenate strings to build queries

```python
# Good
cursor.execute("SELECT * FROM Prompt WHERE type = ?", (prompt_type,))

# Bad
cursor.execute(f"SELECT * FROM Prompt WHERE type = '{prompt_type}'")  # Vulnerable to injection
```

### Query Organization

- Complex queries should be well-formatted with each clause on a new line
- Join conditions should be explicit
- Use table aliases for readability in complex joins
- Include appropriate comments for complex logic

```sql
-- Well-formatted complex query
SELECT 
    p.id,
    p.title,
    p.type,
    c.name AS category_name,
    COUNT(pu.id) AS usage_count,
    AVG(ps.score) AS average_score
FROM 
    Prompt p
LEFT JOIN 
    Category c ON p.category_id = c.id
LEFT JOIN 
    PromptUsage pu ON p.id = pu.prompt_id
LEFT JOIN 
    PromptScore ps ON p.id = ps.prompt_id
WHERE 
    p.is_custom = 0
    AND p.type = 'instruction'
GROUP BY 
    p.id
HAVING 
    COUNT(pu.id) > 0
ORDER BY 
    average_score DESC, usage_count DESC;
```

### Performance Considerations

- Create appropriate indexes for frequently queried columns
- Avoid `SELECT *` in production code, specify needed columns
- Use `EXPLAIN QUERY PLAN` to analyze query performance
- Limit result sets for large tables
- Use transactions for multiple operations

```python
# Using transactions
conn.execute("BEGIN TRANSACTION")
try:
    cursor.execute("INSERT INTO Prompt (title, content) VALUES (?, ?)", 
                  (title, content))
    prompt_id = cursor.lastrowid
    
    for tag_id in tag_ids:
        cursor.execute("INSERT INTO PromptTagAssociation (prompt_id, tag_id) VALUES (?, ?)",
                      (prompt_id, tag_id))
    conn.execute("COMMIT")
except Exception as e:
    conn.execute("ROLLBACK")
    raise e
```

## Data Access Layer Standards

### Repository Pattern

- Use the repository pattern to abstract database access
- Each entity should have its own repository class
- Repository methods should perform single-responsibility operations
- Use consistent method naming (find_by_*, insert, update, delete)

```python
class PromptRepository:
    def __init__(self, connection):
        self.connection = connection
        
    def find_by_id(self, prompt_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Prompt WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_prompt(row)
        
    def find_by_type(self, prompt_type):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Prompt WHERE type = ?", (prompt_type,))
        rows = cursor.fetchall()
        return [self._row_to_prompt(row) for row in rows]
        
    def insert(self, prompt):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO Prompt (title, content, type, category_id, is_custom, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                prompt.title,
                prompt.content,
                prompt.type,
                prompt.category_id,
                1 if prompt.is_custom else 0,
                datetime.now().isoformat()
            )
        )
        self.connection.commit()
        prompt.id = cursor.lastrowid
        return prompt
        
    def _row_to_prompt(self, row):
        return Prompt(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            type=row['type'],
            category_id=row['category_id'],
            is_custom=bool(row['is_custom'])
        )
```

### Connection Management

- Use a connection manager to handle database connections
- Ensure connections are properly closed
- Use context managers for connection handling
- Implement connection pooling for concurrent access

```python
class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    def __enter__(self):
        self.connect()
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

# Usage
with DatabaseConnection('data/prometheus.db') as conn:
    repository = PromptRepository(conn)
    prompt = repository.find_by_id(1)
```

### Error Handling

- Handle database-specific exceptions
- Provide clear error messages
- Log database errors with appropriate context
- Use custom exception classes for data access errors

```python
class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass

class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found"""
    pass

class DataIntegrityError(RepositoryError):
    """Raised when data integrity constraints are violated"""
    pass

# Usage in repository
def update(self, prompt):
    try:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE Prompt 
            SET title = ?, content = ?, type = ?, category_id = ?, 
                is_custom = ?, modified_date = ?
            WHERE id = ?
            """,
            (
                prompt.title,
                prompt.content,
                prompt.type,
                prompt.category_id,
                1 if prompt.is_custom else 0,
                datetime.now().isoformat(),
                prompt.id
            )
        )
        self.connection.commit()
        
        if cursor.rowcount == 0:
            raise EntityNotFoundError(f"Prompt with ID {prompt.id} not found")
            
        return True
    except sqlite3.IntegrityError as e:
        self.connection.rollback()
        raise DataIntegrityError(f"Failed to update prompt: {e}")
    except sqlite3.Error as e:
        self.connection.rollback()
        raise RepositoryError(f"Database error: {e}")
```

## Data Migration and Seeding

### Data Migration

- Create dedicated scripts for data migration tasks
- Use transactions for data migration
- Validate data before and after migration
- Log migration results

```python
def migrate_tags_to_new_schema(old_conn, new_conn):
    """Migrate tags from old schema to new schema"""
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Begin transaction
    new_conn.execute("BEGIN TRANSACTION")
    
    try:
        # Get all tags from old schema
        old_cursor.execute("SELECT id, name, description FROM old_tags")
        tags = old_cursor.fetchall()
        
        # Insert tags into new schema
        for tag in tags:
            new_cursor.execute(
                "INSERT INTO Tag (id, name, description) VALUES (?, ?, ?)",
                (tag['id'], tag['name'], tag['description'])
            )
            
        # Commit transaction
        new_conn.execute("COMMIT")
        print(f"Migrated {len(tags)} tags successfully")
        
    except Exception as e:
        # Rollback on error
        new_conn.execute("ROLLBACK")
        print(f"Migration failed: {e}")
        raise
```

### Data Seeding

- Seed scripts should be idempotent (can be run multiple times safely)
- Use check-before-insert pattern to avoid duplicates
- Include seed data for testing and development environments
- Version seed data scripts alongside migrations

```python
def seed_categories(conn):
    """Seed initial categories"""
    cursor = conn.cursor()
    
    # Categories to seed
    categories = [
        (1, "General", "General purpose prompts", None),
        (2, "Code", "Programming-related prompts", None),
        (3, "Writing", "Creative writing prompts", None),
        (4, "Python", "Python programming prompts", 2),  # Child of Code
        (5, "SQL", "SQL database prompts", 2)  # Child of Code
    ]
    
    for category in categories:
        # Check if category already exists
        cursor.execute("SELECT id FROM Category WHERE id = ?", (category[0],))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO Category (id, name, description, parent_id) VALUES (?, ?, ?, ?)",
                category
            )
            
    conn.commit()
    print("Categories seeded successfully")
```

## Database Backup and Recovery

### Backup Strategy

- Regular database backups should be scheduled
- Backup before each schema migration
- Store backups in a separate location
- Retain multiple backup generations

```python
def backup_database(db_path, backup_dir):
    """Create a timestamped backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_filename = os.path.basename(db_path)
    backup_path = os.path.join(backup_dir, f"{db_filename}.{timestamp}.bak")
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Backup failed: {e}")
        raise
```

### Recovery Procedures

- Document recovery procedures for different failure scenarios
- Test recovery procedures regularly
- Maintain recovery time objectives (RTOs)

```python
def restore_database(backup_path, db_path):
    """Restore database from a backup"""
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # If database already exists, create a pre-restore backup
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = f"{db_path}.pre_restore.{timestamp}"
        shutil.copy2(db_path, pre_restore_backup)
        print(f"Pre-restore backup created at {pre_restore_backup}")
    
    # Restore from backup
    try:
        shutil.copy2(backup_path, db_path)
        print(f"Database restored from {backup_path}")
        return True
    except Exception as e:
        print(f"Restore failed: {e}")
        raise
```

## Database Security

### Data Protection

- Encrypt sensitive data before storing in the database
- Store API keys and credentials encrypted
- Use prepared statements to prevent SQL injection
- Implement access controls at the application level

```python
def encrypt_api_key(key_value, encryption_key):
    """Encrypt an API key for storage"""
    # Simple encryption example (use proper encryption in production)
    cipher = AES.new(encryption_key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(key_value.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt_api_key(encrypted_value, encryption_key):
    """Decrypt a stored API key"""
    # Simple decryption example (use proper decryption in production)
    data = base64.b64decode(encrypted_value.encode('utf-8'))
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')
```

### Audit Logging

- Log database modifications for auditing purposes
- Include timestamp, user, and action details
- Store audit logs securely

```sql
CREATE TABLE AuditLog (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id INTEGER,
    details TEXT
);

-- Trigger example for auditing Prompt changes
CREATE TRIGGER audit_prompt_update AFTER UPDATE ON Prompt
BEGIN
    INSERT INTO AuditLog (timestamp, user_id, action, table_name, record_id, details)
    VALUES (
        datetime('now'),
        NEW.modified_by,
        'UPDATE',
        'Prompt',
        NEW.id,
        json_object('title', NEW.title, 'old_title', OLD.title)
    );
END;
```

## Performance Monitoring

### Query Performance

- Monitor slow queries using SQLite's trace functionality
- Establish performance baselines for common operations
- Optimize queries that exceed performance thresholds

```python
def enable_query_timing(conn):
    """Enable timing of SQL queries"""
    start_time = [0]
    
    def trace_callback(statement):
        start_time[0] = time.time()
    
    def profile_callback(statement, execution_time):
        execution_ms = (time.time() - start_time[0]) * 1000
        if execution_ms > 100:  # Log queries taking more than 100ms
            print(f"Slow query ({execution_ms:.2f}ms): {statement}")
    
    conn.set_trace_callback(trace_callback)
    conn.set_profile_callback(profile_callback)
```

### Connection Monitoring

- Track database connections for resource leaks
- Monitor connection times
- Implement connection pooling for high-concurrency situations

## Conclusion

Following these database standards ensures that the Prometheus AI Prompt Generator maintains a robust, efficient, and maintainable data layer. These standards should be followed by all team members when working with the database.

All database changes should be:
- Version controlled through migration scripts
- Tested thoroughly before deployment
- Reviewed by team members
- Well-documented in both code and external documentation

Last updated: March 9, 2025 