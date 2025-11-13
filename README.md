# 🧠 Intelligent Quiz

An AI-powered quiz application built with Django that generates dynamic questions using OpenAI's GPT-3.5 Turbo. Test your knowledge across multiple categories with real-time scoring, comprehensive analytics, and intelligent answer explanations.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Features
- **AI-Generated Questions**: Dynamic quiz questions powered by OpenAI GPT-3.5 Turbo
- **Multiple Categories**: Academic, Entertainment, Sports, Science, Technology, and more
- **Difficulty Levels**: Easy, Medium, and Hard questions
- **Real-time Timer**: Countdown timer with auto-submit functionality
- **Instant Scoring**: Immediate results with detailed performance breakdown

### 📊 Dashboard & Analytics
- **Comprehensive Statistics**: Track total quizzes, average scores, and time spent
- **Visual Charts**: Interactive pie charts and line graphs using Chart.js
- **Quiz History**: Complete history with search, filter, and sorting capabilities
- **Performance Tracking**: Category-wise and difficulty-wise performance analysis
- **Recent Activity Feed**: View your latest quiz attempts

### 🤖 AI-Powered Features
- **Smart Explanations**: AI-generated explanations for incorrect answers
- **Answer Analysis**: Understand why an answer is correct or incorrect
- **Cached Responses**: Explanations stored for quick access

### 👤 User Management
- **User Authentication**: Secure registration, login, and password reset
- **Profile Management**: Customizable user profiles with avatar upload
- **Progress Tracking**: Monitor improvement over time

### 🎨 UI/UX
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Fully optimized for mobile, tablet, and desktop
- **Modern Interface**: Clean, intuitive design with smooth animations
- **Custom Error Pages**: User-friendly 404 and 500 error pages

### 🔄 Quiz Features
- **Continue Quiz**: Resume incomplete quizzes where you left off
- **Retake Quizzes**: Challenge yourself with new questions in the same category
- **Auto-save Answers**: Your answers are saved automatically
- **Multiple Attempts**: Track all attempts with historical data

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Git (optional, for cloning)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ansukaa22/intelligent-quiz.git
cd intelligent-quiz
```

2. **Create and activate virtual environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Database (default uses SQLite)
# For PostgreSQL production:
# DB_NAME=quiz_db
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create a superuser (admin)**
```bash
python manage.py createsuperuser
```

7. **Load initial categories (optional)**
```bash
python manage.py create_subcategories
```

8. **Run the development server**
```bash
python manage.py runserver
```

9. **Access the application**
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
intelligent-quiz/
├── apps/
│   ├── dashboard/          # Dashboard views and analytics
│   ├── quizzes/            # Quiz logic, AI generation, scoring
│   │   ├── services/       # Business logic (AI, quiz, scoring)
│   │   ├── management/     # Management commands
│   │   └── migrations/     # Database migrations
│   └── users/              # User authentication and profiles
├── config/
│   ├── settings/           # Settings (base, development, production)
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── static/
│   ├── css/                # Stylesheets (including dark mode)
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
│   ├── dashboard/          # Dashboard templates
│   ├── quizzes/            # Quiz templates
│   ├── users/              # User templates
│   ├── base.html           # Base template
│   ├── home.html           # Homepage
│   ├── 404.html            # Custom 404 page
│   └── 500.html            # Custom 500 page
├── media/                  # User uploaded files (avatars)
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## 🎮 Usage Guide

### For Users

1. **Register an Account**
   - Click "Register" in the navigation bar
   - Fill in username, email, and password
   - Verify your email (if configured)

2. **Start a Quiz**
   - Browse categories from the homepage
   - Select a category and subcategory
   - Choose difficulty level (Easy, Medium, Hard)
   - Select number of questions (5, 10, 15, or 20)
   - Click "Start Quiz"

3. **Take the Quiz**
   - Answer questions by selecting one of four options
   - Watch the timer - quizzes auto-submit when time expires
   - Navigate between questions using the question navigator
   - Submit when ready or let the timer expire

4. **View Results**
   - See your score, percentage, and grade
   - Review each question with correct/incorrect indicators
   - Click "Get AI Explanation" for incorrect answers
   - Retake the quiz or try a different category

5. **Track Progress**
   - Visit your dashboard to see statistics
   - View quiz history with filtering options
   - Check category-wise performance
   - Monitor your improvement over time

### For Administrators

1. **Access Admin Panel**
   - Go to http://127.0.0.1:8000/admin/
   - Login with superuser credentials

2. **Manage Categories**
   - Add/edit/delete quiz categories
   - Set category icons and descriptions
   - Organize display order

3. **Manage Subcategories**
   - Create subcategories under main categories
   - Define specific topics (e.g., Python, JavaScript under Programming)

4. **View User Activity**
   - Monitor user quiz attempts
   - View statistics and analytics
   - Manage user accounts

## 🔧 Configuration

### OpenAI Settings

Modify in `config/settings/base.py`:
```python
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = 'gpt-3.5-turbo'  # Change model if needed
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.7
```

### Quiz Settings

```python
QUIZ_QUESTIONS_CACHE_TIMEOUT = 3600  # Cache questions for 1 hour
QUIZ_DEFAULT_TIME_LIMIT = 600  # 10 minutes default
QUIZ_MIN_QUESTIONS = 5
QUIZ_MAX_QUESTIONS = 20
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production settings
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database
- [ ] Configure email backend for password reset
- [ ] Set up static files serving (WhiteNoise or CDN)
- [ ] Configure HTTPS/SSL
- [ ] Set strong `SECRET_KEY`
- [ ] Enable security middleware
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Using Production Settings

```bash
# Set environment variable
export DJANGO_SETTINGS_MODULE=config.settings.production

# Or in .env file
DJANGO_SETTINGS_MODULE=config.settings.production

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# OpenAI
OPENAI_API_KEY=your-production-api-key
```

## 🛠️ Technologies Used

### Backend
- **Django 4.2+** - Web framework
- **Python 3.9+** - Programming language
- **SQLite/PostgreSQL** - Database
- **OpenAI API** - AI question generation

### Frontend
- **Bootstrap 5** - CSS framework
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Vanilla JavaScript** - Interactivity

### Additional Libraries
- **django-crispy-forms** - Beautiful forms
- **Pillow** - Image processing
- **python-decouple** - Environment management

## 📊 Database Schema

### Main Models

- **User** (Custom user model with profile)
- **Category** - Quiz categories
- **Subcategory** - Subcategories within categories
- **Quiz** - Quiz instances
- **Question** - Individual questions
- **UserQuizAttempt** - User quiz sessions
- **UserAnswer** - Individual answers with AI explanations

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- AI explanation generation requires valid OpenAI API key
- Timer may have slight delays on slower connections
- Large number of quiz attempts may slow down dashboard

## 🔮 Future Enhancements

- [ ] Global leaderboard system
- [ ] Achievement badges
- [ ] Social features (share results)
- [ ] Mobile app version
- [ ] Multiplayer quiz mode
- [ ] Custom quiz creation by users
- [ ] More AI models support
- [ ] Voice-based questions

## 📧 Contact & Support

- **Developer**: Ansukaa22
- **Email**: your-email@example.com
- **GitHub**: [https://github.com/Ansukaa22](https://github.com/Ansukaa22)
- **Issues**: [Report a bug](https://github.com/Ansukaa22/intelligent-quiz/issues)

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- Django community for excellent documentation
- Bootstrap team for the UI framework
- All contributors and testers

---

**Made with ❤️ by Ansukaa22**

⭐ Star this repository if you found it helpful!
