"""
Views for quizzes app
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Category, Subcategory, Quiz, Question, UserQuizAttempt, UserAnswer
from .services.quiz_service import quiz_service
from .services.scoring_service import scoring_service
import json
import logging

logger = logging.getLogger(__name__)


def category_list_view(request):
    """
    Display all quiz categories
    """
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories': categories,
    }
    return render(request, 'quizzes/category_list.html', context)


def category_detail_view(request, category_slug):
    """
    Display category details and subcategories
    """
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    
    context = {
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'quizzes/category_detail.html', context)


@login_required
def subcategory_selection_view(request, category_slug):
    """
    Display subcategories and quiz configuration options
    Task 2.2: Subcategory Selection Interface
    """
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    
    if request.method == 'POST':
        # Get form data
        subcategory_slug = request.POST.get('subcategory')
        difficulty = request.POST.get('difficulty', 'medium')
        num_questions = int(request.POST.get('num_questions', 10))
        
        # Validate
        if num_questions not in [5, 10, 15, 20]:
            messages.error(request, 'Invalid number of questions selected')
            return redirect('quizzes:subcategory_selection', category_slug=category_slug)
        
        if difficulty not in ['easy', 'medium', 'hard']:
            messages.error(request, 'Invalid difficulty level selected')
            return redirect('quizzes:subcategory_selection', category_slug=category_slug)
        
        try:
            # Create quiz with AI-generated questions
            quiz = quiz_service.get_or_create_quiz(
                user=request.user,
                category_slug=category_slug,
                subcategory_slug=subcategory_slug if subcategory_slug else None,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            # Create attempt
            attempt = UserQuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                total_questions=quiz.total_questions
            )
            
            messages.success(request, f'Quiz started! You have {quiz.time_limit // 60} minutes.')
            return redirect('quizzes:take_quiz', attempt_id=attempt.id)
            
        except Exception as e:
            logger.error(f"Error creating quiz: {str(e)}")
            messages.error(request, f'Error creating quiz: {str(e)}')
            return redirect('quizzes:subcategory_selection', category_slug=category_slug)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'difficulties': ['easy', 'medium', 'hard'],
        'question_counts': [5, 10, 15, 20],
    }
    return render(request, 'quizzes/subcategory_selection.html', context)


@login_required
def start_quiz_view(request):
    """
    Start a new quiz - redirects to category selection
    """
    return redirect('quizzes:category_list')


@login_required
def take_quiz_view(request, attempt_id):
    """
    Take quiz interface
    Task 2.4 & 2.5: Quiz Taking Interface with Timer
    """
    attempt = get_object_or_404(
        UserQuizAttempt.objects.select_related('quiz', 'user'),
        id=attempt_id,
        user=request.user
    )
    
    # Check if already completed
    if attempt.completed:
        messages.warning(request, 'This quiz has already been completed')
        return redirect('quizzes:quiz_results', attempt_id=attempt.id)
    
    # Get questions
    questions = attempt.quiz.questions.all().order_by('order')
    
    # Get user's existing answers
    user_answers = {
        answer.question_id: answer.selected_answer 
        for answer in attempt.answers.all()
    }
    
    # Get list of answered question IDs for JavaScript
    answered_question_ids = list(user_answers.keys())
    
    # Calculate time remaining
    time_elapsed = (timezone.now() - attempt.started_at).total_seconds()
    time_remaining = max(0, attempt.quiz.time_limit - int(time_elapsed))
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'questions': questions,
        'user_answers': user_answers,
        'answered_question_ids': json.dumps(answered_question_ids),
        'time_remaining': time_remaining,
        'time_limit': attempt.quiz.time_limit,
    }
    return render(request, 'quizzes/take_quiz.html', context)


@login_required
def save_answer_view(request):
    """
    AJAX endpoint to save answer during quiz
    Task 2.4: Save user answers
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        
        # Validate
        if not all([attempt_id, question_id, selected_answer]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
        if selected_answer not in ['A', 'B', 'C', 'D']:
            return JsonResponse({'status': 'error', 'message': 'Invalid answer'}, status=400)
        
        # Get attempt
        attempt = get_object_or_404(UserQuizAttempt, id=attempt_id, user=request.user, completed=False)
        
        # Get question
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
        
        # Save answer
        scoring_service.save_answer(attempt, question, selected_answer)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Answer saved'
        })
        
    except Exception as e:
        logger.error(f"Error saving answer: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def submit_quiz_view(request, attempt_id):
    """
    Submit quiz and calculate score
    Task 2.6: Quiz Submission & Score Calculation
    """
    attempt = get_object_or_404(UserQuizAttempt, id=attempt_id, user=request.user)
    
    # Check if already completed
    if attempt.completed:
        messages.warning(request, 'This quiz has already been submitted')
        return redirect('quizzes:quiz_results', attempt_id=attempt.id)
    
    try:
        # Submit and score the quiz
        result = scoring_service.submit_quiz(attempt)
        
        messages.success(
            request, 
            f'Quiz submitted! You scored {result["score"]}/{result["total_questions"]} ({result["percentage"]:.1f}%)'
        )
        return redirect('quizzes:quiz_results', attempt_id=attempt.id)
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        messages.error(request, f'Error submitting quiz: {str(e)}')
        return redirect('quizzes:take_quiz', attempt_id=attempt.id)


@login_required
def quiz_results_view(request, attempt_id):
    """
    Display quiz results with breakdown
    Task 2.7: Quiz Results Display Page
    """
    attempt = get_object_or_404(
        UserQuizAttempt.objects.select_related('quiz', 'user'),
        id=attempt_id,
        user=request.user
    )
    
    # Get detailed results
    results = scoring_service.get_quiz_results(attempt)
    
    # Calculate grade
    grade = scoring_service.calculate_grade(float(attempt.percentage))
    
    # Format time taken
    minutes = attempt.time_taken // 60
    seconds = attempt.time_taken % 60
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'score': attempt.score,
        'total_questions': attempt.total_questions,
        'percentage': float(attempt.percentage),
        'passed': attempt.passed,
        'grade': grade,
        'questions': results['questions'],
        'time_taken_formatted': f"{minutes}m {seconds}s",
        'correct_count': attempt.score,
        'incorrect_count': attempt.total_questions - attempt.score,
    }
    return render(request, 'quizzes/quiz_results.html', context)


