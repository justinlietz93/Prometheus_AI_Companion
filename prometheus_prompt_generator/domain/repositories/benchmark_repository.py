"""
Benchmark Repository for the Prometheus AI Prompt Generator.

This module provides database access for managing benchmark configurations and results.
"""

from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from PySide6.QtSql import QSqlQuery, QSqlError, QSqlDatabase

from prometheus_prompt_generator.domain.models.benchmark import Benchmark
from prometheus_prompt_generator.domain.models.benchmark_result import BenchmarkResult


class BenchmarkRepository:
    """
    Repository for managing benchmark configurations and results.
    
    This class provides methods for storing, retrieving, and managing
    benchmark configurations and their associated results.
    """
    
    def __init__(self, db=None):
        """
        Initialize the BenchmarkRepository.
        
        Args:
            db: QSqlDatabase instance to use (or None to use the default connection)
        """
        self.db = db if db is not None else QSqlDatabase.database()
    
    def save_benchmark(self, benchmark: Benchmark) -> Benchmark:
        """
        Save a benchmark to the database.
        
        Args:
            benchmark: The benchmark to save
            
        Returns:
            The saved benchmark with updated ID if it was a new record
            
        Raises:
            Exception: If the save operation fails
        """
        # Call the save method on the benchmark object
        if not benchmark.save():
            raise Exception(f"Failed to save benchmark: {benchmark.name}")
        
        return benchmark
    
    def get_benchmark_by_id(self, benchmark_id: int) -> Optional[Benchmark]:
        """
        Get a benchmark by its ID.
        
        Args:
            benchmark_id: ID of the benchmark to retrieve
            
        Returns:
            The retrieved benchmark, or None if not found
            
        Raises:
            Exception: If the retrieval operation fails
        """
        benchmark = Benchmark(benchmark_id)
        if benchmark.id is None:
            return None
        
        return benchmark
    
    def get_all_benchmarks(self) -> List[Benchmark]:
        """
        Get all benchmarks.
        
        Returns:
            List of all benchmarks
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return Benchmark.get_all_benchmarks()
    
    def delete_benchmark(self, benchmark_id: int) -> bool:
        """
        Delete a benchmark.
        
        Args:
            benchmark_id: ID of the benchmark to delete
            
        Returns:
            True if the benchmark was deleted, False otherwise
            
        Raises:
            Exception: If the delete operation fails
        """
        benchmark = self.get_benchmark_by_id(benchmark_id)
        if benchmark is None:
            return False
        
        return benchmark.delete()
    
    def get_benchmarks_by_user(self, user_id: str) -> List[Benchmark]:
        """
        Get all benchmarks created by a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of benchmarks created by the user
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return Benchmark.get_benchmarks_by_user(user_id)
    
    def save_result(self, result: BenchmarkResult) -> BenchmarkResult:
        """
        Save a benchmark result to the database.
        
        Args:
            result: The benchmark result to save
            
        Returns:
            The saved benchmark result with updated ID if it was a new record
            
        Raises:
            Exception: If the save operation fails
        """
        # Call the save method on the result object
        if not result.save():
            raise Exception(f"Failed to save benchmark result for benchmark ID: {result.benchmark_id}")
        
        return result
    
    def get_results_by_benchmark_id(self, benchmark_id: int) -> List[BenchmarkResult]:
        """
        Get all results for a specific benchmark.
        
        Args:
            benchmark_id: ID of the benchmark
            
        Returns:
            List of benchmark results for the benchmark
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return BenchmarkResult.get_results_by_benchmark(benchmark_id)
    
    def get_results_by_model_id(self, model_id: int) -> List[BenchmarkResult]:
        """
        Get all results for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of benchmark results for the model
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return BenchmarkResult.get_results_by_model(model_id)
    
    def get_result(self, benchmark_id: int, model_id: int) -> Optional[BenchmarkResult]:
        """
        Get the most recent result for a specific benchmark and model.
        
        Args:
            benchmark_id: ID of the benchmark
            model_id: ID of the model
            
        Returns:
            The most recent benchmark result, or None if not found
            
        Raises:
            Exception: If the retrieval operation fails
        """
        return BenchmarkResult.get_result(benchmark_id, model_id) 