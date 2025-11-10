"""
Views for user authentication and profile management
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserPreferencesForm
from .models import User, UserPreferences


def register_view(request):
    """
    Handle user registration
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserPreferences are created automatically via signal
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            login(request, user)
            return redirect('dashboard:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Handle user login
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember_me
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'dashboard:home')
                return redirect(next_page)
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    Display user profile
    """
    user = request.user
    
    # Get or create preferences
    preferences, created = UserPreferences.objects.get_or_create(user=user)
    
    # Get user statistics
    context = {
        'user': user,
        'total_quizzes': user.total_quizzes_taken,
        'average_score': user.average_score,
        'total_points': user.total_points,
        'preferences': preferences,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Handle profile editing
    """
    user = request.user
    preferences, created = UserPreferences.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
        preferences_form = UserPreferencesForm(request.POST, instance=preferences)
        
        if profile_form.is_valid() and preferences_form.is_valid():
            profile_form.save()
            preferences_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        profile_form = UserProfileForm(instance=user)
        preferences_form = UserPreferencesForm(instance=preferences)
    
    context = {
        'profile_form': profile_form,
        'preferences_form': preferences_form,
    }
    
    return render(request, 'users/profile_edit.html', context)


@login_required
def delete_avatar_view(request):
    """
    Delete user avatar
    """
    if request.method == 'POST':
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
            messages.success(request, 'Avatar deleted successfully!')
        else:
            messages.info(request, 'No avatar to delete.')
    
    return redirect('users:profile_edit')
