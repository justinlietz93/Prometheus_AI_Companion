"""
Prometheus AI Prompt Generator - PromptScore Analytics Model

This module defines the PromptScore class, which represents performance and usage
metrics for prompts in the system. This analytics model helps track various 
metrics like usage count, success rate, and user satisfaction scores.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlQuery, QSqlError


class PromptScore(QObject):
    """
    Analytics model for tracking prompt performance metrics.
    
    This class maintains and calculates various metrics related to a prompt's 
    performance and usage patterns, such as usage count, success rate, average 
    tokens used, and user satisfaction scores.
    
    Signals:
        score_updated: Emitted when any score metrics are updated
        error_occurred: Emitted when an error occurs during database operations
    """
    
    # Signals
    score_updated = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, prompt_id: Optional[int] = None):
        """
        Initialize a PromptScore instance.
        
        Args:
            prompt_id: Optional ID of the prompt to load metrics for
        """
        super().__init__()
        
        # Basic properties
        self._id: Optional[int] = None
        self._prompt_id: Optional[int] = None
        self._usage_count: int = 0
        self._success_count: int = 0
        self._failure_count: int = 0
        self._total_tokens: int = 0
        self._total_cost: float = 0.0
        self._avg_satisfaction: float = 0.0
        self._last_used: Optional[datetime] = None
        self._created_at: Optional[datetime] = None
        self._updated_at: Optional[datetime] = None
        
        # Calculated metrics
        self._success_rate: float = 0.0
        self._avg_tokens: float = 0.0
        self._avg_cost: float = 0.0
        
        # If prompt_id is provided, load the data
        if prompt_id is not None:
            self.load(prompt_id)
    
    @property
    def id(self) -> Optional[int]:
        """Get the ID of this score record."""
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
    def usage_count(self) -> int:
        """Get the total number of times the prompt has been used."""
        return self._usage_count
    
    @property
    def success_rate(self) -> float:
        """Get the calculated success rate (ratio of successes to total usage)."""
        return self._success_rate
    
    @property
    def avg_tokens(self) -> float:
        """Get the average number of tokens used per prompt execution."""
        return self._avg_tokens
    
    @property
    def avg_cost(self) -> float:
        """Get the average cost per prompt execution."""
        return self._avg_cost
    
    @property
    def avg_satisfaction(self) -> float:
        """Get the average user satisfaction score (0-5 scale)."""
        return self._avg_satisfaction
    
    @property
    def last_used(self) -> Optional[datetime]:
        """Get the date/time when the prompt was last used."""
        return self._last_used
    
    @property
    def created_at(self) -> Optional[datetime]:
        """Get the creation date of this score record."""
        return self._created_at
    
    @property
    def updated_at(self) -> Optional[datetime]:
        """Get the last update date of this score record."""
        return self._updated_at
    
    def load(self, prompt_id: int) -> bool:
        """
        Load the score metrics for a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt to load metrics for
            
        Returns:
            True if the score was loaded successfully, False otherwise
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT id, prompt_id, usage_count, success_count, failure_count,
                   total_tokens, total_cost, avg_satisfaction, last_used,
                   created_at, updated_at
            FROM PromptScores
            WHERE prompt_id = ?
        """)
        query.addBindValue(prompt_id)
        
        if not query.exec_():
            self.error_occurred.emit(f"Error loading prompt score: {query.lastError().text()}")
            return False
        
        if query.next():
            self._id = query.value(0)
            self._prompt_id = query.value(1)
            self._usage_count = query.value(2)
            self._success_count = query.value(3)
            self._failure_count = query.value(4)
            self._total_tokens = query.value(5)
            self._total_cost = query.value(6)
            self._avg_satisfaction = query.value(7)
            
            # Parse datetime strings
            last_used_str = query.value(8)
            self._last_used = datetime.fromisoformat(last_used_str) if last_used_str else None
            
            created_at_str = query.value(9)
            self._created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
            
            updated_at_str = query.value(10)
            self._updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else None
            
            # Calculate derived metrics
            self._calculate_metrics()
            return True
        else:
            # No existing record found, but this isn't an error - it's a new prompt
            self._prompt_id = prompt_id
            return False
    
    def save(self) -> bool:
        """
        Save the current score metrics to the database.
        
        This method will insert a new record if none exists for this prompt,
        or update an existing record.
        
        Returns:
            True if the save operation was successful, False otherwise
        """
        if self._prompt_id is None:
            self.error_occurred.emit("Cannot save score: No prompt ID specified")
            return False
        
        # Update the updated_at timestamp
        self._updated_at = datetime.now()
        
        query = QSqlQuery()
        
        if self._id is None:
            # This is a new record - insert it
            self._created_at = datetime.now()
            
            query.prepare("""
                INSERT INTO PromptScores (
                    prompt_id, usage_count, success_count, failure_count, 
                    total_tokens, total_cost, avg_satisfaction, last_used,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
            
            query.addBindValue(self._prompt_id)
            query.addBindValue(self._usage_count)
            query.addBindValue(self._success_count)
            query.addBindValue(self._failure_count)
            query.addBindValue(self._total_tokens)
            query.addBindValue(self._total_cost)
            query.addBindValue(self._avg_satisfaction)
            query.addBindValue(self._last_used.isoformat() if self._last_used else None)
            query.addBindValue(self._created_at.isoformat())
            query.addBindValue(self._updated_at.isoformat())
            
            if not query.exec_():
                self.error_occurred.emit(f"Error creating prompt score: {query.lastError().text()}")
                return False
            
            # Get the new record ID
            self._id = query.lastInsertId()
        else:
            # Update existing record
            query.prepare("""
                UPDATE PromptScores
                SET usage_count = ?, success_count = ?, failure_count = ?,
                    total_tokens = ?, total_cost = ?, avg_satisfaction = ?,
                    last_used = ?, updated_at = ?
                WHERE id = ?
            """)
            
            query.addBindValue(self._usage_count)
            query.addBindValue(self._success_count)
            query.addBindValue(self._failure_count)
            query.addBindValue(self._total_tokens)
            query.addBindValue(self._total_cost)
            query.addBindValue(self._avg_satisfaction)
            query.addBindValue(self._last_used.isoformat() if self._last_used else None)
            query.addBindValue(self._updated_at.isoformat())
            query.addBindValue(self._id)
            
            if not query.exec_():
                self.error_occurred.emit(f"Error updating prompt score: {query.lastError().text()}")
                return False
        
        return True
    
    def record_usage(self, success: bool, tokens_used: int = 0,
                     cost: float = 0.0, satisfaction: Optional[float] = None) -> bool:
        """
        Record a new usage of the prompt.
        
        Args:
            success: Whether the prompt usage was successful
            tokens_used: Number of tokens consumed by this usage
            cost: Cost of this prompt usage
            satisfaction: User satisfaction score (0-5)
            
        Returns:
            True if the usage was recorded successfully, False otherwise
        """
        # Update usage statistics
        self._usage_count += 1
        if success:
            self._success_count += 1
        else:
            self._failure_count += 1
        
        self._total_tokens += tokens_used
        self._total_cost += cost
        
        # Update satisfaction score if provided
        if satisfaction is not None:
            # Calculate new average satisfaction
            if self._avg_satisfaction == 0:
                self._avg_satisfaction = satisfaction
            else:
                # Weighted average (more weight to existing average)
                self._avg_satisfaction = (
                    (self._avg_satisfaction * (self._usage_count - 1) + satisfaction) / 
                    self._usage_count
                )
        
        # Update last used timestamp
        self._last_used = datetime.now()
        
        # Recalculate derived metrics
        self._calculate_metrics()
        
        # Save changes to database
        result = self.save()
        
        if result:
            self.score_updated.emit()
        
        return result
    
    def get_monthly_usage(self, year: int, month: int) -> int:
        """
        Get the usage count for a specific month.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            The number of times the prompt was used in the specified month
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT COUNT(*)
            FROM PromptUsageLogs
            WHERE prompt_id = ? AND 
                  strftime('%Y', timestamp) = ? AND 
                  strftime('%m', timestamp) = ?
        """)
        
        query.addBindValue(self._prompt_id)
        query.addBindValue(str(year))
        query.addBindValue(str(month).zfill(2))  # Ensure 2-digit month
        
        if not query.exec_() or not query.next():
            self.error_occurred.emit(f"Error retrieving monthly usage: {query.lastError().text()}")
            return 0
        
        return query.value(0)
    
    def get_usage_trend(self, days: int = 30) -> List[Tuple[str, int]]:
        """
        Get usage trend data for the last N days.
        
        Args:
            days: Number of days to include in the trend data
            
        Returns:
            List of (date, count) tuples
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT date(timestamp) as day, COUNT(*) as count
            FROM PromptUsageLogs
            WHERE prompt_id = ? AND 
                  timestamp >= date('now', ?)
            GROUP BY day
            ORDER BY day
        """)
        
        query.addBindValue(self._prompt_id)
        query.addBindValue(f"-{days} days")
        
        if not query.exec_():
            self.error_occurred.emit(f"Error retrieving usage trend: {query.lastError().text()}")
            return []
        
        trend_data = []
        while query.next():
            day = query.value(0)
            count = query.value(1)
            trend_data.append((day, count))
        
        return trend_data
    
    def get_success_trend(self, days: int = 30) -> List[Tuple[str, float]]:
        """
        Get success rate trend data for the last N days.
        
        Args:
            days: Number of days to include in the trend data
            
        Returns:
            List of (date, success_rate) tuples
        """
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                date(timestamp) as day, 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                COUNT(*) as total
            FROM PromptUsageLogs
            WHERE prompt_id = ? AND 
                  timestamp >= date('now', ?)
            GROUP BY day
            ORDER BY day
        """)
        
        query.addBindValue(self._prompt_id)
        query.addBindValue(f"-{days} days")
        
        if not query.exec_():
            self.error_occurred.emit(f"Error retrieving success trend: {query.lastError().text()}")
            return []
        
        trend_data = []
        while query.next():
            day = query.value(0)
            successes = query.value(1)
            total = query.value(2)
            success_rate = successes / total if total > 0 else 0
            trend_data.append((day, success_rate))
        
        return trend_data
    
    def get_comparative_rank(self) -> Dict[str, Union[int, float]]:
        """
        Get ranking information for this prompt compared to others.
        
        Returns:
            Dictionary with rank information
        """
        results = {
            'usage_rank': 0,
            'success_rank': 0,
            'satisfaction_rank': 0,
            'percentile': 0.0
        }
        
        # Get total number of prompts with scores
        count_query = QSqlQuery()
        count_query.exec_("SELECT COUNT(*) FROM PromptScores")
        if not count_query.next():
            return results
        
        total_prompts = count_query.value(0)
        if total_prompts == 0:
            return results
        
        # Get usage rank
        usage_query = QSqlQuery()
        usage_query.prepare("""
            SELECT COUNT(*) 
            FROM PromptScores 
            WHERE usage_count > (SELECT usage_count FROM PromptScores WHERE prompt_id = ?)
        """)
        usage_query.addBindValue(self._prompt_id)
        
        if usage_query.exec_() and usage_query.next():
            results['usage_rank'] = usage_query.value(0) + 1  # +1 because ranks start at 1
        
        # Get success rate rank
        success_query = QSqlQuery()
        success_query.prepare("""
            SELECT COUNT(*) 
            FROM PromptScores 
            WHERE (success_count * 1.0 / CASE WHEN usage_count = 0 THEN 1 ELSE usage_count END) > 
                  (SELECT (success_count * 1.0 / CASE WHEN usage_count = 0 THEN 1 ELSE usage_count END) 
                   FROM PromptScores WHERE prompt_id = ?)
            AND usage_count > 5  -- Minimum threshold to avoid rankings with insufficient data
        """)
        success_query.addBindValue(self._prompt_id)
        
        if success_query.exec_() and success_query.next():
            results['success_rank'] = success_query.value(0) + 1
        
        # Get satisfaction rank
        sat_query = QSqlQuery()
        sat_query.prepare("""
            SELECT COUNT(*) 
            FROM PromptScores 
            WHERE avg_satisfaction > (SELECT avg_satisfaction FROM PromptScores WHERE prompt_id = ?)
            AND usage_count > 5  -- Minimum threshold
        """)
        sat_query.addBindValue(self._prompt_id)
        
        if sat_query.exec_() and sat_query.next():
            results['satisfaction_rank'] = sat_query.value(0) + 1
        
        # Calculate percentile based on usage
        percentile = (total_prompts - results['usage_rank'] + 1) / total_prompts * 100
        results['percentile'] = round(percentile, 1)
        
        return results
    
    def _calculate_metrics(self):
        """Calculate derived metrics from raw data."""
        # Calculate success rate
        if self._usage_count > 0:
            self._success_rate = self._success_count / self._usage_count
        else:
            self._success_rate = 0.0
        
        # Calculate average tokens
        if self._usage_count > 0:
            self._avg_tokens = self._total_tokens / self._usage_count
        else:
            self._avg_tokens = 0.0
        
        # Calculate average cost
        if self._usage_count > 0:
            self._avg_cost = self._total_cost / self._usage_count
        else:
            self._avg_cost = 0.0
    
    @staticmethod
    def get_top_prompts(limit: int = 10, metric: str = "usage") -> List[Dict[str, Union[int, float, str]]]:
        """
        Get the top performing prompts based on a specific metric.
        
        Args:
            limit: Maximum number of prompts to return
            metric: Which metric to rank by (usage, success, satisfaction)
            
        Returns:
            List of dictionaries with prompt data
        """
        order_clause = {
            "usage": "ps.usage_count DESC",
            "success": "(ps.success_count * 1.0 / CASE WHEN ps.usage_count = 0 THEN 1 ELSE ps.usage_count END) DESC",
            "satisfaction": "ps.avg_satisfaction DESC",
            "cost_efficiency": "(ps.success_count * 1.0 / CASE WHEN ps.total_cost = 0 THEN 1 ELSE ps.total_cost END) DESC"
        }.get(metric, "ps.usage_count DESC")
        
        query = QSqlQuery()
        query.prepare(f"""
            SELECT 
                p.id as prompt_id, 
                p.title, 
                ps.usage_count,
                (ps.success_count * 1.0 / CASE WHEN ps.usage_count = 0 THEN 1 ELSE ps.usage_count END) as success_rate,
                ps.avg_satisfaction
            FROM 
                Prompts p
                JOIN PromptScores ps ON p.id = ps.prompt_id
            WHERE 
                ps.usage_count > 5  -- Minimum threshold to avoid rankings with insufficient data
            ORDER BY 
                {order_clause}
            LIMIT ?
        """)
        
        query.addBindValue(limit)
        
        if not query.exec_():
            return []
        
        result = []
        while query.next():
            result.append({
                'prompt_id': query.value(0),
                'title': query.value(1),
                'usage_count': query.value(2),
                'success_rate': query.value(3),
                'avg_satisfaction': query.value(4)
            })
        
        return result 