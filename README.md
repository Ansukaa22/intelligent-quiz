# Intelligent Quiz - AI-Powered Quiz Application

An intelligent quiz application built with Django that generates dynamic questions using OpenAI's GPT-3.5 Turbo. The application features user authentication, category-based quizzes, real-time scoring, and comprehensive performance tracking.

## 🚀 Features

### Milestone 1 - Foundation & User Management (✅ COMPLETED)

- **User Authentication System**
  - User registration with email validation
  - Login with "Remember Me" functionality
  - Password reset via email
  - Session management

- **User Profile Management**
  - Customizable user profiles with avatar upload
  - Profile editing (name, email, bio, preferences)
  - User statistics display (quizzes taken, average score, total points)
  - Quiz preferences (difficulty, theme, timer settings)

- **Responsive UI/UX**
  - Modern, clean design with Bootstrap 5
  - Responsive navigation with user dropdown
  - Flash messages for user feedback
  - Mobile-friendly interface

- **Dashboard**
  - Overview of user statistics
  - Recent quiz attempts
  - Performance by category
  - Quick action buttons

- **Category System**
  - Multiple quiz categories (Academic, Entertainment, General Knowledge, etc.)
  - Subcategories for better organization
  - Category browsing interface

### Milestone 2 - Quiz Engine & AI Integration (✅ COMPLETED)

- **AI-Powered Question Generation**
  - Dynamic question generation using GPT-3.5 Turbo
  - Intelligent prompt engineering for quality questions
  - Response caching to minimize API costs
  - Question validation and quality control

- **Quiz Configuration**
  - Select category and subcategory
  - Choose difficulty level (Easy, Medium, Hard)
  - Select number of questions (5, 10, 15, 20)
  - Time limit calculation based on difficulty

- **Interactive Quiz Taking**
  - Clean, intuitive question interface
  - Real-time countdown timer with warnings
  - Progress bar and question counter
  - Question navigator sidebar
  - AJAX-powered answer saving
  - Auto-submit when time expires

- **Comprehensive Results**
  - Score display with percentage
  - Letter grade (A+, A, B+, etc.)
  - Time tracking
  - Question-by-question breakdown
  - Correct answer highlighting
  - Detailed explanations
  - Retake functionality

## 📁 Project Structure

```
intelligent-quiz/
├── apps/
│   ├── users/              # User authentication & profiles
│   │   ├── models.py       # User and UserPreferences models
│   │   ├── views.py        # Auth views (register, login, profile)
│   │   ├── forms.py        # User forms (registration, login, profile)
│   │   ├── urls.py         # User URL patterns
│   │   ├── admin.py        # Admin configuration
│   │   └── signals.py      # Auto-create user preferences
│   ├── quizzes/            # Quiz engine
│   │   ├── models.py       # Category, Quiz, Question, UserQuizAttempt models
│   │   ├── views.py        # Quiz views
│   │   ├── urls.py         # Quiz URL patterns
│   │   ├── admin.py        # Admin configuration
│   │   └── services/
│   │       └── ai_service.py  # OpenAI GPT integration
│   └── dashboard/          # User dashboard
│       ├── views.py        # Dashboard views
│       └── urls.py         # Dashboard URL patterns
├── config/
│   ├── settings/
│   │   ├── base.py         # Base settings
│   │   ├── development.py  # Development settings
│   │   └── production.py   # Production settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── templates/
│   ├── base.html           # Base template
│   ├── home.html           # Homepage
│   ├── users/              # User templates
│   ├── quizzes/            # Quiz templates
│   └── dashboard/          # Dashboard templates
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # JavaScript utilities
├── media/                  # User uploads (avatars, images)
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (SECRET!)
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone/Navigate to Project

```cmd
cd "C:\Users\ArMo\Desktop\Intelligent Quiz"
```

### Step 2: Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 4: Environment Configuration

The `.env` file is already created with your OpenAI API key. **IMPORTANT SECURITY NOTE:**

⚠️ **Your OpenAI API key is currently exposed in this file. After testing, you should:**
1. Rotate your API key in the OpenAI dashboard
2. Never commit the `.env` file to version control (already in `.gitignore`)
3. Use environment variables in production

### Step 5: Database Setup

```cmd
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)

```cmd
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 7: Create Sample Categories (Optional)

Open the Django shell:

```cmd
python manage.py shell
```

Then run:

```python
from apps.quizzes.models import Category, Subcategory

