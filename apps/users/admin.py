"""
Admin configuration for users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPreferences


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'preferred_difficulty']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('avatar', 'bio', 'date_of_birth', 'phone_number')
        }),
        ('Preferences', {
            'fields': ('preferred_difficulty', 'email_notifications')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name')
        }),
    )


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Admin interface for UserPreferences model
    """
    list_display = ['user', 'show_timer', 'show_progress', 'auto_submit']
    list_filter = ['show_timer', 'show_progress', 'auto_submit']
    search_fields = ['user__username', 'user__email']
    ordering = ['-created_at']
