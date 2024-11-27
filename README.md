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

## Documentation

- [API Documentation](apidoc.md) - Detailed API specification
- [Postman Collection](SimpleImap2Api.postman_collection.json) - Ready-to-use API collection for testing

## Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SimpleImap2Api.git
cd SimpleImap2Api
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Edit the .env file with your settings:
```bash
# Django settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=simple_imap2api
DB_USER=dbuser
DB_PASSWORD=your-secure-password
```

4. Start the services:
```bash
./manage.sh prod
```

5. Create a superuser:
```bash
./manage.sh createsuperuser
```

### Development Setup

1. Start development environment:
```bash
./manage.sh dev
```

2. Run migrations:
```bash
./manage.sh migrate
```

3. Create superuser:
```bash
./manage.sh createsuperuser
```

## Usage

### Web Interface

1. Access the admin interface at `/admin`
2. Add IMAP server configuration
3. Configure sync settings:
   - Select folders to sync
   - Set sync limits (time-based or message count)
   - Enable/disable trash folder exclusion
4. Access emails at the root URL `/`

### API Usage

1. Obtain authentication token:
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

### Management Commands

The `manage.sh` script provides common operations:

```bash
./manage.sh help          # Show available commands
./manage.sh dev          # Start development environment
./manage.sh prod         # Start production environment
./manage.sh stop         # Stop all containers
./manage.sh backup       # Create database backup
./manage.sh restore      # Restore database from backup
./manage.sh sync_emails  # Run email synchronization
```

## Configuration

### Environment Variables

Key environment variables:

```bash
DJANGO_SECRET_KEY        # Django secret key
DJANGO_DEBUG            # Debug mode (True/False)
ALLOWED_HOSTS           # Comma-separated list of allowed hosts
DB_NAME                 # Database name
DB_USER                # Database user
DB_PASSWORD            # Database password
REDIS_URL              # Redis connection URL
```

### Sync Settings

Configure in the admin interface or API:

- Sync limit types:
  * All messages
  * Last N messages
  * Messages from last N days/weeks/months
- Folder selection
- Trash folder exclusion
- SSL/TLS settings

## Development

### Project Structure

```
SimpleImap2Api/
├── api/                # API implementation
├── emails/            # Core email functionality
├── templates/         # HTML templates
├── static/           # Static files
├── media/            # User-uploaded files
├── logs/             # Application logs
└── backups/          # Database backups
```

### Running Tests

```bash
./manage.sh test
```

## Production Deployment

1. Update production settings:
   - Set secure passwords
   - Configure allowed hosts
   - Enable SSL/TLS
   - Set up proper email backend

2. Deploy using Docker:
```bash
./manage.sh prod
```

3. Set up SSL certificate:
   - Configure SSL in nginx.conf
   - Update allowed hosts
   - Enable secure cookies

4. Set up regular backups:
```bash
./manage.sh backup
```

## Security Considerations

1. Use strong passwords
2. Enable SSL/TLS for IMAP connections
3. Keep Django secret key secure
4. Use HTTPS in production
5. Regularly update dependencies
6. Monitor server logs
7. Back up database regularly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

- Create an issue for bug reports
- Submit pull requests for improvements
- Check documentation for common issues
