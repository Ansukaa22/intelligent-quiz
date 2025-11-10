"""
Views for dashboard app
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from apps.quizzes.models import Category, UserQuizAttempt


@login_required
def dashboard_home_view(request):
    """
    Main dashboard view
    """
    user = request.user
    
    # Get user statistics
    total_quizzes = UserQuizAttempt.objects.filter(user=user, completed=True).count()
    average_score = UserQuizAttempt.objects.filter(user=user, completed=True).aggregate(Avg('percentage'))['percentage__avg'] or 0
    
    # Get recent attempts
    recent_attempts = UserQuizAttempt.objects.filter(user=user, completed=True).order_by('-completed_at')[:5]
    
    # Get categories
    categories = Category.objects.filter(is_active=True).annotate(quiz_count=Count('quizzes'))
    
    # Get performance by category
    category_performance = UserQuizAttempt.objects.filter(
        user=user, 
        completed=True
    ).values(
        'quiz__category__name'
    ).annotate(
        avg_score=Avg('percentage'),
        total_attempts=Count('id')
    ).order_by('-avg_score')
    
    context = {
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 2),
        'recent_attempts': recent_attempts,
        'categories': categories,
        'category_performance': category_performance,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_history_view(request):
    """
    View quiz history
    """
    user = request.user
    attempts = UserQuizAttempt.objects.filter(user=user, completed=True).order_by('-completed_at')
    
    context = {
        'attempts': attempts,
    }
    
    return render(request, 'dashboard/history.html', context)


@login_required
def dashboard_statistics_view(request):
    """
    View detailed statistics
    """
    user = request.user
    
    # Overall stats
    total_quizzes = UserQuizAttempt.objects.filter(user=user, completed=True).count()
    total_passed = UserQuizAttempt.objects.filter(user=user, completed=True, passed=True).count()
    total_failed = total_quizzes - total_passed
    
    average_score = UserQuizAttempt.objects.filter(user=user, completed=True).aggregate(Avg('percentage'))['percentage__avg'] or 0
    
    # Performance by difficulty
    difficulty_stats = UserQuizAttempt.objects.filter(
        user=user,
        completed=True
    ).values(
        'quiz__difficulty'
    ).annotate(
        avg_score=Avg('percentage'),
        total_attempts=Count('id'),
        passed=Count('id', filter=Q(passed=True))
    ).order_by('quiz__difficulty')
    
    # Performance by category
    category_stats = UserQuizAttempt.objects.filter(
        user=user,
        completed=True
    ).values(
        'quiz__category__name'
    ).annotate(
        avg_score=Avg('percentage'),
        total_attempts=Count('id'),
        passed=Count('id', filter=Q(passed=True))
    ).order_by('-avg_score')
    
    context = {
        'total_quizzes': total_quizzes,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'average_score': round(average_score, 2),
        'difficulty_stats': difficulty_stats,
        'category_stats': category_stats,
    }
    
    return render(request, 'dashboard/statistics.html', context)
