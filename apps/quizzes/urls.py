"""
URL patterns for quizzes app
"""

from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Category and Subcategory
    path('categories/', views.category_list_view, name='category_list'),
    path('category/<slug:category_slug>/', views.category_detail_view, name='category_detail'),
    path('category/<slug:category_slug>/select/', views.subcategory_selection_view, name='subcategory_selection'),
    
    # Quiz selection and taking
    path('start/', views.start_quiz_view, name='start_quiz'),
    path('take/<int:attempt_id>/', views.take_quiz_view, name='take_quiz'),
    path('submit/<int:attempt_id>/', views.submit_quiz_view, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results_view, name='quiz_results'),
    
    # AJAX endpoints
    path('save-answer/', views.save_answer_view, name='save_answer'),
]
