#!/bin/bash

# OrderFlow API Deployment Script
# This script automates the deployment process on your VPS

set -e  # Exit on any error

echo "🚀 OrderFlow API Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        print_status "Created .env file from template"
        print_warning "Please edit .env file with your configuration before continuing"
        echo "Press Enter to continue after editing .env file..."
        read
    else
        print_error "env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
print_status "Building Docker images..."
docker-compose build

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service status..."
if docker-compose ps | grep -q "Up"; then
    print_status "Services are running"
else
    print_error "Some services failed to start"
    docker-compose logs
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Check if superuser exists, if not create one
print_status "Checking for superuser..."
if ! docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" 2>/dev/null | grep -q "Superuser exists"; then
    print_warning "No superuser found. You will need to create one manually:"
    echo "docker-compose exec web python manage.py createsuperuser"
fi

# Load seed data if available
if [ -f seeders.py ]; then
    print_status "Loading seed data..."
    docker-compose exec -T web python manage.py shell < seeders.py 2>/dev/null || print_warning "Failed to load seed data (this is normal if no seeders)"
fi

# Test API endpoints
print_status "Testing API endpoints..."
sleep 5

# Get the IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "🌐 Access URLs:"
echo "   API: http://$IP_ADDRESS:8000"
echo "   Admin: http://$IP_ADDRESS:8000/admin/"
echo "   RabbitMQ Management: http://$IP_ADDRESS:15672"
echo "   Flower (Celery Monitor): http://$IP_ADDRESS:5555"
echo ""
echo "📋 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Check Celery workers: docker-compose exec web celery -A orderflow inspect active"
echo ""
echo "🔧 Next Steps:"
echo "   1. Test the API: curl http://$IP_ADDRESS:8000/api/v1/products/"
echo "   2. Create superuser if needed: docker-compose exec web python manage.py createsuperuser"
echo "   3. Configure Nginx (optional) - see DEPLOY.md"
echo "   4. Set up SSL certificate (optional) - see DEPLOY.md"
echo ""
print_status "Deployment completed! 🚀"
