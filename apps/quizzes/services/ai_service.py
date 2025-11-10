"""
AI Service for generating quiz questions using OpenAI GPT-3.5 Turbo
"""

from openai import OpenAI
import json
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class AIQuestionGenerator:
    """
    Service class for generating quiz questions using AI
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    def generate_questions(self, category, subcategory, difficulty, num_questions=10):
        """
        Generate quiz questions based on parameters
        
        Args:
            category (str): Quiz category
            subcategory (str): Quiz subcategory
            difficulty (str): Difficulty level (easy, medium, hard)
            num_questions (int): Number of questions to generate
        
        Returns:
            list: List of question dictionaries
        """
        # Check cache first
        cache_key = f"quiz_questions_{category}_{subcategory}_{difficulty}_{num_questions}"
        cached_questions = cache.get(cache_key)
        
        if cached_questions:
            logger.info(f"Retrieved {num_questions} questions from cache")
            return cached_questions
        
        # Generate prompt
        prompt = self._create_prompt(category, subcategory, difficulty, num_questions)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert quiz question generator. Generate high-quality, accurate multiple-choice questions in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            questions = self._parse_questions(content)
            
            # Cache the questions
            cache.set(cache_key, questions, settings.QUIZ_QUESTIONS_CACHE_TIMEOUT)
            
            logger.info(f"Generated {len(questions)} questions using AI")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise Exception(f"Failed to generate questions: {str(e)}")
    
    def _create_prompt(self, category, subcategory, difficulty, num_questions):
        """
        Create prompt for AI question generation
        """
        difficulty_desc = {
            'easy': 'basic and straightforward',
            'medium': 'moderate complexity requiring some knowledge',
            'hard': 'advanced and challenging'
        }
        
        prompt = f"""Generate {num_questions} multiple-choice quiz questions about {subcategory or category}.

Requirements:
- Difficulty level: {difficulty} ({difficulty_desc.get(difficulty, '')})
- Each question must have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Include a brief explanation for the correct answer
- Questions should be clear, unambiguous, and educational
- Avoid trick questions or overly obscure topics

Return ONLY a JSON array in this exact format:
[
    {{
        "question": "What is the primary purpose of Python's 'self' parameter?",
        "options": {{
            "A": "To refer to the class itself",
            "B": "To refer to the instance of the class",
            "C": "To create a new object",
            "D": "To delete an instance"
        }},
        "correct_answer": "B",
        "explanation": "The 'self' parameter refers to the instance of the class and is used to access instance variables and methods."
    }}
]

Generate {num_questions} questions now:"""
        
        return prompt
    
    def _parse_questions(self, content):
        """
        Parse AI response into question format
        """
        try:
            # Try to find JSON in the content
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                questions = json.loads(json_str)
                
                # Validate structure
                validated_questions = []
                for q in questions:
                    if self._validate_question(q):
                        validated_questions.append(q)
                
                return validated_questions
            else:
                raise ValueError("No JSON array found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Failed to parse questions: {str(e)}")
    
    def _validate_question(self, question):
        """
        Validate question structure
        """
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        
        # Check required fields
        if not all(field in question for field in required_fields):
            return False
        
        # Check options
        options = question.get('options', {})
        if not all(key in options for key in ['A', 'B', 'C', 'D']):
            return False
        
        # Check correct answer
        if question.get('correct_answer') not in ['A', 'B', 'C', 'D']:
            return False
        
        return True
    
    def estimate_cost(self, num_questions):
        """
        Estimate API cost for generating questions
        
        GPT-3.5-turbo pricing (approximate):
        - Input: $0.0015 per 1K tokens
        - Output: $0.002 per 1K tokens
        """
        # Rough estimate: ~300 tokens per question
        estimated_tokens = num_questions * 300
        estimated_cost = (estimated_tokens / 1000) * 0.002
        
        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost_usd': round(estimated_cost, 4)
        }


# Singleton instance
ai_generator = AIQuestionGenerator()
