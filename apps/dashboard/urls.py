"""
URL patterns for dashboard app
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home_view, name='home'),
    path('history/', views.dashboard_history_view, name='history'),
    path('statistics/', views.dashboard_statistics_view, name='statistics'),
]
