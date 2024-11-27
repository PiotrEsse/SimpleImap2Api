# Simple IMAP2API

A Django-based system that fetches emails from IMAP servers and provides access through a web interface and REST API. The system is designed to be simple yet powerful, with features like email threading, folder management, and flexible sync options.

## Features

### Core Functionality
- IMAP server integration with SSL/TLS support
- Email threading support
- Flexible sync options (all messages, last N messages, time-based)
- Folder management with exclusion rules
- Web interface for email viewing and management
- REST API compatible with Gmail API structure
- Token-based authentication

### Email Processing
- UTF-8 encoding support
- Full email content storage (headers, body, attachments)
- Thread detection and grouping
- Folder-based organization

### Web Interface
- Responsive design using Bootstrap
- Email list with threading support
- Advanced search and filtering
- IMAP server management
- User authentication

### API Features
- RESTful endpoints
- Token authentication
- Search and filtering capabilities
- Thread-aware email retrieval
- Folder management

## Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/PiotrEsse/SimpleImap2Api.git
cd SimpleImap2Api
```

2. Create a `.env` file:
```bash
# Django settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=simple_imap2api
DB_USER=dbuser
DB_PASSWORD=dbpassword
DB_HOST=db
DB_PORT=5432
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SimpleImap2Api.git
cd SimpleImap2Api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### IMAP Server Setup

1. Log in to the admin interface at `/admin`
2. Add a new IMAP server configuration:
   - Server name (for identification)
   - Host and port
   - Username and password
   - SSL/TLS settings
   - Sync options:
     * All messages
     * Last N messages
     * Messages from last N days/weeks/months
   - Folder settings:
     * Specific folders to sync
     * Exclude trash option

### Email Syncing

#### Manual Sync
Use the web interface:
1. Go to IMAP Servers page
2. Click "Sync" button for the desired server

#### Automated Sync
Set up a cron job to run:
```bash
# In Docker:
docker-compose exec web python manage.py sync_emails

# Manual installation:
python manage.py sync_emails
```

Optional parameters:
- `--user <id>`: Sync specific user's servers
- `--days <number>`: Override sync period

## API Usage

### Authentication

1. Obtain an authentication token:
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

2. Use the token in requests:
```bash
curl -H "Authorization: Token your_token_here" \
     http://localhost:8000/api/emails/
```

### API Endpoints

#### Emails
- `GET /api/emails/`: List emails
- `GET /api/emails/{id}/`: Get email details
- `GET /api/emails/{id}/thread/`: Get email thread
- `GET /api/emails/threads/`: List email threads

Query parameters:
- `q`: Search term
- `folder`: Filter by folder
- `date_from`, `date_to`: Date range
- `thread`: Show threaded view

#### IMAP Servers
- `GET /api/imap-servers/`: List servers
- `POST /api/imap-servers/`: Add server
- `PUT /api/imap-servers/{id}/`: Update server
- `POST /api/imap-servers/{id}/sync/`: Trigger sync

## Docker Deployment

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  web:
    build: .
    command: gunicorn simple_imap2api.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - 8000
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DEBUG=${DJANGO_DEBUG}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
    depends_on:
      - db

  nginx:
    image: nginx:1.21
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "simple_imap2api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Production Deployment

1. Set up environment variables in `.env`
2. Build and start containers:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

4. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Set up cron job for email syncing:
```bash
docker-compose exec web python manage.py sync_emails
```

## Security Considerations

1. Use strong passwords
2. Enable SSL/TLS for IMAP connections
3. Keep Django secret key secure
4. Use HTTPS in production
5. Regularly update dependencies
6. Monitor server logs
7. Back up database regularly

## Troubleshooting

### Common Issues

1. Connection errors:
   - Check IMAP server credentials
   - Verify SSL/TLS settings
   - Check firewall rules

2. Sync issues:
   - Check folder permissions
   - Verify folder names
   - Check server timeout settings

3. Threading issues:
   - Verify message IDs
   - Check reference headers
   - Validate email format

### Logs

Access logs in Docker:
```bash
docker-compose logs web
```

Access Django logs:
```bash
tail -f logs/debug.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit pull request

## License

MIT License - see LICENSE file for details
