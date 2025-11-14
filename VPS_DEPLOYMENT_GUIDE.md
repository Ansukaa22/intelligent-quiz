# 🚀 VPS Deployment Guide for Intelligent Quiz

## Step 1: Choose a VPS Provider

### Recommended Options (November 2025):

#### 🏆 **DigitalOcean** (Easiest for beginners)
- **Cost**: $6/month (1GB RAM, 1 vCPU, 25GB SSD)
- **Pros**: Simple interface, good documentation, 1-click apps
- **Setup Time**: 5 minutes
- **URL**: https://digitalocean.com

#### 🥈 **Linode** (Best performance)
- **Cost**: $5/month (1GB RAM, 1 vCPU, 25GB SSD)
- **Pros**: Excellent performance, advanced networking
- **Setup Time**: 10 minutes
- **URL**: https://linode.com

#### 🥉 **AWS Lightsail** (If you have AWS credits)
- **Cost**: $3.50/month (512MB RAM, 1 vCPU, 20GB SSD)
- **Pros**: AWS ecosystem, scalable
- **Setup Time**: 15 minutes
- **URL**: https://aws.amazon.com/lightsail

#### 🏠 **Hetzner** (Budget option)
- **Cost**: €3.29/month (1GB RAM, 1 vCPU, 20GB SSD)
- **Pros**: Very cheap, good performance
- **Setup Time**: 10 minutes
- **URL**: https://hetzner.com

### VPS Requirements:
- **OS**: Ubuntu 22.04 LTS (latest LTS)
- **RAM**: Minimum 1GB, Recommended 2GB
- **Storage**: 25GB SSD minimum
- **CPU**: 1 vCPU minimum

## Step 2: Initial Server Setup

After provisioning your VPS, connect via SSH:

```bash
# Connect to your server (replace with your server's IP)
ssh root@YOUR_SERVER_IP
```

### Update System and Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx supervisor
sudo apt install -y git curl wget
sudo apt install -y certbot python3-certbot-nginx

# Install additional tools
sudo apt install -y htop iotop ncdu tree
sudo apt install -y fail2ban ufw

# Clean up
sudo apt autoremove -y
```

### Configure Firewall

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp

# Check status
sudo ufw status
```

### Create Application User

```bash
# Create non-root user
sudo adduser intelligent_quiz
sudo usermod -aG sudo intelligent_quiz

# Switch to new user
su - intelligent_quiz
```

## Step 3: PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE intelligent_quiz_prod;
CREATE USER quiz_user WITH PASSWORD 'your-very-strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE intelligent_quiz_prod TO quiz_user;
ALTER USER quiz_user CREATEDB;

# Exit PostgreSQL
\\q
```

## Step 4: Application Deployment

```bash
# Clone repository
cd /home/intelligent_quiz
git clone https://github.com/Ansukaa22/intelligent-quiz.git
cd intelligent-quiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary gunicorn

# Create logs directory
mkdir -p logs
```

## Step 5: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Add these production values:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-minimum-50-characters-long-here-make-it-very-long-and-random
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DB_NAME=intelligent_quiz_prod
DB_USER=quiz_user
DB_PASSWORD=your-very-strong-database-password-here
DB_HOST=localhost
DB_PORT=5432

# Email (configure with your email provider)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-your-production-openai-api-key-here

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Step 6: Database Migration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial quiz data
python manage.py create_subcategories

# Collect static files
python manage.py collectstatic --noinput
```

## Step 7: Gunicorn Setup

```bash
# Create supervisor config
sudo cp deployment/intelligent_quiz.conf /etc/supervisor/conf.d/

# Edit paths in supervisor config
sudo nano /etc/supervisor/conf.d/intelligent_quiz.conf

# Update these lines:
command=/home/intelligent_quiz/intelligent-quiz/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 30
directory=/home/intelligent_quiz/intelligent-quiz
user=intelligent_quiz

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start intelligent_quiz
```

## Step 8: Nginx Configuration

```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/intelligent_quiz

# Edit nginx config
sudo nano /etc/nginx/sites-available/intelligent_quiz

# Update server_name and paths:
server_name yourdomain.com www.yourdomain.com;

location /static/ {
    alias /home/intelligent_quiz/intelligent-quiz/staticfiles/;
}

location /media/ {
    alias /home/intelligent_quiz/intelligent-quiz/media/;
}

# Enable site
sudo ln -s /etc/nginx/sites-available/intelligent_quiz /etc/nginx/sites-enabled/

# Remove default nginx site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Step 9: SSL Certificate

```bash
# Get SSL certificate (run after DNS is pointed to server)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

## Step 10: Final Testing

```bash
# Check all services
sudo supervisorctl status
sudo systemctl status nginx

# Test application
curl -I https://yourdomain.com

# Check logs
sudo tail -f /var/log/intelligent_quiz/gunicorn.log
sudo tail -f /var/log/nginx/error.log
```

## 🔧 Troubleshooting

### Common Issues:

1. **Permission Errors**
```bash
sudo chown -R intelligent_quiz:intelligent_quiz /home/intelligent_quiz
sudo chown -R intelligent_quiz:intelligent_quiz /var/log/intelligent_quiz
```

2. **Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

3. **Database Connection Issues**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
python manage.py dbshell
```

4. **Application Not Starting**
```bash
# Check supervisor logs
sudo supervisorctl tail intelligent_quiz

# Check environment variables
python manage.py shell -c "import os; print(os.environ.get('DJANGO_SETTINGS_MODULE'))"
```

## 📊 Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Check system resources
htop

# Check disk usage
df -h

# Check application logs
sudo tail -f /var/log/intelligent_quiz/gunicorn.log
```

## 🔄 Updates

To update the application:

```bash
cd /home/intelligent_quiz/intelligent-quiz
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart intelligent_quiz
```

---

**🎯 Ready to deploy? Choose your VPS provider and let's get your Intelligent Quiz application live!**