#!/usr/bin/env python
"""
Database Initialization Script for Prometheus AI

This script initializes the SQLite database for the Prometheus AI application
by applying all migration scripts in the correct order.
"""

import os
import sys
import sqlite3
import glob
import logging
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_init')

# Default paths
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prometheus.db')
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')


class DatabaseInitializer:
    """Initializes the SQLite database by applying migrations."""
    
    def __init__(self, db_path: str, migrations_dir: str = MIGRATIONS_DIR):
        """
        Initialize the database initializer.
        
        Args:
            db_path: Path to the SQLite database file
            migrations_dir: Directory containing migration scripts
        """
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Connect to the SQLite database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    def get_applied_migrations(self) -> List[int]:
        """
        Get a list of already applied migration versions.
        
        Returns:
            List[int]: List of applied migration version numbers
        """
        # Check if SchemaVersion table exists
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'"
        )
        if not self.cursor.fetchone():
            logger.info("SchemaVersion table does not exist. No migrations applied yet.")
            return []
        
        # Get applied versions
        self.cursor.execute("SELECT version FROM SchemaVersion ORDER BY version")
        versions = [row[0] for row in self.cursor.fetchall()]
        logger.info(f"Found {len(versions)} applied migrations: {versions}")
        return versions
    
    def get_available_migrations(self) -> List[Tuple[int, str]]:
        """
        Get a list of available migration scripts.
        
        Returns:
            List[Tuple[int, str]]: List of (version, path) tuples for available migrations
        """
        # Find migration files
        migration_files = glob.glob(os.path.join(self.migrations_dir, "*.sql"))
        migrations = []
        
        for file_path in migration_files:
            file_name = os.path.basename(file_path)
            # Extract version number from file name (e.g., "001_initial_schema.sql" -> 1)
            try:
                version = int(file_name.split('_')[0])
                migrations.append((version, file_path))
            except (ValueError, IndexError):
                logger.warning(f"Skipping file with invalid naming format: {file_name}")
        
        # Sort by version number
        migrations.sort(key=lambda x: x[0])
        logger.info(f"Found {len(migrations)} available migrations")
        return migrations
    
    def apply_migration(self, version: int, file_path: str) -> bool:
        """
        Apply a single migration.
        
        Args:
            version: Migration version number
            file_path: Path to the migration SQL file
            
        Returns:
            bool: True if migration was applied successfully, False otherwise
        """
        logger.info(f"Applying migration {version}: {os.path.basename(file_path)}")
        
        try:
            # Read migration SQL
            with open(file_path, 'r') as f:
                sql = f.read()
            
            # Execute migration in a transaction
            self.connection.executescript(sql)
            self.connection.commit()
            
            logger.info(f"Migration {version} applied successfully")
            return True
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"Error applying migration {version}: {str(e)}")
            return False
    
    def json_to_sqlite_converter(self, json_dir: Optional[str] = None) -> bool:
        """
        Convert existing JSON prompt files to SQLite.
        
        Args:
            json_dir: Directory containing JSON prompt files
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        if not json_dir:
            json_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompts')
        
        if not os.path.exists(json_dir):
            logger.warning(f"JSON directory not found: {json_dir}")
            return False
        
        try:
            # Find all JSON files
            json_files = glob.glob(os.path.join(json_dir, "*.json"))
            logger.info(f"Found {len(json_files)} JSON prompt files to convert")
            
            conversion_count = 0
            for file_path in json_files:
                try:
                    with open(file_path, 'r') as f:
                        prompt_data = json.load(f)
                    
                    # Extract prompt data
                    prompt_type = prompt_data.get('name', os.path.basename(file_path).replace('.json', ''))
                    title = prompt_data.get('description', prompt_type.capitalize())
                    
                    # Check if prompt already exists
                    self.cursor.execute(
                        "SELECT id FROM Prompts WHERE type = ?", (prompt_type,)
                    )
                    existing_prompt = self.cursor.fetchone()
                    
                    if existing_prompt:
                        logger.info(f"Prompt '{prompt_type}' already exists, skipping")
                        continue
                    
                    # Get metadata
                    metadata = prompt_data.get('metadata', {})
                    author = metadata.get('author', 'Prometheus AI')
                    version = metadata.get('version', '1.0.0')
                    created_date = metadata.get('created', datetime.now().strftime('%Y-%m-%d'))
                    
                    # Get the highest urgency prompt template
                    prompts = prompt_data.get('prompts', {})
                    # Convert numeric string keys to integers for sorting
                    urgency_levels = {int(k): v for k, v in prompts.items() if k.isdigit()}
                    template = urgency_levels.get(10, urgency_levels.get(5, next(iter(urgency_levels.values()), '')))
                    
                    # Insert prompt into database
                    self.cursor.execute(
                        """
                        INSERT INTO Prompts (
                            type, title, template, description, author, version, created_date, updated_date, category_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            prompt_type, title, template, title, author, version, 
                            created_date, datetime.now().strftime('%Y-%m-%d'), 
                            1  # Default to General category
                        )
                    )
                    prompt_id = self.cursor.lastrowid
                    
                    # Insert prompt versions for different urgency levels
                    for urgency, prompt_text in urgency_levels.items():
                        self.cursor.execute(
                            """
                            INSERT INTO PromptVersions (
                                prompt_id, version_num, template, created_date, author
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                prompt_id, int(urgency), prompt_text, created_date, author
                            )
                        )
                    
                    # Add tags
                    tags = metadata.get('tags', [])
                    for tag_name in tags:
                        # Check if tag exists
                        self.cursor.execute(
                            "SELECT id FROM Tags WHERE name = ?", (tag_name,)
                        )
                        tag_row = self.cursor.fetchone()
                        
                        if tag_row:
                            tag_id = tag_row[0]
                        else:
                            # Create new tag
                            self.cursor.execute(
                                "INSERT INTO Tags (name, description) VALUES (?, ?)",
                                (tag_name, f"{tag_name.capitalize()} tag")
                            )
                            tag_id = self.cursor.lastrowid
                        
                        # Associate tag with prompt
                        self.cursor.execute(
                            "INSERT INTO PromptTagAssociation (prompt_id, tag_id) VALUES (?, ?)",
                            (prompt_id, tag_id)
                        )
                    
                    conversion_count += 1
                    
                except Exception as e:
                    logger.error(f"Error converting file {file_path}: {str(e)}")
            
            self.connection.commit()
            logger.info(f"Successfully converted {conversion_count} prompt files to SQLite")
            return True
        
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error in JSON conversion: {str(e)}")
            return False
    
    def initialize(self, convert_json: bool = True) -> bool:
        """
        Initialize the database by applying all pending migrations.
        
        Args:
            convert_json: Whether to convert existing JSON prompt files
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database
        if not self.connect():
            return False
        
        try:
            # Get applied and available migrations
            applied_versions = self.get_applied_migrations()
            available_migrations = self.get_available_migrations()
            
            # Apply pending migrations
            for version, file_path in available_migrations:
                if version not in applied_versions:
                    logger.info(f"Applying migration {version}")
                    if not self.apply_migration(version, file_path):
                        logger.error(f"Failed to apply migration {version}")
                        return False
                else:
                    logger.info(f"Migration {version} already applied, skipping")
            
            # Convert JSON prompt files if requested
            if convert_json and not applied_versions:
                logger.info("Converting JSON prompt files to SQLite")
                self.json_to_sqlite_converter()
            
            logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            return False
        finally:
            if self.connection:
                self.connection.close()


def main():
    """Main entry point for the database initializer script."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = DEFAULT_DB_PATH
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize database
    initializer = DatabaseInitializer(db_path)
    success = initializer.initialize()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 