"""
URL patterns for dashboard app
"""

from django.urls import path
from . import views
from . import leaderboard_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home_view, name='home'),
    path('history/', views.dashboard_history_view, name='history'),
    path('statistics/', views.dashboard_statistics_view, name='statistics'),
    
    # Leaderboard
    path('leaderboard/', leaderboard_views.leaderboard_view, name='leaderboard'),
    path('leaderboard/category/<slug:category_slug>/', leaderboard_views.leaderboard_category_view, name='leaderboard_category'),
]
