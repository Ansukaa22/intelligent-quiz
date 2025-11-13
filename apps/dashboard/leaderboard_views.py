"""
Views for leaderboard functionality
Task 3.5: Leaderboard & Rankings
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Sum, Q, F
from django.contrib.auth import get_user_model
from apps.quizzes.models import Category, UserQuizAttempt
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


def leaderboard_view(request):
    """
    Global leaderboard showing top performers
    """
    # Get time filter
    time_filter = request.GET.get('time', 'all-time')
    
    # Base queryset - only users who opted in
    users = User.objects.filter(show_on_leaderboard=True)
    
    # Apply time filter
    attempts_filter = Q(quiz_attempts__completed=True)
    if time_filter == 'weekly':
        week_ago = timezone.now() - timedelta(days=7)
        attempts_filter &= Q(quiz_attempts__completed_at__gte=week_ago)
    elif time_filter == 'monthly':
        month_ago = timezone.now() - timedelta(days=30)
        attempts_filter &= Q(quiz_attempts__completed_at__gte=month_ago)
    
    # Calculate leaderboard statistics
    leaderboard_data = users.annotate(
        total_quizzes=Count('quiz_attempts', filter=attempts_filter),
        avg_score=Avg('quiz_attempts__percentage', filter=attempts_filter),
        total_score=Sum('quiz_attempts__score', filter=attempts_filter),
        passed_quizzes=Count('quiz_attempts', filter=attempts_filter & Q(quiz_attempts__passed=True))
    ).filter(
        total_quizzes__gt=0  # Only show users with at least one quiz
    ).order_by('-avg_score', '-total_quizzes')[:50]  # Top 50
    
    # Add rank
    for index, user in enumerate(leaderboard_data, start=1):
        user.rank = index
    
    # Get current user's rank if logged in and opted in
    user_rank = None
    if request.user.is_authenticated and request.user.show_on_leaderboard:
        user_stats = User.objects.filter(show_on_leaderboard=True).annotate(
            total_quizzes=Count('quiz_attempts', filter=attempts_filter),
            avg_score=Avg('quiz_attempts__percentage', filter=attempts_filter)
        ).filter(
            total_quizzes__gt=0
        ).order_by('-avg_score', '-total_quizzes')
        
        for index, user in enumerate(user_stats, start=1):
            if user.id == request.user.id:
                user_rank = index
                break
    
    # Get all categories for the bottom section
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'leaderboard_data': leaderboard_data,
        'user_rank': user_rank,
        'time_filter': time_filter,
        'total_participants': leaderboard_data.count(),
        'categories': categories,
    }
    
    return render(request, 'dashboard/leaderboard.html', context)


def leaderboard_category_view(request, category_slug):
    """
    Category-specific leaderboard
    """
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    time_filter = request.GET.get('time', 'all-time')
    
    # Base queryset
    users = User.objects.filter(show_on_leaderboard=True)
    
    # Apply time filter
    attempts_filter = Q(quiz_attempts__completed=True, quiz_attempts__quiz__category=category)
    if time_filter == 'weekly':
        week_ago = timezone.now() - timedelta(days=7)
        attempts_filter &= Q(quiz_attempts__completed_at__gte=week_ago)
    elif time_filter == 'monthly':
        month_ago = timezone.now() - timedelta(days=30)
        attempts_filter &= Q(quiz_attempts__completed_at__gte=month_ago)
    
    # Calculate leaderboard statistics for this category
    leaderboard_data = users.annotate(
        total_quizzes=Count('quiz_attempts', filter=attempts_filter),
        avg_score=Avg('quiz_attempts__percentage', filter=attempts_filter),
        total_score=Sum('quiz_attempts__score', filter=attempts_filter),
        passed_quizzes=Count('quiz_attempts', filter=attempts_filter & Q(quiz_attempts__passed=True))
    ).filter(
        total_quizzes__gt=0
    ).order_by('-avg_score', '-total_quizzes')[:50]
    
    # Add rank
    for index, user in enumerate(leaderboard_data, start=1):
        user.rank = index
    
    # Get current user's rank
    user_rank = None
    if request.user.is_authenticated and request.user.show_on_leaderboard:
        user_stats = User.objects.filter(show_on_leaderboard=True).annotate(
            total_quizzes=Count('quiz_attempts', filter=attempts_filter),
            avg_score=Avg('quiz_attempts__percentage', filter=attempts_filter)
        ).filter(
            total_quizzes__gt=0
        ).order_by('-avg_score', '-total_quizzes')
        
        for index, user in enumerate(user_stats, start=1):
            if user.id == request.user.id:
                user_rank = index
                break
    
    context = {
        'leaderboard_data': leaderboard_data,
        'category': category,
        'user_rank': user_rank,
        'time_filter': time_filter,
        'total_participants': leaderboard_data.count(),
    }
    
    return render(request, 'dashboard/leaderboard_category.html', context)

