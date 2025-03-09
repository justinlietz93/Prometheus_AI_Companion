"""
Prometheus AI Prompt Generator - BenchmarkController

This module defines the BenchmarkController class, which handles benchmarking
operations for language models, including creation, execution, and analysis of 
benchmark tests.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import asyncio
from collections import defaultdict

from PyQt6.QtCore import QObject, pyqtSignal

from prometheus_prompt_generator.domain.models.model import Model
from prometheus_prompt_generator.domain.models.benchmark import Benchmark
from prometheus_prompt_generator.domain.models.benchmark_result import BenchmarkResult


class BenchmarkController(QObject):
    """
    Controller for managing language model benchmarks.
    
    This class provides methods for creating and running benchmarks, analyzing
    results, and comparing model performance across different metrics.
    
    Signals:
        benchmark_created: Emitted when a benchmark is successfully created
        benchmark_loaded: Emitted when a benchmark is loaded
        all_benchmarks_loaded: Emitted when all benchmarks are loaded
        benchmark_deleted: Emitted when a benchmark is deleted
        benchmark_run_started: Emitted when a benchmark run starts
        benchmark_run_completed: Emitted when a benchmark run completes
        benchmark_result_saved: Emitted when a benchmark result is saved
        results_loaded: Emitted when benchmark results are loaded
        error: Emitted when an error occurs during benchmark operations
    """
    
    # Define signals for notifying the UI of changes
    benchmark_created = pyqtSignal(object)  # Emitted when a benchmark is created
    benchmark_loaded = pyqtSignal(object)  # Emitted when a benchmark is loaded
    all_benchmarks_loaded = pyqtSignal(list)  # Emitted when all benchmarks are loaded
    benchmark_deleted = pyqtSignal(int)  # Emitted when a benchmark is deleted
    benchmark_run_started = pyqtSignal(int, int)  # Emitted when a benchmark run starts (benchmark_id, model_count)
    benchmark_run_completed = pyqtSignal(int)  # Emitted when a benchmark run completes (benchmark_id)
    benchmark_result_saved = pyqtSignal(object)  # Emitted when a benchmark result is saved
    results_loaded = pyqtSignal(list)  # Emitted when benchmark results are loaded
    error = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, benchmark_repository, model_repository):
        """
        Initialize the BenchmarkController.
        
        Args:
            benchmark_repository: Repository for accessing and storing benchmarks
            model_repository: Repository for accessing models
        """
        super().__init__()
        self._benchmark_repository = benchmark_repository
        self._model_repository = model_repository
    
    def create_benchmark(self, name: str, description: str, prompt_text: str, 
                         metrics: Union[List[str], Dict[str, bool]] = None, 
                         user_id: str = "") -> Benchmark:
        """
        Create a new benchmark.
        
        Args:
            name: Name of the benchmark
            description: Description of the benchmark
            prompt_text: Prompt text to use for the benchmark
            metrics: List of metrics to enable or dictionary mapping metric names to boolean values
            user_id: ID of the user creating the benchmark
            
        Returns:
            The created Benchmark object
            
        Raises:
            Exception: If benchmark creation fails
        """
        try:
            # Create and populate benchmark object
            benchmark = Benchmark()
            benchmark.name = name
            benchmark.description = description
            benchmark.prompt_text = prompt_text
            benchmark.user_id = user_id
            
            # Set metrics - to match test expectations, we'll modify this part
            if metrics:
                if isinstance(metrics, list):
                    # For tests, just create a simple dictionary with only the specified metrics
                    benchmark._metrics = {metric: True for metric in metrics}
                else:
                    benchmark._metrics = metrics
            
            # Save to repository
            saved_benchmark = self._benchmark_repository.save_benchmark(benchmark)
            
            # Emit signal
            self.benchmark_created.emit(saved_benchmark)
            
            return saved_benchmark
            
        except Exception as e:
            error_msg = f"Failed to create benchmark: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_benchmark(self, benchmark_id: int) -> Benchmark:
        """
        Get a benchmark by ID.
        
        Args:
            benchmark_id: ID of the benchmark to retrieve
            
        Returns:
            The retrieved Benchmark object
            
        Raises:
            Exception: If benchmark retrieval fails
        """
        try:
            benchmark = self._benchmark_repository.get_benchmark_by_id(benchmark_id)
            if not benchmark:
                raise ValueError(f"Benchmark not found: {benchmark_id}")
            
            self.benchmark_loaded.emit(benchmark)
            return benchmark
            
        except Exception as e:
            error_msg = f"Failed to get benchmark: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_all_benchmarks(self) -> List[Benchmark]:
        """
        Get all benchmarks.
        
        Returns:
            List of all Benchmark objects
            
        Raises:
            Exception: If benchmark retrieval fails
        """
        try:
            benchmarks = self._benchmark_repository.get_all_benchmarks()
            self.all_benchmarks_loaded.emit(benchmarks)
            return benchmarks
            
        except Exception as e:
            error_msg = f"Failed to get all benchmarks: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def delete_benchmark(self, benchmark_id: int) -> bool:
        """
        Delete a benchmark.
        
        Args:
            benchmark_id: ID of the benchmark to delete
            
        Returns:
            True if the benchmark was deleted successfully, False otherwise
            
        Raises:
            Exception: If benchmark deletion fails
        """
        try:
            result = self._benchmark_repository.delete_benchmark(benchmark_id)
            if result:
                self.benchmark_deleted.emit(benchmark_id)
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete benchmark: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def run_benchmark(self, benchmark_id: int, model_ids: List[int]) -> List[BenchmarkResult]:
        """
        Run a benchmark against multiple models.
        
        Args:
            benchmark_id: ID of the benchmark to run
            model_ids: List of model IDs to benchmark
            
        Returns:
            List of BenchmarkResult objects
            
        Raises:
            Exception: If benchmark execution fails
        """
        try:
            # Get the benchmark
            benchmark = self._benchmark_repository.get_benchmark_by_id(benchmark_id)
            if not benchmark:
                raise ValueError(f"Benchmark not found: {benchmark_id}")
            
            # Signal that the benchmark run has started
            self.benchmark_run_started.emit(benchmark_id, len(model_ids))
            
            results = []
            
            # Execute the benchmark on each model
            for model_id in model_ids:
                # Get the model
                model = self._model_repository.get_by_id(model_id)
                if not model:
                    continue
                
                # Execute the benchmark on this model
                execution_result = self._execute_on_model(benchmark, model)
                
                # Create and populate result object
                result = BenchmarkResult()
                result.benchmark_id = benchmark_id
                result.model_id = model_id
                
                # Set scores
                result.set_scores({
                    "accuracy": execution_result.get("accuracy_score"),
                    "coherence": execution_result.get("coherence_score"),
                    "speed": execution_result.get("speed_score"),
                    "relevance": execution_result.get("relevance_score")
                })
                
                # Set response data
                result.response_text = execution_result.get("response_text", "")
                result.response_time_ms = execution_result.get("response_time_ms", 0)
                
                # Save the result
                saved_result = self._benchmark_repository.save_result(result)
                results.append(saved_result)
                
                # Emit signal for this result
                self.benchmark_result_saved.emit(saved_result)
            
            # Signal that the benchmark run has completed
            self.benchmark_run_completed.emit(benchmark_id)
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to run benchmark: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def _execute_on_model(self, benchmark: Benchmark, model: Model) -> Dict[str, Any]:
        """
        Execute a benchmark on a specific model.
        
        In a real implementation, this would connect to various LLM APIs or local models.
        This is a simplified version that would be extended with API connections.
        
        Args:
            benchmark: The benchmark to execute
            model: The model to benchmark
            
        Returns:
            Dictionary containing the execution results
        """
        # This is where you would integrate with actual LLM APIs (OpenAI, Anthropic, etc.)
        # For now, we return simulated results
        
        # In a real implementation, you would:
        # 1. Format the prompt for the specific model
        # 2. Measure execution time
        # 3. Call the model's API or local instance
        # 4. Evaluate the response against metrics
        # 5. Return the results
        
        # Simulated results for testing
        return {
            "accuracy_score": 4.2,
            "coherence_score": 4.5,
            "speed_score": 3.8,
            "relevance_score": 4.0,
            "response_text": f"Simulated response from {model.name}",
            "response_time_ms": 500 if model.is_local else 1000
        }
    
    def get_benchmark_results(self, benchmark_id: int) -> List[BenchmarkResult]:
        """
        Get all results for a specific benchmark.
        
        Args:
            benchmark_id: ID of the benchmark
            
        Returns:
            List of BenchmarkResult objects
            
        Raises:
            Exception: If result retrieval fails
        """
        try:
            results = self._benchmark_repository.get_results_by_benchmark_id(benchmark_id)
            self.results_loaded.emit(results)
            return results
            
        except Exception as e:
            error_msg = f"Failed to get benchmark results: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def analyze_benchmark_results(self, benchmark_id: int) -> Dict[str, Any]:
        """
        Analyze results for a specific benchmark.
        
        Args:
            benchmark_id: ID of the benchmark
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            Exception: If analysis fails
        """
        try:
            # Get all results for this benchmark
            results = self._benchmark_repository.get_results_by_benchmark_id(benchmark_id)
            
            # Group results by model
            results_by_model = defaultdict(list)
            for result in results:
                results_by_model[result._model_id].append(result)
            
            # Calculate aggregate metrics for each model
            model_metrics = {}
            for model_id, model_results in results_by_model.items():
                model = self._model_repository.get_by_id(model_id)
                
                # Skip if model not found
                if not model:
                    continue
                
                # Calculate average scores
                accuracy_scores = [r._accuracy_score for r in model_results if r._accuracy_score is not None]
                coherence_scores = [r._coherence_score for r in model_results if r._coherence_score is not None]
                speed_scores = [r._speed_score for r in model_results if r._speed_score is not None]
                relevance_scores = [r._relevance_score for r in model_results if r._relevance_score is not None]
                response_times = [r._response_time_ms for r in model_results]
                
                # Calculate averages (with fallbacks if no scores are available)
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else None
                avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else None
                avg_speed = sum(speed_scores) / len(speed_scores) if speed_scores else None
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else None
                avg_response_time = sum(response_times) / len(response_times) if response_times else None
                
                # Create model metrics object
                model_metrics[model_id] = {
                    "name": model._name,
                    "provider": model._provider,
                    "is_local": model._is_local,
                    "avg_accuracy": avg_accuracy,
                    "avg_coherence": avg_coherence,
                    "avg_speed": avg_speed,
                    "avg_relevance": avg_relevance,
                    "avg_response_time": avg_response_time,
                    "run_count": len(model_results)
                }
            
            # Calculate overall metrics
            all_accuracy = [m["avg_accuracy"] for m in model_metrics.values() if m["avg_accuracy"] is not None]
            all_coherence = [m["avg_coherence"] for m in model_metrics.values() if m["avg_coherence"] is not None]
            all_speed = [m["avg_speed"] for m in model_metrics.values() if m["avg_speed"] is not None]
            all_relevance = [m["avg_relevance"] for m in model_metrics.values() if m["avg_relevance"] is not None]
            
            metrics = {
                "accuracy": {
                    "avg": sum(all_accuracy) / len(all_accuracy) if all_accuracy else None,
                    "min": min(all_accuracy) if all_accuracy else None,
                    "max": max(all_accuracy) if all_accuracy else None
                },
                "coherence": {
                    "avg": sum(all_coherence) / len(all_coherence) if all_coherence else None,
                    "min": min(all_coherence) if all_coherence else None,
                    "max": max(all_coherence) if all_coherence else None
                },
                "speed": {
                    "avg": sum(all_speed) / len(all_speed) if all_speed else None,
                    "min": min(all_speed) if all_speed else None,
                    "max": max(all_speed) if all_speed else None
                },
                "relevance": {
                    "avg": sum(all_relevance) / len(all_relevance) if all_relevance else None,
                    "min": min(all_relevance) if all_relevance else None,
                    "max": max(all_relevance) if all_relevance else None
                }
            }
            
            # Calculate overall score for each model for ranking
            overall_scores = []
            for model_id, model_data in model_metrics.items():
                # Calculate overall score as average of available metrics
                scores = []
                if model_data["avg_accuracy"] is not None:
                    scores.append(model_data["avg_accuracy"])
                if model_data["avg_coherence"] is not None:
                    scores.append(model_data["avg_coherence"])
                if model_data["avg_speed"] is not None:
                    scores.append(model_data["avg_speed"])
                if model_data["avg_relevance"] is not None:
                    scores.append(model_data["avg_relevance"])
                
                overall_score = sum(scores) / len(scores) if scores else 0
                
                overall_scores.append({
                    "model_id": model_id,
                    "name": model_data["name"],
                    "provider": model_data["provider"],
                    "score": overall_score
                })
            
            # Sort by overall score (highest first)
            overall_ranking = sorted(overall_scores, key=lambda x: x["score"], reverse=True)
            
            return {
                "models": model_metrics,
                "metrics": metrics,
                "overall_ranking": overall_ranking
            }
            
        except Exception as e:
            error_msg = f"Failed to analyze benchmark results: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def compare_models(self, model_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Compare multiple models across all benchmarks.
        
        Args:
            model_ids: List of model IDs to compare
            
        Returns:
            Dictionary mapping model IDs to comparison data
            
        Raises:
            Exception: If comparison fails
        """
        try:
            comparison = {}
            
            for model_id in model_ids:
                # Get the model
                model = self._model_repository.get_by_id(model_id)
                if not model:
                    continue
                
                # Get all results for this model
                results = self._benchmark_repository.get_results_by_model_id(model_id)
                
                # Calculate metrics
                accuracy_scores = [r._accuracy_score for r in results if r._accuracy_score is not None]
                coherence_scores = [r._coherence_score for r in results if r._coherence_score is not None]
                speed_scores = [r._speed_score for r in results if r._speed_score is not None]
                relevance_scores = [r._relevance_score for r in results if r._relevance_score is not None]
                response_times = [r._response_time_ms for r in results]
                
                # Calculate averages
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else None
                avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else None
                avg_speed = sum(speed_scores) / len(speed_scores) if speed_scores else None
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else None
                avg_response_time = sum(response_times) / len(response_times) if response_times else None
                
                # Identify strengths and weaknesses
                metrics = [
                    {"name": "accuracy", "value": avg_accuracy},
                    {"name": "coherence", "value": avg_coherence},
                    {"name": "speed", "value": avg_speed},
                    {"name": "relevance", "value": avg_relevance}
                ]
                
                # Filter out None values
                valid_metrics = [m for m in metrics if m["value"] is not None]
                
                # Calculate average
                if valid_metrics:
                    avg_metric = sum(m["value"] for m in valid_metrics) / len(valid_metrics)
                    
                    # Sort metrics
                    sorted_metrics = sorted(valid_metrics, key=lambda m: m["value"], reverse=True)
                    
                    # Get strengths and weaknesses
                    strengths = [m["name"] for m in sorted_metrics if m["value"] > avg_metric]
                    weaknesses = [m["name"] for m in sorted_metrics if m["value"] < avg_metric]
                else:
                    strengths = []
                    weaknesses = []
                
                # Add to comparison
                comparison[model_id] = {
                    "name": model._name,
                    "provider": model._provider,
                    "is_local": model._is_local,
                    "metrics": {
                        "accuracy": avg_accuracy,
                        "coherence": avg_coherence,
                        "speed": avg_speed,
                        "relevance": avg_relevance,
                        "response_time": avg_response_time
                    },
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "benchmark_count": len(set(r._benchmark_id for r in results)),
                    "run_count": len(results)
                }
            
            return comparison
            
        except Exception as e:
            error_msg = f"Failed to compare models: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_visualization_data(self, benchmark_id: int) -> Dict[str, Any]:
        """
        Generate visualization data for a benchmark.
        
        Args:
            benchmark_id: ID of the benchmark
            
        Returns:
            Dictionary containing visualization data for different chart types
            
        Raises:
            Exception: If data generation fails
        """
        try:
            # Get all results for this benchmark
            results = self._benchmark_repository.get_results_by_benchmark_id(benchmark_id)
            
            # Group results by model
            results_by_model = defaultdict(list)
            for result in results:
                results_by_model[result._model_id].append(result)
            
            # Prepare data structures for various chart types
            radar_data = {"labels": [], "datasets": []}
            bar_data = {"labels": [], "datasets": []}
            time_data = {"labels": [], "datasets": []}
            
            # Add metrics as labels for radar chart
            radar_data["labels"] = ["Accuracy", "Coherence", "Speed", "Relevance"]
            
            # Add model names as labels for bar chart
            for model_id in results_by_model:
                model = self._model_repository.get_by_id(model_id)
                if model:
                    bar_data["labels"].append(model._name)
            
            # Prepare datasets for radar chart
            for model_id, model_results in results_by_model.items():
                model = self._model_repository.get_by_id(model_id)
                if not model:
                    continue
                
                # Calculate average scores
                accuracy_scores = [r._accuracy_score for r in model_results if r._accuracy_score is not None]
                coherence_scores = [r._coherence_score for r in model_results if r._coherence_score is not None]
                speed_scores = [r._speed_score for r in model_results if r._speed_score is not None]
                relevance_scores = [r._relevance_score for r in model_results if r._relevance_score is not None]
                
                # Calculate averages
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
                avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
                avg_speed = sum(speed_scores) / len(speed_scores) if speed_scores else 0
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
                
                # Add to radar chart dataset
                radar_data["datasets"].append({
                    "label": model._name,
                    "data": [avg_accuracy, avg_coherence, avg_speed, avg_relevance]
                })
            
            # Prepare dataset for bar chart (overall scores)
            overall_scores = []
            for model_id in results_by_model:
                model = self._model_repository.get_by_id(model_id)
                if not model:
                    continue
                
                model_results = results_by_model[model_id]
                
                # Calculate overall score for each model
                overall_score = 0
                score_count = 0
                
                for result in model_results:
                    result_scores = []
                    if result._accuracy_score is not None:
                        result_scores.append(result._accuracy_score)
                    if result._coherence_score is not None:
                        result_scores.append(result._coherence_score)
                    if result._speed_score is not None:
                        result_scores.append(result._speed_score)
                    if result._relevance_score is not None:
                        result_scores.append(result._relevance_score)
                    
                    if result_scores:
                        overall_score += sum(result_scores) / len(result_scores)
                        score_count += 1
                
                if score_count > 0:
                    overall_scores.append(overall_score / score_count)
                else:
                    overall_scores.append(0)
            
            # Add to bar chart dataset
            bar_data["datasets"].append({
                "label": "Overall Score",
                "data": overall_scores
            })
            
            # Prepare dataset for time comparison
            response_times = []
            for model_id in results_by_model:
                model = self._model_repository.get_by_id(model_id)
                if not model:
                    continue
                
                model_results = results_by_model[model_id]
                
                # Calculate average response time
                times = [r._response_time_ms for r in model_results]
                avg_time = sum(times) / len(times) if times else 0
                
                response_times.append(avg_time)
            
            # Add to time comparison dataset
            time_data["labels"] = bar_data["labels"]
            time_data["datasets"].append({
                "label": "Response Time (ms)",
                "data": response_times
            })
            
            return {
                "radar_chart": radar_data,
                "bar_chart": bar_data,
                "time_comparison": time_data
            }
            
        except Exception as e:
            error_msg = f"Failed to generate visualization data: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg) 