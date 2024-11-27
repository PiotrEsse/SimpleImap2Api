#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_message $RED "Error: Docker is not running"
        exit 1
    fi
}

# Function to create and check .env file
check_env() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_message $YELLOW "Created .env file from .env.example"
            print_message $YELLOW "Please update the .env file with your settings"
            exit 1
        else
            print_message $RED "Error: .env.example file not found"
            exit 1
        fi
    fi
}

# Function to run development environment
dev() {
    check_docker
    check_env
    print_message $GREEN "Starting development environment..."
    docker-compose up --build
}

# Function to run production environment
prod() {
    check_docker
    check_env
    print_message $GREEN "Starting production environment..."
    docker-compose -f docker-compose.prod.yml up -d --build
}

# Function to stop all containers
stop() {
    check_docker
    print_message $GREEN "Stopping all containers..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
}

# Function to create database backup
backup() {
    check_docker
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_${timestamp}.sql"
    print_message $GREEN "Creating database backup: ${backup_file}"
    docker-compose exec db pg_dump -U $DB_USER $DB_NAME > "backups/${backup_file}"
}

# Function to restore database from backup
restore() {
    check_docker
    if [ -z "$1" ]; then
        print_message $RED "Error: Please provide backup file name"
        exit 1
    fi
    if [ ! -f "backups/$1" ]; then
        print_message $RED "Error: Backup file not found: $1"
        exit 1
    fi
    print_message $GREEN "Restoring database from: $1"
    docker-compose exec -T db psql -U $DB_USER $DB_NAME < "backups/$1"
}

# Function to run tests
test() {
    check_docker
    print_message $GREEN "Running tests..."
    docker-compose exec web python manage.py test
}

# Function to create superuser
createsuperuser() {
    check_docker
    print_message $GREEN "Creating superuser..."
    docker-compose exec web python manage.py createsuperuser
}

# Function to run migrations
migrate() {
    check_docker
    print_message $GREEN "Running migrations..."
    docker-compose exec web python manage.py migrate
}

# Function to make migrations
makemigrations() {
    check_docker
    print_message $GREEN "Making migrations..."
    docker-compose exec web python manage.py makemigrations
}

# Function to collect static files
collectstatic() {
    check_docker
    print_message $GREEN "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
}

# Function to show logs
logs() {
    check_docker
    if [ -z "$1" ]; then
        print_message $GREEN "Showing logs for all services..."
        docker-compose logs -f
    else
        print_message $GREEN "Showing logs for $1..."
        docker-compose logs -f $1
    fi
}

# Function to sync emails
sync_emails() {
    check_docker
    print_message $GREEN "Syncing emails..."
    docker-compose exec web python manage.py sync_emails
}

# Function to show help
show_help() {
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev              Start development environment"
    echo "  prod             Start production environment"
    echo "  stop             Stop all containers"
    echo "  backup           Create database backup"
    echo "  restore [file]   Restore database from backup"
    echo "  test             Run tests"
    echo "  createsuperuser  Create superuser"
    echo "  migrate          Run migrations"
    echo "  makemigrations   Make migrations"
    echo "  collectstatic    Collect static files"
    echo "  logs [service]   Show logs (optionally for specific service)"
    echo "  sync_emails      Run email synchronization"
    echo "  help             Show this help message"
}

# Main script logic
case "$1" in
    dev)
        dev
        ;;
    prod)
        prod
        ;;
    stop)
        stop
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    test)
        test
        ;;
    createsuperuser)
        createsuperuser
        ;;
    migrate)
        migrate
        ;;
    makemigrations)
        makemigrations
        ;;
    collectstatic)
        collectstatic
        ;;
    logs)
        logs "$2"
        ;;
    sync_emails)
        sync_emails
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0
