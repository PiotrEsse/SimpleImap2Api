# Simple IMAP2API - API Documentation

## Overview

The Simple IMAP2API provides a RESTful API for managing IMAP email accounts and accessing email data. The API is designed to be compatible with the Gmail API structure where possible.

## Base URL

```
http://your-domain/api/
```

## Authentication

The API uses token-based authentication. All requests must include an Authorization header:

```
Authorization: Token your-token-here
```

### Obtaining a Token

```http
POST /api-token-auth/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "token": "your-auth-token"
}
```

## API Endpoints

### IMAP Servers

#### List IMAP Servers

```http
GET /api/imap-servers/
```

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "My Gmail",
            "host": "imap.gmail.com",
            "port": 993,
            "username": "user@gmail.com",
            "use_ssl": true,
            "sync_limit_type": "days",
            "sync_limit_value": 30,
            "folders_to_sync": "INBOX,Sent",
            "exclude_trash": true,
            "last_sync": "2024-11-27T12:00:00Z"
        }
    ]
}
```

#### Create IMAP Server

```http
POST /api/imap-servers/
Content-Type: application/json

{
    "name": "My Gmail",
    "host": "imap.gmail.com",
    "port": 993,
    "username": "user@gmail.com",
    "password": "your-password",
    "use_ssl": true,
    "sync_limit_type": "days",
    "sync_limit_value": 30,
    "folders_to_sync": "INBOX,Sent",
    "exclude_trash": true
}
```

#### Update IMAP Server

```http
PUT /api/imap-servers/{id}/
Content-Type: application/json

{
    "name": "Updated Gmail",
    "sync_limit_type": "weeks",
    "sync_limit_value": 2
}
```

#### Delete IMAP Server

```http
DELETE /api/imap-servers/{id}/
```

#### Sync IMAP Server

```http
POST /api/imap-servers/{id}/sync/
```

Response:
```json
{
    "status": "success",
    "message": "Email sync completed"
}
```

### Emails

#### List Emails

```http
GET /api/emails/
```

Query Parameters:
- `q`: Search term (searches in subject, sender, recipient, body)
- `folder`: Filter by folder name
- `imap_server`: Filter by IMAP server ID
- `date_from`: Filter by date (format: YYYY-MM-DD)
- `date_to`: Filter by date (format: YYYY-MM-DD)
- `thread`: Show threaded view (true/false)
- `ordering`: Sort field (e.g., -date, subject)
- `page`: Page number
- `page_size`: Results per page

Response:
```json
{
    "count": 100,
    "next": "http://your-domain/api/emails/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "message_id": "<message-id>",
            "subject": "Email Subject",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com",
            "date": "2024-11-27T12:00:00Z",
            "folder": "INBOX",
            "thread_id": "thread-123",
            "thread_count": 3
        }
    ]
}
```

#### Get Email Details

```http
GET /api/emails/{id}/
```

Response:
```json
{
    "id": 1,
    "message_id": "<message-id>",
    "subject": "Email Subject",
    "sender": "sender@example.com",
    "recipient": "recipient@example.com",
    "date": "2024-11-27T12:00:00Z",
    "body_text": "Plain text content",
    "body_html": "<html>HTML content</html>",
    "folder": "INBOX",
    "created_at": "2024-11-27T12:00:00Z",
    "updated_at": "2024-11-27T12:00:00Z",
    "thread_id": "thread-123",
    "in_reply_to": "<parent-message-id>",
    "thread_emails": [
        {
            "id": 2,
            "subject": "Re: Email Subject",
            "sender": "another@example.com",
            "recipient": "sender@example.com",
            "date": "2024-11-27T12:30:00Z",
            "body_text": "Reply content",
            "body_html": "<html>Reply HTML content</html>",
            "folder": "INBOX"
        }
    ]
}
```

#### Get Email Thread

```http
GET /api/emails/{id}/thread/
```

Response:
```json
[
    {
        "id": 1,
        "subject": "Original Email",
        "sender": "sender@example.com",
        "recipient": "recipient@example.com",
        "date": "2024-11-27T12:00:00Z",
        "body_text": "Original content",
        "body_html": "<html>Original HTML content</html>",
        "folder": "INBOX"
    },
    {
        "id": 2,
        "subject": "Re: Original Email",
        "sender": "recipient@example.com",
        "recipient": "sender@example.com",
        "date": "2024-11-27T12:30:00Z",
        "body_text": "Reply content",
        "body_html": "<html>Reply HTML content</html>",
        "folder": "INBOX"
    }
]
```

#### List Email Threads

```http
GET /api/emails/threads/
```

Response:
```json
{
    "count": 50,
    "next": "http://your-domain/api/emails/threads/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "subject": "Thread Subject",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com",
            "date": "2024-11-27T12:00:00Z",
            "folder": "INBOX",
            "thread_id": "thread-123",
            "thread_count": 3
        }
    ]
}
```

#### List Available Folders

```http
GET /api/emails/folders/
```

Response:
```json
[
    "INBOX",
    "Sent",
    "Important",
    "Work",
    "Personal"
]
```

#### Get Email Statistics

```http
GET /api/emails/statistics/
```

Response:
```json
{
    "total_emails": 1250,
    "total_threads": 428,
    "folders": {
        "INBOX": 500,
        "Sent": 300,
        "Important": 200,
        "Work": 150,
        "Personal": 100
    }
}
```

## Error Responses

### Authentication Error

```json
{
    "detail": "Invalid token."
}
```

### Validation Error

```json
{
    "field_name": [
        "Error message"
    ]
}
```

### Server Error

```json
{
    "detail": "Internal server error message"
}
```

## Rate Limiting

The API implements rate limiting based on user authentication:

- Authenticated users: 1000 requests per hour
- Anonymous users: 100 requests per hour

Rate limit response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638024000
```

## Pagination

All list endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 50, max: 100)

## Filtering and Searching

Most list endpoints support:
- Field filtering using query parameters
- Search using the `q` parameter
- Ordering using the `ordering` parameter (prefix with `-` for descending order)

## Data Formats

- All timestamps are in ISO 8601 format
- All requests and responses use UTF-8 encoding
- Request bodies should be JSON
- Response bodies are JSON

## API Versioning

The current API version is v1. The version is included in the URL:
```
/api/v1/...
```

Future versions will be available at `/api/v2/`, etc., when released.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins in development and configurable in production.

## Security

- All requests must use HTTPS in production
- Authentication tokens are required for all endpoints except token generation
- Passwords are never returned in responses
- Rate limiting protects against abuse
- Request size limits are enforced

## Webhook Support

The API supports webhooks for the following events:
- Email sync completion
- New email arrival
- Thread updates

Webhook configuration is available through the admin interface.
