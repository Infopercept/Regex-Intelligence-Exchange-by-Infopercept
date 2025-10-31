# Regex Intelligence Exchange API Documentation

## Overview

The Regex Intelligence Exchange provides a comprehensive RESTful API for accessing and working with technology fingerprinting patterns. This API allows developers to integrate pattern matching capabilities into their own applications for technology detection, security scanning, and web application analysis.

## Base URL

```
http://localhost:5001/api/v1
```

In production environments, this will be your configured domain.

## Authentication

The current version of the API does not require authentication for read operations. However, this may change in future versions to support rate limiting and access control.

## Rate Limiting

There are currently no rate limits enforced on the API. In production environments, rate limiting may be implemented to prevent abuse.

## Content Types

All API requests and responses use JSON format.

- **Request Content-Type**: `application/json`
- **Response Content-Type**: `application/json`

## Error Handling

All API endpoints follow standard HTTP status codes:

- **200**: Success
- **400**: Bad Request - Invalid parameters or missing required fields
- **404**: Not Found - Resource not found
- **500**: Internal Server Error - Server-side error

Error responses follow this format:

```json
{
  "error": "Error message describing the problem",
  "status_code": 400
}
```

## Endpoints

### Get All Patterns

```
GET /patterns
```

Retrieve a list of all patterns with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Description | Default | Max |
|-----------|------|-------------|---------|-----|
| limit | integer | Limit the number of patterns returned | 20 | 100 |
| offset | integer | Offset for pagination | 0 | N/A |
| category | string | Filter by category | N/A | N/A |
| vendor | string | Filter by vendor ID | N/A | N/A |
| q | string | Search query (vendor, product, or category) | N/A | N/A |

#### Response

```json
{
  "patterns": [
    {
      "vendor": "Apache",
      "vendor_id": "apache",
      "product": "Apache",
      "product_id": "apache",
      "category": "web",
      "subcategory": "web-server",
      "pattern_count": 5
    }
  ],
  "total": 1577,
  "offset": 0,
  "limit": 20
}
```

#### Example Requests

```bash
# Get all patterns
curl http://localhost:5001/api/v1/patterns

# Get first 10 web patterns
curl "http://localhost:5001/api/v1/patterns?category=web&limit=10"

# Search for Apache patterns
curl "http://localhost:5001/api/v1/patterns?q=apache"

# Get patterns for specific vendor
curl "http://localhost:5001/api/v1/patterns?vendor=microsoft"
```

### Get Specific Pattern

```
GET /patterns/{vendor_id}/{product_id}
```

Retrieve detailed information for a specific pattern.

#### Path Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| vendor_id | string | Vendor ID | Yes |
| product_id | string | Product ID | Yes |

#### Response

```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "Apache",
  "product_id": "apache",
  "category": "web",
  "subcategory": "web-server",
  "versions": {},
  "all_versions": [
    {
      "name": "Apache Pattern",
      "pattern": "<title>Test\\ Page\\ for\\ Apache\\ Installation</title>",
      "version_group": 0,
      "priority": 100,
      "confidence": 0.8,
      "metadata": {
        "author": "WhatWeb Project",
        "created_at": "2025-01-01",
        "updated_at": "2025-01-01",
        "description": "Pattern extracted from WhatWeb plugin for Apache",
        "tags": ["whatweb", "extracted"],
        "test_cases": [
          {
            "input": "<title>Test Page for Apache Installation</title>",
            "expected_version": "unknown"
          }
        ],
        "source": "WhatWeb",
        "license": "MIT",
        "severity": "low",
        "cvss_score": 0.0,
        "cwe_ids": [],
        "affected_versions": [],
        "remediation": "Keep the software updated to the latest stable version",
        "compiled_pattern": true
      }
    }
  ]
}
```

#### Example Request

```bash
# Get Apache pattern details
curl http://localhost:5001/api/v1/patterns/apache/apache
```

### Match Patterns

```
POST /match
```

Match patterns against input text to identify technologies.

#### Request Body

```json
{
  "text": "Server: Apache/2.4.41 (Ubuntu)"
}
```

#### Response

```json
[
  {
    "vendor": "Apache",
    "product": "Apache",
    "vendor_id": "apache",
    "product_id": "apache",
    "pattern_name": "HTTP Server Header",
    "matched_text": "Server: Apache/2.4.41 (Ubuntu)",
    "version": "2.4.41",
    "version_range": null
  }
]
```

#### Example Request

```bash
# Match text against patterns
curl -X POST http://localhost:5001/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"text": "Server: Apache/2.4.41 (Ubuntu)"}'
```

### Get Categories

```
GET /categories
```

Retrieve a list of all available categories.

#### Response

```json
{
  "categories": [
    "web",
    "security",
    "database",
    "os",
    "framework"
  ]
}
```

#### Example Request

```bash
# Get all categories
curl http://localhost:5001/api/v1/categories
```

### Get Vendors

```
GET /vendors
```

Retrieve a list of all available vendors.

#### Response

```json
{
  "vendors": [
    "Apache",
    "Microsoft",
    "Oracle",
    "IBM"
  ]
}
```

#### Example Request

```bash
# Get all vendors
curl http://localhost:5001/api/v1/vendors
```

### Get Statistics

```
GET /stats
```

Retrieve database statistics and distribution information.

#### Response

