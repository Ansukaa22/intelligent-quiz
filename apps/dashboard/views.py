"""
Views for dashboard app
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q, Sum
from apps.quizzes.models import Category, UserQuizAttempt
import json


@login_required
def dashboard_home_view(request):
    """
    Main dashboard view with analytics
    Task 3.2: Added total time spent calculation and chart data
    """
    user = request.user
    
    # Get user statistics
    completed_attempts = UserQuizAttempt.objects.filter(user=user, completed=True).select_related('quiz', 'quiz__category')
    total_quizzes = completed_attempts.count()
    average_score = completed_attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0
    
    # Task 3.2: Calculate total time spent
    total_time_seconds = completed_attempts.aggregate(Sum('time_taken'))['time_taken__sum'] or 0
    total_time_minutes = round(total_time_seconds / 60, 1)
    total_time_hours = round(total_time_seconds / 3600, 1)
    
    # Get recent attempts
    recent_attempts = completed_attempts.order_by('-completed_at')[:5]
    
    # Task 3.4: Get incomplete attempts for "Continue Quiz" feature
    incomplete_attempts = UserQuizAttempt.objects.filter(
        user=user, 
        completed=False
    ).select_related('quiz', 'quiz__category').order_by('-started_at')[:3]
    
    # Get categories
    categories = Category.objects.filter(is_active=True).annotate(quiz_count=Count('quizzes'))
    
    # Get performance by category
    category_performance = completed_attempts.values(
        'quiz__category__name'
    ).annotate(
        avg_score=Avg('percentage'),
        total_attempts=Count('id')
    ).order_by('-avg_score')
    
    # Task 3.2: Prepare chart data for Chart.js
    # Category performance pie chart data
    category_chart_labels = [perf['quiz__category__name'] for perf in category_performance]
    category_chart_data = [float(perf['avg_score']) for perf in category_performance]
    
    # Score over time line chart data
    score_over_time = completed_attempts.order_by('completed_at')[:20]
    score_timeline_labels = [attempt.completed_at.strftime('%m/%d') for attempt in score_over_time]
    score_timeline_data = [float(attempt.percentage) for attempt in score_over_time]
    
    # Task 3.2: Recent Activity Feed (last 10 actions)
    recent_activity = completed_attempts.order_by('-completed_at')[:10]
    
    context = {
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 2),
        'total_time_minutes': total_time_minutes,
        'total_time_hours': total_time_hours,
        'recent_attempts': recent_attempts,
        'incomplete_attempts': incomplete_attempts,
        'categories': categories,
        'category_performance': category_performance,
        'recent_activity': recent_activity,
        # Chart data as JSON for JavaScript
        'category_chart_labels': json.dumps(category_chart_labels),
        'category_chart_data': json.dumps(category_chart_data),
        'score_timeline_labels': json.dumps(score_timeline_labels),
        'score_timeline_data': json.dumps(score_timeline_data),
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_history_view(request):
    """
    View quiz history with sorting and filtering
    Task 3.1: Added sorting, filtering, and search functionality
    """
    user = request.user
    attempts = UserQuizAttempt.objects.filter(user=user, completed=True).select_related('quiz', 'quiz__category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        attempts = attempts.filter(
            Q(quiz__title__icontains=search_query) |
            Q(quiz__category__name__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        attempts = attempts.filter(quiz__category__slug=category_filter)
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        attempts = attempts.filter(quiz__difficulty=difficulty_filter)
    
    # Filter by result (passed/failed)
    result_filter = request.GET.get('result', '')
    if result_filter == 'passed':
        attempts = attempts.filter(passed=True)
    elif result_filter == 'failed':
        attempts = attempts.filter(passed=False)
    
    # Sorting
    sort_by = request.GET.get('sort', '-completed_at')
    valid_sorts = ['-completed_at', 'completed_at', '-percentage', 'percentage', '-time_taken', 'time_taken']
    if sort_by in valid_sorts:
        attempts = attempts.order_by(sort_by)
    else:
        attempts = attempts.order_by('-completed_at')
    
    # Get all categories for filter dropdown
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'attempts': attempts,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'result_filter': result_filter,
        'sort_by': sort_by,
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
