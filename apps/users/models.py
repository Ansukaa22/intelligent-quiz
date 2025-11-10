"""
User models for Intelligent Quiz
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    """
    Extended User model with additional profile fields
    """
    email = models.EmailField(unique=True, verbose_name='Email Address')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        help_text='Upload a profile picture (JPG, PNG, or GIF)'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biography')
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Preferences
    preferred_difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='medium',
        verbose_name='Preferred Difficulty'
    )
    email_notifications = models.BooleanField(default=True)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def total_quizzes_taken(self):
        """Return total number of quizzes taken"""
        return self.quiz_attempts.filter(completed=True).count()
    
    @property
    def average_score(self):
        """Calculate average score across all completed quizzes"""
        from django.db.models import Avg
        result = self.quiz_attempts.filter(completed=True).aggregate(Avg('score'))
        return round(result['score__avg'] or 0, 2)
    
    @property
    def total_points(self):
        """Calculate total points earned"""
        from django.db.models import Sum
        result = self.quiz_attempts.filter(completed=True).aggregate(Sum('score'))
        return result['score__sum'] or 0


class UserPreferences(models.Model):
    """
    Additional user preferences and settings
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        default='light'
    )
    show_timer = models.BooleanField(default=True, help_text='Display timer during quiz')
    show_progress = models.BooleanField(default=True, help_text='Display progress bar during quiz')
    auto_submit = models.BooleanField(default=True, help_text='Auto-submit when time expires')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"
