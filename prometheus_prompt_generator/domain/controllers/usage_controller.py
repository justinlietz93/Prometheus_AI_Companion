"""
Prometheus AI Prompt Generator - UsageController

This module defines the UsageController class, which handles tracking and analyzing
prompt usage patterns in the system.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict

from PyQt6.QtCore import QObject, pyqtSignal

from prometheus_prompt_generator.domain.models.prompt_usage import PromptUsage


class UsageController(QObject):
    """
    Controller for managing prompt usage tracking and analytics.
    
    This class provides methods for recording prompt usage events, retrieving
    usage data, and calculating various usage statistics and trends to help
    analyze prompt effectiveness and user behavior.
    
    Signals:
        usage_recorded: Emitted when a usage record is successfully saved
        batch_recorded: Emitted when a batch of usage records is saved
        usages_loaded: Emitted when usage records are loaded
        all_usages_loaded: Emitted when all usage records are loaded
        error: Emitted when an error occurs during usage operations
    """
    
    # Define signals for notifying the UI of changes
    usage_recorded = pyqtSignal(object)  # Emitted when a usage is recorded
    batch_recorded = pyqtSignal(int)  # Emitted when a batch is recorded (passes count)
    usages_loaded = pyqtSignal(list)  # Emitted when usages are loaded
    all_usages_loaded = pyqtSignal(list)  # Emitted when all usages are loaded
    error = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, usage_repository, prompt_repository):
        """
        Initialize the UsageController.
        
        Args:
            usage_repository: Repository for accessing and storing prompt usage records
            prompt_repository: Repository for accessing prompts
        """
        super().__init__()
        self._usage_repository = usage_repository
        self._prompt_repository = prompt_repository
    
    def record_usage(self, prompt_id: int, user_id: str, context: str, 
                     model: Optional[str] = None, duration: Optional[float] = None,
                     token_count: Optional[int] = None, cost: Optional[float] = None,
                     was_successful: Optional[bool] = None, 
                     response_quality: Optional[int] = None,
                     feedback: Optional[str] = None) -> PromptUsage:
        """
        Record a new prompt usage event.
        
        Args:
            prompt_id: ID of the prompt used
            user_id: ID of the user who used the prompt
            context: Context in which the prompt was used (e.g., "chatbot", "assistant")
            model: Optional model name used for generation
            duration: Optional duration in seconds for the operation
            token_count: Optional number of tokens used
            cost: Optional cost of the operation
            was_successful: Optional flag indicating if the prompt was successful
            response_quality: Optional quality rating (1-5 scale)
            feedback: Optional feedback text
            
        Returns:
            The saved PromptUsage object
            
        Raises:
            Exception: If saving the usage record fails
        """
        try:
            # Create and populate usage object
            usage = PromptUsage()
            usage._prompt_id = prompt_id
            usage._user_id = user_id
            usage._context = context
            usage._timestamp = datetime.now()
            
            # Set optional properties if provided
            if model is not None:
                usage._model = model
            
            if duration is not None:
                usage._duration = duration
                
            if token_count is not None:
                usage._token_count = token_count
                
            if cost is not None:
                usage._cost = cost
                
            if was_successful is not None:
                usage._was_successful = was_successful
                
            if response_quality is not None:
                usage._response_quality = response_quality
                
            if feedback is not None:
                usage._feedback = feedback
                
            # Save to repository
            saved_usage = self._usage_repository.save(usage)
            
            # Emit signal
            self.usage_recorded.emit(saved_usage)
            
            return saved_usage
            
        except Exception as e:
            error_msg = f"Failed to save usage: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def record_batch_usage(self, usage_records: List[Dict[str, Any]]) -> List[PromptUsage]:
        """
        Record multiple usage records in a batch.
        
        Args:
            usage_records: List of dictionaries containing usage data
            
        Returns:
            List of saved PromptUsage objects
            
        Raises:
            Exception: If saving the batch fails
        """
        try:
            saved_records = []
            
            for record in usage_records:
                # Extract required fields
                prompt_id = record.get("prompt_id")
                user_id = record.get("user_id")
                context = record.get("context")
                
                # Validate required fields
                if not all([prompt_id, user_id, context]):
                    raise ValueError("Missing required fields in usage record")
                    
                # Extract optional fields
                model = record.get("model")
                duration = record.get("duration")
                token_count = record.get("token_count")
                cost = record.get("cost")
                was_successful = record.get("was_successful")
                response_quality = record.get("response_quality")
                feedback = record.get("feedback")
                
                # Record the usage
                usage = self.record_usage(
                    prompt_id=prompt_id,
                    user_id=user_id,
                    context=context,
                    model=model,
                    duration=duration,
                    token_count=token_count,
                    cost=cost,
                    was_successful=was_successful,
                    response_quality=response_quality,
                    feedback=feedback
                )
                
                saved_records.append(usage)
                
            # Emit batch recorded signal
            self.batch_recorded.emit(len(saved_records))
            
            return saved_records
            
        except Exception as e:
            error_msg = f"Failed to save batch usage: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_usage_by_prompt(self, prompt_id: int) -> List[PromptUsage]:
        """
        Get all usage records for a specific prompt.
        
        Args:
            prompt_id: ID of the prompt to get usage for
            
        Returns:
            List of PromptUsage objects
            
        Raises:
            Exception: If retrieving usage fails
        """
        try:
            usages = self._usage_repository.get_by_prompt_id(prompt_id)
            self.usages_loaded.emit(usages)
            return usages
        except Exception as e:
            error_msg = f"Failed to get usage for prompt: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_usage_by_user(self, user_id: str) -> List[PromptUsage]:
        """
        Get all usage records for a specific user.
        
        Args:
            user_id: ID of the user to get usage for
            
        Returns:
            List of PromptUsage objects
            
        Raises:
            Exception: If retrieving usage fails
        """
        try:
            usages = self._usage_repository.get_by_user_id(user_id)
            self.usages_loaded.emit(usages)
            return usages
        except Exception as e:
            error_msg = f"Failed to get usage for user: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_usage_by_date_range(self, start_date: datetime, end_date: datetime) -> List[PromptUsage]:
        """
        Get all usage records within a date range.
        
        Args:
            start_date: Start date for the range (inclusive)
            end_date: End date for the range (inclusive)
            
        Returns:
            List of PromptUsage objects
            
        Raises:
            Exception: If retrieving usage fails
        """
        try:
            usages = self._usage_repository.get_by_date_range(start_date, end_date)
            self.usages_loaded.emit(usages)
            return usages
        except Exception as e:
            error_msg = f"Failed to get usage by date range: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_all_usage(self) -> List[PromptUsage]:
        """
        Get all usage records.
        
        Returns:
            List of all PromptUsage objects
            
        Raises:
            Exception: If retrieving usage fails
        """
        try:
            usages = self._usage_repository.get_all()
            self.all_usages_loaded.emit(usages)
            return usages
        except Exception as e:
            error_msg = f"Failed to get all usage records: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def calculate_usage_statistics(self) -> Dict[str, Any]:
        """
        Calculate usage statistics across all recorded usage.
        
        Returns:
            Dictionary containing various statistics
        """
        try:
            # Get all usage records
            all_usages = self.get_all_usage()
            
            # Initialize result dictionary
            result = {
                "total_count": len(all_usages),
                "by_prompt": defaultdict(int),
                "by_user": defaultdict(int),
                "by_context": defaultdict(int),
                "by_model": defaultdict(int),
                "by_day": defaultdict(int),
                "success_count": 0,
                "total_duration": 0.0,
                "total_tokens": 0,
                "total_cost": 0.0
            }
            
            # Calculate statistics
            for usage in all_usages:
                # Count by prompt
                result["by_prompt"][usage._prompt_id] += 1
                
                # Count by user
                result["by_user"][usage._user_id] += 1
                
                # Count by context
                if hasattr(usage, "_context"):
                    result["by_context"][usage._context] += 1
                
                # Count by model
                if hasattr(usage, "_model") and usage._model:
                    result["by_model"][usage._model] += 1
                
                # Count by day
                if hasattr(usage, "_timestamp") and usage._timestamp:
                    day_key = usage._timestamp.date().isoformat()
                    result["by_day"][day_key] += 1
                
                # Count successful operations
                if hasattr(usage, "_was_successful") and usage._was_successful:
                    result["success_count"] += 1
                
                # Sum duration
                if hasattr(usage, "_duration") and usage._duration:
                    result["total_duration"] += usage._duration
                
                # Sum tokens
                if hasattr(usage, "_token_count") and usage._token_count:
                    result["total_tokens"] += usage._token_count
                
                # Sum cost
                if hasattr(usage, "_cost") and usage._cost:
                    result["total_cost"] += usage._cost
            
            # Calculate derived metrics
            if result["total_count"] > 0:
                result["success_rate"] = result["success_count"] / result["total_count"]
                result["avg_duration"] = result["total_duration"] / result["total_count"]
                result["avg_token_count"] = result["total_tokens"] / result["total_count"]
                result["avg_cost"] = result["total_cost"] / result["total_count"]
            else:
                result["success_rate"] = 0
                result["avg_duration"] = 0
                result["avg_token_count"] = 0
                result["avg_cost"] = 0
            
            # Convert defaultdicts to regular dicts for easier serialization
            result["by_prompt"] = dict(result["by_prompt"])
            result["by_user"] = dict(result["by_user"])
            result["by_context"] = dict(result["by_context"])
            result["by_model"] = dict(result["by_model"])
            result["by_day"] = dict(result["by_day"])
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate usage statistics: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_usage_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get usage trends over a specified number of days.
        
        Args:
            days: Number of days to include in trends
            
        Returns:
            List of dictionaries with daily stats
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get usage records in the date range
            usages = self.get_usage_by_date_range(start_date, end_date)
            
            # Group by day
            daily_data = defaultdict(list)
            for usage in usages:
                if usage._timestamp:
                    day_key = usage._timestamp.date().isoformat()
                    daily_data[day_key].append(usage)
            
            # Generate a list of all dates in the range
            all_dates = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                all_dates.append(current_date.isoformat())
                current_date += timedelta(days=1)
            
            # Calculate daily metrics
            result = []
            for date_str in all_dates:
                day_usages = daily_data.get(date_str, [])
                
                # Calculate metrics for this day
                day_metrics = {
                    "date": date_str,
                    "count": len(day_usages),
                    "success_count": sum(1 for u in day_usages if hasattr(u, "_was_successful") and u._was_successful),
                    "total_duration": sum(u._duration for u in day_usages if hasattr(u, "_duration") and u._duration),
                    "total_tokens": sum(u._token_count for u in day_usages if hasattr(u, "_token_count") and u._token_count),
                    "total_cost": sum(u._cost for u in day_usages if hasattr(u, "_cost") and u._cost)
                }
                
                # Calculate derived metrics
                if day_metrics["count"] > 0:
                    day_metrics["success_rate"] = day_metrics["success_count"] / day_metrics["count"]
                    day_metrics["avg_duration"] = day_metrics["total_duration"] / day_metrics["count"]
                    day_metrics["avg_tokens"] = day_metrics["total_tokens"] / day_metrics["count"]
                    day_metrics["avg_cost"] = day_metrics["total_cost"] / day_metrics["count"]
                else:
                    day_metrics["success_rate"] = 0
                    day_metrics["avg_duration"] = 0
                    day_metrics["avg_tokens"] = 0
                    day_metrics["avg_cost"] = 0
                
                result.append(day_metrics)
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate usage trends: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_prompt_performance(self, prompt_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get performance metrics for specific prompts.
        
        Args:
            prompt_ids: List of prompt IDs to analyze
            
        Returns:
            Dictionary mapping prompt_id to performance metrics
        """
        try:
            result = {}
            
            # Process each prompt
            for prompt_id in prompt_ids:
                # Get usage records for this prompt
                prompt_usages = self.get_usage_by_prompt(prompt_id)
                
                # Skip if no usage records
                if not prompt_usages:
                    result[prompt_id] = {
                        "usage_count": 0,
                        "success_rate": 0,
                        "avg_response_quality": 0,
                        "avg_token_count": 0,
                        "avg_duration": 0,
                        "avg_cost": 0,
                        "total_cost": 0
                    }
                    continue
                
                # Calculate metrics
                success_count = sum(1 for u in prompt_usages if hasattr(u, "_was_successful") and u._was_successful)
                total_quality = sum(u._response_quality for u in prompt_usages if hasattr(u, "_response_quality") and u._response_quality)
                quality_count = sum(1 for u in prompt_usages if hasattr(u, "_response_quality") and u._response_quality)
                total_tokens = sum(u._token_count for u in prompt_usages if hasattr(u, "_token_count") and u._token_count)
                total_duration = sum(u._duration for u in prompt_usages if hasattr(u, "_duration") and u._duration)
                total_cost = sum(u._cost for u in prompt_usages if hasattr(u, "_cost") and u._cost)
                
                # Store metrics
                metrics = {
                    "usage_count": len(prompt_usages),
                    "success_rate": success_count / len(prompt_usages) if prompt_usages else 0,
                    "avg_response_quality": total_quality / quality_count if quality_count else 0,
                    "avg_token_count": total_tokens / len(prompt_usages) if prompt_usages else 0,
                    "avg_duration": total_duration / len(prompt_usages) if prompt_usages else 0,
                    "avg_cost": total_cost / len(prompt_usages) if prompt_usages else 0,
                    "total_cost": total_cost
                }
                
                result[prompt_id] = metrics
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate prompt performance: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_model_comparison(self) -> Dict[str, Dict[str, Any]]:
        """
        Compare performance metrics across different LLM models.
        
        Returns:
            Dictionary mapping model name to performance metrics
        """
        try:
            # Get all usage records
            all_usages = self.get_all_usage()
            
            # Group by model
            model_data = defaultdict(list)
            for usage in all_usages:
                if hasattr(usage, "_model") and usage._model:
                    model_data[usage._model].append(usage)
            
            # Calculate metrics for each model
            result = {}
            for model, usages in model_data.items():
                # Skip if no usage records
                if not usages:
                    continue
                
                # Calculate metrics
                success_count = sum(1 for u in usages if hasattr(u, "_was_successful") and u._was_successful)
                total_quality = sum(u._response_quality for u in usages if hasattr(u, "_response_quality") and u._response_quality)
                quality_count = sum(1 for u in usages if hasattr(u, "_response_quality") and u._response_quality)
                total_tokens = sum(u._token_count for u in usages if hasattr(u, "_token_count") and u._token_count)
                total_duration = sum(u._duration for u in usages if hasattr(u, "_duration") and u._duration)
                total_cost = sum(u._cost for u in usages if hasattr(u, "_cost") and u._cost)
                
                # Store metrics
                metrics = {
                    "usage_count": len(usages),
                    "success_rate": success_count / len(usages) if usages else 0,
                    "avg_response_quality": total_quality / quality_count if quality_count else 0,
                    "avg_token_count": total_tokens / len(usages) if usages else 0,
                    "avg_duration": total_duration / len(usages) if usages else 0,
                    "avg_cost": total_cost / len(usages) if usages else 0,
                    "total_cost": total_cost
                }
                
                result[model] = metrics
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate model comparison: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_user_activity(self) -> Dict[str, Dict[str, Any]]:
        """
        Get activity statistics for all users.
        
        Returns:
            Dictionary mapping user_id to activity metrics
        """
        try:
            # Get all usage records
            all_usages = self.get_all_usage()
            
            # Group by user
            user_data = defaultdict(list)
            for usage in all_usages:
                if usage._user_id:
                    user_data[usage._user_id].append(usage)
            
            # Calculate metrics for each user
            result = {}
            for user_id, usages in user_data.items():
                # Skip if no usage records
                if not usages:
                    continue
                
                # Calculate timestamps
                timestamps = [u._timestamp for u in usages if hasattr(u, "_timestamp") and u._timestamp]
                first_activity = min(timestamps) if timestamps else None
                last_activity = max(timestamps) if timestamps else None
                
                # Calculate prompts used
                prompts_used = set(u._prompt_id for u in usages if hasattr(u, "_prompt_id") and u._prompt_id)
                
                # Calculate models used
                models_used = defaultdict(int)
                for u in usages:
                    if hasattr(u, "_model") and u._model:
                        models_used[u._model] += 1
                
                # Calculate contexts
                contexts = defaultdict(int)
                for u in usages:
                    if hasattr(u, "_context") and u._context:
                        contexts[u._context] += 1
                
                # Calculate metrics
                success_count = sum(1 for u in usages if hasattr(u, "_was_successful") and u._was_successful)
                total_cost = sum(u._cost for u in usages if hasattr(u, "_cost") and u._cost)
                
                # Store metrics
                metrics = {
                    "usage_count": len(usages),
                    "first_activity": first_activity.isoformat() if first_activity else None,
                    "last_activity": last_activity.isoformat() if last_activity else None,
                    "prompts_used": list(prompts_used),
                    "models_used": dict(models_used),
                    "success_rate": success_count / len(usages) if usages else 0,
                    "contexts": dict(contexts),
                    "total_cost": total_cost
                }
                
                result[user_id] = metrics
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate user activity: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg) 