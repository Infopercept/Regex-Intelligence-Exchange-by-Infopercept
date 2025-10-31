# Regex Intelligence Exchange API Documentation

## Overview

The Regex Intelligence Exchange provides a RESTful API for accessing and working with technology fingerprinting patterns. This API allows developers to integrate pattern matching capabilities into their own applications.

## Base URL

```
http://localhost:5001/api/v1
```

## Authentication

The API does not currently require authentication for read operations. However, this may change in future versions.

## Rate Limiting

There are currently no rate limits enforced on the API. Please be respectful of server resources.

## Endpoints

### Get All Patterns

```
GET /patterns
```

Retrieve a list of all patterns with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Limit the number of patterns returned |
| offset | integer | Offset for pagination |
| category | string | Filter by category |
| vendor | string | Filter by vendor |
| q | string | Search query |

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
      "subcategory": "web-application",
      "pattern_count": 10
    }
  ],
  "total": 1577,
  "offset": 0,
  "limit": 20
}
```

### Get Specific Pattern

```
GET /patterns/{vendor_id}/{product_id}
```

Retrieve details for a specific pattern.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| vendor_id | string | Vendor ID |
| product_id | string | Product ID |

#### Response

```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "Apache",
  "product_id": "apache",
  "category": "web",
  "subcategory": "web-application",
  "versions": {},
  "all_versions": [
    {
      "name": "Apache Pattern",
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
      },
      "pattern": "<title>Test\\ Page\\ for\\ Apache\\ Installation</title>",
      "version_group": 0
    }
  ]
}
```

### Match Patterns

```
POST /match
```

Match patterns against input text.

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
    "version": "2.4.41"
  }
]
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

### Get Statistics

```
GET /stats
```

Retrieve database statistics.

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
    "web-application": 500,
    "web-server": 300,
    "firewall": 150,
    "ids": 50,
    "unknown": 677
  },
  "last_updated": "2025-01-01T12:00:00Z"
}
```

### Health Check

```
GET /health
```

Check the health status of the API.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "pattern_count": 1577
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Example Usage

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
```

## SDKs

Currently, there are no official SDKs available. However, the API can be easily integrated using standard HTTP libraries in any programming language.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.