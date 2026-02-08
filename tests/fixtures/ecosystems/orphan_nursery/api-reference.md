# API Reference

> Complete list of available endpoints and methods.

## Authentication

All requests require API key authentication via Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### GET /services

List all available services.

**Response:**
```json
{
  "services": [
    {"id": "compute", "name": "Compute"},
    {"id": "storage", "name": "Object Storage"}
  ]
}
```

### GET /services/{id}

Get details about a specific service.

**Parameters:**
- `id` (string): Service identifier

**Response:** Service details object
