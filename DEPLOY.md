# 🚀 OrderFlow API - VPS Deployment Guide

This guide will help you deploy the OrderFlow API to your VPS with full containerization using Docker and Docker Compose.

## 📋 Prerequisites

### VPS Requirements
- **OS:** Ubuntu 20.04+ or CentOS 8+ (Ubuntu recommended)
- **RAM:** Minimum 2GB (4GB recommended)
- **Storage:** Minimum 20GB
- **CPU:** 2 cores minimum

### Software Requirements
- Docker
- Docker Compose
- Git
- Nginx (for reverse proxy)

## 🔧 VPS Setup

### 1. Update System
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Logout and login again for group changes to take effect
exit
# SSH back into your VPS
```

### 3. Install Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 4. Install Nginx (Optional - for reverse proxy)
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🚀 Application Deployment

### 1. Clone Repository
```bash
# Navigate to your preferred directory
cd /opt

# Clone the repository
sudo git clone https://github.com/your-username/backend-interview.git orderflow
sudo chown -R $USER:$USER orderflow
cd orderflow
```

### 2. Environment Configuration
```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-vps-ip,your-domain.com

# Database (Docker Compose will handle this)
DATABASE_URL=postgresql://orderflow_user:orderflow_password@postgres:5432/orderflow

# Celery Settings
CELERY_BROKER_URL=amqp://orderflow_user:orderflow_password@rabbitmq:5672/orderflow
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Africa's Talking SMS
AFRICASTALKING_API_KEY=your-api-key
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_SENDER_ID=ORDERFLOW

# OIDC Settings (if using)
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_ISSUER_URL=https://your-oidc-provider.com
```

### 3. Build and Start Services
```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Database Setup
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data (if you have seeders)
docker-compose exec web python manage.py shell < seeders.py
```

### 5. Static Files
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 🔍 Service Verification

### 1. Check All Services
```bash
# Check all containers are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 2. Test API Endpoints
```bash
# Test health check
curl http://your-vps-ip:8000/api/v1/health/

# Test products endpoint
curl http://your-vps-ip:8000/api/v1/products/
```

### 3. Monitor Celery Workers
```bash
# Check Celery workers
docker-compose exec web celery -A orderflow inspect active

# Check Celery queues
docker-compose exec web celery -A orderflow inspect stats
```

## 🌐 Nginx Configuration (Optional)

### 1. Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/orderflow
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com your-vps-ip;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/orderflow/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/orderflow/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
```

### 2. Enable Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/orderflow /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## 🔒 SSL Certificate (Optional)

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring and Management

### 1. Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart celery_email_worker

# View logs
docker-compose logs -f celery_email_worker
```

### 2. Database Management
```bash
# Backup database
docker-compose exec postgres pg_dump -U orderflow_user orderflow > backup.sql

# Restore database
docker-compose exec -T postgres psql -U orderflow_user orderflow < backup.sql
```

### 3. Celery Management
```bash
# Check worker status
docker-compose exec web celery -A orderflow inspect active

# Purge all queues
docker-compose exec web celery -A orderflow purge

# Monitor tasks
docker-compose exec web celery -A orderflow events
```

## 🔧 Troubleshooting

### 1. Common Issues

**Services not starting:**
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory
free -h
```

**Database connection issues:**
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test database connection
docker-compose exec web python manage.py dbshell
```

**Celery workers not processing tasks:**
```bash
# Check RabbitMQ
docker-compose exec rabbitmq rabbitmqctl status

# Check Redis
docker-compose exec redis redis-cli ping

# Restart Celery workers
docker-compose restart celery_sms_worker celery_email_worker celery_notifications_worker
```

### 2. Performance Optimization

**Increase worker concurrency:**
```bash
# Edit docker-compose.yml and increase --concurrency=4
```

**Add more workers:**
```bash
# Scale workers
docker-compose up -d --scale celery_email_worker=3
```

## 📈 Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure email settings
- [ ] Set up SSL certificate
- [ ] Configure backup strategy
- [ ] Set up monitoring (optional)
- [ ] Configure log rotation
- [ ] Set up firewall rules
- [ ] Configure automatic updates

## 🚀 Quick Start Commands

```bash
# Complete deployment
git clone https://github.com/your-username/backend-interview.git
cd backend-interview
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput

# Check status
docker-compose ps
curl http://your-vps-ip:8000/api/v1/products/
```

## 📞 Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check service status: `docker-compose ps`
4. Test individual services

---

**🎉 Congratulations! Your OrderFlow API is now deployed and ready to use!**
