# 🚀 Deployment Checklist for Intelligent Quiz

## Pre-Deployment Steps

### 1. Code Review & Testing
- [ ] All features tested thoroughly
- [ ] No console errors or warnings
- [ ] All forms validated properly
- [ ] Error handling in place
- [ ] API calls have timeouts and error handling
- [ ] Database migrations are up to date
- [ ] No hardcoded credentials in code

### 2. Security Configuration

#### Django Settings
- [ ] Set `DEBUG = False` in production.py
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set strong, random `SECRET_KEY` (50+ characters)
- [ ] Enable `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Enable `SECURE_BROWSER_XSS_FILTER = True`
- [ ] Enable `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] Set `X_FRAME_OPTIONS = 'DENY'`
- [ ] Configure `SECURE_HSTS_SECONDS` (e.g., 31536000 for 1 year)

#### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-super-secret-production-key-minimum-50-characters-long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.production
```

### 3. Database Setup

#### PostgreSQL (Recommended for Production)
- [ ] Install PostgreSQL on server
- [ ] Create production database
- [ ] Create database user with appropriate permissions
- [ ] Configure database connection in .env:
```env
DB_NAME=intelligent_quiz_prod
DB_USER=quiz_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432
```
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load initial data: `python manage.py create_subcategories`

### 4. Static Files Configuration

- [ ] Install WhiteNoise: `pip install whitenoise`
- [ ] Add WhiteNoise to middleware (already configured)
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Verify static files are served correctly
- [ ] Consider using CDN for static files (optional)

### 5. Media Files Configuration

- [ ] Set up media file storage (local or S3)
- [ ] Configure appropriate permissions for media folder
- [ ] Set up backup strategy for media files
- [ ] Consider using AWS S3 or similar for production

### 6. Email Configuration

Configure email backend for password reset:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Test email functionality:
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Testing email', 'from@example.com', ['to@example.com'])
```

### 7. OpenAI API Configuration

- [ ] Verify OpenAI API key is valid
- [ ] Set up billing and usage limits in OpenAI dashboard
- [ ] Configure rate limiting
- [ ] Set up monitoring for API usage
```env
OPENAI_API_KEY=sk-your-production-api-key
```

### 8. Server Requirements

#### System Requirements
- Python 3.9 or higher
- 1GB+ RAM (2GB+ recommended)
- 10GB+ disk space
- Ubuntu 20.04+ or similar Linux distribution

#### Install System Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-dev
sudo apt install postgresql postgresql-contrib
sudo apt install nginx
sudo apt install supervisor  # For process management
```

### 9. Application Server Setup

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Create Gunicorn Configuration
File: `/etc/supervisor/conf.d/intelligent_quiz.conf`
```ini
[program:intelligent_quiz]
command=/path/to/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/path/to/intelligent-quiz
user=your-username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/intelligent_quiz/gunicorn.log
```

Start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start intelligent_quiz
```

### 10. Nginx Configuration

File: `/etc/nginx/sites-available/intelligent_quiz`
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /path/to/intelligent-quiz/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/intelligent-quiz/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/intelligent_quiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. SSL/HTTPS Setup (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run  # Test auto-renewal
```

### 12. Monitoring & Logging

#### Set up logging
File: `config/settings/production.py`
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/intelligent_quiz/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

Create log directory:
```bash
sudo mkdir -p /var/log/intelligent_quiz
sudo chown your-username:your-username /var/log/intelligent_quiz
```

#### Monitoring Tools (Optional)
- [ ] Set up Sentry for error tracking
- [ ] Configure New Relic or similar APM tool
- [ ] Set up server monitoring (CPU, memory, disk)
- [ ] Configure uptime monitoring

### 13. Backup Strategy

#### Database Backups
Create backup script: `/home/username/backup_db.sh`
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/intelligent_quiz"
mkdir -p $BACKUP_DIR

pg_dump -U quiz_user intelligent_quiz_prod > $BACKUP_DIR/db_backup_$DATE.sql
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add: Daily backup at 2 AM
0 2 * * * /home/username/backup_db.sh
```

#### Media Files Backup
```bash
rsync -avz /path/to/media/ backup-server:/backups/media/
```

### 14. Performance Optimization

- [ ] Enable Django caching (Redis recommended)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```
- [ ] Optimize database queries (already done with select_related)
- [ ] Enable gzip compression in Nginx
- [ ] Set up CDN for static files (optional)
- [ ] Configure browser caching headers

### 15. Final Testing

- [ ] Test all major user flows
- [ ] Test registration and login
- [ ] Test quiz creation and submission
- [ ] Test password reset email
- [ ] Test file uploads (avatars)
- [ ] Test on different browsers
- [ ] Test on mobile devices
- [ ] Load testing (optional)
- [ ] Security audit (optional)

### 16. Go Live Checklist

- [ ] Domain DNS pointed to server
- [ ] SSL certificate installed and working
- [ ] All environment variables set correctly
- [ ] Database backed up
- [ ] Monitoring tools configured
- [ ] Error pages (404, 500) working
- [ ] Admin panel accessible
- [ ] All static files loading
- [ ] Email notifications working
- [ ] OpenAI integration working

## Post-Deployment

### Regular Maintenance

#### Daily
- [ ] Check error logs
- [ ] Monitor server resources
- [ ] Check backup completion

#### Weekly
- [ ] Review application performance
- [ ] Check OpenAI API usage and costs
- [ ] Review user feedback/issues

#### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review and optimize database
- [ ] Check disk space usage
- [ ] Review backup integrity

### Update Procedure

1. Pull latest code: `git pull origin main`
2. Activate virtual environment: `source venv/bin/activate`
3. Install new dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Collect static files: `python manage.py collectstatic --noinput`
6. Restart application: `sudo supervisorctl restart intelligent_quiz`
7. Clear cache if needed
8. Test critical functionality

## Rollback Procedure

If deployment fails:

1. Restore database from backup:
```bash
gunzip db_backup_YYYYMMDD_HHMMSS.sql.gz
psql -U quiz_user intelligent_quiz_prod < db_backup_YYYYMMDD_HHMMSS.sql
```

2. Checkout previous version:
```bash
git checkout <previous-commit-hash>
```

3. Reinstall dependencies:
```bash
pip install -r requirements.txt
```

4. Restart application:
```bash
sudo supervisorctl restart intelligent_quiz
```

## Support & Resources

- Django Deployment Docs: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Gunicorn Docs: https://docs.gunicorn.org/
- Nginx Docs: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/getting-started/
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

**Note**: This checklist assumes deployment on a Linux server (Ubuntu/Debian). Adjust commands for other operating systems as needed.
