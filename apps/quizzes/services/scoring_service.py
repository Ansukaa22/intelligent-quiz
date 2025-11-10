"""
Scoring service for quiz attempts
"""

from django.utils import timezone
from apps.quizzes.models import UserQuizAttempt, UserAnswer
import logging

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Service class for scoring quiz attempts
    """
    
    @staticmethod
    def submit_quiz(attempt):
        """
        Submit and score a quiz attempt
        
        Args:
            attempt: UserQuizAttempt object
        
        Returns:
            Dictionary with score results
        """
        try:
            # Mark as completed
            attempt.mark_completed()
            
            # Calculate score
            score = attempt.calculate_score()
            
            result = {
                'attempt_id': attempt.id,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': float(attempt.percentage),
                'passed': attempt.passed,
                'time_taken': attempt.time_taken,
                'correct_answers': attempt.score,
                'incorrect_answers': attempt.total_questions - attempt.score,
            }
            
            logger.info(f"Quiz submitted: {attempt.user.username} scored {attempt.score}/{attempt.total_questions}")
            return result
            
        except Exception as e:
            logger.error(f"Error submitting quiz: {str(e)}")
            raise
    
    @staticmethod
    def save_answer(attempt, question, selected_answer):
        """
        Save a user's answer for a question
        
        Args:
            attempt: UserQuizAttempt object
            question: Question object
            selected_answer: Selected option (A, B, C, or D)
        
        Returns:
            UserAnswer object
        """
        try:
            # Check if correct
            is_correct = (selected_answer == question.correct_answer)
            
            # Create or update answer
            answer, created = UserAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': is_correct
                }
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"Error saving answer: {str(e)}")
            raise
    
    @staticmethod
    def get_quiz_results(attempt):
        """
        Get detailed results for a quiz attempt
        
        Returns:
            Dictionary with detailed results
        """
        try:
            answers = attempt.answers.select_related('question').order_by('question__order')
            
            questions_data = []
            for answer in answers:
                question = answer.question
                questions_data.append({
                    'order': question.order,
                    'question_text': question.question_text,
                    'options': question.get_options(),
                    'selected_answer': answer.selected_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': answer.is_correct,
                    'explanation': question.explanation,
                })
            
            return {
                'attempt': attempt,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': float(attempt.percentage),
                'passed': attempt.passed,
                'time_taken': attempt.time_taken,
                'questions': questions_data,
            }
            
        except Exception as e:
            logger.error(f"Error getting quiz results: {str(e)}")
            raise
    
    @staticmethod
    def calculate_grade(percentage):
        """
        Calculate letter grade based on percentage
        
        Returns:
            Letter grade (A+, A, B+, etc.)
        """
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'A-'
        elif percentage >= 80:
            return 'B+'
        elif percentage >= 75:
            return 'B'
        elif percentage >= 70:
            return 'B-'
        elif percentage >= 65:
            return 'C+'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 55:
            return 'C-'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'


# Singleton instance
scoring_service = ScoringService()
