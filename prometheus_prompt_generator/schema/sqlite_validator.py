#!/usr/bin/env python
"""
SQLite Schema Validator for Prometheus AI

This script validates the SQLite database schema for the Prometheus AI application.
It checks for common issues, circular references, and orphaned tables.

Usage:
  python sqlite_validator.py [path_to_database]
"""

import os
import sys
import sqlite3
import logging
from typing import List, Dict, Tuple, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('schema_validator')

class SchemaValidator:
    """Validates SQLite database schema for common issues."""
    
    def __init__(self, db_path: str):
        """
        Initialize the validator with database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.tables = []
        self.foreign_keys = {}
        self.issues = []
    
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
            return True
        except sqlite3.Error as e:
            self.issues.append(f"Connection error: {str(e)}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        Get all tables in the database.
        
        Returns:
            List[str]: List of table names
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        self.tables = [row[0] for row in self.cursor.fetchall()]
        return self.tables
    
    def get_foreign_keys(self) -> Dict[str, List[Dict]]:
        """
        Get all foreign key relationships.
        
        Returns:
            Dict[str, List[Dict]]: Dictionary mapping table names to their foreign keys
        """
        self.foreign_keys = {}
        
        for table in self.tables:
            self.cursor.execute(f"PRAGMA foreign_key_list({table})")
            fk_list = self.cursor.fetchall()
            
            if fk_list:
                self.foreign_keys[table] = []
                for fk in fk_list:
                    self.foreign_keys[table].append({
                        'id': fk[0],
                        'seq': fk[1],
                        'table': fk[2],
                        'from': fk[3],
                        'to': fk[4],
                        'on_update': fk[5],
                        'on_delete': fk[6],
                        'match': fk[7]
                    })
        
        return self.foreign_keys
    
    def check_circular_references(self) -> List[str]:
        """
        Check for circular references in foreign keys.
        
        Returns:
            List[str]: List of circular reference chains found
        """
        circular_refs = []
        
        # Build dependency graph
        graph = {}
        for table, fk_list in self.foreign_keys.items():
            if table not in graph:
                graph[table] = []
            
            for fk in fk_list:
                referenced_table = fk['table']
                if referenced_table not in graph:
                    graph[referenced_table] = []
                
                # Add edge from table to referenced table
                graph[table].append(referenced_table)
        
        # Check for cycles in the graph
        def find_cycles(node, visited, path):
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycles = find_cycles(neighbor, visited.copy(), path.copy())
                    if cycles:
                        return cycles
                elif neighbor in path:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            return None
        
        for node in graph:
            cycle = find_cycles(node, set(), [])
            if cycle and ' -> '.join(cycle) not in circular_refs:
                circular_refs.append(' -> '.join(cycle))
        
        return circular_refs
    
    def check_orphaned_tables(self) -> List[str]:
        """
        Check for orphaned tables (no foreign keys pointing to or from them).
        
        Returns:
            List[str]: List of orphaned table names
        """
        orphaned_tables = []
        
        # Build set of tables involved in foreign key relationships
        involved_tables = set()
        
        for table, fk_list in self.foreign_keys.items():
            involved_tables.add(table)
            for fk in fk_list:
                involved_tables.add(fk['table'])
        
        # Find tables not involved in any relationship
        for table in self.tables:
            if table not in involved_tables:
                orphaned_tables.append(table)
        
        return orphaned_tables
    
    def check_index_coverage(self) -> List[str]:
        """
        Check that foreign keys have appropriate indices.
        
        Returns:
            List[str]: List of missing indices
        """
        missing_indices = []
        
        for table, fk_list in self.foreign_keys.items():
            # Get indices for this table
            self.cursor.execute(f"PRAGMA index_list({table})")
            indices = self.cursor.fetchall()
            
            # Extract indexed columns for each index
            indexed_columns = {}
            for idx in indices:
                idx_name = idx[1]
                self.cursor.execute(f"PRAGMA index_info({idx_name})")
                cols = [col[2] for col in self.cursor.fetchall()]
                indexed_columns[idx_name] = cols
            
            # Check each foreign key has an index
            for fk in fk_list:
                fk_col = fk['from']
                has_index = False
                
                for cols in indexed_columns.values():
                    # Check if the foreign key column is the first column in any index
                    if cols and cols[0] == fk_col:
                        has_index = True
                        break
                
                if not has_index:
                    missing_indices.append(f"Missing index on {table}({fk_col}) for FK to {fk['table']}({fk['to']})")
        
        return missing_indices
    
    def check_table_schemas(self) -> List[str]:
        """
        Check for common schema issues in tables.
        
        Returns:
            List[str]: List of schema issues
        """
        schema_issues = []
        
        for table in self.tables:
            # Get table info
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = self.cursor.fetchall()
            
            # Check if primary key exists
            has_primary_key = any(col[5] > 0 for col in columns)
            if not has_primary_key:
                schema_issues.append(f"Table {table} has no PRIMARY KEY")
            
            # Check column naming convention
            for col in columns:
                col_name = col[1]
                
                # Check for uppercase in column names (should be snake_case)
                if any(c.isupper() for c in col_name):
                    schema_issues.append(f"Column {table}.{col_name} uses uppercase (should be snake_case)")
                
                # Check for proper ID naming
                if col_name.endswith('_id') and col[2] != 'INTEGER':
                    schema_issues.append(f"Column {table}.{col_name} is an ID but not INTEGER type")
        
        return schema_issues
    
    def validate(self) -> List[str]:
        """
        Run all validation checks.
        
        Returns:
            List[str]: List of all validation issues
        """
        if not self.connect():
            return self.issues
        
        try:
            # Get database structure
            self.get_tables()
            self.get_foreign_keys()
            
            # Run checks
            circular_refs = self.check_circular_references()
            if circular_refs:
                self.issues.extend([f"Circular reference: {ref}" for ref in circular_refs])
            
            orphaned_tables = self.check_orphaned_tables()
            if orphaned_tables:
                self.issues.extend([f"Orphaned table: {table}" for table in orphaned_tables])
            
            missing_indices = self.check_index_coverage()
            if missing_indices:
                self.issues.extend(missing_indices)
            
            schema_issues = self.check_table_schemas()
            if schema_issues:
                self.issues.extend(schema_issues)
            
            return self.issues
            
        except sqlite3.Error as e:
            self.issues.append(f"Validation error: {str(e)}")
            return self.issues
        finally:
            if self.connection:
                self.connection.close()
    
    def print_report(self) -> None:
        """Print the validation report."""
        issues = self.validate()
        
        if not issues:
            logger.info("✓ Database schema validation passed with no issues.")
            return
        
        logger.warning(f"⚠ Found {len(issues)} issues with the database schema:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"  {i}. {issue}")


def main():
    """Main entry point for the validator script."""
    if len(sys.argv) < 2:
        # Default database path
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prometheus.db')
    else:
        db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return 1
    
    validator = SchemaValidator(db_path)
    validator.print_report()
    
    return 0 if not validator.issues else 1


if __name__ == "__main__":
    sys.exit(main()) 