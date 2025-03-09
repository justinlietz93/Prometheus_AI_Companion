"""
Base test class for model tests in the Prometheus AI Prompt Generator.

This module provides a base test framework for all model tests, setting up an in-memory
SQLite database with the appropriate schema and test data for isolated testing.
"""

import os
import unittest
import tempfile
from importlib import import_module
from typing import List, Any, Optional, Type

from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError


class ModelTestBase(unittest.TestCase):
    """
    Base test class for model tests.
    
    This class sets up an in-memory SQLite database with the appropriate schema
    and test data for isolated testing of model classes.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests in the class."""
        # Determine project root and schema directories
        cls.project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..'
        ))
        cls.schema_dir = os.path.join(cls.project_root, 'database', 'schema')
        cls.migrations_dir = os.path.join(cls.project_root, 'database', 'migrations')
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Create a database connection
        self.db = QSqlDatabase.addDatabase('QSQLITE', 'test_connection')
        self.db.setDatabaseName(self.db_path)
        
        if not self.db.open():
            self.fail(f"Failed to open database: {self.db.lastError().text()}")
        
        # Apply schema and insert test data
        self._apply_schema()
        self._insert_test_data()
    
    def tearDown(self):
        """Clean up after each test."""
        # Close the database connection
        self.db.close()
        
        # Remove the database connection
        QSqlDatabase.removeDatabase('test_connection')
        
        # Close and remove the temporary database file
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _apply_schema(self):
        """Apply the database schema and migrations."""
        # Check if schema file exists
        schema_file = os.path.join(self.schema_dir, 'schema.sql')
        if not os.path.exists(schema_file):
            self.fail(f"Schema file not found: {schema_file}")
        
        # Apply schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            query = QSqlQuery(self.db)
            if not query.exec_(schema_sql):
                self.fail(f"Failed to apply schema: {query.lastError().text()}")
        
        # Apply migrations if they exist
        if os.path.exists(self.migrations_dir):
            migration_files = sorted([
                f for f in os.listdir(self.migrations_dir)
                if f.endswith('.sql')
            ])
            
            for migration_file in migration_files:
                with open(os.path.join(self.migrations_dir, migration_file), 'r') as f:
                    migration_sql = f.read()
                    query = QSqlQuery(self.db)
                    if not query.exec_(migration_sql):
                        self.fail(f"Failed to apply migration {migration_file}: {query.lastError().text()}")
    
    def _insert_test_data(self):
        """Insert test data into the database."""
        # Insert test users
        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT INTO Users (username, email, password_hash, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """)
        query.addBindValue("testuser")
        query.addBindValue("test@example.com")
        query.addBindValue("hashed_password")
        query.addBindValue(1)
        if not query.exec_():
            self.fail(f"Failed to insert test user: {query.lastError().text()}")
        
        # Insert test categories
        categories = [
            ("AI Tools", "Prompts for various AI tools and platforms", None),
            ("Programming", "Code-related prompts", None),
            ("Writing", "Creative and technical writing prompts", None)
        ]
        
        for name, description, parent_id in categories:
            query = QSqlQuery(self.db)
            query.prepare("""
                INSERT INTO Categories (name, description, parent_id, display_order, created_at, updated_at)
                VALUES (?, ?, ?, 0, datetime('now'), datetime('now'))
            """)
            query.addBindValue(name)
            query.addBindValue(description)
            query.addBindValue(parent_id)
            if not query.exec_():
                self.fail(f"Failed to insert test category: {query.lastError().text()}")
        
        # Insert test tags
        tags = [
            ("python", "Python programming language", "#3776AB"),
            ("javascript", "JavaScript programming language", "#F7DF1E"),
            ("writing", "Writing and content creation", "#6B8E23"),
            ("data-analysis", "Data analysis and visualization", "#4682B4")
        ]
        
        for name, description, color in tags:
            query = QSqlQuery(self.db)
            query.prepare("""
                INSERT INTO Tags (name, description, color, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """)
            query.addBindValue(name)
            query.addBindValue(description)
            query.addBindValue(color)
            if not query.exec_():
                self.fail(f"Failed to insert test tag: {query.lastError().text()}")
        
        # Insert test prompts
        prompts = [
            ("Python Helper", "I want you to act as a Python expert...", "Helps with Python coding tasks", 1),
            ("JavaScript Debugger", "Debug the following JavaScript code...", "Helps debug JavaScript code", 2),
            ("Blog Post Writer", "Write a blog post about...", "Generates blog post content", 3)
        ]
        
        for title, content, description, category_id in prompts:
            query = QSqlQuery(self.db)
            query.prepare("""
                INSERT INTO Prompts (
                    title, content, description, category_id, user_id,
                    is_public, is_featured, is_custom, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 1, 1, 0, 0, datetime('now'), datetime('now'))
            """)
            query.addBindValue(title)
            query.addBindValue(content)
            query.addBindValue(description)
            query.addBindValue(category_id)
            if not query.exec_():
                self.fail(f"Failed to insert test prompt: {query.lastError().text()}")
        
        # Insert prompt-tag relationships
        prompt_tags = [
            (1, 1),  # Python Helper - python
            (2, 2),  # JavaScript Debugger - javascript
            (3, 3),  # Blog Post Writer - writing
            (1, 4)   # Python Helper - data-analysis
        ]
        
        for prompt_id, tag_id in prompt_tags:
            query = QSqlQuery(self.db)
            query.prepare("""
                INSERT INTO PromptTags (prompt_id, tag_id)
                VALUES (?, ?)
            """)
            query.addBindValue(prompt_id)
            query.addBindValue(tag_id)
            if not query.exec_():
                self.fail(f"Failed to insert test prompt-tag: {query.lastError().text()}")
        
        # Insert test API keys
        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT INTO ApiKeys (
                user_id, provider, api_key, is_active, created_at, updated_at
            )
            VALUES (1, 'openai', 'encrypted_api_key', 1, datetime('now'), datetime('now'))
        """)
        if not query.exec_():
            self.fail(f"Failed to insert test API key: {query.lastError().text()}")
    
    def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> QSqlQuery:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            sql: The SQL query to execute
            params: Optional list of parameters to bind to the query
            
        Returns:
            The executed QSqlQuery object
        """
        query = QSqlQuery(self.db)
        query.prepare(sql)
        
        if params:
            for param in params:
                query.addBindValue(param)
        
        if not query.exec_():
            self.fail(f"Query failed: {query.lastError().text()}")
        
        return query
    
    def get_row_count(self, table: str, where_clause: Optional[str] = None, params: Optional[List[Any]] = None) -> int:
        """
        Get the number of rows in a table that match the given criteria.
        
        Args:
            table: The name of the table
            where_clause: Optional WHERE clause (without the 'WHERE' keyword)
            params: Optional parameters to bind to the query
            
        Returns:
            The number of matching rows
        """
        sql = f"SELECT COUNT(*) FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        query = self.execute_query(sql, params)
        if query.next():
            return query.value(0)
        return 0
    
    def assert_row_exists(self, table: str, where_clause: Optional[str] = None, params: Optional[List[Any]] = None):
        """
        Assert that at least one row exists in the table matching the criteria.
        
        Args:
            table: The name of the table
            where_clause: Optional WHERE clause (without the 'WHERE' keyword)
            params: Optional parameters to bind to the query
        """
        count = self.get_row_count(table, where_clause, params)
        self.assertGreater(count, 0, f"No rows found in {table} matching the criteria")
    
    def get_model_class(self, class_name: str) -> Type:
        """
        Dynamically import and return a model class by name.
        
        Args:
            class_name: The name of the model class to import
            
        Returns:
            The imported model class
        """
        module = import_module('prometheus_prompt_generator.domain.models')
        return getattr(module, class_name)


if __name__ == "__main__":
    unittest.main() 