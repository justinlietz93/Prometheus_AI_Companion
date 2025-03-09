#!/usr/bin/env python
"""
Schema Validator for Prometheus AI Prompt Generator

This script validates the SQLite schema against requirements and tests 
performance of typical queries.

Usage:
    python schema_validator.py [database_path]
"""

import os
import sys
import time
import sqlite3
from pathlib import Path


class SchemaValidator:
    """Validates the SQLite schema and tests performance of typical queries."""
    
    def __init__(self, db_path):
        """Initialize the validator with the database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.validation_results = []
        self.performance_results = []
    
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def validate_schema(self):
        """Validate the database schema against requirements."""
        required_tables = [
            'Prompts', 'Tags', 'Categories', 'PromptTagAssociation', 
            'PromptVersions', 'CategoryHierarchy', 'PromptScores',
            'PromptUsage', 'LlmModels', 'Benchmarks', 'BenchmarkResults',
            'DocumentationContext'
        ]
        
        # Check if required tables exist
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row['name'] for row in self.cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                self.validation_results.append(f"✅ Table {table} exists")
            else:
                self.validation_results.append(f"❌ Required table {table} does not exist")
        
        # Check for foreign key constraints
        self.cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = self.cursor.fetchall()
        if fk_errors:
            for error in fk_errors:
                self.validation_results.append(f"❌ Foreign key constraint violation in {error}")
        else:
            self.validation_results.append("✅ No foreign key constraint violations")
        
        # Check for indices on frequently queried columns
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indices = [row['name'] for row in self.cursor.fetchall()]
        required_indices = [
            'idx_prompts_type', 'idx_prompts_category', 
            'idx_prompt_tag_prompt_id', 'idx_prompt_tag_tag_id'
        ]
        
        for index in required_indices:
            if any(index in idx for idx in indices):
                self.validation_results.append(f"✅ Index {index} exists")
            else:
                self.validation_results.append(f"❌ Required index {index} does not exist")
    
    def test_query_performance(self):
        """Test performance of typical queries."""
        test_queries = [
            {
                'name': 'Get all prompts',
                'sql': 'SELECT * FROM Prompts',
                'iterations': 5
            },
            {
                'name': 'Get prompts by type',
                'sql': 'SELECT * FROM Prompts WHERE type = "character"',
                'iterations': 5
            },
            {
                'name': 'Get prompts with tags',
                'sql': '''
                SELECT p.*, GROUP_CONCAT(t.name) as tags 
                FROM Prompts p
                LEFT JOIN PromptTagAssociation pta ON p.id = pta.prompt_id
                LEFT JOIN Tags t ON pta.tag_id = t.id
                GROUP BY p.id
                ''',
                'iterations': 5
            },
            {
                'name': 'Get prompt usage statistics',
                'sql': '''
                SELECT p.id, p.title, COUNT(pu.id) as usage_count
                FROM Prompts p
                LEFT JOIN PromptUsage pu ON p.id = pu.prompt_id
                GROUP BY p.id
                ORDER BY usage_count DESC
                ''',
                'iterations': 5
            },
            {
                'name': 'Search prompts by title or description',
                'sql': '''
                SELECT * FROM Prompts 
                WHERE title LIKE '%AI%' OR description LIKE '%AI%'
                ''',
                'iterations': 5
            }
        ]
        
        # Insert test data if the database is empty
        self.cursor.execute("SELECT COUNT(*) FROM Prompts")
        if self.cursor.fetchone()[0] == 0:
            self._insert_test_data()
        
        # Run performance tests
        for query in test_queries:
            total_time = 0
            for i in range(query['iterations']):
                start_time = time.time()
                self.cursor.execute(query['sql'])
                results = self.cursor.fetchall()
                end_time = time.time()
                total_time += (end_time - start_time)
            
            avg_time = (total_time / query['iterations']) * 1000  # Convert to ms
            result = f"{query['name']}: {avg_time:.2f}ms (avg over {query['iterations']} runs, {len(results)} rows)"
            self.performance_results.append(result)
            
            # Check against performance requirements
            if avg_time < 100:
                self.performance_results.append(f"✅ Performance within requirements (<100ms)")
            else:
                self.performance_results.append(f"❌ Performance exceeds requirement: {avg_time:.2f}ms (>100ms)")
    
    def _insert_test_data(self):
        """Insert test data for performance testing."""
        print("Inserting test data for performance testing...")
        
        # Insert test categories
        categories = [
            (1, 'Creative', 'For creative writing and storytelling'),
            (2, 'Technical', 'For technical tasks and programming'),
            (3, 'Business', 'For business and professional use')
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO Categories (id, name, description) VALUES (?, ?, ?)",
            categories
        )
        
        # Insert test tags
        tags = [
            (1, 'Fiction', 'Fiction writing', '#FF5733'),
            (2, 'AI', 'Artificial Intelligence', '#33FF57'),
            (3, 'Programming', 'Programming tasks', '#3357FF'),
            (4, 'Python', 'Python language', '#7D33FF'),
            (5, 'Marketing', 'Marketing content', '#FF33A8')
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO Tags (id, name, description, color) VALUES (?, ?, ?, ?)",
            tags
        )
        
        # Insert test prompts (100 for adequate testing)
        prompts = []
        for i in range(1, 101):
            category_id = (i % 3) + 1
            prompt_type = ['character', 'scenario', 'instruction'][i % 3]
            title = f"Test Prompt {i}"
            template = f"This is a test template for prompt {i}. It can be used for {{parameter1}} with {{parameter2}}."
            description = f"Test description for prompt {i} related to {prompt_type} generation."
            
            prompts.append((
                i, prompt_type, title, template, description, 
                'test_author', '1.0', '2025-03-09', '2025-03-09', category_id
            ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO Prompts 
            (id, type, title, template, description, author, version, created_date, updated_date, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            prompts
        )
        
        # Insert test prompt-tag associations
        prompt_tags = []
        for prompt_id in range(1, 101):
            # Each prompt gets 1-3 tags
            for tag_id in range(1, min(5, (prompt_id % 5) + 1)):
                prompt_tags.append((prompt_id, tag_id))
        
        self.cursor.executemany(
            "INSERT OR IGNORE INTO PromptTagAssociation (prompt_id, tag_id) VALUES (?, ?)",
            prompt_tags
        )
        
        # Insert test prompt usage data
        usage_data = []
        for prompt_id in range(1, 101):
            # Each prompt used 0-10 times
            for i in range(prompt_id % 11):
                usage_data.append((
                    prompt_id, '2025-03-09', 'test_user', 'test_session'
                ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO PromptUsage 
            (prompt_id, usage_date, user_id, session_id)
            VALUES (?, ?, ?, ?)
            """,
            usage_data
        )
        
        # Commit the test data
        self.conn.commit()
        print(f"Test data inserted: 100 prompts, {len(prompt_tags)} tag associations, {len(usage_data)} usage records")
    
    def run_validation(self):
        """Run all validation and performance tests."""
        if not self.connect():
            return False
        
        print("\n=== Schema Validation ===")
        self.validate_schema()
        for result in self.validation_results:
            print(result)
        
        print("\n=== Performance Testing ===")
        self.test_query_performance()
        for result in self.performance_results:
            print(result)
        
        self.close()
        return True
    
    def generate_report(self):
        """Generate a validation report."""
        report_path = Path(self.db_path).parent / 'schema_validation_report.md'
        with open(report_path, 'w') as f:
            f.write("# Schema Validation Report\n\n")
            f.write(f"Database: {self.db_path}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Schema Validation Results\n\n")
            for result in self.validation_results:
                f.write(f"- {result}\n")
            
            f.write("\n## Performance Test Results\n\n")
            for result in self.performance_results:
                f.write(f"- {result}\n")
            
            # Summary
            validation_success = all("❌" not in result for result in self.validation_results)
            performance_success = all("❌" not in result for result in self.performance_results)
            
            f.write("\n## Summary\n\n")
            if validation_success:
                f.write("✅ Schema validation passed\n")
            else:
                f.write("❌ Schema validation failed\n")
            
            if performance_success:
                f.write("✅ Performance tests passed\n")
            else:
                f.write("❌ Performance tests failed\n")
        
        print(f"\nValidation report saved to: {report_path}")


def main():
    """Main entry point for the script."""
    # Define the default database path
    default_db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        'prometheus.db'
    )
    
    # Use command line argument if provided, otherwise use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db_path
    
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")
    
    # Create the database if it doesn't exist
    if not os.path.exists(db_path):
        # Check if the schema files exist
        schema_dir = os.path.dirname(os.path.abspath(__file__))
        migrations_dir = os.path.join(schema_dir, 'migrations')
        
        if os.path.exists(migrations_dir):
            print(f"Database does not exist. Creating from migration scripts in {migrations_dir}")
            conn = sqlite3.connect(db_path)
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # Apply migrations in order
            migration_files = sorted([
                f for f in os.listdir(migrations_dir) if f.endswith('.sql')
            ])
            
            for migration_file in migration_files:
                print(f"Applying migration: {migration_file}")
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    sql = f.read()
                    conn.executescript(sql)
            
            conn.commit()
            conn.close()
            print(f"Database created: {db_path}")
        else:
            print(f"Error: Migration directory not found: {migrations_dir}")
            return 1
    
    # Run the validation
    validator = SchemaValidator(db_path)
    validator.run_validation()
    validator.generate_report()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 