# Create Academic Category
academic = Category.objects.create(
    name="Academic",
    slug="academic",
    description="Test your knowledge in academic subjects",
    icon="fas fa-graduation-cap",
    order=1
)

Subcategory.objects.create(
    category=academic,
    name="Python Programming",
    slug="python",
    description="Test your Python programming skills"
)

Subcategory.objects.create(
    category=academic,
    name="Mathematics",
    slug="mathematics",
    description="Mathematical problems and concepts"
)

# Create Entertainment Category
entertainment = Category.objects.create(
    name="Entertainment",
    slug="entertainment",
    description="Fun quizzes about movies, music, and pop culture",
    icon="fas fa-film",
    order=2
)

Subcategory.objects.create(
    category=entertainment,
    name="Movies",
    slug="movies",
    description="Test your movie knowledge"
)

# Create General Knowledge Category
general = Category.objects.create(
    name="General Knowledge",
    slug="general-knowledge",
    description="Broad range of general knowledge topics",
    icon="fas fa-brain",
    order=3
)

print("Sample categories created successfully!")
exit()
```

### Step 8: Run Development Server

```cmd
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 🎯 Usage Guide

### For Regular Users

1. **Register**: Create an account at `/users/register/`
2. **Login**: Sign in at `/users/login/`
3. **Browse Categories**: Explore quiz categories
4. **View Dashboard**: Check your statistics and recent attempts
5. **Edit Profile**: Customize your profile and preferences

### For Administrators

1. Access admin panel: http://127.0.0.1:8000/admin/
2. Manage users, categories, subcategories, and quizzes
3. Review quiz attempts and user answers
4. Monitor system usage

## 🔐 Security Features

- CSRF protection
- Password validation (minimum 8 characters)
- Session management
- Secure password reset
- Environment-based configuration
- SQL injection protection (Django ORM)

## 💰 API Cost Management

The application uses GPT-3.5 Turbo with built-in cost optimization:

- **Question Caching**: Generated questions are cached for 1 hour
- **Batch Generation**: Questions generated in batches to reduce API calls
- **Rate Limiting**: Configurable limits in settings
- **Estimated Cost**: ~$0.002 per 10 questions

### Monitoring API Usage

Check `apps/quizzes/services/ai_service.py` for the `estimate_cost()` method.

## 🎨 Customization

### Change Color Scheme

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4f46e5;  /* Change primary color */
    --secondary-color: #06b6d4; /* Change secondary color */
    /* ... */
}
```

### Add New Categories

1. Go to Admin Panel
2. Navigate to Quizzes > Categories
3. Click "Add Category"
4. Fill in details and save

## 📊 Database Models

### User Model
- Extended Django User with profile fields
- Avatar, bio, date of birth, phone number
- Quiz preferences (difficulty, notifications)

### Category & Subcategory
- Hierarchical organization of quiz topics
- Icons and images support
- Active/inactive status

### Quiz Model
- Title, description, time limit
- Difficulty levels (Easy, Medium, Hard)
- Pass percentage threshold

### Question Model
- Multiple choice (4 options)
- Correct answer tracking
- Optional explanations

### UserQuizAttempt
- Tracks individual quiz sessions
- Score, percentage, time taken
- Pass/fail status

## 🚧 Next Steps (Milestone 2)

1. Implement AI question generation service
2. Build quiz-taking interface with timer
3. Create question navigation system
4. Implement answer submission and validation
5. Build results display page
6. Add quiz review functionality

## 📝 Development Notes

### Adding New Features

1. Create feature in appropriate app (`users`, `quizzes`, `dashboard`)
2. Add models if needed and run migrations
3. Create views in `views.py`
4. Add URL patterns in `urls.py`
5. Create templates in `templates/app_name/`
6. Update admin.py for admin interface

### Running Tests

```cmd
python manage.py test
```

### Collecting Static Files (Production)

```cmd
python manage.py collectstatic
```

## 🐛 Troubleshooting

### Issue: Module import errors
**Solution**: Make sure virtual environment is activated and dependencies are installed

### Issue: Database errors
**Solution**: Run `python manage.py migrate`

### Issue: Static files not loading
**Solution**: Run `python manage.py collectstatic` and check `STATIC_ROOT` in settings

### Issue: OpenAI API errors
**Solution**: Verify API key in `.env` file and check your OpenAI account balance

## 📄 License

This project is created for educational purposes.

## 🤝 Contributing

This is a personal project. Feedback and suggestions are welcome!

## 📧 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ using Django and OpenAI GPT-3.5 Turbo**
