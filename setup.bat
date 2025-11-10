@echo off
echo Cleaning up database...
del /Q db.sqlite3 2>nul
echo.
echo Running migrations...
venv\Scripts\python.exe manage.py migrate
echo.
echo Creating superuser...
venv\Scripts\python.exe manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@quiz.com', 'admin123'); print('Superuser created!')"
echo.
echo Creating sample categories...
venv\Scripts\python.exe manage.py shell -c "from apps.quizzes.models import Category; Category.objects.get_or_create(name='Academic', defaults={'description': 'Test your knowledge in academic subjects', 'icon': '📚'}); Category.objects.get_or_create(name='Entertainment', defaults={'description': 'Fun quizzes about movies, music, and pop culture', 'icon': '🎬'}); Category.objects.get_or_create(name='General Knowledge', defaults={'description': 'Broad range of topics to challenge yourself', 'icon': '🌍'}); print('Categories created!')"
echo.
echo ========================================
echo Milestone 1 Setup Complete!
echo ========================================
echo.
echo Superuser Credentials:
echo Username: admin
echo Password: admin123
echo Email: admin@quiz.com
echo.
echo To start the server, run:
echo venv\Scripts\python.exe manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin
echo ========================================
pause
