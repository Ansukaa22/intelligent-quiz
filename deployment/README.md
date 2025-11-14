# 🚀 Production Deployment Guide

This guide will help you deploy the Intelligent Quiz application to a production server.

## 📋 Prerequisites

- Ubuntu 20.04+ or Debian 11+ server
- Domain name pointing to your server
- Root or sudo access

## 🛠️ Quick Deployment

### 1. Run the deployment script on your server

```bash
# Upload deploy.sh to your server and run:
chmod +x deploy.sh
./deploy.sh
```

### 2. Clone and setup the application

```bash
# Clone repository
cd /var/www
git clone https://github.com/Ansukaa22/intelligent-quiz.git
cd intelligent-quiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary  # For PostgreSQL
```

### 3. Environment Configuration

```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

Update the following variables in `.env`:
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-minimum-50-characters-long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DB_NAME=intelligent_quiz_prod
DB_USER=quiz_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-your-production-api-key
```

### 4. Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE intelligent_quiz_prod;
CREATE USER quiz_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE intelligent_quiz_prod TO quiz_user;
ALTER USER quiz_user CREATEDB;
\q
```

### 5. Django Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py create_subcategories

# Collect static files
python manage.py collectstatic --noinput
```

### 6. Server Configuration

#### Supervisor Setup
```bash
# Copy supervisor config
sudo cp deployment/intelligent_quiz.conf /etc/supervisor/conf.d/

# Update paths in config file
sudo nano /etc/supervisor/conf.d/intelligent_quiz.conf
# Change /path/to/your/venv and /path/to/intelligent-quiz to actual paths

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start intelligent_quiz
```

#### Nginx Setup
```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/intelligent_quiz

# Update paths in config file
sudo nano /etc/nginx/sites-available/intelligent_quiz
# Change /path/to/intelligent-quiz to actual path
# Update server_name with your domain

# Enable site
sudo ln -s /etc/nginx/sites-available/intelligent_quiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

### 8. Final Steps

```bash
# Test the application
curl -I https://yourdomain.com

# Check logs
sudo supervisorctl status intelligent_quiz
sudo tail -f /var/log/intelligent_quiz/gunicorn.log

# Set up log rotation
sudo nano /etc/logrotate.d/intelligent_quiz
```

Add to logrotate:
```
/var/log/intelligent_quiz/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        supervisorctl restart intelligent_quiz
    endscript
}
```

## 🔧 Configuration Files

- `intelligent_quiz.conf` - Supervisor configuration for Gunicorn
- `nginx.conf` - Nginx web server configuration
- `deploy.sh` - Initial server setup script

## 📊 Monitoring

After deployment, set up monitoring:

1. **Error Tracking**: Consider adding Sentry
2. **Server Monitoring**: CPU, memory, disk usage
3. **Application Monitoring**: Response times, error rates

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
cd /var/www/intelligent-quiz
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo supervisorctl restart intelligent_quiz
```

## 🛡️ Security Checklist

- [ ] Strong SECRET_KEY (50+ characters)
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] SSL/HTTPS enabled
- [ ] Secure cookies enabled
- [ ] Database credentials secure
- [ ] File permissions correct
- [ ] Firewall configured
- [ ] Regular security updates

## 📞 Support

If you encounter issues:
1. Check application logs: `sudo tail -f /var/log/intelligent_quiz/gunicorn.log`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify supervisor status: `sudo supervisorctl status`

---

**Note**: This is a basic production setup. For high-traffic sites, consider load balancing, Redis caching, and CDN setup.