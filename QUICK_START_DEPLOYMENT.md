# 🚀 Quick Start VPS Deployment Checklist

## Pre-Deployment (Local Machine)

### 1. Choose VPS Provider
- [ ] **DigitalOcean** ($6/month) - Recommended for beginners
- [ ] **Linode** ($5/month) - Best performance
- [ ] **AWS Lightsail** ($3.50/month) - If you have AWS credits
- [ ] **Hetzner** (€3.29/month) - Budget option

**Requirements:**
- Ubuntu 22.04 LTS
- 1GB RAM minimum (2GB recommended)
- 25GB SSD storage

### 2. Domain Setup
- [ ] Register domain name (Namecheap, GoDaddy, etc.)
- [ ] Point domain DNS to VPS IP address
- [ ] Wait for DNS propagation (can take 24-48 hours)

### 3. Prepare Credentials
- [ ] Generate strong Django SECRET_KEY (50+ characters)
- [ ] Get OpenAI API key
- [ ] Set up email account for notifications
- [ ] Choose strong database password

## Server Deployment (VPS)

### 4. Initial Server Access
```bash
# Connect to your VPS
ssh root@YOUR_VPS_IP

# Download deployment script
wget https://raw.githubusercontent.com/Ansukaa22/intelligent-quiz/main/deploy_vps.sh
chmod +x deploy_vps.sh
```

### 5. Configure Deployment Script
```bash
# Edit the script with your actual values
nano deploy_vps.sh

# Update these variables at the top:
DOMAIN_NAME="yourdomain.com"
DB_PASSWORD="your-very-strong-db-password"
DJANGO_SECRET_KEY="your-50-plus-character-secret-key"
OPENAI_API_KEY="sk-your-openai-key"
EMAIL_HOST_USER="your-email@gmail.com"
EMAIL_HOST_PASSWORD="your-email-password"
```

### 6. Run Automated Deployment
```bash
# Run the deployment script
./deploy_vps.sh
```

### 7. Post-Deployment Setup
```bash
# Create Django superuser
su - intelligent_quiz
cd intelligent-quiz
source venv/bin/activate
python manage.py createsuperuser

# Load quiz categories
python manage.py create_subcategories
```

### 8. SSL Certificate
```bash
# After DNS is propagated, get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

## Testing & Verification

### 9. Test Application
- [ ] Visit https://yourdomain.com
- [ ] Test user registration
- [ ] Test quiz functionality
- [ ] Test admin panel
- [ ] Check all static files load

### 10. Verify Services
```bash
# Check all services are running
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql

# Check logs for errors
sudo tail -f /var/log/intelligent_quiz/gunicorn.log
sudo tail -f /var/log/nginx/error.log
```

## Monitoring & Maintenance

### 11. Set Up Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Check system resources
htop

# Set up log rotation
sudo nano /etc/logrotate.d/intelligent_quiz
```

### 12. Backup Setup
```bash
# Create backup script
sudo nano /home/intelligent_quiz/backup.sh
# Add database backup commands
```

## Emergency Contacts

**If something goes wrong:**
1. Check logs: `sudo tail -f /var/log/intelligent_quiz/gunicorn.log`
2. Restart services: `sudo supervisorctl restart intelligent_quiz`
3. Check nginx: `sudo systemctl restart nginx`
4. Database issues: Check PostgreSQL status

## Cost Estimate (Monthly)

- **VPS**: $5-10
- **Domain**: $10-15
- **SSL**: Free (Let's Encrypt)
- **OpenAI API**: Variable (based on usage)
- **Total**: ~$20-30/month

---

## 🎯 Ready to Deploy?

1. **Choose your VPS provider** and create an account
2. **Register a domain** and point DNS to VPS IP
3. **Run the deployment script** on your server
4. **Test everything thoroughly**
5. **Go live!** 🚀

**Need help?** The deployment script handles 90% of the work automatically!