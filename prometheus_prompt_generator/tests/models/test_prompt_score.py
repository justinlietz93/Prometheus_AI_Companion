"""
Unit tests for the PromptScore analytics model in the Prometheus AI Prompt Generator.

This module tests the PromptScore model's ability to track and analyze prompt usage metrics,
including record keeping, trend analysis, and comparative statistics.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from PySide6.QtSql import QSqlQuery

from prometheus_prompt_generator.tests.models.test_base import ModelTestBase
from prometheus_prompt_generator.domain.models import PromptScore, Prompt


class TestPromptScore(ModelTestBase):
    """Test case for the PromptScore class."""
    
    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        
        # Create a test prompt to work with
        self.prompt = Prompt()
        self.prompt.title = "Test Prompt for Analytics"
        self.prompt.content = "This is a test prompt for analytics testing."
        self.prompt.description = "A prompt used in analytics tests."
        self.prompt.category_id = 1
        self.prompt.save()
        
        # Create a PromptScore instance
        self.score = PromptScore(self.prompt.id)
        
        # Create usage logs
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
            
            # Delete score record
            query = QSqlQuery()
            query.prepare("DELETE FROM PromptScores WHERE prompt_id = ?")
            query.addBindValue(self.prompt.id)
            query.exec_()
            
            # Delete the prompt
            self.prompt.delete()
        
        super().tearDown()
    
    def _create_test_usage_logs(self):
        """Create test usage logs for the prompt."""
        # Create PromptScores record
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO PromptScores (
                prompt_id, usage_count, success_count, failure_count,
                total_tokens, total_cost, avg_satisfaction, last_used,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)
        
        now = datetime.now()
        query.addBindValue(self.prompt.id)
        query.addBindValue(10)  # usage_count
        query.addBindValue(8)   # success_count
        query.addBindValue(2)   # failure_count
        query.addBindValue(5000)  # total_tokens
        query.addBindValue(0.5)   # total_cost
        query.addBindValue(4.2)   # avg_satisfaction
        query.addBindValue(now.isoformat())  # last_used
        query.addBindValue(now.isoformat())  # created_at
        query.addBindValue(now.isoformat())  # updated_at
        
        query.exec_()
        
        # Create usage logs for the last 30 days
        query = QSqlQuery()
        for i in range(30):
            date = now - timedelta(days=i)
            
            # Add 1-2 logs per day
            logs_count = 1 + (i % 2)
            for j in range(logs_count):
                success = (i % 3 != 0) or (j == 0)  # Some failures
                tokens = 500 + (i * 10)
                cost = tokens * 0.0001
                satisfaction = 4.0 + (j * 0.5 / 5)  # Values between 4.0 and 5.0
                
                query.prepare("""
                    INSERT INTO PromptUsageLogs (
                        prompt_id, timestamp, success, tokens_used, cost, satisfaction
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """)
                
                query.addBindValue(self.prompt.id)
                query.addBindValue(date.isoformat())
                query.addBindValue(1 if success else 0)
                query.addBindValue(tokens)
                query.addBindValue(cost)
                query.addBindValue(satisfaction)
                
                query.exec_()
    
    def test_load_prompt_score(self):
        """Test loading an existing prompt score."""
        # The setup already creates a score record
        # Load it explicitly
        score = PromptScore(self.prompt.id)
        
        # Verify loaded data
        self.assertEqual(score.prompt_id, self.prompt.id)
        self.assertEqual(score.usage_count, 10)
        self.assertEqual(score.success_rate, 0.8)  # 8/10
        self.assertEqual(score.avg_tokens, 500)    # 5000/10
        self.assertEqual(score.avg_cost, 0.05)     # 0.5/10
        self.assertEqual(score.avg_satisfaction, 4.2)
    
    def test_new_prompt_score(self):
        """Test creating a score for a new prompt."""
        # Create a new prompt
        new_prompt = Prompt()
        new_prompt.title = "New Test Prompt"
        new_prompt.content = "Content for new test prompt"
        new_prompt.category_id = 1
        new_prompt.save()
        
        # Create a score for it
        score = PromptScore(new_prompt.id)
        
        # Should have default values
        self.assertEqual(score.prompt_id, new_prompt.id)
        self.assertEqual(score.usage_count, 0)
        self.assertEqual(score.success_rate, 0)
        self.assertEqual(score.avg_tokens, 0)
        self.assertEqual(score.avg_cost, 0)
        self.assertEqual(score.avg_satisfaction, 0)
        
        # Clean up
        new_prompt.delete()
    
    def test_record_usage_new(self):
        """Test recording usage for a new prompt."""
        # Create a new prompt
        new_prompt = Prompt()
        new_prompt.title = "Usage Test Prompt"
        new_prompt.content = "Content for usage test prompt"
        new_prompt.category_id = 1
        new_prompt.save()
        
        # Create a score for it
        score = PromptScore(new_prompt.id)
        
        # Record a successful usage
        result = score.record_usage(
            success=True,
            tokens_used=1000,
            cost=0.1,
            satisfaction=4.5
        )
        
        # Should succeed
        self.assertTrue(result)
        
        # Check updated metrics
        self.assertEqual(score.usage_count, 1)
        self.assertEqual(score.success_rate, 1.0)  # 100% success
        self.assertEqual(score.avg_tokens, 1000)
        self.assertEqual(score.avg_cost, 0.1)
        self.assertEqual(score.avg_satisfaction, 4.5)
        
        # Record another usage with failure
        score.record_usage(
            success=False,
            tokens_used=500,
            cost=0.05
        )
        
        # Check updated metrics
        self.assertEqual(score.usage_count, 2)
        self.assertEqual(score.success_rate, 0.5)  # 50% success
        self.assertEqual(score.avg_tokens, 750)    # Average of 1000 and 500
        self.assertEqual(score.avg_cost, 0.075)    # Average of 0.1 and 0.05
        self.assertEqual(score.avg_satisfaction, 4.5)  # Unchanged (no new rating)
        
        # Clean up
        new_prompt.delete()
    
    def test_record_usage_existing(self):
        """Test recording usage for an existing prompt with score."""
        # Start with initial values from setup
        initial_usage = self.score.usage_count
        initial_success = self.score.success_rate
        
        # Record a successful usage
        self.score.record_usage(
            success=True,
            tokens_used=1000,
            cost=0.1,
            satisfaction=5.0
        )
        
        # Check updated metrics
        self.assertEqual(self.score.usage_count, initial_usage + 1)
        
        # Reload to verify database persistence
        reloaded_score = PromptScore(self.prompt.id)
        self.assertEqual(reloaded_score.usage_count, initial_usage + 1)
    
    def test_get_monthly_usage(self):
        """Test getting usage count for a specific month."""
        # Get current date
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Get usage for current month
        monthly_usage = self.score.get_monthly_usage(current_year, current_month)
        
        # Should have data from our test logs
        self.assertGreater(monthly_usage, 0)
    
    def test_get_usage_trend(self):
        """Test getting usage trend data."""
        # Get trend for last 30 days
        trend_data = self.score.get_usage_trend(30)
        
        # Should have data points
        self.assertGreater(len(trend_data), 0)
        
        # Each data point should be (date, count) tuple
        first_point = trend_data[0]
        self.assertEqual(len(first_point), 2)
        
        # Get trend for last 7 days
        short_trend = self.score.get_usage_trend(7)
        
        # Should have fewer data points
        self.assertLessEqual(len(short_trend), 7)
    
    def test_get_success_trend(self):
        """Test getting success rate trend data."""
        # Get trend for last 30 days
        trend_data = self.score.get_success_trend(30)
        
        # Should have data points
        self.assertGreater(len(trend_data), 0)
        
        # Each data point should be (date, success_rate) tuple
        first_point = trend_data[0]
        self.assertEqual(len(first_point), 2)
        
        # Success rate should be between 0 and 1
        success_rate = first_point[1]
        self.assertTrue(0 <= success_rate <= 1)
    
    @patch('PySide6.QtSql.QSqlQuery')
    def test_get_comparative_rank(self, mock_query):
        """Test getting comparative rank information."""
        # Mock the query responses
        mock_instances = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_query.side_effect = mock_instances
        
        # Setup return values for the count query
        mock_instances[0].next.return_value = True
        mock_instances[0].value.return_value = 100  # Total 100 prompts
        
        # Setup for usage rank query
        mock_instances[1].exec_.return_value = True
        mock_instances[1].next.return_value = True
        mock_instances[1].value.return_value = 19  # 19 prompts have higher usage
        
        # Setup for success rate rank query
        mock_instances[2].exec_.return_value = True
        mock_instances[2].next.return_value = True
        mock_instances[2].value.return_value = 9  # 9 prompts have higher success rate
        
        # Setup for satisfaction rank query
        mock_instances[3].exec_.return_value = True
        mock_instances[3].next.return_value = True
        mock_instances[3].value.return_value = 4  # 4 prompts have higher satisfaction
        
        # Get the rank info
        with patch('prometheus_prompt_generator.domain.models.prompt_score.QSqlQuery', mock_query):
            rank_info = self.score.get_comparative_rank()
        
        # Check results
        self.assertEqual(rank_info['usage_rank'], 20)      # 19 + 1
        self.assertEqual(rank_info['success_rank'], 10)    # 9 + 1
        self.assertEqual(rank_info['satisfaction_rank'], 5)  # 4 + 1
        self.assertEqual(rank_info['percentile'], 81.0)    # (100 - 20 + 1)/100 * 100
    
    @patch('PySide6.QtSql.QSqlQuery')
    def test_get_top_prompts(self, mock_query):
        """Test getting top performing prompts."""
        # Mock the query response
        mock_instance = MagicMock()
        mock_query.return_value = mock_instance
        
        # Setup return values for the query execution
        mock_instance.exec_.return_value = True
        
        # Setup next() to return True twice then False (two prompts)
        mock_instance.next.side_effect = [True, True, False]
        
        # Setup values for the first prompt
        mock_instance.value.side_effect = [
            1, "Top Prompt 1", 50, 0.9, 4.8,  # First prompt data
            2, "Top Prompt 2", 40, 0.85, 4.7  # Second prompt data
        ]
        
        # Get top prompts
        with patch('prometheus_prompt_generator.domain.models.prompt_score.QSqlQuery', mock_query):
            top_prompts = PromptScore.get_top_prompts(limit=5, metric="usage")
        
        # Should have 2 prompts
        self.assertEqual(len(top_prompts), 2)
        
        # Check first prompt
        self.assertEqual(top_prompts[0]['prompt_id'], 1)
        self.assertEqual(top_prompts[0]['title'], "Top Prompt 1")
        self.assertEqual(top_prompts[0]['usage_count'], 50)
        self.assertEqual(top_prompts[0]['success_rate'], 0.9)
        self.assertEqual(top_prompts[0]['avg_satisfaction'], 4.8)


if __name__ == "__main__":
    unittest.main() 