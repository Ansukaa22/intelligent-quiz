#!/bin/bash

# 🚀 Intelligent Quiz - Automated VPS Deployment Script
# Run this script on your Ubuntu 22.04 LTS server as root

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables (edit these before running)
DOMAIN_NAME="yourdomain.com"
WWW_DOMAIN="www.${DOMAIN_NAME}"
APP_USER="intelligent_quiz"
APP_DIR="/home/${APP_USER}/intelligent-quiz"
DB_NAME="intelligent_quiz_prod"
DB_USER="quiz_user"
DB_PASSWORD="CHANGE_THIS_STRONG_PASSWORD"
DJANGO_SECRET_KEY="CHANGE_THIS_TO_A_VERY_LONG_RANDOM_SECRET_KEY_MINIMUM_50_CHARS"
OPENAI_API_KEY="sk-your-openai-api-key-here"
EMAIL_HOST_USER="your-email@gmail.com"
EMAIL_HOST_PASSWORD="your-email-app-password"

echo -e "${BLUE}🚀 Starting Intelligent Quiz VPS Deployment${NC}"
echo "=================================================="

# Function to print status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

echo "Step 1: Updating system packages..."
apt update && apt upgrade -y
print_status "System updated"

echo "Step 2: Installing required packages..."
apt install -y python3 python3-pip python3-venv python3-dev postgresql postgresql-contrib nginx supervisor git curl wget htop iotop ncdu tree fail2ban ufw certbot python3-certbot-nginx
print_status "Packages installed"

echo "Step 3: Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 22/tcp
print_status "Firewall configured"

echo "Step 4: Creating application user..."
if id "$APP_USER" &>/dev/null; then
    print_warning "User $APP_USER already exists"
else
    useradd -m -s /bin/bash $APP_USER
    usermod -aG sudo $APP_USER
    print_status "User $APP_USER created"
fi

echo "Step 5: Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || print_warning "Database $DB_NAME may already exist"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || print_warning "User $DB_USER may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
print_status "PostgreSQL configured"

echo "Step 6: Cloning repository..."
if [ -d "$APP_DIR" ]; then
    print_warning "Directory $APP_DIR already exists, pulling latest changes..."
    cd $APP_DIR
    git pull origin main
else
    mkdir -p /home/$APP_USER
    chown $APP_USER:$APP_USER /home/$APP_USER
    su - $APP_USER -c "git clone https://github.com/Ansukaa22/intelligent-quiz.git $APP_DIR"
fi
print_status "Repository ready"

echo "Step 7: Setting up Python environment..."
su - $APP_USER -c "cd $APP_DIR && python3 -m venv venv"
su - $APP_USER -c "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt && pip install psycopg2-binary gunicorn"
print_status "Python environment ready"

echo "Step 8: Creating environment configuration..."
cat > $APP_DIR/.env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$DJANGO_SECRET_KEY
ALLOWED_HOSTS=$DOMAIN_NAME,$WWW_DOMAIN
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL=noreply@$DOMAIN_NAME

# OpenAI
OPENAI_API_KEY=$OPENAI_API_KEY

# Security
CSRF_TRUSTED_ORIGINS=https://$DOMAIN_NAME,https://$WWW_DOMAIN
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env
print_status "Environment configured"

echo "Step 9: Setting up directories and permissions..."
mkdir -p /var/log/intelligent_quiz
chown $APP_USER:$APP_USER /var/log/intelligent_quiz
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/media
chown -R $APP_USER:$APP_USER $APP_DIR
print_status "Directories and permissions set"

echo "Step 10: Running Django migrations..."
su - $APP_USER -c "cd $APP_DIR && source venv/bin/activate && python manage.py migrate"
print_status "Database migrated"

echo "Step 11: Collecting static files..."
su - $APP_USER -c "cd $APP_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"
print_status "Static files collected"

echo "Step 12: Configuring Supervisor..."
cat > /etc/supervisor/conf.d/intelligent_quiz.conf << EOF
[program:intelligent_quiz]
command=$APP_DIR/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 30
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/intelligent_quiz/gunicorn.log
stderr_logfile=/var/log/intelligent_quiz/gunicorn_error.log
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8
EOF

supervisorctl reread
supervisorctl update
print_status "Supervisor configured"

echo "Step 13: Configuring Nginx..."
cat > /etc/nginx/sites-available/intelligent_quiz << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME $WWW_DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $APP_DIR/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# Enable site and disable default
ln -sf /etc/nginx/sites-available/intelligent_quiz /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t
systemctl restart nginx
print_status "Nginx configured"

echo ""
echo -e "${GREEN}🎉 Basic deployment completed!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Point your domain DNS to this server's IP address"
echo "2. Run SSL certificate setup:"
echo "   sudo certbot --nginx -d $DOMAIN_NAME -d $WWW_DOMAIN"
echo "3. Create Django superuser:"
echo "   su - $APP_USER"
echo "   cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo "4. Load initial quiz data:"
echo "   python manage.py create_subcategories"
echo "5. Test your application at https://$DOMAIN_NAME"
echo ""
echo "🔍 Useful commands:"
echo "- Check app status: sudo supervisorctl status"
echo "- View app logs: sudo tail -f /var/log/intelligent_quiz/gunicorn.log"
echo "- Restart app: sudo supervisorctl restart intelligent_quiz"
echo "- Check nginx: sudo systemctl status nginx"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "- Change default passwords in this script"
echo "- Set up regular backups"
echo "- Configure monitoring"
echo "- Test all functionality thoroughly"