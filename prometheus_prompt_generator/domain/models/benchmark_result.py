"""
Prometheus AI Prompt Generator - BenchmarkResult Entity

This module defines the BenchmarkResult class, which represents the results of
running a benchmark test on a specific language model.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlQuery, QSqlError


class BenchmarkResult(QObject):
    """
    BenchmarkResult entity for storing results of language model benchmarks.
    
    This class represents the results of running a benchmark on a specific
    language model, including scores for various metrics and the model's response.
    
    Signals:
        changed: Emitted when any property of the result changes
        error: Emitted when an error occurs during result operations
        saved: Emitted when the result is successfully saved
    """
    
    # Define signals
    changed = Signal()
    error = Signal(str)
    saved = Signal()
    
    def __init__(self, result_id: Optional[int] = None):
        """
        Initialize a BenchmarkResult instance.
        
        Args:
            result_id: Optional ID of an existing result to load from the database
        """
        super().__init__()
        
        # Initialize properties
        self._id: Optional[int] = None
        self._benchmark_id: Optional[int] = None
        self._model_id: Optional[int] = None
        self._prompt_id: Optional[int] = None
        self._accuracy_score: Optional[float] = None
        self._coherence_score: Optional[float] = None
        self._speed_score: Optional[float] = None
        self._relevance_score: Optional[float] = None
        self._response_text: str = ""
        self._response_time_ms: int = 0
        self._timestamp: datetime = datetime.now()
        
        # Load the result if an ID is provided
        if result_id is not None:
            self.load(result_id)
    
    @property
    def id(self) -> Optional[int]:
        """Get the result ID."""
        return self._id
    
    @property
    def benchmark_id(self) -> Optional[int]:
        """Get the benchmark ID."""
        return self._benchmark_id
    
    @benchmark_id.setter
    def benchmark_id(self, value: int):
        """Set the benchmark ID."""
        self._benchmark_id = value
        self.changed.emit()
    
    @property
    def model_id(self) -> Optional[int]:
        """Get the model ID."""
        return self._model_id
    
    @model_id.setter
    def model_id(self, value: int):
        """Set the model ID."""
        self._model_id = value
        self.changed.emit()
    
    @property
    def prompt_id(self) -> Optional[int]:
        """Get the prompt ID."""
        return self._prompt_id
    
    @prompt_id.setter
    def prompt_id(self, value: Optional[int]):
        """Set the prompt ID."""
        self._prompt_id = value
        self.changed.emit()
    
    @property
    def accuracy_score(self) -> Optional[float]:
        """Get the accuracy score."""
        return self._accuracy_score
    
    @accuracy_score.setter
    def accuracy_score(self, value: Optional[float]):
        """Set the accuracy score."""
        if value is not None and (value < 0 or value > 5):
            self.error.emit("Accuracy score must be between 0 and 5")
            return
        
        self._accuracy_score = value
        self.changed.emit()
    
    @property
    def coherence_score(self) -> Optional[float]:
        """Get the coherence score."""
        return self._coherence_score
    
    @coherence_score.setter
    def coherence_score(self, value: Optional[float]):
        """Set the coherence score."""
        if value is not None and (value < 0 or value > 5):
            self.error.emit("Coherence score must be between 0 and 5")
            return
        
        self._coherence_score = value
        self.changed.emit()
    
    @property
    def speed_score(self) -> Optional[float]:
        """Get the speed score."""
        return self._speed_score
    
    @speed_score.setter
    def speed_score(self, value: Optional[float]):
        """Set the speed score."""
        if value is not None and (value < 0 or value > 5):
            self.error.emit("Speed score must be between 0 and 5")
            return
        
        self._speed_score = value
        self.changed.emit()
    
    @property
    def relevance_score(self) -> Optional[float]:
        """Get the relevance score."""
        return self._relevance_score
    
    @relevance_score.setter
    def relevance_score(self, value: Optional[float]):
        """Set the relevance score."""
        if value is not None and (value < 0 or value > 5):
            self.error.emit("Relevance score must be between 0 and 5")
            return
        
        self._relevance_score = value
        self.changed.emit()
    
    @property
    def response_text(self) -> str:
        """Get the model's response text."""
        return self._response_text
    
    @response_text.setter
    def response_text(self, value: str):
        """Set the model's response text."""
        self._response_text = value
        self.changed.emit()
    
    @property
    def response_time_ms(self) -> int:
        """Get the response time in milliseconds."""
        return self._response_time_ms
    
    @response_time_ms.setter
    def response_time_ms(self, value: int):
        """Set the response time in milliseconds."""
        if value < 0:
            self.error.emit("Response time cannot be negative")
            return
        
        self._response_time_ms = value
        self.changed.emit()
    
    @property
    def timestamp(self) -> datetime:
        """Get the timestamp when the benchmark was run."""
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, value: datetime):
        """Set the timestamp when the benchmark was run."""
        self._timestamp = value
        self.changed.emit()
    
    def get_all_scores(self) -> Dict[str, float]:
        """
        Get all scores as a dictionary.
        
        Returns:
            Dictionary mapping score names to values
        """
        scores = {}
        if self._accuracy_score is not None:
            scores["accuracy"] = self._accuracy_score
        if self._coherence_score is not None:
            scores["coherence"] = self._coherence_score
        if self._speed_score is not None:
            scores["speed"] = self._speed_score
        if self._relevance_score is not None:
            scores["relevance"] = self._relevance_score
        
        return scores
    
    def set_scores(self, scores: Dict[str, float]):
        """
        Set multiple scores at once.
        
        Args:
            scores: Dictionary mapping score names to values
        """
        if "accuracy" in scores:
            self.accuracy_score = scores["accuracy"]
        if "coherence" in scores:
            self.coherence_score = scores["coherence"]
        if "speed" in scores:
            self.speed_score = scores["speed"]
        if "relevance" in scores:
            self.relevance_score = scores["relevance"]
    
    def get_overall_score(self) -> float:
        """
        Calculate an overall score based on all available metrics.
        
        Returns:
            Overall score (average of all available metrics)
        """
        scores = self.get_all_scores()
        if not scores:
            return 0.0
        
        return sum(scores.values()) / len(scores)
    
    def validate(self) -> bool:
        """
        Validate the benchmark result data.
        
        Returns:
            True if the result data is valid, False otherwise
        """
        if self._benchmark_id is None:
            self.error.emit("Benchmark ID is required")
            return False
        
        if self._model_id is None:
            self.error.emit("Model ID is required")
            return False
        
        # Ensure at least one score is set
        if all(score is None for score in [
            self._accuracy_score, self._coherence_score, 
            self._speed_score, self._relevance_score
        ]):
            self.error.emit("At least one score must be set")
            return False
        
        return True
    
    def load(self, result_id: int) -> bool:
        """
        Load a benchmark result from the database.
        
        Args:
            result_id: ID of the result to load
            
        Returns:
            True if the result was loaded successfully, False otherwise
        """
        try:
            query = QSqlQuery()
            query.prepare("""
                SELECT id, benchmark_id, model_id, prompt_id, accuracy_score, 
                       coherence_score, speed_score, relevance_score, 
                       response_text, response_time_ms, timestamp
                FROM BenchmarkResults
                WHERE id = ?
            """)
            query.addBindValue(result_id)
            
            if not query.exec() or not query.first():
                self.error.emit(f"Failed to load benchmark result: {query.lastError().text()}")
                return False
            
            # Populate properties
            self._id = query.value(0)
            self._benchmark_id = query.value(1)
            self._model_id = query.value(2)
            self._prompt_id = query.value(3)
            self._accuracy_score = query.value(4)
            self._coherence_score = query.value(5)
            self._speed_score = query.value(6)
            self._relevance_score = query.value(7)
            self._response_text = query.value(8)
            self._response_time_ms = query.value(9)
            self._timestamp = datetime.fromisoformat(query.value(10))
            
            return True
            
        except Exception as e:
            self.error.emit(f"Error loading benchmark result: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save the benchmark result to the database.
        
        Returns:
            True if the result was saved successfully, False otherwise
        """
        try:
            # Validate result data
            if not self.validate():
                return False
            
            query = QSqlQuery()
            
            # Update existing or insert new
            if self._id is not None:
                query.prepare("""
                    UPDATE BenchmarkResults
                    SET benchmark_id = ?, model_id = ?, prompt_id = ?,
                        accuracy_score = ?, coherence_score = ?, speed_score = ?,
                        relevance_score = ?, response_text = ?, response_time_ms = ?,
                        timestamp = ?
                    WHERE id = ?
                """)
                query.addBindValue(self._benchmark_id)
                query.addBindValue(self._model_id)
                query.addBindValue(self._prompt_id)
                query.addBindValue(self._accuracy_score)
                query.addBindValue(self._coherence_score)
                query.addBindValue(self._speed_score)
                query.addBindValue(self._relevance_score)
                query.addBindValue(self._response_text)
                query.addBindValue(self._response_time_ms)
                query.addBindValue(self._timestamp.isoformat())
                query.addBindValue(self._id)
                
                if not query.exec():
                    self.error.emit(f"Failed to update benchmark result: {query.lastError().text()}")
                    return False
                    
            else:
                # Insert new result
                query.prepare("""
                    INSERT INTO BenchmarkResults 
                    (benchmark_id, model_id, prompt_id, accuracy_score, coherence_score,
                     speed_score, relevance_score, response_text, response_time_ms, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """)
                query.addBindValue(self._benchmark_id)
                query.addBindValue(self._model_id)
                query.addBindValue(self._prompt_id)
                query.addBindValue(self._accuracy_score)
                query.addBindValue(self._coherence_score)
                query.addBindValue(self._speed_score)
                query.addBindValue(self._relevance_score)
                query.addBindValue(self._response_text)
                query.addBindValue(self._response_time_ms)
                query.addBindValue(self._timestamp.isoformat())
                
                if not query.exec():
                    self.error.emit(f"Failed to create benchmark result: {query.lastError().text()}")
                    return False
                
                # Get the new ID
                self._id = query.lastInsertId()
            
            self.saved.emit()
            return True
            
        except Exception as e:
            self.error.emit(f"Error saving benchmark result: {str(e)}")
            return False
    
    @staticmethod
    def get_results_by_benchmark(benchmark_id: int) -> List['BenchmarkResult']:
        """
        Get all results for a specific benchmark.
        
        Args:
            benchmark_id: ID of the benchmark
            
        Returns:
            List of BenchmarkResult objects
        """
        results = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM BenchmarkResults WHERE benchmark_id = ? ORDER BY timestamp DESC")
            query.addBindValue(benchmark_id)
            
            if not query.exec():
                raise Exception(f"Failed to query benchmark results: {query.lastError().text()}")
            
            while query.next():
                result_id = query.value(0)
                result = BenchmarkResult(result_id)
                results.append(result)
            
        except Exception as e:
            print(f"Error retrieving benchmark results: {str(e)}")
        
        return results
    
    @staticmethod
    def get_results_by_model(model_id: int) -> List['BenchmarkResult']:
        """
        Get all results for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of BenchmarkResult objects
        """
        results = []
        
        try:
            query = QSqlQuery()
            query.prepare("SELECT id FROM BenchmarkResults WHERE model_id = ? ORDER BY timestamp DESC")
            query.addBindValue(model_id)
            
            if not query.exec():
                raise Exception(f"Failed to query benchmark results: {query.lastError().text()}")
            
            while query.next():
                result_id = query.value(0)
                result = BenchmarkResult(result_id)
                results.append(result)
            
        except Exception as e:
            print(f"Error retrieving benchmark results: {str(e)}")
        
        return results
    
    @staticmethod
    def get_result(benchmark_id: int, model_id: int) -> Optional['BenchmarkResult']:
        """
        Get the most recent result for a specific benchmark and model.
        
        Args:
            benchmark_id: ID of the benchmark
            model_id: ID of the model
            
        Returns:
            The most recent BenchmarkResult, or None if not found
        """
        try:
            query = QSqlQuery()
            query.prepare("""
                SELECT id FROM BenchmarkResults 
                WHERE benchmark_id = ? AND model_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            query.addBindValue(benchmark_id)
            query.addBindValue(model_id)
            
            if not query.exec() or not query.first():
                return None
            
            result_id = query.value(0)
            result = BenchmarkResult(result_id)
            return result
            
        except Exception as e:
            print(f"Error retrieving benchmark result: {str(e)}")
            return None 