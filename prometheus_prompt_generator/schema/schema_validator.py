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
            'PromptUsage', 'Models', 'Benchmarks', 'BenchmarkResults',
            'Documentation', 'UsageContext', 'ReportingMetrics', 'PromptDocContext',
            'ApiKeys', 'CodeMapUsage', 'LlmUsage', 'SchemaExtension'
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
            'idx_prompts_type', 'idx_prompts_category', 'idx_prompts_custom',
            'idx_prompt_scores', 'idx_prompt_usage', 'idx_reporting_metrics',
            'idx_benchmark_results', 'idx_prompt_doc_context',
            'idx_api_keys', 'idx_code_map_usage', 'idx_llm_usage', 'idx_llm_usage_billing',
            'idx_schema_extension'
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
            },
            {
                'name': 'Get benchmark results by model',
                'sql': '''
                SELECT b.name, m.name, AVG(br.accuracy_score) as avg_accuracy
                FROM BenchmarkResults br
                JOIN Benchmarks b ON br.benchmark_id = b.id
                JOIN Models m ON br.model_id = m.id
                GROUP BY b.id, m.id
                ''',
                'iterations': 5
            },
            {
                'name': 'Get API keys by provider',
                'sql': '''
                SELECT * FROM ApiKeys 
                WHERE provider = 'OpenAI' AND is_active = 1
                ''',
                'iterations': 5
            },
            {
                'name': 'Get LLM usage statistics',
                'sql': '''
                SELECT provider, model, SUM(total_tokens) as tokens, SUM(estimated_cost) as cost 
                FROM LlmUsage 
                WHERE timestamp >= date('now', '-30 days')
                GROUP BY provider, model
                ORDER BY cost DESC
                ''',
                'iterations': 5
            },
            {
                'name': 'Get code map usage by user',
                'sql': '''
                SELECT user_id, COUNT(*) as usage_count, AVG(map_complexity_score) as avg_complexity 
                FROM CodeMapUsage 
                GROUP BY user_id
                ORDER BY usage_count DESC
                ''',
                'iterations': 5
            }
        ]
        
        # Insert test data if the database is empty
        self.cursor.execute("SELECT COUNT(*) FROM Prompts")
        if self.cursor.fetchone()[0] == 0:
            try:
                self._insert_test_data()
            except sqlite3.Error as e:
                print(f"Error inserting test data: {e}")
                # Continue with validation even if test data insertion fails
        
        # Run performance tests
        for query in test_queries:
            total_time = 0
            for i in range(query['iterations']):
                start_time = time.time()
                try:
                    self.cursor.execute(query['sql'])
                    results = self.cursor.fetchall()
                    end_time = time.time()
                    total_time += (end_time - start_time)
                    
                    # Log the query performance
                    iteration_time = (end_time - start_time) * 1000  # Convert to ms
                    print(f"  Query: {query['name']}, Iteration {i+1}: {iteration_time:.2f}ms, {len(results)} rows")
                    
                except sqlite3.Error as e:
                    print(f"Error executing query '{query['name']}': {e}")
                    break
            
            if i + 1 < query['iterations']:
                # Query failed, skip performance calculation
                self.performance_results.append(f"❌ Query '{query['name']}' failed to execute")
                continue
                
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
        
        # Insert usage context data
        usage_contexts = [
            (1, 'Project', 'Website Content', 'Content creation for website'),
            (2, 'Task', 'Email Marketing', 'Email campaign content'),
            (3, 'Project', 'Product Description', 'E-commerce product descriptions')
        ]
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO UsageContext 
            (id, context_type, context_name, description)
            VALUES (?, ?, ?, ?)
            """,
            usage_contexts
        )
        
        # Insert test prompt usage data
        usage_data = []
        for prompt_id in range(1, 101):
            # Each prompt used 0-10 times
            for i in range(prompt_id % 11):
                context_id = (i % 3) + 1
                usage_data.append((
                    prompt_id, '2025-03-09T12:00:00', context_id, 'test_user', 
                    1, 250, 'Successfully generated content'
                ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO PromptUsage 
            (prompt_id, timestamp, context_id, user_id, successful, response_time_ms, result_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            usage_data
        )
        
        # Insert test documentation
        documentation = [
            (1, 'Python API Docs', 'Python API documentation content', '/docs/python_api.md', 'API', '["python","api"]', '2025-03-09', '2025-03-09'),
            (2, 'SQL Patterns', 'Common SQL patterns for prompts', '/docs/sql_patterns.md', 'Tutorial', '["sql","database"]', '2025-03-09', '2025-03-09'),
            (3, 'Prompt Guidelines', 'Best practices for prompt creation', '/docs/prompt_guidelines.md', 'Guide', '["prompts","guidelines"]', '2025-03-09', '2025-03-09')
        ]
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO Documentation 
            (id, title, content, file_path, doc_type, tags, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            documentation
        )
        
        # Insert test models
        models = [
            (1, 'gpt-4-turbo', 'OpenAI', '2023-11', 'Large-scale language model with 1.8 trillion parameters', 0),
            (2, 'claude-3-opus', 'Anthropic', '2024-01', 'Advanced reasoning model with 175 billion parameters', 0),
            (3, 'llama-3-70b', 'Meta', '2024-02', 'Open source model with 70 billion parameters', 1)
        ]
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO Models 
            (id, name, provider, version, description, is_local)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            models
        )
        
        # Insert test benchmarks
        benchmarks = [
            (1, 'Coherence Test', 'Tests response coherence', 'Generate a coherent explanation of quantum computing', '2025-03-09', 'test_user', '{"metrics":["coherence","relevance"]}'),
            (2, 'Speed Test', 'Tests response speed', 'Generate a 500-word story quickly', '2025-03-09', 'test_user', '{"metrics":["speed","coherence"]}')
        ]
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO Benchmarks 
            (id, name, description, prompt_text, created_date, user_id, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            benchmarks
        )
        
        # Insert test benchmark results
        benchmark_results = []
        for benchmark_id in range(1, 3):
            for model_id in range(1, 4):
                for i in range(5):  # 5 runs per benchmark/model combination
                    prompt_id = (benchmark_id * model_id * i) % 100 + 1
                    benchmark_results.append((
                        benchmark_id, model_id, prompt_id, 
                        4.5 - (i * 0.1), 4.2 - (i * 0.1), 4.8 - (i * 0.1), 4.0 - (i * 0.1),
                        f"Test response for benchmark {benchmark_id}, model {model_id}, run {i}",
                        100 + (model_id * 50), '2025-03-09T12:00:00'
                    ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO BenchmarkResults 
            (benchmark_id, model_id, prompt_id, accuracy_score, coherence_score, 
             speed_score, relevance_score, response_text, response_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            benchmark_results
        )
        
        # Insert test reporting metrics
        metrics = [
            ('usage', 'daily_count', '2025-03-09', 10, 'prompt_type', 'character'),
            ('usage', 'daily_count', '2025-03-09', 15, 'prompt_type', 'scenario'),
            ('usage', 'daily_count', '2025-03-09', 20, 'prompt_type', 'instruction'),
            ('score', 'avg_rating', '2025-03-09', 4.5, 'prompt_id', '1'),
            ('score', 'avg_rating', '2025-03-09', 4.2, 'prompt_id', '2')
        ]
        
        for metric in metrics:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO ReportingMetrics 
                    (metric_type, metric_name, timestamp, value, dimension, dimension_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    metric
                )
            except sqlite3.Error as e:
                print(f"Warning: Could not insert reporting metric: {e}")
                
        # Insert test API keys
        api_keys = [
            (1, 'OpenAI', 'Production Key', 'encrypted-key-value-1', 1, '2025-03-09', '2025-03-09', '2025-03-09', 'admin', 100.0, 45.75, 'Production'),
            (2, 'Anthropic', 'Testing Key', 'encrypted-key-value-2', 1, '2025-03-09', '2025-03-09', '2025-03-09', 'admin', 50.0, 12.25, 'Development'),
            (3, 'Cohere', 'Backup Key', 'encrypted-key-value-3', 0, '2025-03-09', '2025-03-09', '2025-03-08', 'admin', 25.0, 0.0, 'Staging')
        ]
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO ApiKeys 
            (id, provider, key_name, key_value, is_active, created_date, updated_date, last_used_date, user_id, usage_limit, usage_current, env_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            api_keys
        )
        
        # Insert test code map usage
        code_map_usage = [
            (1, '2025-03-09T10:00:00', 'user1', 'session123', '/path/to/repo1', 120, 450, 600, 1250, 0.75, 1, None, 1),
            (2, '2025-03-09T11:30:00', 'user2', 'session124', '/path/to/repo2', 85, 320, 420, 980, 0.62, 1, None, 2),
            (3, '2025-03-09T14:15:00', 'user1', 'session125', '/path/to/repo3', 210, 780, 950, 1850, 0.91, 1, None, 3)
        ]
        
        for usage in code_map_usage:
            try:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO CodeMapUsage 
                    (id, timestamp, user_id, session_id, repo_path, file_count, node_count, edge_count, generation_time_ms, map_complexity_score, successful, error_message, prompt_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    usage
                )
            except sqlite3.Error as e:
                print(f"Warning: Could not insert code map usage: {e}")
        
        # Insert test LLM usage
        llm_usage = [
            (1, '2025-03-09T09:20:00', 'OpenAI', 'gpt-4-turbo', 1, 750, 350, 1100, 0.22, 'Development', 'user1', 'project1', 'code_completion', 1, 'req123', 1200),
            (2, '2025-03-09T10:45:00', 'Anthropic', 'claude-3-opus', 2, 1200, 650, 1850, 0.37, 'Production', 'user2', 'project2', 'prompt_generation', 2, 'req124', 950),
            (3, '2025-03-09T13:15:00', 'OpenAI', 'gpt-4-turbo', 1, 500, 250, 750, 0.15, 'Development', 'user1', 'project1', 'code_explanation', 3, 'req125', 850)
        ]
        
        for usage in llm_usage:
            try:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO LlmUsage 
                    (id, timestamp, provider, model, api_key_id, prompt_tokens, completion_tokens, total_tokens, estimated_cost, billing_category, user_id, project_id, feature_used, prompt_id, request_id, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    usage
                )
            except sqlite3.Error as e:
                print(f"Warning: Could not insert LLM usage: {e}")
        
        # Insert schema extension log entries
        schema_extensions = [
            (1, 'Prompts', 'is_custom', 'INTEGER', 4, '2025-03-09', 'Track custom vs. system prompts', 1),
            (2, 'Models', 'max_context_length', 'INTEGER', 4, '2025-03-09', 'Track model context window size', 0)
        ]
        
        for extension in schema_extensions:
            try:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO SchemaExtension 
                    (id, table_name, column_name, column_type, migration_id, added_date, reason, is_required)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    extension
                )
            except sqlite3.Error as e:
                print(f"Warning: Could not insert schema extension: {e}")
        
        # Commit the test data
        self.conn.commit()
        print(f"Test data inserted: 100 prompts, {len(prompt_tags)} tag associations, {len(usage_data)} usage records, {len(benchmark_results)} benchmark results, {len(metrics)} metrics, {len(api_keys)} API keys, {len(code_map_usage)} code map usages, {len(llm_usage)} LLM usages, {len(schema_extensions)} schema extensions")
    
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
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Schema Validation Report\n\n")
            f.write(f"Database: {self.db_path}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Schema Validation Results\n\n")
            for result in self.validation_results:
                # Replace Unicode with ASCII for Windows compatibility
                ascii_result = result.replace("✅", "[PASS]").replace("❌", "[FAIL]")
                f.write(f"- {ascii_result}\n")
            
            f.write("\n## Performance Test Results\n\n")
            for result in self.performance_results:
                # Replace Unicode with ASCII for Windows compatibility
                ascii_result = result.replace("✅", "[PASS]").replace("❌", "[FAIL]")
                f.write(f"- {ascii_result}\n")
            
            # Summary
            validation_success = all("❌" not in result for result in self.validation_results)
            performance_success = all("❌" not in result for result in self.performance_results)
            
            f.write("\n## Summary\n\n")
            if validation_success:
                f.write("[PASS] Schema validation passed\n")
            else:
                f.write("[FAIL] Schema validation failed\n")
            
            if performance_success:
                f.write("[PASS] Performance tests passed\n")
            else:
                f.write("[FAIL] Performance tests failed\n")
        
        print(f"\nValidation report saved to: {report_path}")


def main():
    """Main entry point for the script."""
    print("Starting schema validator...")
    
    # Define the default database path
    default_db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        'prometheus.db'
    )
    print(f"Default database path: {default_db_path}")
    
    # Use command line argument if provided, otherwise use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db_path
    print(f"Using database path: {db_path}")
    
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
        print(f"Schema directory: {schema_dir}")
        print(f"Migrations directory: {migrations_dir}")
        
        if os.path.exists(migrations_dir):
            print(f"Database does not exist. Creating from migration scripts in {migrations_dir}")
            conn = sqlite3.connect(db_path)
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # Apply migrations in order
                migration_files = sorted([
                    f for f in os.listdir(migrations_dir) if f.endswith('.sql')
                ])
                print(f"Found migration files: {migration_files}")
                
                for migration_file in migration_files:
                    print(f"Applying migration: {migration_file}")
                    with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                        sql = f.read()
                        conn.executescript(sql)
                
                conn.commit()
                conn.close()
                print(f"Database created: {db_path}")
            except Exception as e:
                print(f"Error creating database: {e}")
                return 1
        else:
            print(f"Error: Migration directory not found: {migrations_dir}")
            return 1
    
    # Run the validation
    try:
        validator = SchemaValidator(db_path)
        validator.run_validation()
        validator.generate_report()
    except Exception as e:
        print(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 