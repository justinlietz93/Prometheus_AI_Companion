"""
Unit tests for the UsageController class.

This module contains test cases for the UsageController, which handles
tracking and analyzing prompt usage patterns in the system.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal

from prometheus_prompt_generator.domain.models.prompt_usage import PromptUsage
from prometheus_prompt_generator.domain.controllers.usage_controller import UsageController


class MockPromptUsage(PromptUsage):
    """
    Mock version of PromptUsage that allows direct setting of properties.
    This is used for testing to bypass database operations.
    """
    
    def __init__(self, **kwargs):
        """Initialize a MockPromptUsage with provided values."""
        super().__init__()
        # Allow direct setting of otherwise read-only properties
        for key, value in kwargs.items():
            if key.startswith('_'):
                setattr(self, key, value)
            else:
                setattr(self, f"_{key}", value)


class MockPromptUsageRepository:
    """Mock repository for testing UsageController."""
    
    def __init__(self):
        self.usages = {}  # id -> MockPromptUsage
        self.next_id = 1
        self.error_on_get_by_prompt_id = False
        self.error_on_get_by_user_id = False
        self.error_on_get_by_date_range = False
        self.error_on_get_all = False
        self.error_on_add = False
        self.error_on_save = False
        # Add tracking attributes
        self.save_called = False
        self.get_by_prompt_id_called = False
        self.get_by_user_id_called = False
        self.get_by_date_range_called = False
        self.get_all_called = False
        self.add_called = False

    def save(self, usage):
        self.save_called = True
        if self.error_on_save:
            raise Exception("Simulated error in save method")
            
        usage_id = self.next_id
        self.next_id += 1
        usage._id = usage_id
        self.usages[usage_id] = usage
        return usage
        
    def get_by_prompt_id(self, prompt_id):
        """Get all usage records for a specific prompt."""
        self.get_by_prompt_id_called = True
        if self.error_on_get_by_prompt_id:
            raise Exception("Failed to get usage for prompt")
            
        return [usage for usage in self.usages.values() if usage._prompt_id == prompt_id]
        
    def get_by_user_id(self, user_id):
        """Get all usage records for a specific user."""
        self.get_by_user_id_called = True
        if self.error_on_get_by_user_id:
            raise Exception("Failed to get usage for user")
            
        return [usage for usage in self.usages.values() if usage._user_id == user_id]
        
    def get_by_date_range(self, start_date, end_date):
        """Get all usage records within a date range."""
        self.get_by_date_range_called = True
        if self.error_on_get_by_date_range:
            raise Exception("Failed to get usage by date range")
            
        return [
            usage for usage in self.usages.values() 
            if start_date <= usage._timestamp <= end_date
        ]
        
    def get_all(self):
        """Get all usage records in the repository."""
        self.get_all_called = True
        if self.error_on_get_all:
            raise Exception("Failed to get all usage records")
            
        return list(self.usages.values())

    def add(self, prompt_usage):
        self.add_called = True
        if self.error_on_add:
            raise Exception("Simulated error in add method")
            
        usage_id = len(self.usages) + 1
        prompt_usage._id = usage_id
        self.usages[usage_id] = prompt_usage
        return prompt_usage


class MockPromptRepository:
    """Mock repository for testing prompt retrieval."""
    
    def __init__(self):
        self.prompts = {}
        
    def get_by_id(self, prompt_id):
        """Get a prompt by its ID."""
        return self.prompts.get(prompt_id)


@pytest.fixture
def usage_repository():
    """Fixture to create a mock usage repository."""
    return MockPromptUsageRepository()


@pytest.fixture
def prompt_repository():
    """Fixture to create a mock prompt repository."""
    return MockPromptRepository()


@pytest.fixture
def controller(usage_repository, prompt_repository):
    """Fixture to create a UsageController instance."""
    return UsageController(usage_repository, prompt_repository)


@pytest.fixture
def sample_usage():
    """Fixture to create a sample PromptUsage."""
    return MockPromptUsage(
        id=1,
        prompt_id=100,
        user_id="user123",
        context="chatbot",
        model="gpt-4",
        timestamp=datetime.now(),
        duration=2.5,
        token_count=150,
        cost=0.002,
        was_successful=True,
        response_quality=4,
        feedback="Good response, very helpful."
    )


class TestUsageController:
    """Test cases for the UsageController class."""
    
    def test_init(self, controller, usage_repository, prompt_repository):
        """Test initialization of the controller."""
        assert controller._usage_repository == usage_repository
        assert controller._prompt_repository == prompt_repository
        
    def test_record_usage(self, controller, usage_repository):
        """Test recording a new usage."""
        # Define test data
        prompt_id = 100
        user_id = "user123"
        context = "chatbot"
        model = "gpt-4"
        duration = 2.5
        token_count = 150
        cost = 0.002
        successful = True
        quality = 4
        feedback = "Good response, very helpful."
        
        # Set up signal handler to verify emission
        usage_recorded_emitted = False
        
        def on_usage_recorded(usage):
            nonlocal usage_recorded_emitted
            usage_recorded_emitted = True
            assert usage._prompt_id == prompt_id
            assert usage._user_id == user_id
            assert usage._context == context
            assert usage._model == model
            assert usage._duration == duration
            assert usage._token_count == token_count
            assert usage._cost == cost
            assert usage._was_successful == successful
            assert usage._response_quality == quality
            assert usage._feedback == feedback
            
        controller.usage_recorded.connect(on_usage_recorded)
        
        # Execute the method
        result = controller.record_usage(
            prompt_id=prompt_id,
            user_id=user_id,
            context=context,
            model=model,
            duration=duration,
            token_count=token_count,
            cost=cost,
            was_successful=successful,
            response_quality=quality,
            feedback=feedback
        )
        
        # Verify results
        assert result._prompt_id == prompt_id
        assert result._user_id == user_id
        assert result._context == context
        assert result._model == model
        assert result._duration == duration
        assert result._token_count == token_count
        assert result._cost == cost
        assert result._was_successful == successful
        assert result._response_quality == quality
        assert result._feedback == feedback
        
        # Verify the usage was saved to the repository
        assert len(usage_repository.usages) == 1
        assert usage_repository.usages[result._id] == result
        
        # Verify signal was emitted
        assert usage_recorded_emitted is True
        
    def test_record_usage_error(self, controller, usage_repository):
        """Test error handling when record_usage fails."""
        # Setup to cause error during record_usage
        usage_repository.error_on_save = True
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to save usage"):
            controller.record_usage(
                prompt_id=1,
                user_id="user123",
                context="test",
                model="gpt-4",
                token_count=100,
                was_successful=True
            )
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Failed to save usage" in error_message
        
    def test_record_minimal_usage(self, controller, usage_repository):
        """Test recording usage with only required fields."""
        # Set up signal handler to verify emission
        usage_recorded_emitted = False
        
        def on_usage_recorded(usage):
            nonlocal usage_recorded_emitted
            usage_recorded_emitted = True
            assert usage._prompt_id == 100
            assert usage._user_id == "user123"
            assert usage._context == "chatbot"
            
        controller.usage_recorded.connect(on_usage_recorded)
        
        # Execute the method
        result = controller.record_usage(
            prompt_id=100,
            user_id="user123",
            context="chatbot"
        )
        
        # Verify results
        assert result._prompt_id == 100
        assert result._user_id == "user123"
        assert result._context == "chatbot"
        assert usage_repository.save_called is True
        assert usage_recorded_emitted is True
        
    def test_record_batch_usage(self, controller, usage_repository):
        """Test recording multiple usage records in a batch."""
        # Define test data for multiple records
        usages = [
            {
                "prompt_id": 100,
                "user_id": "user123",
                "context": "chatbot",
                "model": "gpt-4"
            },
            {
                "prompt_id": 101,
                "user_id": "user456",
                "context": "assistant",
                "model": "gpt-3.5"
            },
            {
                "prompt_id": 102,
                "user_id": "user789",
                "context": "search",
                "model": "llama-2"
            }
        ]
        
        # Set up signal handler to verify emission
        batch_recorded_emitted = False
        
        def on_batch_recorded(count):
            nonlocal batch_recorded_emitted
            batch_recorded_emitted = True
            assert count == len(usages)
            
        controller.batch_recorded.connect(on_batch_recorded)
        
        # Execute the method
        results = controller.record_batch_usage(usages)
        
        # Verify results
        assert len(results) == len(usages)
        assert usage_repository.save_called is True
        assert batch_recorded_emitted is True
        
    def test_get_usage_by_prompt(self, controller, usage_repository, sample_usage):
        """Test retrieving usage records for a specific prompt."""
        # Add the sample usage to the repository
        usage_repository.usages[sample_usage._id] = sample_usage
        
        # Set up signal handler to verify emission
        usages_loaded_emitted = False
        
        def on_usages_loaded(usages):
            nonlocal usages_loaded_emitted
            usages_loaded_emitted = True
            assert len(usages) == 1
            assert usages[0]._id == sample_usage._id
            
        controller.usages_loaded.connect(on_usages_loaded)
        
        # Execute the method
        usages = controller.get_usage_by_prompt(sample_usage._prompt_id)
        
        # Verify results
        assert len(usages) == 1
        assert usages[0]._id == sample_usage._id
        assert usage_repository.get_by_prompt_id_called is True
        assert usages_loaded_emitted is True
        
    def test_get_usage_by_prompt_error(self, controller, usage_repository):
        """Test error handling when retrieving usage by prompt fails."""
        prompt_id = 100
        
        # Set repository to simulate an error
        usage_repository.error_on_get_by_prompt_id = True
        
        # Set up signal handler to verify emission
        error_emitted = False
        
        def on_error(message):
            nonlocal error_emitted
            error_emitted = True
            assert "Failed to get usage for prompt" in message
            
        controller.error.connect(on_error)
        
        # Execute the method and verify it raises an exception
        with pytest.raises(Exception, match="Failed to get usage for prompt"):
            controller.get_usage_by_prompt(prompt_id)
            
        assert error_emitted is True
        
    def test_get_usage_by_user(self, controller, usage_repository, sample_usage):
        """Test retrieving usage records for a specific user."""
        # Add the sample usage to the repository
        usage_repository.usages[sample_usage._id] = sample_usage
        
        # Set up signal handler to verify emission
        usages_loaded_emitted = False
        
        def on_usages_loaded(usages):
            nonlocal usages_loaded_emitted
            usages_loaded_emitted = True
            assert len(usages) == 1
            assert usages[0]._id == sample_usage._id
            
        controller.usages_loaded.connect(on_usages_loaded)
        
        # Execute the method
        usages = controller.get_usage_by_user(sample_usage._user_id)
        
        # Verify results
        assert len(usages) == 1
        assert usages[0]._id == sample_usage._id
        assert usage_repository.get_by_user_id_called is True
        assert usages_loaded_emitted is True
        
    def test_get_usage_by_date_range(self, controller, usage_repository):
        """Test retrieving usage records within a date range."""
        # Create usage records with different dates
        now = datetime.now()
        usages = []
        
        for i in range(5):
            usage = MockPromptUsage(
                id=i + 1,
                prompt_id=100,
                user_id="user123",
                timestamp=now - timedelta(days=i)
            )
            usage_repository.usages[usage._id] = usage
            usages.append(usage)
            
        # Define date range (last 3 days)
        start_date = now - timedelta(days=2)
        end_date = now
        
        # Set up signal handler to verify emission
        usages_loaded_emitted = False
        
        def on_usages_loaded(usages):
            nonlocal usages_loaded_emitted
            usages_loaded_emitted = True
            assert len(usages) == 3  # Should include records from today, yesterday and 2 days ago
            
        controller.usages_loaded.connect(on_usages_loaded)
        
        # Execute the method
        result = controller.get_usage_by_date_range(start_date, end_date)
        
        # Verify results
        assert len(result) == 3
        assert usage_repository.get_by_date_range_called is True
        assert usages_loaded_emitted is True
        
    def test_get_all_usage(self, controller, usage_repository, sample_usage):
        """Test retrieving all usage records."""
        # Add the sample usage to the repository
        usage_repository.usages[sample_usage._id] = sample_usage
        
        # Set up signal handler to verify emission
        all_usages_loaded_emitted = False
        
        def on_all_usages_loaded(usages):
            nonlocal all_usages_loaded_emitted
            all_usages_loaded_emitted = True
            assert len(usages) == 1
            assert usages[0]._id == sample_usage._id
            
        controller.all_usages_loaded.connect(on_all_usages_loaded)
        
        # Execute the method
        usages = controller.get_all_usage()
        
        # Verify results
        assert len(usages) == 1
        assert usages[0]._id == sample_usage._id
        assert usage_repository.get_all_called is True
        assert all_usages_loaded_emitted is True
        
    def test_calculate_usage_statistics(self, controller, usage_repository):
        """Test calculating usage statistics."""
        # Create multiple usage records
        for i in range(10):
            usage = MockPromptUsage(
                id=i + 1,
                prompt_id=100 if i < 7 else 101,  # 7 for prompt_id 100, 3 for prompt_id 101
                user_id="user123" if i < 5 else "user456",  # 5 for user123, 5 for user456
                context="chatbot" if i < 6 else "assistant",  # 6 for chatbot, 4 for assistant
                model="gpt-4" if i < 8 else "gpt-3.5",  # 8 for gpt-4, 2 for gpt-3.5
                timestamp=datetime.now() - timedelta(days=i % 5),
                duration=1.0 + i * 0.5,
                token_count=100 + i * 10,
                cost=0.001 + i * 0.0001,
                was_successful=i % 3 != 0  # 7 successful, 3 unsuccessful
            )
            usage_repository.usages[usage._id] = usage
            
        # Execute the method
        stats = controller.calculate_usage_statistics()
        
        # Verify results
        assert "total_count" in stats
        assert stats["total_count"] == 10
        assert "by_prompt" in stats
        assert len(stats["by_prompt"]) == 2
        assert stats["by_prompt"][100] == 7
        assert stats["by_prompt"][101] == 3
        assert "by_user" in stats
        assert len(stats["by_user"]) == 2
        assert stats["by_user"]["user123"] == 5
        assert stats["by_user"]["user456"] == 5
        assert "by_context" in stats
        assert len(stats["by_context"]) == 2
        assert stats["by_context"]["chatbot"] == 6
        assert stats["by_context"]["assistant"] == 4
        assert "by_model" in stats
        assert len(stats["by_model"]) == 2
        assert stats["by_model"]["gpt-4"] == 8
        assert stats["by_model"]["gpt-3.5"] == 2
        assert "by_day" in stats
        assert len(stats["by_day"]) == 5
        assert "success_rate" in stats
        assert stats["success_rate"] == 0.6  # 6 out of 10 successful (i % 3 != 0 means i = 1, 2, 4, 5, 7, 8)
        assert "avg_duration" in stats
        assert "avg_token_count" in stats
        assert "avg_cost" in stats
        assert "total_cost" in stats
        
    def test_get_usage_trends(self, controller, usage_repository):
        """Test retrieving usage trends over time."""
        # Create usage records over a period
        now = datetime.now()
        for i in range(30):
            day_offset = i // 3  # 3 records per day for 10 days
            usage = MockPromptUsage(
                id=i + 1,
                prompt_id=100,
                user_id="user123",
                context="chatbot",
                timestamp=now - timedelta(days=day_offset),
                duration=1.0 + (i % 5) * 0.5,
                token_count=100 + (i % 5) * 20,
                cost=0.001 + (i % 5) * 0.0002,
                was_successful=(i % 4) != 0  # 75% success rate
            )
            usage_repository.usages[usage._id] = usage
            
        # Execute the method
        trends = controller.get_usage_trends(days=10)
        
        # Verify results
        assert len(trends) == 11  # Should have data for 11 days (includes today)
        for day_data in trends:
            assert "date" in day_data
            assert "count" in day_data
            assert "success_rate" in day_data
            assert "avg_duration" in day_data
            assert "avg_tokens" in day_data
            assert "avg_cost" in day_data
            assert "total_cost" in day_data
            
    def test_get_prompt_performance(self, controller, usage_repository):
        """Test retrieving performance metrics for specific prompts."""
        # Create usage records for different prompts
        prompt_ids = [100, 101, 102]
        for i in range(30):
            prompt_index = i % len(prompt_ids)
            usage = MockPromptUsage(
                id=i + 1,
                prompt_id=prompt_ids[prompt_index],
                user_id=f"user{i % 5 + 1}",
                context="chatbot",
                timestamp=datetime.now() - timedelta(days=i % 10),
                duration=1.0 + (i % 5) * 0.5,
                token_count=100 + (i % 5) * 20,
                cost=0.001 + (i % 5) * 0.0002,
                was_successful=(i % (3 + prompt_index)) != 0,  # Different success rates
                response_quality=(i % 5) + 1  # 1-5 rating
            )
            usage_repository.usages[usage._id] = usage
            
        # Execute the method
        performance = controller.get_prompt_performance(prompt_ids)
        
        # Verify results
        assert len(performance) == len(prompt_ids)
        for prompt_id in prompt_ids:
            assert prompt_id in performance
            metrics = performance[prompt_id]
            assert "usage_count" in metrics
            assert "success_rate" in metrics
            assert "avg_response_quality" in metrics
            assert "avg_token_count" in metrics
            assert "avg_duration" in metrics
            assert "avg_cost" in metrics
            assert "total_cost" in metrics
            
    def test_get_model_comparison(self, controller, usage_repository):
        """Test comparing different model performance."""
        # Create usage records for different models
        models = ["gpt-4", "gpt-3.5", "llama-2"]
        for i in range(30):
            model_index = i % len(models)
            usage = MockPromptUsage(
                id=i + 1,
                prompt_id=100,
                user_id="user123",
                context="chatbot",
                model=models[model_index],
                timestamp=datetime.now() - timedelta(days=i % 5),
                duration=1.0 + model_index * 0.5 + (i % 3) * 0.2,
                token_count=100 + model_index * 30 + (i % 3) * 10,
                cost=(0.001 + model_index * 0.002) * (1 + (i % 3) * 0.1),
                was_successful=(i % (2 + model_index)) != 0,  # Different success rates
                response_quality=min(5, 3 + model_index + (i % 2))  # Different qualities
            )
            usage_repository.usages[usage._id] = usage
            
        # Execute the method
        comparison = controller.get_model_comparison()
        
        # Verify results
        assert len(comparison) == len(models)
        for model in models:
            assert model in comparison
            metrics = comparison[model]
            assert "usage_count" in metrics
            assert "success_rate" in metrics
            assert "avg_response_quality" in metrics
            assert "avg_token_count" in metrics
            assert "avg_duration" in metrics
            assert "avg_cost" in metrics
            assert "total_cost" in metrics
            
    def test_record_batch_usage_missing_fields(self, controller):
        """Test validation error when required fields are missing in batch usage."""
        # Setup test data with missing fields
        batch_data = [
            {
                # Missing prompt_id
                "user_id": "user123",
                "context": "test"
            },
            {
                "prompt_id": 100,
                # Missing user_id
                "context": "test"
            },
            {
                "prompt_id": 100,
                "user_id": "user123",
                # Missing context
            }
        ]
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Missing required fields"):
            controller.record_batch_usage(batch_data)
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Missing required fields" in error_message
    
    def test_get_usage_by_user_error(self, controller, usage_repository):
        """Test error handling when get_by_user_id fails."""
        # Setup
        usage_repository.error_on_get_by_user_id = True
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to get usage for user"):
            controller.get_usage_by_user("user123")
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Failed to get usage for user" in error_message
    
    def test_get_usage_by_date_range_error(self, controller, usage_repository):
        """Test error handling when get_by_date_range fails."""
        # Setup
        usage_repository.error_on_get_by_date_range = True
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to get usage by date range"):
            controller.get_usage_by_date_range(start_date, end_date)
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Failed to get usage by date range" in error_message
    
    def test_get_all_usage_error(self, controller, usage_repository):
        """Test error handling when get_all fails."""
        # Setup
        usage_repository.error_on_get_all = True
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
        
        controller.error.connect(on_error)
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to get all usage records"):
            controller.get_all_usage()
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Failed to get all usage records" in error_message
        
    def test_calculate_usage_statistics_with_empty_data(self, controller):
        """Test calculating statistics with empty usage list."""
        # Execute with empty list
        usages = []
        stats = controller.calculate_usage_statistics()
        
        # Verify results are a dictionary with all the expected values
        assert isinstance(stats, dict)
        assert stats["total_count"] == 0
        assert stats["success_count"] == 0
        assert stats["success_rate"] == 0
        assert stats["avg_duration"] == 0
        assert stats["avg_token_count"] == 0
        assert stats["avg_cost"] == 0
        assert isinstance(stats["by_prompt"], dict)
        assert isinstance(stats["by_user"], dict)
        assert isinstance(stats["by_context"], dict)
        assert isinstance(stats["by_model"], dict)
    
    def test_record_batch_usage_validation_error_propagation(self, controller, usage_repository):
        """Test that validation errors in batch operations are properly propagated."""
        # Setup test data with missing required field
        batch_data = [
            {
                "prompt_id": 1,
                "user_id": "user123",
                # Missing "context" field
                "model": "gpt-4",
                "was_successful": True,
            }
        ]
        
        # Register signal spy
        error_signal_received = False
        error_message = None
        
        def on_error(message):
            nonlocal error_signal_received, error_message
            error_signal_received = True
            error_message = message
            
        controller.error.connect(on_error)
        
        # Execute and verify
        with pytest.raises(Exception, match="Failed to save batch usage"):
            controller.record_batch_usage(batch_data)
            
        # Verify error signal was emitted
        assert error_signal_received
        assert "Missing required fields in usage record" in error_message
        
        # Verify no records were saved
        assert len(usage_repository.usages) == 0
    
    def test_get_usage_trends_with_empty_data(self, controller):
        """Test getting usage trends with empty data."""
        # Execute with empty data
        result = controller.get_usage_trends(days=7)
        
        # Verify
        assert isinstance(result, list)
        assert len(result) == 8  # Today + 7 days
        for day_data in result:
            assert "date" in day_data
            assert "count" in day_data
            assert day_data["count"] == 0 