```json
{
  "total_patterns": 1577,
  "categories": {
    "web": 800,
    "security": 200,
    "database": 150,
    "os": 100,
    "framework": 327
  },
  "subcategories": {
    "web-server": 300,
    "web-application": 500,
    "firewall": 150,
    "ids": 50,
    "unknown": 677
  },
  "last_updated": "2025-01-01T12:00:00Z"
}
```

#### Example Request

```bash
# Get database statistics
curl http://localhost:5001/api/v1/stats
```

### Health Check

```
GET /health
```

Check the health status of the API service.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "pattern_count": 1577
}
```

#### Example Request

```bash
# Check API health
curl http://localhost:5001/api/v1/health
```

## Data Models

### Pattern

Represents a technology fingerprinting pattern.

```json
{
  "vendor": "string",
  "vendor_id": "string",
  "product": "string",
  "product_id": "string",
  "category": "string",
  "subcategory": "string",
  "pattern_count": "integer"
}
```

### Pattern Detail

Detailed information about a specific pattern.

```json
{
  "vendor": "string",
  "vendor_id": "string",
  "product": "string",
  "product_id": "string",
  "category": "string",
  "subcategory": "string",
  "versions": "object",
  "all_versions": [
    {
      "name": "string",
      "pattern": "string",
      "version_group": "integer",
      "priority": "integer",
      "confidence": "number",
      "metadata": "object"
    }
  ]
}
```

### Pattern Metadata

Metadata associated with a pattern.

```json
{
  "author": "string",
  "created_at": "string",
  "updated_at": "string",
  "description": "string",
  "tags": ["string"],
  "test_cases": [
    {
      "input": "string",
      "expected_version": "string"
    }
  ],
  "source": "string",
  "license": "string",
  "severity": "string",
  "cvss_score": "number",
  "cwe_ids": ["string"],
  "affected_versions": ["string"],
  "remediation": "string",
  "compiled_pattern": "boolean"
}
```

## Usage Examples

### Python

```python
import requests

# Get all patterns
response = requests.get('http://localhost:5001/api/v1/patterns')
patterns = response.json()

# Search for specific patterns
response = requests.get('http://localhost:5001/api/v1/patterns?category=web&limit=10')
web_patterns = response.json()

# Match patterns against text
data = {'text': 'Server: Apache/2.4.41 (Ubuntu)'}
response = requests.post('http://localhost:5001/api/v1/match', json=data)
matches = response.json()

# Get pattern details
response = requests.get('http://localhost:5001/api/v1/patterns/apache/apache')
apache_pattern = response.json()
```

### JavaScript

```javascript
// Get all patterns
fetch('http://localhost:5001/api/v1/patterns')
  .then(response => response.json())
  .then(data => console.log(data));

// Search for specific patterns
fetch('http://localhost:5001/api/v1/patterns?category=web&limit=10')
  .then(response => response.json())
  .then(data => console.log(data));

// Match patterns against text
fetch('http://localhost:5001/api/v1/match', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({text: 'Server: Apache/2.4.41 (Ubuntu)'})
})
  .then(response => response.json())
  .then(data => console.log(data));

// Get pattern details
fetch('http://localhost:5001/api/v1/patterns/apache/apache')
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Get all patterns
curl http://localhost:5001/api/v1/patterns

# Search for web patterns
curl "http://localhost:5001/api/v1/patterns?category=web&limit=5"

# Match text against patterns
curl -X POST http://localhost:5001/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"text": "Server: Apache/2.4.41 (Ubuntu)"}'

# Get pattern details
curl http://localhost:5001/api/v1/patterns/apache/apache

# Get categories
curl http://localhost:5001/api/v1/categories

# Get vendors
curl http://localhost:5001/api/v1/vendors

# Get statistics
curl http://localhost:5001/api/v1/stats

# Health check
curl http://localhost:5001/api/v1/health
```

## Best Practices

### Pagination

When retrieving large lists of patterns, use pagination to improve performance:

```bash
# Get first page
curl "http://localhost:5001/api/v1/patterns?limit=50&offset=0"

# Get second page
curl "http://localhost:5001/api/v1/patterns?limit=50&offset=50"
```

### Filtering

Use filtering to reduce the amount of data transferred:

```bash
# Filter by category
curl "http://localhost:5001/api/v1/patterns?category=web"

# Filter by vendor
curl "http://localhost:5001/api/v1/patterns?vendor=apache"

# Combine filters
curl "http://localhost:5001/api/v1/patterns?category=web&vendor=apache"
```

### Error Handling

Always check HTTP status codes and handle errors appropriately:

```python
import requests

response = requests.get('http://localhost:5001/api/v1/patterns')
if response.status_code == 200:
    patterns = response.json()
elif response.status_code == 404:
    print("Patterns not found")
elif response.status_code == 500:
    print("Server error")
else:
    print(f"Unexpected error: {response.status_code}")
```

## SDKs

Currently, there are no official SDKs available. However, the API can be easily integrated using standard HTTP libraries in any programming language.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.

## Versioning

This documentation covers API version 1 (`/api/v1/`). Future versions will be available at `/api/v2/`, etc.

## Changelog

### v1.0.0
- Initial release
- Basic pattern retrieval
- Pattern matching functionality
- Category and vendor listings
- Statistics and health endpoints

## Security Considerations

- The API does not currently implement authentication
- Input validation is performed on all parameters
- Rate limiting may be implemented in future versions
- HTTPS is recommended for production deployments