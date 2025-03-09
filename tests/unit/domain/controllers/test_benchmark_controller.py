"""
Tests for the BenchmarkController class.

This module contains unit tests for the BenchmarkController class, which handles
benchmarking of language models against various prompts and metrics.
"""

import json
from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import QObject, pyqtSignal


# Mock classes for testing
class MockModel(QObject):
    """Mock Model class for testing"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self._id = kwargs.get('id')
        self._name = kwargs.get('name', '')
        self._provider = kwargs.get('provider', '')
        self._version = kwargs.get('version', '')
        self._description = kwargs.get('description', '')
        self._is_local = kwargs.get('is_local', False)


class MockBenchmark(QObject):
    """Mock Benchmark class for testing"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self._id = kwargs.get('id')
        self._name = kwargs.get('name', '')
        self._description = kwargs.get('description', '')
        self._prompt_text = kwargs.get('prompt_text', '')
        self._created_date = kwargs.get('created_date', datetime.now())
        self._user_id = kwargs.get('user_id', '')
        self._metrics = kwargs.get('metrics', {})


class MockBenchmarkResult(QObject):
    """Mock BenchmarkResult class for testing"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self._id = kwargs.get('id')
        self._benchmark_id = kwargs.get('benchmark_id')
        self._model_id = kwargs.get('model_id')
        self._prompt_id = kwargs.get('prompt_id')
        self._accuracy_score = kwargs.get('accuracy_score', 0.0)
        self._coherence_score = kwargs.get('coherence_score', 0.0)
        self._speed_score = kwargs.get('speed_score', 0.0)
        self._relevance_score = kwargs.get('relevance_score', 0.0)
        self._response_text = kwargs.get('response_text', '')
        self._response_time_ms = kwargs.get('response_time_ms', 0)
        self._timestamp = kwargs.get('timestamp', datetime.now())


class MockBenchmarkRepository:
    """Mock repository for benchmarks"""
    
    def __init__(self):
        self.benchmarks = {}
        self.results = {}
        self.next_benchmark_id = 1
        self.next_result_id = 1
        self.should_fail = False
    
    def save_benchmark(self, benchmark):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        if benchmark._id is None:
            benchmark._id = self.next_benchmark_id
            self.next_benchmark_id += 1
        
        self.benchmarks[benchmark._id] = benchmark
        return benchmark
    
    def get_benchmark_by_id(self, benchmark_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return self.benchmarks.get(benchmark_id)
    
    def get_all_benchmarks(self):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return list(self.benchmarks.values())
    
    def delete_benchmark(self, benchmark_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        if benchmark_id in self.benchmarks:
            del self.benchmarks[benchmark_id]
            return True
        return False
    
    def save_result(self, result):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        if result._id is None:
            result._id = self.next_result_id
            self.next_result_id += 1
        
        self.results[result._id] = result
        return result
    
    def get_results_by_benchmark_id(self, benchmark_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return [r for r in self.results.values() if r._benchmark_id == benchmark_id]
    
    def get_results_by_model_id(self, model_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return [r for r in self.results.values() if r._model_id == model_id]


class MockModelRepository:
    """Mock repository for models"""
    
    def __init__(self):
        self.models = {}
        self.next_id = 1
        self.should_fail = False
    
    def save(self, model):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        if model._id is None:
            model._id = self.next_id
            self.next_id += 1
        
        self.models[model._id] = model
        return model
    
    def get_by_id(self, model_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return self.models.get(model_id)
    
    def get_all(self):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        return list(self.models.values())
    
    def delete(self, model_id):
        if self.should_fail:
            raise Exception("Simulated repository error")
        
        if model_id in self.models:
            del self.models[model_id]
            return True
        return False


@pytest.fixture
def benchmark_repository():
    """Fixture for creating a mock benchmark repository"""
    return MockBenchmarkRepository()


@pytest.fixture
def model_repository():
    """Fixture for creating a mock model repository"""
    return MockModelRepository()


@pytest.fixture
def controller(benchmark_repository, model_repository):
    """Fixture for creating a BenchmarkController with mock repositories"""
    from prometheus_prompt_generator.domain.controllers.benchmark_controller import BenchmarkController
    return BenchmarkController(benchmark_repository, model_repository)


@pytest.fixture
def sample_models(model_repository):
    """Fixture for creating sample models"""
    models = [
        MockModel(id=1, name="GPT-4", provider="OpenAI", version="2023-11", description="Large language model", is_local=False),
        MockModel(id=2, name="Claude-3", provider="Anthropic", version="2024-01", description="Advanced reasoning model", is_local=False),
        MockModel(id=3, name="Llama-3", provider="Meta", version="2024-02", description="Open source model", is_local=True)
    ]
    
    for model in models:
        model_repository.save(model)
    
    return models


@pytest.fixture
def sample_benchmark(benchmark_repository):
    """Fixture for creating a sample benchmark"""
    benchmark = MockBenchmark(
        id=1,
        name="Test Benchmark",
        description="A test benchmark for unit testing",
        prompt_text="Explain quantum computing in simple terms",
        created_date=datetime.now(),
        user_id="test_user",
        metrics={"accuracy": True, "coherence": True, "speed": True, "relevance": True}
    )
    
    benchmark_repository.save_benchmark(benchmark)
    return benchmark


@pytest.fixture
def sample_results(benchmark_repository, sample_benchmark, sample_models):
    """Fixture for creating sample benchmark results"""
    results = []
    
    for model in sample_models:
        result = MockBenchmarkResult(
            benchmark_id=sample_benchmark._id,
            model_id=model._id,
            accuracy_score=4.5,
            coherence_score=4.2,
            speed_score=3.8,
            relevance_score=4.0,
            response_text=f"Test response from {model._name}",
            response_time_ms=100 + (model._id * 50),
            timestamp=datetime.now()
        )
        benchmark_repository.save_result(result)
        results.append(result)
    
    return results


class TestBenchmarkController:
    """Tests for the BenchmarkController class"""
    
    def test_init(self, controller, benchmark_repository, model_repository):
        """Test controller initialization"""
        assert controller._benchmark_repository == benchmark_repository
        assert controller._model_repository == model_repository
    
    def test_create_benchmark(self, controller, benchmark_repository):
        """Test creating a new benchmark"""
        # Signals tracking
        signal_received = False
        benchmark_saved = None
        
        def on_benchmark_created(benchmark):
            nonlocal signal_received, benchmark_saved
            signal_received = True
            benchmark_saved = benchmark
        
        controller.benchmark_created.connect(on_benchmark_created)
        
        # Create a benchmark
        benchmark = controller.create_benchmark(
            name="New Benchmark",
            description="Test description",
            prompt_text="Test prompt",
            metrics=["accuracy", "coherence"]
        )
        
        # Verify result
        assert benchmark._id is not None
        assert benchmark._name == "New Benchmark"
        assert benchmark._description == "Test description"
        assert benchmark._prompt_text == "Test prompt"
        assert isinstance(benchmark._metrics, dict)
        assert len(benchmark._metrics) == 2
        assert "accuracy" in benchmark._metrics
        assert "coherence" in benchmark._metrics
        
        # Verify signal was emitted
        assert signal_received
        assert benchmark_saved == benchmark
        
        # Verify benchmark was saved to repository
        assert benchmark._id in benchmark_repository.benchmarks
    
    def test_create_benchmark_error(self, controller, benchmark_repository):
        """Test error handling when creating a benchmark fails"""
        # Prepare for failure
        benchmark_repository.should_fail = True
        
        # Signals tracking
        error_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_received, error_message
            error_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Attempt to create benchmark (should raise exception)
        with pytest.raises(Exception):
            controller.create_benchmark(
                name="New Benchmark",
                description="Test description",
                prompt_text="Test prompt"
            )
        
        # Verify error signal was emitted
        assert error_received
        assert "Failed to create benchmark" in error_message
        
        # Reset repository for other tests
        benchmark_repository.should_fail = False
    
    def test_get_benchmark(self, controller, sample_benchmark):
        """Test retrieving a benchmark by ID"""
        # Signals tracking
        signal_received = False
        benchmark_loaded = None
        
        def on_benchmark_loaded(benchmark):
            nonlocal signal_received, benchmark_loaded
            signal_received = True
            benchmark_loaded = benchmark
        
        controller.benchmark_loaded.connect(on_benchmark_loaded)
        
        # Get the benchmark
        benchmark = controller.get_benchmark(sample_benchmark._id)
        
        # Verify result
        assert benchmark == sample_benchmark
        
        # Verify signal was emitted
        assert signal_received
        assert benchmark_loaded == sample_benchmark
    
    def test_get_benchmark_error(self, controller, benchmark_repository):
        """Test error handling when getting a benchmark fails"""
        # Prepare for failure
        benchmark_repository.should_fail = True
        
        # Signals tracking
        error_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_received, error_message
            error_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Attempt to get benchmark (should raise exception)
        with pytest.raises(Exception):
            controller.get_benchmark(1)
        
        # Verify error signal was emitted
        assert error_received
        assert "Failed to get benchmark" in error_message
        
        # Reset repository for other tests
        benchmark_repository.should_fail = False
    
    def test_get_all_benchmarks(self, controller, sample_benchmark):
        """Test retrieving all benchmarks"""
        # Signals tracking
        signal_received = False
        benchmarks_loaded = None
        
        def on_all_benchmarks_loaded(benchmarks):
            nonlocal signal_received, benchmarks_loaded
            signal_received = True
            benchmarks_loaded = benchmarks
        
        controller.all_benchmarks_loaded.connect(on_all_benchmarks_loaded)
        
        # Get all benchmarks
        benchmarks = controller.get_all_benchmarks()
        
        # Verify result
        assert len(benchmarks) == 1
        assert benchmarks[0] == sample_benchmark
        
        # Verify signal was emitted
        assert signal_received
        assert len(benchmarks_loaded) == 1
        assert benchmarks_loaded[0] == sample_benchmark
    
    def test_delete_benchmark(self, controller, sample_benchmark):
        """Test deleting a benchmark"""
        # Signals tracking
        signal_received = False
        deleted_id = None
        
        def on_benchmark_deleted(benchmark_id):
            nonlocal signal_received, deleted_id
            signal_received = True
            deleted_id = benchmark_id
        
        controller.benchmark_deleted.connect(on_benchmark_deleted)
        
        # Delete the benchmark
        result = controller.delete_benchmark(sample_benchmark._id)
        
        # Verify result
        assert result is True
        
        # Verify signal was emitted
        assert signal_received
        assert deleted_id == sample_benchmark._id
        
        # Verify benchmark was removed from repository
        benchmarks = controller.get_all_benchmarks()
        assert len(benchmarks) == 0
    
    def test_run_benchmark(self, controller, sample_benchmark, sample_models):
        """Test running a benchmark against models"""
        # Signals tracking
        run_started = False
        run_completed = False
        result_saved = False
        results_list = []
        
        def on_benchmark_run_started(benchmark_id, model_count):
            nonlocal run_started
            run_started = True
            assert benchmark_id == sample_benchmark._id
            assert model_count == len(sample_models)
        
        def on_benchmark_run_completed(benchmark_id):
            nonlocal run_completed
            run_completed = True
            assert benchmark_id == sample_benchmark._id
        
        def on_benchmark_result_saved(result):
            nonlocal result_saved, results_list
            result_saved = True
            results_list.append(result)
        
        controller.benchmark_run_started.connect(on_benchmark_run_started)
        controller.benchmark_run_completed.connect(on_benchmark_run_completed)
        controller.benchmark_result_saved.connect(on_benchmark_result_saved)
        
        # Mock the execution function to return predictable results
        controller._execute_on_model = MagicMock()
        controller._execute_on_model.side_effect = lambda benchmark, model: {
            "accuracy_score": 4.5,
            "coherence_score": 4.2,
            "speed_score": 3.8,
            "relevance_score": 4.0,
            "response_text": f"Mocked response from {model._name}",
            "response_time_ms": 100 + (model._id * 50)
        }
        
        # Run the benchmark
        results = controller.run_benchmark(
            benchmark_id=sample_benchmark._id,
            model_ids=[model._id for model in sample_models]
        )
        
        # Verify signals
        assert run_started
        assert run_completed
        assert result_saved
        assert len(results_list) == len(sample_models)
        
        # Verify results
        assert len(results) == len(sample_models)
        for result in results:
            assert result._benchmark_id == sample_benchmark._id
            assert result._model_id in [model._id for model in sample_models]
            assert result._accuracy_score == 4.5
            assert result._coherence_score == 4.2
            assert result._speed_score == 3.8
            assert result._relevance_score == 4.0
            assert "Mocked response from" in result._response_text
    
    def test_run_benchmark_error(self, controller, sample_benchmark, sample_models, benchmark_repository):
        """Test error handling when running a benchmark fails"""
        # Prepare for failure
        benchmark_repository.should_fail = True
        
        # Signals tracking
        error_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_received, error_message
            error_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Attempt to run benchmark (should raise exception)
        with pytest.raises(Exception):
            controller.run_benchmark(
                benchmark_id=sample_benchmark._id,
                model_ids=[model._id for model in sample_models]
            )
        
        # Verify error signal was emitted
        assert error_received
        assert "Failed to run benchmark" in error_message
        
        # Reset repository for other tests
        benchmark_repository.should_fail = False
    
    def test_get_benchmark_results(self, controller, sample_benchmark, sample_results):
        """Test retrieving results for a benchmark"""
        # Signals tracking
        signal_received = False
        results_loaded = None
        
        def on_results_loaded(results):
            nonlocal signal_received, results_loaded
            signal_received = True
            results_loaded = results
        
        controller.results_loaded.connect(on_results_loaded)
        
        # Get results
        results = controller.get_benchmark_results(sample_benchmark._id)
        
        # Verify result
        assert len(results) == len(sample_results)
        
        # Verify signal was emitted
        assert signal_received
        assert len(results_loaded) == len(sample_results)
    
    def test_analyze_results(self, controller, sample_benchmark, sample_results):
        """Test analyzing benchmark results"""
        # Get analysis
        analysis = controller.analyze_benchmark_results(sample_benchmark._id)
        
        # Verify analysis structure
        assert "models" in analysis
        assert "metrics" in analysis
        assert "overall_ranking" in analysis
        
        # Check metrics
        assert "accuracy" in analysis["metrics"]
        assert "coherence" in analysis["metrics"]
        assert "speed" in analysis["metrics"]
        assert "relevance" in analysis["metrics"]
        
        # Check model results
        assert len(analysis["models"]) == 3  # We have 3 models in sample_models
        
        # Check overall ranking
        assert isinstance(analysis["overall_ranking"], list)
        assert len(analysis["overall_ranking"]) == 3
    
    def test_compare_models(self, controller, sample_models, sample_results):
        """Test comparing multiple models"""
        # Get comparison
        model_ids = [model._id for model in sample_models]
        comparison = controller.compare_models(model_ids)
        
        # Verify comparison structure
        assert len(comparison) == len(model_ids)
        for model_id in model_ids:
            assert model_id in comparison
            model_data = comparison[model_id]
            assert "name" in model_data
            assert "provider" in model_data
            assert "metrics" in model_data
            assert "strengths" in model_data
            assert "weaknesses" in model_data
    
    def test_get_visualization_data(self, controller, sample_benchmark, sample_results):
        """Test generating visualization data"""
        # Get visualization data
        viz_data = controller.get_visualization_data(sample_benchmark._id)
        
        # Verify data structure
        assert "radar_chart" in viz_data
        assert "bar_chart" in viz_data
        assert "time_comparison" in viz_data
        
        # Check radar chart data
        assert "labels" in viz_data["radar_chart"]
        assert "datasets" in viz_data["radar_chart"]
        
        # Check bar chart data
        assert "labels" in viz_data["bar_chart"]
        assert "datasets" in viz_data["bar_chart"]
        
        # Check time comparison data
        assert "labels" in viz_data["time_comparison"]
        assert "datasets" in viz_data["time_comparison"] 