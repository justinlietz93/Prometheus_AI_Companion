"""
Prometheus AI Prompt Generator - Benchmark Entity

This module defines the Benchmark class, which represents a benchmark configuration
for testing and comparing language models.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import json

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlQuery, QSqlError


class Benchmark(QObject):
    """
    Benchmark entity for configuring and running language model tests.
    
    This class represents a benchmark configuration that can be used to test
    and compare multiple language models using a specific prompt and metrics.
    
    Signals:
        changed: Emitted when any property of the benchmark changes
        error: Emitted when an error occurs during benchmark operations
        saved: Emitted when the benchmark is successfully saved
    """
    
    # Define signals
    changed = Signal()
    error = Signal(str)
    saved = Signal()
    
    # Available metrics for benchmarking
    AVAILABLE_METRICS = [
        "accuracy", "coherence", "speed", "relevance", 
        "factuality", "creativity", "safety", "brevity"
    ]
    
    def __init__(self, benchmark_id: Optional[int] = None):
        """
        Initialize a Benchmark instance.
        
        Args:
            benchmark_id: Optional ID of an existing benchmark to load from the database
        """
        super().__init__()
        
        # Initialize properties
        self._id: Optional[int] = None
        self._name: str = ""
        self._description: str = ""
        self._prompt_text: str = ""
        self._created_date: datetime = datetime.now()
        self._user_id: str = ""
        self._metrics: Dict[str, bool] = {metric: False for metric in self.AVAILABLE_METRICS}
        
        # Load the benchmark if an ID is provided
        if benchmark_id is not None:
            self.load(benchmark_id)
    
    @property
    def id(self) -> Optional[int]:
        """Get the benchmark ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get the benchmark name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the benchmark name."""
        if not value:
            self.error.emit("Benchmark name cannot be empty")
            return
        
        self._name = value
        self.changed.emit()
    
    @property
    def description(self) -> str:
        """Get the benchmark description."""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """Set the benchmark description."""
        self._description = value
        self.changed.emit()
    
    @property
    def prompt_text(self) -> str:
        """Get the benchmark prompt text."""
        return self._prompt_text
    
    @prompt_text.setter
    def prompt_text(self, value: str):
        """Set the benchmark prompt text."""
        if not value:
            self.error.emit("Benchmark prompt text cannot be empty")
            return
        
        self._prompt_text = value
        self.changed.emit()
    
    @property
    def created_date(self) -> datetime:
        """Get the benchmark creation date."""
        return self._created_date
    
    @property
    def user_id(self) -> str:
        """Get the user ID that created the benchmark."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: str):
        """Set the user ID that created the benchmark."""
        self._user_id = value
        self.changed.emit()
    
    @property
    def metrics(self) -> Dict[str, bool]:
        """Get the metrics configuration."""
        return self._metrics.copy()
    
    def set_metric(self, metric_name: str, enabled: bool):
        """
        Enable or disable a specific metric.
        
        Args:
            metric_name: Name of the metric
            enabled: Whether the metric should be enabled
        """
        if metric_name in self.AVAILABLE_METRICS:
            self._metrics[metric_name] = enabled
            self.changed.emit()
        else:
            self.error.emit(f"Unknown metric: {metric_name}")
    
    def set_metrics(self, metrics: Union[Dict[str, bool], List[str]]):
        """
        Set multiple metrics at once.
        
        Args:
            metrics: Either a dictionary mapping metric names to boolean values,
                    or a list of metric names to enable (others will be disabled)
        """
        if isinstance(metrics, dict):
            for metric, enabled in metrics.items():
                if metric in self.AVAILABLE_METRICS:
                    self._metrics[metric] = enabled
                else:
                    self.error.emit(f"Unknown metric: {metric}")
        else:
            # Reset all metrics to False
            self._metrics = {metric: False for metric in self.AVAILABLE_METRICS}
            # Enable the specified metrics
            for metric in metrics:
                if metric in self.AVAILABLE_METRICS:
                    self._metrics[metric] = True
                else:
                    self.error.emit(f"Unknown metric: {metric}")
        
        self.changed.emit()
    
    def validate(self) -> bool:
        """
        Validate the benchmark data.
        
        Returns:
            True if the benchmark data is valid, False otherwise
        """
        if not self._name:
            self.error.emit("Benchmark name cannot be empty")
            return False
        
        if not self._prompt_text:
            self.error.emit("Benchmark prompt text cannot be empty")
            return False
        
        if not any(self._metrics.values()):
            self.error.emit("At least one metric must be enabled")
            return False
        
        return True
    
    def load(self, benchmark_id: int) -> bool:
        """
        Load a benchmark from the database.
        
        Args:
            benchmark_id: ID of the benchmark to load
            
        Returns:
            True if the benchmark was loaded successfully, False otherwise
        """
        try:
            query = QSqlQuery()
            query.prepare("""
                SELECT id, name, description, prompt_text, created_date, user_id, metrics
                FROM Benchmarks
                WHERE id = ?
            """)
            query.addBindValue(benchmark_id)
            
            if not query.exec() or not query.first():
                self.error.emit(f"Failed to load benchmark: {query.lastError().text()}")
                return False
            
            # Populate properties
            self._id = query.value(0)
            self._name = query.value(1)
            self._description = query.value(2)
            self._prompt_text = query.value(3)
            self._created_date = datetime.fromisoformat(query.value(4))
            self._user_id = query.value(5)
            
            # Parse metrics from JSON
            metrics_json = query.value(6)
            try:
                metrics_data = json.loads(metrics_json)
                # Reset all metrics to False
                self._metrics = {metric: False for metric in self.AVAILABLE_METRICS}
                # Apply stored metrics
                if "metrics" in metrics_data:
                    for metric in metrics_data["metrics"]:
                        if metric in self.AVAILABLE_METRICS:
                            self._metrics[metric] = True
            except (json.JSONDecodeError, TypeError):
                self.error.emit("Failed to parse metrics from database")
            
            return True
            
        except Exception as e:
            self.error.emit(f"Error loading benchmark: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save the benchmark to the database.
        
        Returns:
            True if the benchmark was saved successfully, False otherwise
        """
        try:
            # Validate benchmark data
            if not self.validate():
                return False
            
            # Prepare metrics JSON
            metrics_json = json.dumps({
                "metrics": [m for m, enabled in self._metrics.items() if enabled]
            })
            
            query = QSqlQuery()
            
            # Update existing or insert new
            if self._id is not None:
                query.prepare("""
                    UPDATE Benchmarks
                    SET name = ?, description = ?, prompt_text = ?, user_id = ?, metrics = ?
                    WHERE id = ?
                """)
                query.addBindValue(self._name)
                query.addBindValue(self._description)
                query.addBindValue(self._prompt_text)
                query.addBindValue(self._user_id)
                query.addBindValue(metrics_json)
                query.addBindValue(self._id)
                
                if not query.exec():
                    self.error.emit(f"Failed to update benchmark: {query.lastError().text()}")
                    return False
                    
            else:
                # Format created_date as ISO string
                created_date_str = self._created_date.isoformat()
                
                # Insert new benchmark
                query.prepare("""
                    INSERT INTO Benchmarks (name, description, prompt_text, created_date, user_id, metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """)
                query.addBindValue(self._name)
                query.addBindValue(self._description)
                query.addBindValue(self._prompt_text)
                query.addBindValue(created_date_str)
                query.addBindValue(self._user_id)
                query.addBindValue(metrics_json)
                
                if not query.exec():
                    self.error.emit(f"Failed to create benchmark: {query.lastError().text()}")
                    return False
                
                # Get the new ID
                self._id = query.lastInsertId()
            
            self.saved.emit()
            return True
            
        except Exception as e:
            self.error.emit(f"Error saving benchmark: {str(e)}")
            return False
    
    def delete(self) -> bool:
        """
        Delete the benchmark from the database.
        
        Returns:
            True if the benchmark was deleted successfully, False otherwise
        """
        try:
            if self._id is None:
                self.error.emit("Cannot delete benchmark: no ID specified")
                return False
            
            query = QSqlQuery()
            query.prepare("DELETE FROM Benchmarks WHERE id = ?")
            query.addBindValue(self._id)
            
            if not query.exec():
                self.error.emit(f"Failed to delete benchmark: {query.lastError().text()}")
                return False
            
            # Reset properties
            self._id = None
            
            return True
            
        except Exception as e:
            self.error.emit(f"Error deleting benchmark: {str(e)}")
            return False
    
    @staticmethod
    def get_all_benchmarks() -> List['Benchmark']:
        """
        Get all benchmarks from the database.
        
        Returns:
            List of Benchmark objects
        """
        benchmarks = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM Benchmarks ORDER BY name")
            
            if not query.exec():
                raise Exception(f"Failed to query benchmarks: {query.lastError().text()}")
            
            while query.next():
                benchmark_id = query.value(0)
                benchmark = Benchmark(benchmark_id)
                benchmarks.append(benchmark)
            
        except Exception as e:
            print(f"Error retrieving benchmarks: {str(e)}")
        
        return benchmarks
    
    @staticmethod
    def get_benchmarks_by_user(user_id: str) -> List['Benchmark']:
        """
        Get all benchmarks created by a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Benchmark objects
        """
        benchmarks = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM Benchmarks WHERE user_id = ? ORDER BY created_date DESC")
            query.addBindValue(user_id)
            
            if not query.exec():
                raise Exception(f"Failed to query benchmarks: {query.lastError().text()}")
            
            while query.next():
                benchmark_id = query.value(0)
                benchmark = Benchmark(benchmark_id)
                benchmarks.append(benchmark)
            
        except Exception as e:
            print(f"Error retrieving benchmarks: {str(e)}")
        
        return benchmarks 