@login_required
def ai_explanation_view(request, answer_id):
    """
    Task 3.3: Generate AI explanation for incorrect answer
    AJAX endpoint that returns explanation for a user's answer
    """
    try:
        # Get the user answer
        answer = get_object_or_404(
            UserAnswer.objects.select_related('question', 'attempt'),
            id=answer_id,
            attempt__user=request.user
        )
        
        # Check if explanation already exists (cached)
        if answer.ai_explanation:
            return JsonResponse({
                'success': True,
                'explanation': answer.ai_explanation,
                'cached': True
            })
        
        # Generate new explanation
        from django.conf import settings as django_settings
        
        # Check if API key is configured
        if not django_settings.OPENAI_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.'
            }, status=503)
        
        from .services.ai_service import ai_generator
        
        question = answer.question
        options = question.get_options()
        
        explanation = ai_generator.generate_answer_explanation(
            question_text=question.question_text,
            selected_answer=answer.selected_answer,
            correct_answer=question.correct_answer,
            options=options
        )
        
        # Cache the explanation
        answer.ai_explanation = explanation
        answer.save()
        
        return JsonResponse({
            'success': True,
            'explanation': explanation,
            'cached': False
        })
        
    except UserAnswer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Answer not found'
        }, status=404)
    except Exception as e:
        import traceback
        logger.error(f"Error generating AI explanation: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Failed to generate explanation: {str(e)}'
        }, status=500)
