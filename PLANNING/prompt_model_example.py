"""
Prompt Model Example for SQLite Implementation

This file provides an example implementation of the Prompt model class
that would be used in the SQLite-based MVC architecture.
"""

import sqlite3
import datetime
from typing import List, Dict, Optional, Any, Tuple


class Prompt:
    """Model class representing a prompt in the database."""
    
    def __init__(self, 
                 prompt_id: Optional[int] = None,
                 prompt_type: str = "",
                 title: str = "",
                 template: str = "",
                 description: str = "",
                 author: str = "",
                 version: str = "1.0", 
                 created_date: str = "",
                 updated_date: str = "",
                 category_id: Optional[int] = None):
        """Initialize a Prompt object.
        
        Args:
            prompt_id: Database ID (None for new prompts)
            prompt_type: Unique identifier for the prompt (e.g., "api")
            title: Display name for the prompt
            template: The prompt template text
            description: Description of the prompt's purpose
            author: Creator of the prompt
            version: Version string
            created_date: ISO format date string
            updated_date: ISO format date string
            category_id: ID of the category this prompt belongs to
        """
        self.id = prompt_id
        self.type = prompt_type
        self.title = title
        self.template = template
        self.description = description
        self.author = author
        self.version = version
        
        # Set default dates if not provided
        if not created_date:
            self.created_date = datetime.datetime.now().isoformat()
        else:
            self.created_date = created_date
            
        if not updated_date:
            self.updated_date = self.created_date
        else:
            self.updated_date = updated_date
            
        self.category_id = category_id
        self._tags = []  # Will be populated from DB when needed
        
    @property
    def tags(self) -> List[str]:
        """Get tags associated with this prompt."""
        return self._tags
        
    def set_tags(self, tags: List[str]) -> None:
        """Set tags for this prompt."""
        self._tags = tags
        
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the prompt data.
        
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - List of validation error messages
        """
        errors = []
        
        if not self.type:
            errors.append("Prompt type is required")
        
        if not self.title:
            errors.append("Title is required")
            
        if not self.template:
            errors.append("Template is required")
            
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert prompt to dictionary representation.
        
        Returns:
            Dictionary containing prompt data
        """
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "template": self.template,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "category_id": self.category_id,
            "tags": self._tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prompt':
        """Create a Prompt object from a dictionary.
        
        Args:
            data: Dictionary containing prompt data
            
        Returns:
            Prompt object
        """
        prompt = cls(
            prompt_id=data.get("id"),
            prompt_type=data.get("type", ""),
            title=data.get("title", ""),
            template=data.get("template", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0"),
            created_date=data.get("created_date", ""),
            updated_date=data.get("updated_date", ""),
            category_id=data.get("category_id")
        )
        
        if "tags" in data:
            prompt.set_tags(data["tags"])
            
        return prompt


class PromptRepository:
    """Repository class for prompt data access."""
    
    def __init__(self, db_path: str):
        """Initialize repository with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable row factory for dict-like access
        return conn
        
    def get_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """Get a prompt by ID.
        
        Args:
            prompt_id: The database ID of the prompt
            
        Returns:
            Prompt object or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get prompt data
            cursor.execute("""
                SELECT * FROM Prompts 
                WHERE id = ?
            """, (prompt_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            # Convert row to dict
            prompt_data = dict(row)
            
            # Get tags
            cursor.execute("""
                SELECT t.name 
                FROM Tags t
                JOIN PromptTagAssociation pta ON t.id = pta.tag_id
                WHERE pta.prompt_id = ?
            """, (prompt_id,))
            
            tags = [row['name'] for row in cursor.fetchall()]
            prompt_data['tags'] = tags
            
            return Prompt.from_dict(prompt_data)
            
        finally:
            conn.close()
            
    def get_by_type(self, prompt_type: str) -> Optional[Prompt]:
        """Get a prompt by its type.
        
        Args:
            prompt_type: The unique type identifier of the prompt
            
        Returns:
            Prompt object or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get prompt data
            cursor.execute("""
                SELECT * FROM Prompts 
                WHERE type = ?
            """, (prompt_type,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            prompt_data = dict(row)
            prompt_id = prompt_data['id']
            
            # Get tags
            cursor.execute("""
                SELECT t.name 
                FROM Tags t
                JOIN PromptTagAssociation pta ON t.id = pta.tag_id
                WHERE pta.prompt_id = ?
            """, (prompt_id,))
            
            tags = [row['name'] for row in cursor.fetchall()]
            prompt_data['tags'] = tags
            
            return Prompt.from_dict(prompt_data)
            
        finally:
            conn.close()
    
    def get_all(self) -> List[Prompt]:
        """Get all prompts from the database.
        
        Returns:
            List of Prompt objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get all prompts
            cursor.execute("SELECT * FROM Prompts")
            prompts = []
            
            for row in cursor.fetchall():
                prompt_data = dict(row)
                prompt_id = prompt_data['id']
                
                # Get tags for this prompt
                cursor.execute("""
                    SELECT t.name 
                    FROM Tags t
                    JOIN PromptTagAssociation pta ON t.id = pta.tag_id
                    WHERE pta.prompt_id = ?
                """, (prompt_id,))
                
                tags = [row['name'] for row in cursor.fetchall()]
                prompt_data['tags'] = tags
                
                prompts.append(Prompt.from_dict(prompt_data))
                
            return prompts
            
        finally:
            conn.close()
    
    def save(self, prompt: Prompt) -> Prompt:
        """Save a prompt to the database.
        
        Args:
            prompt: The Prompt object to save
            
        Returns:
            Updated Prompt object with ID
        """
        # Validate prompt data
        valid, errors = prompt.validate()
        if not valid:
            raise ValueError(f"Invalid prompt data: {', '.join(errors)}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Update timestamp
            prompt.updated_date = datetime.datetime.now().isoformat()
            
            if prompt.id is None:
                # Insert new prompt
                cursor.execute("""
                    INSERT INTO Prompts 
                    (type, title, template, description, author, version, 
                     created_date, updated_date, category_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prompt.type, prompt.title, prompt.template, 
                    prompt.description, prompt.author, prompt.version,
                    prompt.created_date, prompt.updated_date, prompt.category_id
                ))
                
                prompt.id = cursor.lastrowid
            else:
                # Update existing prompt
                cursor.execute("""
                    UPDATE Prompts SET
                    type = ?, title = ?, template = ?, description = ?,
                    author = ?, version = ?, updated_date = ?, category_id = ?
                    WHERE id = ?
                """, (
                    prompt.type, prompt.title, prompt.template,
                    prompt.description, prompt.author, prompt.version,
                    prompt.updated_date, prompt.category_id, prompt.id
                ))
            
            # Handle tags (delete existing associations and add new ones)
            if prompt.id is not None:
                # Delete existing tag associations
                cursor.execute("""
                    DELETE FROM PromptTagAssociation
                    WHERE prompt_id = ?
                """, (prompt.id,))
                
                # Add new tag associations
                for tag_name in prompt.tags:
                    # Get or create tag
                    cursor.execute("""
                        SELECT id FROM Tags
                        WHERE name = ?
                    """, (tag_name,))
                    
                    row = cursor.fetchone()
                    if row:
                        tag_id = row['id']
                    else:
                        # Create new tag
                        cursor.execute("""
                            INSERT INTO Tags (name)
                            VALUES (?)
                        """, (tag_name,))
                        tag_id = cursor.lastrowid
                    
                    # Create association
                    cursor.execute("""
                        INSERT INTO PromptTagAssociation
                        (prompt_id, tag_id)
                        VALUES (?, ?)
                    """, (prompt.id, tag_id))
            
            conn.commit()
            return prompt
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete(self, prompt_id: int) -> bool:
        """Delete a prompt from the database.
        
        Args:
            prompt_id: ID of the prompt to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if prompt exists
            cursor.execute("SELECT id FROM Prompts WHERE id = ?", (prompt_id,))
            if not cursor.fetchone():
                return False
                
            # Delete the prompt (tag associations will be deleted by cascade)
            cursor.execute("DELETE FROM Prompts WHERE id = ?", (prompt_id,))
            conn.commit()
            
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


# Example usage
if __name__ == "__main__":
    # This would be part of your application initialization
    repo = PromptRepository("prompts.db")
    
    # Create a new prompt
    api_prompt = Prompt(
        prompt_type="api",
        title="API Design Prompt",
        template="Design a RESTful API for {service_description}...",
        description="A technical prompt for designing APIs",
        author="Prometheus Team"
    )
    api_prompt.set_tags(["api", "design", "backend"])
    
    # Save to database
    api_prompt = repo.save(api_prompt)
    print(f"Saved prompt with ID: {api_prompt.id}")
    
    # Retrieve and modify
    retrieved_prompt = repo.get_by_type("api")
    if retrieved_prompt:
        retrieved_prompt.description += " (Updated)"
        repo.save(retrieved_prompt)
        print(f"Updated prompt: {retrieved_prompt.title}")
    
    # List all prompts
    all_prompts = repo.get_all()
    print(f"Total prompts: {len(all_prompts)}")
    for p in all_prompts:
        print(f"- {p.title} ({p.type}): {', '.join(p.tags)}") 