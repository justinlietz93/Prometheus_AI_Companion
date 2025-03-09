"""
Prometheus AI Prompt Generator - ScoringController

This module defines the ScoringController class, which handles scoring and evaluation
of prompts based on various metrics such as clarity, creativity, relevance, etc.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union

from PyQt6.QtCore import QObject, pyqtSignal

from prometheus_prompt_generator.domain.models.prompt_score import PromptScore


class ScoringController(QObject):
    """
    Controller for managing prompt scores and analytics.
    
    This class provides methods for scoring prompts (both manually and automatically),
    retrieving score history, and calculating various analytics metrics related to prompt
    quality and effectiveness.
    
    Signals:
        score_saved: Emitted when a score is successfully saved
        scores_loaded: Emitted when scores for a specific prompt are loaded
        all_scores_loaded: Emitted when all scores are loaded
        error: Emitted when an error occurs during scoring operations
    """
    
    # Define signals for notifying the UI of changes
    score_saved = pyqtSignal(object)  # Emitted when a score is saved
    scores_loaded = pyqtSignal(list)  # Emitted when scores for a prompt are loaded
    all_scores_loaded = pyqtSignal(list)  # Emitted when all scores are loaded
    error = pyqtSignal(str)  # Emitted when an error occurs
    
    # Standard scoring metrics
    METRICS = ["clarity", "creativity", "relevance", "specificity", "feasibility"]
    
    # Default weights for calculating overall score
    DEFAULT_WEIGHTS = {
        "clarity": 0.25,
        "creativity": 0.15,
        "relevance": 0.25,
        "specificity": 0.2,
        "feasibility": 0.15
    }
    
    def __init__(self, score_repository, prompt_repository):
        """
        Initialize the ScoringController.
        
        Args:
            score_repository: Repository for accessing and storing prompt scores
            prompt_repository: Repository for accessing prompts
        """
        super().__init__()
        self._score_repository = score_repository
        self._prompt_repository = prompt_repository
    
    def calculate_overall_score(self, metrics: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate an overall score from individual metrics.
        
        Args:
            metrics: Dictionary of metric names and their values (0-10 scale)
            weights: Optional dictionary of weights for each metric 
                     (defaults to standard weights if not provided)
                     
        Returns:
            The weighted average score as a float (0-10 scale)
        """
        # Use default weights if not provided
        if weights is None:
            weights = self.DEFAULT_WEIGHTS
            
        # Calculate weighted average
        total_weight = sum(weight for metric, weight in weights.items() if metric in metrics)
        weighted_sum = sum(
            metrics[metric] * weights[metric] 
            for metric in metrics if metric in weights
        )
        
        # Return weighted average (or 0 if no valid metrics)
        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0
    
    def score_prompt_manual(self, prompt_id: int, metrics: Dict[str, float], 
                           evaluator_id: Optional[str] = None, 
                           notes: Optional[str] = None) -> PromptScore:
        """
        Score a prompt manually with provided metrics.
        
        Args:
            prompt_id: ID of the prompt to score
            metrics: Dictionary of metric names and their scores (0-10 scale)
            evaluator_id: Optional ID of the user providing the evaluation
            notes: Optional notes about the evaluation
            
        Returns:
            The saved PromptScore object
            
        Raises:
            Exception: If saving the score fails
        """
        try:
            # Calculate overall score
            overall_score = self.calculate_overall_score(metrics)
            
            # Create and populate score object
            score = PromptScore()
            score._prompt_id = prompt_id
            
            # Set metrics
            for metric_name in self.METRICS:
                if metric_name in metrics:
                    setattr(score, f"_{metric_name}", metrics[metric_name])
            
            # Set additional properties
            score._overall_score = overall_score
            score._evaluation_method = "manual"
            score._timestamp = datetime.now()
            
            if evaluator_id:
                score._evaluator_id = evaluator_id
                
            if notes:
                score._notes = notes
                
            # Save to repository
            saved_score = self._score_repository.save(score)
            
            # Emit signal
            self.score_saved.emit(saved_score)
            
            return saved_score
            
        except Exception as e:
            error_msg = f"Failed to save score: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def score_prompt_auto(self, prompt_id: int) -> PromptScore:
        """
        Automatically score a prompt based on its content.
        
        Uses NLP techniques to evaluate prompt quality metrics.
        
        Args:
            prompt_id: ID of the prompt to score
            
        Returns:
            The saved PromptScore object
            
        Raises:
            ValueError: If prompt doesn't exist
            Exception: If scoring or saving fails
        """
        try:
            # Get the prompt
            prompt = self._prompt_repository.get_by_id(prompt_id)
            if not prompt:
                error_msg = f"Prompt not found: {prompt_id}"
                self.error.emit(error_msg)
                raise ValueError(error_msg)
                
            # Apply automatic scoring algorithms based on prompt content
            # This is a simplified implementation; in a real system this would
            # use more sophisticated NLP analysis
            content = prompt.content
            
            # Example metrics calculation (simplified for demonstration)
            metrics = self._calculate_automated_metrics(content)
            
            # Calculate overall score
            overall_score = self.calculate_overall_score(metrics)
            
            # Create and populate score object
            score = PromptScore()
            score._prompt_id = prompt_id
            
            # Set metrics
            for metric_name in self.METRICS:
                setattr(score, f"_{metric_name}", metrics[metric_name])
            
            # Set additional properties
            score._overall_score = overall_score
            score._evaluation_method = "auto"
            score._timestamp = datetime.now()
            score._notes = "Automated scoring"
                
            # Save to repository
            saved_score = self._score_repository.save(score)
            
            # Emit signal
            self.score_saved.emit(saved_score)
            
            return saved_score
            
        except ValueError:
            # Re-raise ValueError (prompt not found)
            raise
        except Exception as e:
            error_msg = f"Failed to automatically score prompt: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def _calculate_automated_metrics(self, content: str) -> Dict[str, float]:
        """
        Calculate metrics automatically based on prompt content.
        
        This is a simplified implementation. A real system would use
        more sophisticated NLP techniques.
        
        Args:
            content: The prompt content
            
        Returns:
            Dictionary of metric scores
        """
        # Simple scoring based on length, variety of words, etc.
        # This is just a placeholder implementation
        metrics = {}
        
        # Length-based clarity (longer prompts tend to be clearer)
        length = len(content)
        metrics["clarity"] = min(10, max(1, length / 50))
        
        # Word variety for creativity
        unique_words = len(set(content.lower().split()))
        metrics["creativity"] = min(10, max(1, unique_words / 15))
        
        # Presence of specific keywords for relevance
        keywords = ["specific", "clear", "detailed", "context", "example"]
        keyword_count = sum(1 for word in keywords if word in content.lower())
        metrics["relevance"] = min(10, max(1, 5 + keyword_count))
        
        # Number of sentences for specificity
        sentences = content.count(". ") + content.count("! ") + content.count("? ")
        metrics["specificity"] = min(10, max(1, sentences * 2))
        
        # Readability for feasibility
        avg_word_length = sum(len(word) for word in content.split()) / max(1, len(content.split()))
        metrics["feasibility"] = min(10, max(1, 10 - (avg_word_length - 5)))
        
        return metrics
    
    def get_scores_for_prompt(self, prompt_id: int) -> List[PromptScore]:
        """
        Get all scores for a specific prompt.
        
        Args:
            prompt_id: ID of the prompt to get scores for
            
        Returns:
            List of PromptScore objects
            
        Raises:
            Exception: If retrieving scores fails
        """
        try:
            scores = self._score_repository.get_by_prompt_id(prompt_id)
            self.scores_loaded.emit(scores)
            return scores
        except Exception as e:
            error_msg = f"Failed to get scores for prompt: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_all_scores(self) -> List[PromptScore]:
        """
        Get all scores in the system.
        
        Returns:
            List of all PromptScore objects
            
        Raises:
            Exception: If retrieving scores fails
        """
        try:
            scores = self._score_repository.get_all()
            self.all_scores_loaded.emit(scores)
            return scores
        except Exception as e:
            error_msg = f"Failed to get all scores: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def get_score_history(self, prompt_id: int) -> List[PromptScore]:
        """
        Get score history for a prompt ordered by timestamp.
        
        Args:
            prompt_id: ID of the prompt to get history for
            
        Returns:
            List of PromptScore objects ordered by timestamp (newest first)
        """
        try:
            scores = self.get_scores_for_prompt(prompt_id)
            # Sort by timestamp, newest first
            return sorted(scores, key=lambda s: s._timestamp, reverse=True)
        except Exception as e:
            error_msg = f"Failed to get score history: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def calculate_average_scores(self) -> Dict[int, Dict[str, float]]:
        """
        Calculate average scores for each prompt.
        
        Returns:
            Dictionary mapping prompt_id to a dictionary of average metric scores
        """
        try:
            result = {}
            all_scores = self.get_all_scores()
            
            # Group scores by prompt ID
            scores_by_prompt = {}
            for score in all_scores:
                if score._prompt_id not in scores_by_prompt:
                    scores_by_prompt[score._prompt_id] = []
                scores_by_prompt[score._prompt_id].append(score)
            
            # Calculate averages for each prompt
            for prompt_id, prompt_scores in scores_by_prompt.items():
                # Initialize metrics
                metric_sums = {metric: 0 for metric in self.METRICS}
                metric_sums["overall_score"] = 0
                
                # Sum all metrics
                for score in prompt_scores:
                    for metric in self.METRICS:
                        metric_sums[metric] += getattr(score, f"_{metric}", 0)
                    metric_sums["overall_score"] += score._overall_score
                
                # Calculate averages
                avg_count = len(prompt_scores)
                avg_metrics = {
                    metric: metric_sums[metric] / avg_count
                    for metric in metric_sums
                }
                
                # Store in result
                result[prompt_id] = avg_metrics
                
            return result
            
        except Exception as e:
            error_msg = f"Failed to calculate average scores: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg)
    
    def analyze_prompt_strengths_weaknesses(self, prompt_id: int) -> Dict[str, List[str]]:
        """
        Analyze a prompt's strengths and weaknesses based on its scores.
        
        Args:
            prompt_id: ID of the prompt to analyze
            
        Returns:
            Dictionary with 'strengths' and 'weaknesses' lists
        """
        try:
            # Get scores for the prompt
            scores = self.get_scores_for_prompt(prompt_id)
            if not scores:
                return {"strengths": [], "weaknesses": []}
            
            # Calculate average for each metric
            metric_sums = {metric: 0 for metric in self.METRICS}
            for score in scores:
                for metric in self.METRICS:
                    metric_sums[metric] += getattr(score, f"_{metric}", 0)
            
            avg_metrics = {
                metric: metric_sums[metric] / len(scores)
                for metric in metric_sums
            }
            
            # Calculate average of all metrics
            all_metrics_avg = sum(avg_metrics.values()) / len(avg_metrics)
            
            # Determine strengths and weaknesses
            strengths = [metric for metric, value in avg_metrics.items() 
                         if value > all_metrics_avg]
            weaknesses = [metric for metric, value in avg_metrics.items() 
                          if value < all_metrics_avg]
            
            # Sort by score (highest first for strengths, lowest first for weaknesses)
            strengths.sort(key=lambda m: avg_metrics[m], reverse=True)
            weaknesses.sort(key=lambda m: avg_metrics[m])
            
            return {
                "strengths": strengths,
                "weaknesses": weaknesses
            }
            
        except Exception as e:
            error_msg = f"Failed to analyze prompt strengths and weaknesses: {str(e)}"
            self.error.emit(error_msg)
            raise Exception(error_msg) 