"""
Prometheus AI Prompt Generator - PromptUsage Analytics Model

This module defines the PromptUsage class, which represents individual usage logs
for prompts in the system. This analytics model helps track detailed information
about each prompt execution, including context, parameters, and results.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlQuery, QSqlError


class PromptUsage(QObject):
    """
    Analytics model for tracking individual prompt usage events.
    
    This class maintains detailed information about each time a prompt is used,
    including the context, parameters, results, and performance metrics.
    
    Signals:
        error_occurred: Emitted when an error occurs during database operations
    """
    
    # Signals
    error_occurred = Signal(str)
    
    def __init__(self, usage_id: Optional[int] = None):
        """
        Initialize a PromptUsage instance.
        
        Args:
            usage_id: Optional ID of an existing usage log to load
        """
        super().__init__()
        
        # Basic properties
        self._id: Optional[int] = None
        self._prompt_id: Optional[int] = None
        self._user_id: Optional[int] = None
        self._timestamp: Optional[datetime] = None
        self._success: bool = False
        self._tokens_used: int = 0
        self._cost: float = 0.0
        self._satisfaction: Optional[float] = None
        self._duration_ms: int = 0
        self._provider: str = ""
        self._model: str = ""
        self._context_length: int = 0
        self._response_length: int = 0
        self._parameters: Dict[str, Any] = {}
        self._error_message: str = ""
        self._tags: List[str] = []
        
        # If usage_id is provided, load the data
        if usage_id is not None:
            self.load(usage_id)
    
    @property
    def id(self) -> Optional[int]:
        """Get the ID of this usage log."""
        return self._id
    
    @property
    def prompt_id(self) -> Optional[int]:
        """Get the ID of the associated prompt."""
        return self._prompt_id
    
    @prompt_id.setter
    def prompt_id(self, value: int):
        """Set the ID of the associated prompt."""
        self._prompt_id = value
    
    @property
    def user_id(self) -> Optional[int]:
        """Get the ID of the user who used the prompt."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: int):
        """Set the ID of the user who used the prompt."""
        self._user_id = value
    
    @property
    def timestamp(self) -> Optional[datetime]:
        """Get the timestamp when the prompt was used."""
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, value: datetime):
        """Set the timestamp when the prompt was used."""
        self._timestamp = value
    
    @property
    def success(self) -> bool:
        """Get whether the prompt usage was successful."""
        return self._success
    
    @success.setter
    def success(self, value: bool):
        """Set whether the prompt usage was successful."""
        self._success = value
    
    @property
    def tokens_used(self) -> int:
        """Get the number of tokens used for this prompt execution."""
        return self._tokens_used
    
    @tokens_used.setter
    def tokens_used(self, value: int):
        """Set the number of tokens used for this prompt execution."""
        self._tokens_used = value
    
    @property
    def cost(self) -> float:
        """Get the cost of this prompt execution."""
        return self._cost
    
    @cost.setter
    def cost(self, value: float):
        """Set the cost of this prompt execution."""
        self._cost = value
    
    @property
    def satisfaction(self) -> Optional[float]:
        """Get the user satisfaction score (0-5 scale)."""
        return self._satisfaction
    
    @satisfaction.setter
    def satisfaction(self, value: Optional[float]):
        """Set the user satisfaction score (0-5 scale)."""
        self._satisfaction = value
    
    @property
    def duration_ms(self) -> int:
        """Get the duration of the prompt execution in milliseconds."""
        return self._duration_ms
    
    @duration_ms.setter
    def duration_ms(self, value: int):
        """Set the duration of the prompt execution in milliseconds."""
        self._duration_ms = value
    
    @property
    def provider(self) -> str:
        """Get the AI provider used for this prompt execution."""
        return self._provider
    
    @provider.setter
    def provider(self, value: str):
        """Set the AI provider used for this prompt execution."""
        self._provider = value
    
    @property
    def model(self) -> str:
        """Get the AI model used for this prompt execution."""
        return self._model
    
    @model.setter
    def model(self, value: str):
        """Set the AI model used for this prompt execution."""
        self._model = value
    
    @property
    def context_length(self) -> int:
        """Get the length of the context in tokens."""
        return self._context_length
    
    @context_length.setter
    def context_length(self, value: int):
        """Set the length of the context in tokens."""
        self._context_length = value
    
    @property
    def response_length(self) -> int:
        """Get the length of the response in tokens."""
        return self._response_length
    
    @response_length.setter
    def response_length(self, value: int):
        """Set the length of the response in tokens."""
        self._response_length = value
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the parameters used for this prompt execution."""
        return self._parameters
    
    @parameters.setter
    def parameters(self, value: Dict[str, Any]):
        """Set the parameters used for this prompt execution."""
        self._parameters = value
    
    @property
    def error_message(self) -> str:
        """Get the error message if the prompt execution failed."""
        return self._error_message
    
    @error_message.setter
    def error_message(self, value: str):
        """Set the error message if the prompt execution failed."""
        self._error_message = value
    
    @property
    def tags(self) -> List[str]:
        """Get the tags associated with this usage log."""
        return self._tags
    
    @tags.setter
    def tags(self, value: List[str]):
        """Set the tags associated with this usage log."""
        self._tags = value
    
    def load(self, usage_id: int) -> bool:
        """
        Load an existing usage log from the database.
        
        Args:
            usage_id: The ID of the usage log to load
            
        Returns:
            True if the usage log was loaded successfully, False otherwise
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT id, prompt_id, user_id, timestamp, success, tokens_used,
                   cost, satisfaction, duration_ms, provider, model,
                   context_length, response_length, parameters, error_message, tags
            FROM PromptUsageLogs
            WHERE id = ?
        """)
        query.addBindValue(usage_id)
        
        if not query.exec_():
            self.error_occurred.emit(f"Error loading prompt usage: {query.lastError().text()}")
            return False
        
        if query.next():
            self._id = query.value(0)
            self._prompt_id = query.value(1)
            self._user_id = query.value(2)
            
            # Parse timestamp
            timestamp_str = query.value(3)
            self._timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            
            self._success = bool(query.value(4))
            self._tokens_used = query.value(5)
            self._cost = query.value(6)
            self._satisfaction = query.value(7)
            self._duration_ms = query.value(8)
            self._provider = query.value(9)
            self._model = query.value(10)
            self._context_length = query.value(11)
            self._response_length = query.value(12)
            
            # Parse JSON parameters
            import json
            params_str = query.value(13)
            self._parameters = json.loads(params_str) if params_str else {}
            
            self._error_message = query.value(14)
            
            # Parse tags
            tags_str = query.value(15)
            self._tags = json.loads(tags_str) if tags_str else []
            
            return True
        else:
            self.error_occurred.emit(f"Usage log with ID {usage_id} not found")
            return False
    
    def save(self) -> bool:
        """
        Save the usage log to the database.
        
        This method will insert a new record if none exists for this usage,
        or update an existing record.
        
        Returns:
            True if the save operation was successful, False otherwise
        """
        if self._prompt_id is None:
            self.error_occurred.emit("Cannot save usage log: No prompt ID specified")
            return False
        
        # Set timestamp if not already set
        if self._timestamp is None:
            self._timestamp = datetime.now()
        
        # Convert parameters and tags to JSON
        import json
        params_json = json.dumps(self._parameters)
        tags_json = json.dumps(self._tags)
        
        query = QSqlQuery()
        
        if self._id is None:
            # This is a new record - insert it
            query.prepare("""
                INSERT INTO PromptUsageLogs (
                    prompt_id, user_id, timestamp, success, tokens_used,
                    cost, satisfaction, duration_ms, provider, model,
                    context_length, response_length, parameters, error_message, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
            
            query.addBindValue(self._prompt_id)
            query.addBindValue(self._user_id)
            query.addBindValue(self._timestamp.isoformat())
            query.addBindValue(1 if self._success else 0)
            query.addBindValue(self._tokens_used)
            query.addBindValue(self._cost)
            query.addBindValue(self._satisfaction)
            query.addBindValue(self._duration_ms)
            query.addBindValue(self._provider)
            query.addBindValue(self._model)
            query.addBindValue(self._context_length)
            query.addBindValue(self._response_length)
            query.addBindValue(params_json)
            query.addBindValue(self._error_message)
            query.addBindValue(tags_json)
            
            if not query.exec_():
                self.error_occurred.emit(f"Error creating prompt usage log: {query.lastError().text()}")
                return False
            
            # Get the new record ID
            self._id = query.lastInsertId()
        else:
            # Update existing record
            query.prepare("""
                UPDATE PromptUsageLogs
                SET prompt_id = ?, user_id = ?, timestamp = ?, success = ?,
                    tokens_used = ?, cost = ?, satisfaction = ?, duration_ms = ?,
                    provider = ?, model = ?, context_length = ?, response_length = ?,
                    parameters = ?, error_message = ?, tags = ?
                WHERE id = ?
            """)
            
            query.addBindValue(self._prompt_id)
            query.addBindValue(self._user_id)
            query.addBindValue(self._timestamp.isoformat())
            query.addBindValue(1 if self._success else 0)
            query.addBindValue(self._tokens_used)
            query.addBindValue(self._cost)
            query.addBindValue(self._satisfaction)
            query.addBindValue(self._duration_ms)
            query.addBindValue(self._provider)
            query.addBindValue(self._model)
            query.addBindValue(self._context_length)
            query.addBindValue(self._response_length)
            query.addBindValue(params_json)
            query.addBindValue(self._error_message)
            query.addBindValue(tags_json)
            query.addBindValue(self._id)
            
            if not query.exec_():
                self.error_occurred.emit(f"Error updating prompt usage log: {query.lastError().text()}")
                return False
        
        return True
    
    def delete(self) -> bool:
        """
        Delete this usage log from the database.
        
        Returns:
            True if the deletion was successful, False otherwise
        """
        if self._id is None:
            self.error_occurred.emit("Cannot delete usage log: No ID specified")
            return False
        
        query = QSqlQuery()
        query.prepare("DELETE FROM PromptUsageLogs WHERE id = ?")
        query.addBindValue(self._id)
        
        if not query.exec_():
            self.error_occurred.emit(f"Error deleting prompt usage log: {query.lastError().text()}")
            return False
        
        # Clear the ID to indicate the object is no longer in the database
        self._id = None
        return True
    
    @staticmethod
    def get_usage_logs_for_prompt(prompt_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get usage logs for a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt to get logs for
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of dictionaries with usage log data
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT id, timestamp, success, tokens_used, cost, satisfaction, duration_ms,
                   provider, model, context_length, response_length
            FROM PromptUsageLogs
            WHERE prompt_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """)
        
        query.addBindValue(prompt_id)
        query.addBindValue(limit)
        query.addBindValue(offset)
        
        if not query.exec_():
            return []
        
        result = []
        while query.next():
            # Parse timestamp
            timestamp_str = query.value(1)
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            
            result.append({
                'id': query.value(0),
                'timestamp': timestamp,
                'success': bool(query.value(2)),
                'tokens_used': query.value(3),
                'cost': query.value(4),
                'satisfaction': query.value(5),
                'duration_ms': query.value(6),
                'provider': query.value(7),
                'model': query.value(8),
                'context_length': query.value(9),
                'response_length': query.value(10)
            })
        
        return result
    
    @staticmethod
    def get_usage_logs_for_user(user_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get usage logs for a specific user.
        
        Args:
            user_id: The ID of the user to get logs for
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of dictionaries with usage log data
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT l.id, l.prompt_id, p.title, l.timestamp, l.success, 
                   l.tokens_used, l.cost, l.satisfaction, l.duration_ms,
                   l.provider, l.model
            FROM PromptUsageLogs l
            JOIN Prompts p ON l.prompt_id = p.id
            WHERE l.user_id = ?
            ORDER BY l.timestamp DESC
            LIMIT ? OFFSET ?
        """)
        
        query.addBindValue(user_id)
        query.addBindValue(limit)
        query.addBindValue(offset)
        
        if not query.exec_():
            return []
        
        result = []
        while query.next():
            # Parse timestamp
            timestamp_str = query.value(3)
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            
            result.append({
                'id': query.value(0),
                'prompt_id': query.value(1),
                'prompt_title': query.value(2),
                'timestamp': timestamp,
                'success': bool(query.value(4)),
                'tokens_used': query.value(5),
                'cost': query.value(6),
                'satisfaction': query.value(7),
                'duration_ms': query.value(8),
                'provider': query.value(9),
                'model': query.value(10)
            })
        
        return result
    
    @staticmethod
    def search_usage_logs(
        prompt_id: Optional[int] = None,
        user_id: Optional[int] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for usage logs based on various criteria.
        
        Args:
            prompt_id: Optional prompt ID to filter by
            user_id: Optional user ID to filter by
            provider: Optional provider to filter by
            model: Optional model to filter by
            success: Optional success status to filter by
            start_date: Optional start date to filter by
            end_date: Optional end date to filter by
            tags: Optional list of tags to filter by
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of dictionaries with usage log data
        """
        # Build the WHERE clause based on the provided filters
        where_clauses = []
        bindings = []
        
        if prompt_id is not None:
            where_clauses.append("l.prompt_id = ?")
            bindings.append(prompt_id)
        
        if user_id is not None:
            where_clauses.append("l.user_id = ?")
            bindings.append(user_id)
        
        if provider is not None:
            where_clauses.append("l.provider = ?")
            bindings.append(provider)
        
        if model is not None:
            where_clauses.append("l.model = ?")
            bindings.append(model)
        
        if success is not None:
            where_clauses.append("l.success = ?")
            bindings.append(1 if success else 0)
        
        if start_date is not None:
            where_clauses.append("l.timestamp >= ?")
            bindings.append(start_date.isoformat())
        
        if end_date is not None:
            where_clauses.append("l.timestamp <= ?")
            bindings.append(end_date.isoformat())
        
        if tags is not None and len(tags) > 0:
            # For each tag, check if it's in the JSON tags array
            tag_clauses = []
            for tag in tags:
                tag_clauses.append("l.tags LIKE ?")
                bindings.append(f"%{tag}%")
            
            where_clauses.append(f"({' OR '.join(tag_clauses)})")
        
        # Combine all WHERE clauses
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Build and execute the query
        query = QSqlQuery()
        query.prepare(f"""
            SELECT l.id, l.prompt_id, p.title, l.user_id, l.timestamp, l.success, 
                   l.tokens_used, l.cost, l.satisfaction, l.duration_ms,
                   l.provider, l.model, l.tags
            FROM PromptUsageLogs l
            JOIN Prompts p ON l.prompt_id = p.id
            WHERE {where_clause}
            ORDER BY l.timestamp DESC
            LIMIT ? OFFSET ?
        """)
        
        # Add all bindings
        for binding in bindings:
            query.addBindValue(binding)
        
        query.addBindValue(limit)
        query.addBindValue(offset)
        
        if not query.exec_():
            return []
        
        # Process results
        import json
        result = []
        while query.next():
            # Parse timestamp
            timestamp_str = query.value(4)
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            
            # Parse tags
            tags_str = query.value(12)
            tags = json.loads(tags_str) if tags_str else []
            
            result.append({
                'id': query.value(0),
                'prompt_id': query.value(1),
                'prompt_title': query.value(2),
                'user_id': query.value(3),
                'timestamp': timestamp,
                'success': bool(query.value(5)),
                'tokens_used': query.value(6),
                'cost': query.value(7),
                'satisfaction': query.value(8),
                'duration_ms': query.value(9),
                'provider': query.value(10),
                'model': query.value(11),
                'tags': tags
            })
        
        return result
    
    @staticmethod
    def get_usage_statistics(
        prompt_id: Optional[int] = None,
        user_id: Optional[int] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Union[int, float]]:
        """
        Get aggregated statistics for usage logs.
        
        Args:
            prompt_id: Optional prompt ID to filter by
            user_id: Optional user ID to filter by
            provider: Optional provider to filter by
            model: Optional model to filter by
            start_date: Optional start date to filter by
            end_date: Optional end date to filter by
            
        Returns:
            Dictionary with aggregated statistics
        """
        # Build the WHERE clause based on the provided filters
        where_clauses = []
        bindings = []
        
        if prompt_id is not None:
            where_clauses.append("prompt_id = ?")
            bindings.append(prompt_id)
        
        if user_id is not None:
            where_clauses.append("user_id = ?")
            bindings.append(user_id)
        
        if provider is not None:
            where_clauses.append("provider = ?")
            bindings.append(provider)
        
        if model is not None:
            where_clauses.append("model = ?")
            bindings.append(model)
        
        if start_date is not None:
            where_clauses.append("timestamp >= ?")
            bindings.append(start_date.isoformat())
        
        if end_date is not None:
            where_clauses.append("timestamp <= ?")
            bindings.append(end_date.isoformat())
        
        # Combine all WHERE clauses
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Build and execute the query
        query = QSqlQuery()
        query.prepare(f"""
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count,
                SUM(tokens_used) as total_tokens,
                SUM(cost) as total_cost,
                AVG(CASE WHEN satisfaction IS NOT NULL THEN satisfaction ELSE NULL END) as avg_satisfaction,
                AVG(duration_ms) as avg_duration,
                MIN(timestamp) as first_usage,
                MAX(timestamp) as last_usage
            FROM PromptUsageLogs
            WHERE {where_clause}
        """)
        
        # Add all bindings
        for binding in bindings:
            query.addBindValue(binding)
        
        if not query.exec_() or not query.next():
            return {
                'total_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'success_rate': 0.0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_tokens': 0.0,
                'avg_cost': 0.0,
                'avg_satisfaction': 0.0,
                'avg_duration_ms': 0,
                'first_usage': None,
                'last_usage': None
            }
        
        # Extract values
        total_count = query.value(0) or 0
        success_count = query.value(1) or 0
        failure_count = query.value(2) or 0
        total_tokens = query.value(3) or 0
        total_cost = query.value(4) or 0
        avg_satisfaction = query.value(5) or 0.0
        avg_duration = query.value(6) or 0
        
        # Parse timestamps
        first_usage_str = query.value(7)
        first_usage = datetime.fromisoformat(first_usage_str) if first_usage_str else None
        
        last_usage_str = query.value(8)
        last_usage = datetime.fromisoformat(last_usage_str) if last_usage_str else None
        
        # Calculate derived metrics
        success_rate = success_count / total_count if total_count > 0 else 0.0
        avg_tokens = total_tokens / total_count if total_count > 0 else 0.0
        avg_cost = total_cost / total_count if total_count > 0 else 0.0
        
        return {
            'total_count': total_count,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': success_rate,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'avg_tokens': avg_tokens,
            'avg_cost': avg_cost,
            'avg_satisfaction': avg_satisfaction,
            'avg_duration_ms': avg_duration,
            'first_usage': first_usage,
            'last_usage': last_usage
        } 