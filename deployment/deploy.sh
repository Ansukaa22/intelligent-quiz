#!/bin/bash

# Intelligent Quiz Deployment Script
# Run this script on your Ubuntu/Debian server

set -e

echo "🚀 Starting Intelligent Quiz deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx supervisor
sudo apt install -y certbot python3-certbot-nginx

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/intelligent-quiz
sudo chown -R $USER:$USER /var/www/intelligent-quiz

# Create logs directory
echo "📝 Creating logs directory..."
sudo mkdir -p /var/log/intelligent_quiz
sudo chown -R $USER:$USER /var/log/intelligent_quiz

# Create media directory
echo "🖼️ Creating media directory..."
sudo mkdir -p /var/www/intelligent-quiz/media
sudo chown -R $USER:$USER /var/www/intelligent-quiz/media

echo "✅ Basic server setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone https://github.com/Ansukaa22/intelligent-quiz.git /var/www/intelligent-quiz"
echo "2. Set up Python virtual environment and install dependencies"
echo "3. Configure environment variables"
echo "4. Set up PostgreSQL database"
echo "5. Run migrations and collect static files"
echo "6. Configure supervisor and nginx"
echo "7. Set up SSL certificate"