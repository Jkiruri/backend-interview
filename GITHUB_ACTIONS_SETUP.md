# GitHub Actions Setup Guide

## Required GitHub Variables

Go to your repository → Settings → Secrets and variables → Actions → Variables tab and add:

### Variables
- `SERVER_HOST`: ``
- `SERVER_USER`: ``
- `DEPLOY_PATH`: ``

## Required GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → Secrets tab and add:

### Secrets (private - encrypted)
- `DEPLOY_KEY`: Your SSH private key for connecting to the server

## How to Add Variables/Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click on "Variables" tab for public variables or "Secrets" tab for private keys
5. Click "New repository variable" or "New repository secret"
6. Add the name and value
7. Click "Add variable" or "Add secret"

## SSH Key Setup

### Generate SSH Key (if you don't have one):
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### Add Public Key to Server:
```bash
# Copy the public key content
cat ~/.ssh/id_rsa.pub

# On your server, add to authorized_keys
echo "your-public-key-content" >> ~/.ssh/authorized_keys
```

### Add Private Key to GitHub Secrets:
Copy the entire private key content (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) and add it as the `DEPLOY_KEY` secret.

## Workflow Features

The updated workflow includes:

✅ **Docker-based deployment** using your docker-compose.yml
✅ **Database migrations** with `python manage.py migrate`
✅ **Static file collection** with `python manage.py collectstatic`
✅ **Service health checks** and status monitoring
✅ **Graceful container management** (down → build → up)
✅ **Comprehensive logging** for deployment tracking

## Optional Seeding

For initial deployment or when you need to seed data, uncomment these lines in the workflow:
```yaml
# docker compose exec -T web python manage.py seed_data
# docker compose exec -T web python seeder/seeders.py
```

## Monitoring

After deployment, you can monitor your services:
- **Web App**: Port 8002
- **PostgreSQL**: Port 5434
- **Redis**: Port 6381
- **RabbitMQ**: Port 5674 (AMQP), 15674 (Management UI)
- **Flower**: Port 5557 (Celery monitoring)
