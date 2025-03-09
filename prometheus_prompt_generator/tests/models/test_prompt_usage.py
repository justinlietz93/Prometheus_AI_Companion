"""
Unit tests for the PromptUsage analytics model in the Prometheus AI Prompt Generator.

This module tests the PromptUsage model's ability to track and analyze individual
prompt usage events, including detailed metrics and search capabilities.
"""

import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from PySide6.QtSql import QSqlQuery

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import PromptUsage, Prompt


class TestPromptUsage(ModelTestBase):
    """Test case for the PromptUsage class."""
    
    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        
        # Create a test prompt to work with
        self.prompt = Prompt()
        self.prompt.title = "Test Prompt for Usage"
        self.prompt.content = "This is a test prompt for usage testing."
        self.prompt.description = "A prompt used in usage tests."
        self.prompt.category_id = 1
        self.prompt.save()
        
        # Create test usage logs
        self._create_test_usage_logs()
    
    def tearDown(self):
        """Clean up after the test."""
        # Clean up test data
        if hasattr(self, 'prompt') and self.prompt.id is not None:
            # Delete usage logs first (foreign key constraint)
            query = QSqlQuery()
            query.prepare("DELETE FROM PromptUsageLogs WHERE prompt_id = ?")
            query.addBindValue(self.prompt.id)
            query.exec_()
            
            # Delete the prompt
            self.prompt.delete()
        
        super().tearDown()
    
    def _create_test_usage_logs(self):
        """Create test usage logs for the prompt."""
        # Create usage logs for the last 30 days
        now = datetime.now()
        
        # Create a table for PromptUsageLogs if it doesn't exist
        query = QSqlQuery()
        query.exec_("""
            CREATE TABLE IF NOT EXISTS PromptUsageLogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                user_id INTEGER,
                timestamp TEXT NOT NULL,
                success INTEGER NOT NULL,
                tokens_used INTEGER NOT NULL,
                cost REAL NOT NULL,
                satisfaction REAL,
                duration_ms INTEGER NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                context_length INTEGER NOT NULL,
                response_length INTEGER NOT NULL,
                parameters TEXT,
                error_message TEXT,
                tags TEXT,
                FOREIGN KEY (prompt_id) REFERENCES Prompts(id),
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)
        
        # Create 10 usage logs with different parameters
        for i in range(10):
            date = now - timedelta(days=i)
            success = i % 3 != 0  # Every third log is a failure
            tokens_used = 500 + (i * 50)
            cost = tokens_used * 0.0001
            satisfaction = 4.0 + (i * 0.1) if i < 5 else None  # Only half have satisfaction ratings
            duration_ms = 1000 + (i * 100)
            provider = "openai" if i % 2 == 0 else "anthropic"
            model = "gpt-4" if provider == "openai" else "claude-3"
            context_length = 200 + (i * 20)
            response_length = 300 + (i * 30)
            
            # Create parameters JSON
            parameters = {
                "temperature": 0.7 + (i * 0.02),
                "max_tokens": 1000 + (i * 100),
                "top_p": 0.9,
                "frequency_penalty": 0.5
            }
            
            # Create tags
            tags = ["test", "usage"]
            if i % 2 == 0:
                tags.append("even")
            else:
                tags.append("odd")
            
            # Add provider-specific tag
            tags.append(provider)
            
            # Error message for failures
            error_message = f"Test error {i}" if not success else ""
            
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO PromptUsageLogs (
                    prompt_id, user_id, timestamp, success, tokens_used,
                    cost, satisfaction, duration_ms, provider, model,
                    context_length, response_length, parameters, error_message, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
            
            query.addBindValue(self.prompt.id)
            query.addBindValue(1)  # User ID
            query.addBindValue(date.isoformat())
            query.addBindValue(1 if success else 0)
            query.addBindValue(tokens_used)
            query.addBindValue(cost)
            query.addBindValue(satisfaction)
            query.addBindValue(duration_ms)
            query.addBindValue(provider)
            query.addBindValue(model)
            query.addBindValue(context_length)
            query.addBindValue(response_length)
            query.addBindValue(json.dumps(parameters))
            query.addBindValue(error_message)
            query.addBindValue(json.dumps(tags))
            
            query.exec_()
    
    def test_load_usage_log(self):
        """Test loading an existing usage log."""
        # Get the ID of the first usage log
        query = QSqlQuery()
        query.prepare("SELECT id FROM PromptUsageLogs WHERE prompt_id = ? LIMIT 1")
        query.addBindValue(self.prompt.id)
        query.exec_()
        
        if not query.next():
            self.fail("No usage logs found for test prompt")
        
        usage_id = query.value(0)
        
        # Load the usage log
        usage = PromptUsage(usage_id)
        
        # Verify basic properties
        self.assertEqual(usage.id, usage_id)
        self.assertEqual(usage.prompt_id, self.prompt.id)
        self.assertEqual(usage.user_id, 1)
        self.assertIsNotNone(usage.timestamp)
        self.assertIsInstance(usage.success, bool)
        self.assertGreater(usage.tokens_used, 0)
        self.assertGreater(usage.cost, 0)
        self.assertIsInstance(usage.provider, str)
        self.assertIsInstance(usage.model, str)
        self.assertGreater(usage.context_length, 0)
        self.assertGreater(usage.response_length, 0)
        self.assertIsInstance(usage.parameters, dict)
        self.assertIsInstance(usage.tags, list)
    
    def test_create_usage_log(self):
        """Test creating a new usage log."""
        # Create a new usage log
        usage = PromptUsage()
        usage.prompt_id = self.prompt.id
        usage.user_id = 1
        usage.timestamp = datetime.now()
        usage.success = True
        usage.tokens_used = 1000
        usage.cost = 0.1
        usage.satisfaction = 4.5
        usage.duration_ms = 1500
        usage.provider = "openai"
        usage.model = "gpt-4"
        usage.context_length = 300
        usage.response_length = 700
        usage.parameters = {
            "temperature": 0.8,
            "max_tokens": 2000,
            "top_p": 0.95
        }
        usage.tags = ["test", "new", "openai"]
        
        # Save to database
        result = usage.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # ID should be set after save
        self.assertIsNotNone(usage.id)
        
        # Verify the usage log was saved to the database
        query = QSqlQuery()
        query.prepare("SELECT COUNT(*) FROM PromptUsageLogs WHERE id = ?")
        query.addBindValue(usage.id)
        query.exec_()
        query.next()
        self.assertEqual(query.value(0), 1)
    
    def test_update_usage_log(self):
        """Test updating an existing usage log."""
        # Get the ID of the first usage log
        query = QSqlQuery()
        query.prepare("SELECT id FROM PromptUsageLogs WHERE prompt_id = ? LIMIT 1")
        query.addBindValue(self.prompt.id)
        query.exec_()
        
        if not query.next():
            self.fail("No usage logs found for test prompt")
        
        usage_id = query.value(0)
        
        # Load the usage log
        usage = PromptUsage(usage_id)
        
        # Update fields
        original_tokens = usage.tokens_used
        usage.tokens_used = original_tokens + 500
        usage.satisfaction = 5.0
        usage.tags = usage.tags + ["updated"]
        
        # Save changes
        result = usage.save()
        
        # Should save successfully
        self.assertTrue(result)
        
        # Reload to verify changes
        updated_usage = PromptUsage(usage_id)
        self.assertEqual(updated_usage.tokens_used, original_tokens + 500)
        self.assertEqual(updated_usage.satisfaction, 5.0)
        self.assertIn("updated", updated_usage.tags)
    
    def test_delete_usage_log(self):
        """Test deleting a usage log."""
        # Create a new usage log to delete
        usage = PromptUsage()
        usage.prompt_id = self.prompt.id
        usage.user_id = 1
        usage.timestamp = datetime.now()
        usage.success = True
        usage.tokens_used = 1000
        usage.cost = 0.1
        usage.duration_ms = 1500
        usage.provider = "openai"
        usage.model = "gpt-4"
        usage.context_length = 300
        usage.response_length = 700
        usage.save()
        
        usage_id = usage.id
        
        # Delete it
        result = usage.delete()
        
        # Should delete successfully
        self.assertTrue(result)
        
        # ID should be None after deletion
        self.assertIsNone(usage.id)
        
        # Verify it's gone from database
        query = QSqlQuery()
        query.prepare("SELECT COUNT(*) FROM PromptUsageLogs WHERE id = ?")
        query.addBindValue(usage_id)
        query.exec_()
        query.next()
        self.assertEqual(query.value(0), 0)
    
    def test_get_usage_logs_for_prompt(self):
        """Test getting usage logs for a specific prompt."""
        # Get usage logs for our test prompt
        logs = PromptUsage.get_usage_logs_for_prompt(self.prompt.id)
        
        # Should have at least the logs we created in setup
        self.assertGreaterEqual(len(logs), 10)
        
        # Check structure of first log
        first_log = logs[0]
        self.assertIn('id', first_log)
        self.assertIn('timestamp', first_log)
        self.assertIn('success', first_log)
        self.assertIn('tokens_used', first_log)
        self.assertIn('cost', first_log)
        self.assertIn('provider', first_log)
        self.assertIn('model', first_log)
        
        # Test with limit
        limited_logs = PromptUsage.get_usage_logs_for_prompt(self.prompt.id, limit=5)
        self.assertEqual(len(limited_logs), 5)
        
        # Test with offset
        offset_logs = PromptUsage.get_usage_logs_for_prompt(self.prompt.id, offset=5)
        self.assertEqual(offset_logs[0]['id'], logs[5]['id'])
    
    def test_get_usage_logs_for_user(self):
        """Test getting usage logs for a specific user."""
        # Get usage logs for user ID 1
        logs = PromptUsage.get_usage_logs_for_user(1)
        
        # Should have at least the logs we created in setup
        self.assertGreaterEqual(len(logs), 10)
        
        # Check structure of first log
        first_log = logs[0]
        self.assertIn('id', first_log)
        self.assertIn('prompt_id', first_log)
        self.assertIn('prompt_title', first_log)
        self.assertIn('timestamp', first_log)
        self.assertIn('success', first_log)
        self.assertIn('tokens_used', first_log)
        self.assertIn('provider', first_log)
        self.assertIn('model', first_log)
    
    def test_search_usage_logs(self):
        """Test searching for usage logs based on various criteria."""
        # Search for logs with openai provider
        openai_logs = PromptUsage.search_usage_logs(provider="openai")
        
        # Should have some logs
        self.assertGreater(len(openai_logs), 0)
        
        # All should have openai provider
        for log in openai_logs:
            self.assertEqual(log['provider'], "openai")
        
        # Search for successful logs
        success_logs = PromptUsage.search_usage_logs(success=True)
        
        # Should have some logs
        self.assertGreater(len(success_logs), 0)
        
        # All should be successful
        for log in success_logs:
            self.assertTrue(log['success'])
        
        # Search for logs with specific tag
        tag_logs = PromptUsage.search_usage_logs(tags=["even"])
        
        # Should have some logs
        self.assertGreater(len(tag_logs), 0)
        
        # All should have the tag
        for log in tag_logs:
            self.assertIn("even", log['tags'])
        
        # Search with multiple criteria
        complex_logs = PromptUsage.search_usage_logs(
            provider="openai",
            success=True,
            tags=["test"]
        )
        
        # Should have some logs
        self.assertGreater(len(complex_logs), 0)
        
        # All should match criteria
        for log in complex_logs:
            self.assertEqual(log['provider'], "openai")
            self.assertTrue(log['success'])
            self.assertIn("test", log['tags'])
    
    def test_get_usage_statistics(self):
        """Test getting aggregated statistics for usage logs."""
        # Get statistics for all logs
        stats = PromptUsage.get_usage_statistics()
        
        # Should have at least the logs we created in setup
        self.assertGreaterEqual(stats['total_count'], 10)
        
        # Check structure of stats
        self.assertIn('total_count', stats)
        self.assertIn('success_count', stats)
        self.assertIn('failure_count', stats)
        self.assertIn('success_rate', stats)
        self.assertIn('total_tokens', stats)
        self.assertIn('total_cost', stats)
        self.assertIn('avg_tokens', stats)
        self.assertIn('avg_cost', stats)
        self.assertIn('avg_satisfaction', stats)
        self.assertIn('avg_duration_ms', stats)
        self.assertIn('first_usage', stats)
        self.assertIn('last_usage', stats)
        
        # Get statistics for openai provider
        openai_stats = PromptUsage.get_usage_statistics(provider="openai")
        
        # Should have fewer logs than total
        self.assertLess(openai_stats['total_count'], stats['total_count'])
        
        # Get statistics for successful logs
        success_stats = PromptUsage.get_usage_statistics(success=True)
        
        # Success rate should be 1.0
        self.assertEqual(success_stats['success_rate'], 1.0)
        
        # Get statistics for date range
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        recent_stats = PromptUsage.get_usage_statistics(
            start_date=week_ago,
            end_date=now
        )
        
        # Should have fewer logs than total
        self.assertLessEqual(recent_stats['total_count'], stats['total_count'])


if __name__ == "__main__":
    unittest.main() 