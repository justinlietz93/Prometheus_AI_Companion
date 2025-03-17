"""
Prompt Repository for Prometheus AI Prompt Generator.

This module contains the repository classes that handle data access for prompts.
"""

def import_prompt_from_file(self, file_path):
    """
    Import a prompt from a JSON file to the database.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        int: ID of the imported prompt, or None if import failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)
        
        # Start a transaction
        self._db.transaction()
        
        # Determine prompt type from file name if not in data
        if "name" not in prompt_data:
            filename = os.path.basename(file_path)
            prompt_type = os.path.splitext(filename)[0]
            prompt_data["name"] = prompt_type
            
        prompt_type = prompt_data["name"]
        prompt_id = None
        
        # Check if this is a template-based or urgency-based prompt
        if "template" in prompt_data:
            # This is a template-based prompt
            template = prompt_data["template"]
            title = prompt_data.get("title", prompt_type.title() + " Prompt")
            description = prompt_data.get("description", "")
            
            # Create the prompt record
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO Prompts (
                    type, title, template, description, author, version, 
                    created_date, updated_date, uses_urgency_levels
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """)
            
            query.addBindValue(prompt_type)
            query.addBindValue(title)
            query.addBindValue(template)
            query.addBindValue(description)
            query.addBindValue(prompt_data.get("metadata", {}).get("author", "Prometheus AI"))
            query.addBindValue(prompt_data.get("metadata", {}).get("version", "1.0.0"))
            query.addBindValue(prompt_data.get("metadata", {}).get("created", datetime.now().isoformat()))
            query.addBindValue(prompt_data.get("metadata", {}).get("updated", datetime.now().isoformat()))
            
            if not query.exec():
                raise Exception(f"Failed to import prompt: {query.lastError().text()}")
                
            prompt_id = query.lastInsertId()
            
        elif "prompts" in prompt_data:
            # This is an urgency-based prompt with levels 1-10
            title = prompt_data.get("title", prompt_type.title() + " Prompt")
            description = prompt_data.get("description", "")
            
            # Create the base prompt record
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO Prompts (
                    type, title, template, description, author, version, 
                    created_date, updated_date, uses_urgency_levels
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """)
            
            # For urgency-based prompts, we use the highest urgency level as the template
            # but mark it as using urgency levels
            highest_level = "10"
            template = ""
            
            if highest_level in prompt_data["prompts"]:
                template = prompt_data["prompts"][highest_level]
            else:
                # Find the highest available level
                available_levels = list(prompt_data["prompts"].keys())
                if available_levels:
                    level = max(available_levels, key=lambda x: int(x) if x.isdigit() else 0)
                    template = prompt_data["prompts"][level]
            
            query.addBindValue(prompt_type)
            query.addBindValue(title)
            query.addBindValue(template)  # Store highest level as default template
            query.addBindValue(description)
            query.addBindValue(prompt_data.get("metadata", {}).get("author", "Prometheus AI"))
            query.addBindValue(prompt_data.get("metadata", {}).get("version", "1.0.0"))
            query.addBindValue(prompt_data.get("metadata", {}).get("created", datetime.now().isoformat()))
            query.addBindValue(prompt_data.get("metadata", {}).get("updated", datetime.now().isoformat()))
            
            if not query.exec():
                raise Exception(f"Failed to import prompt: {query.lastError().text()}")
                
            prompt_id = query.lastInsertId()
            
            # Now add all the urgency levels
            for level, content in prompt_data["prompts"].items():
                # Validate level is numeric
                try:
                    level_int = int(level)
                    if level_int < 1 or level_int > 10:
                        continue  # Skip invalid levels
                except ValueError:
                    continue  # Skip non-numeric levels
                
                level_query = QSqlQuery()
                level_query.prepare("""
                    INSERT INTO PromptUrgencyLevels (
                        prompt_id, urgency_level, content
                    ) VALUES (?, ?, ?)
                """)
                
                level_query.addBindValue(prompt_id)
                level_query.addBindValue(level_int)
                level_query.addBindValue(content)
                
                if not level_query.exec():
                    raise Exception(f"Failed to import urgency level {level}: {level_query.lastError().text()}")
        
        # Import tags if present
        if "metadata" in prompt_data and "tags" in prompt_data["metadata"]:
            for tag_name in prompt_data["metadata"]["tags"]:
                # First ensure the tag exists
                tag_id = self._get_or_create_tag(tag_name)
                
                # Then associate it with the prompt
                if tag_id:
                    assoc_query = QSqlQuery()
                    assoc_query.prepare("""
                        INSERT INTO PromptTagAssociation (prompt_id, tag_id)
                        VALUES (?, ?)
                    """)
                    assoc_query.addBindValue(prompt_id)
                    assoc_query.addBindValue(tag_id)
                    
                    if not assoc_query.exec():
                        logger.warning(f"Failed to associate tag {tag_name}: {assoc_query.lastError().text()}")
        
        # Commit the transaction
        self._db.commit()
        return prompt_id
        
    except Exception as e:
        self._db.rollback()
        logger.error(f"Error importing prompt from file: {str(e)}")
        return None

def _get_or_create_tag(self, tag_name):
    """
    Get tag ID by name or create if it doesn't exist.
    
    Args:
        tag_name (str): Name of the tag
        
    Returns:
        int: Tag ID or None if failed
    """
    query = QSqlQuery()
    query.prepare("SELECT id FROM Tags WHERE name = ?")
    query.addBindValue(tag_name)
    
    if query.exec() and query.next():
        return query.value(0)
    
    # Tag doesn't exist, create it
    insert_query = QSqlQuery()
    insert_query.prepare("INSERT INTO Tags (name) VALUES (?)")
    insert_query.addBindValue(tag_name)
    
    if insert_query.exec():
        return insert_query.lastInsertId()
    
    logger.error(f"Failed to create tag {tag_name}: {insert_query.lastError().text()}")
    return None

def get_prompt_with_urgency_level(self, prompt_id, urgency_level=10):
    """
    Get a prompt with a specific urgency level.
    
    Args:
        prompt_id (int): ID of the prompt
        urgency_level (int): Urgency level (1-10), defaults to 10
        
    Returns:
        dict: Prompt data with content at requested urgency level
    """
    # First get the prompt
    prompt = self.get_by_id(prompt_id)
    if not prompt:
        return None
        
    # If this prompt doesn't use urgency levels, just return it
    if not prompt.get("uses_urgency_levels"):
        return prompt
        
    # Get the requested urgency level content
    query = QSqlQuery()
    query.prepare("""
        SELECT content FROM PromptUrgencyLevels
        WHERE prompt_id = ? AND urgency_level = ?
    """)
    query.addBindValue(prompt_id)
    query.addBindValue(urgency_level)
    
    if query.exec() and query.next():
        # Replace the template with the urgency level content
        prompt["template"] = query.value(0)
        return prompt
    
    # If exact urgency level not found, get the closest available level
    # Prefer higher urgency if exact match not found
    query = QSqlQuery()
    query.prepare("""
        SELECT urgency_level, content FROM PromptUrgencyLevels
        WHERE prompt_id = ?
        ORDER BY ABS(urgency_level - ?), urgency_level DESC
        LIMIT 1
    """)
    query.addBindValue(prompt_id)
    query.addBindValue(urgency_level)
    
    if query.exec() and query.next():
        # Replace the template with the closest urgency level content
        prompt["template"] = query.value(1)
        return prompt
    
    # If no urgency levels found, return the prompt as is
    return prompt 