"""
Models for quiz system
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    """
    Quiz categories (Academic, Entertainment, General Knowledge, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class or emoji')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    @property
    def total_quizzes(self):
        """Return total number of quizzes in this category"""
        return self.quizzes.count()


class Subcategory(models.Model):
    """
    Subcategories within a category (e.g., Python, JavaScript under Programming)
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'
        unique_together = ['category', 'slug']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Quiz(models.Model):
    """
    Quiz model representing a quiz session
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    
    description = models.TextField(blank=True)
    time_limit = models.IntegerField(
        default=600,
        validators=[MinValueValidator(60), MaxValueValidator(3600)],
        help_text='Time limit in seconds'
    )
    pass_percentage = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Minimum percentage to pass'
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quizzes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return self.title
    
    @property
    def total_questions(self):
        """Return total number of questions"""
        return self.questions.count()
    
    @property
    def total_attempts(self):
        """Return total number of attempts"""
        return self.attempts.count()


class Question(models.Model):
    """
    Question model for quiz questions
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ('A', 'Option A'),
            ('B', 'Option B'),
            ('C', 'Option C'),
            ('D', 'Option D'),
        ]
    )
    explanation = models.TextField(blank=True, help_text='Explanation for the correct answer')
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
    
    def get_options(self):
        """Return all options as a dictionary"""
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }


class UserQuizAttempt(models.Model):
    """
    Track user quiz attempts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    time_taken = models.IntegerField(default=0, help_text='Time taken in seconds')
    completed = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total_questions})"
    
    def calculate_score(self):
        """Calculate score based on correct answers"""
        correct_answers = self.answers.filter(is_correct=True).count()
        self.score = correct_answers
        self.total_questions = self.answers.count()
        
        if self.total_questions > 0:
            self.percentage = (self.score / self.total_questions) * 100
            self.passed = self.percentage >= self.quiz.pass_percentage
        
        self.save()
        return self.score
    
    def mark_completed(self):
        """Mark quiz as completed"""
        self.completed = True
        self.completed_at = timezone.now()
        
        if self.started_at:
            time_diff = self.completed_at - self.started_at
            self.time_taken = int(time_diff.total_seconds())
        
        self.save()


class UserAnswer(models.Model):
    """
    Store user answers for each question
    """
    attempt = models.ForeignKey(UserQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    is_correct = models.BooleanField(default=False)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question__order']
        verbose_name = 'User Answer'
        verbose_name_plural = 'User Answers'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.order}: {self.selected_answer}"
    
    def save(self, *args, **kwargs):
        """Check if answer is correct before saving"""
        self.is_correct = (self.selected_answer == self.question.correct_answer)
        super().save(*args, **kwargs)
