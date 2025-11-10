"""
Quiz service for handling quiz creation and management
"""

from django.db import transaction
from django.utils.text import slugify
from apps.quizzes.models import Quiz, Question, Category, Subcategory
from apps.quizzes.services.ai_service import ai_generator
import logging

logger = logging.getLogger(__name__)


class QuizService:
    """
    Service class for quiz operations
    """
    
    @staticmethod
    def create_quiz_with_questions(user, category_slug, subcategory_slug=None, 
                                   difficulty='medium', num_questions=10):
        """
        Create a new quiz with AI-generated questions
        
        Args:
            user: User creating the quiz
            category_slug: Category slug
            subcategory_slug: Subcategory slug (optional)
            difficulty: Difficulty level
            num_questions: Number of questions
        
        Returns:
            Quiz object with questions
        """
        try:
            # Get category
            category = Category.objects.get(slug=category_slug, is_active=True)
            
            # Get subcategory if provided
            subcategory = None
            subcategory_name = None
            if subcategory_slug:
                subcategory = Subcategory.objects.get(
                    slug=subcategory_slug, 
                    category=category, 
                    is_active=True
                )
                subcategory_name = subcategory.name
            
            # Generate questions using AI
            logger.info(f"Generating {num_questions} questions for {category.name}/{subcategory_name}")
            ai_questions = ai_generator.generate_questions(
                category=category.name,
                subcategory=subcategory_name,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            if not ai_questions:
                raise Exception("No questions were generated")
            
            # Create quiz and questions in a transaction
            with transaction.atomic():
                # Create quiz
                quiz_title = f"{category.name}"
                if subcategory:
                    quiz_title += f" - {subcategory.name}"
                quiz_title += f" ({difficulty.capitalize()})"
                
                quiz = Quiz.objects.create(
                    title=quiz_title,
                    category=category,
                    subcategory=subcategory,
                    difficulty=difficulty,
                    created_by=user,
                    time_limit=QuizService._calculate_time_limit(num_questions, difficulty),
                    pass_percentage=QuizService._calculate_pass_percentage(difficulty),
                )
                
                # Create questions
                for idx, q_data in enumerate(ai_questions, start=1):
                    Question.objects.create(
                        quiz=quiz,
                        question_text=q_data['question'],
                        option_a=q_data['options']['A'],
                        option_b=q_data['options']['B'],
                        option_c=q_data['options']['C'],
                        option_d=q_data['options']['D'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        order=idx
                    )
                
                logger.info(f"Created quiz '{quiz.title}' with {len(ai_questions)} questions")
                return quiz
                
        except Category.DoesNotExist:
            raise Exception(f"Category '{category_slug}' not found")
        except Subcategory.DoesNotExist:
            raise Exception(f"Subcategory '{subcategory_slug}' not found")
        except Exception as e:
            logger.error(f"Error creating quiz: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_time_limit(num_questions, difficulty):
        """
        Calculate time limit based on number of questions and difficulty
        
        Returns:
            Time limit in seconds
        """
        base_time_per_question = {
            'easy': 30,    # 30 seconds per question
            'medium': 45,  # 45 seconds per question
            'hard': 60,    # 60 seconds per question
        }
        
        seconds_per_q = base_time_per_question.get(difficulty, 45)
        return num_questions * seconds_per_q
    
    @staticmethod
    def _calculate_pass_percentage(difficulty):
        """
        Calculate pass percentage based on difficulty
        
        Returns:
            Pass percentage (0-100)
        """
        pass_percentages = {
            'easy': 60,
            'medium': 70,
            'hard': 75,
        }
        
        return pass_percentages.get(difficulty, 70)
    
    @staticmethod
    def get_or_create_quiz(user, category_slug, subcategory_slug=None,
                           difficulty='medium', num_questions=10):
        """
        Get existing quiz or create new one
        
        This checks if a quiz with the same parameters exists
        to avoid regenerating questions unnecessarily
        """
        try:
            category = Category.objects.get(slug=category_slug)
            subcategory = None
            
            if subcategory_slug:
                subcategory = Subcategory.objects.get(slug=subcategory_slug, category=category)
            
            # Try to find existing quiz with same parameters
            quiz = Quiz.objects.filter(
                category=category,
                subcategory=subcategory,
                difficulty=difficulty,
                is_active=True
            ).first()
            
            # Check if it has the right number of questions
            if quiz and quiz.total_questions == num_questions:
                logger.info(f"Using existing quiz: {quiz.title}")
                return quiz
            
            # Create new quiz
            return QuizService.create_quiz_with_questions(
                user, category_slug, subcategory_slug, difficulty, num_questions
            )
            
        except Exception as e:
            logger.error(f"Error in get_or_create_quiz: {str(e)}")
            raise


# Singleton instance
quiz_service = QuizService()
