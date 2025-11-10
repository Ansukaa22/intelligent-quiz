"""
Admin configuration for quizzes app
"""

from django.contrib import admin
from .models import Category, Subcategory, Quiz, Question, UserQuizAttempt, UserAnswer


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    fields = ['name', 'slug', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    inlines = [SubcategoryInline]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'subcategory', 'difficulty', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'subcategory', 'difficulty', 'description')
        }),
        ('Quiz Settings', {
            'fields': ('time_limit', 'pass_percentage', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'quiz', 'correct_answer', 'order', 'created_at']
    list_filter = ['quiz__category', 'quiz__difficulty', 'created_at']
    search_fields = ['question_text', 'quiz__title']
    ordering = ['quiz', 'order']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ['question', 'selected_answer', 'is_correct', 'answered_at']
    can_delete = False


@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_questions', 'percentage', 'passed', 'completed', 'started_at']
    list_filter = ['completed', 'passed', 'quiz__category', 'started_at']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['score', 'total_questions', 'percentage', 'time_taken', 'started_at', 'completed_at']
    ordering = ['-started_at']
    inlines = [UserAnswerInline]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question_short', 'selected_answer', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['attempt__user__username', 'question__question_text']
    readonly_fields = ['is_correct']
    ordering = ['-answered_at']
    
    def question_short(self, obj):
        return obj.question.question_text[:50] + '...'
    question_short.short_description = 'Question'
