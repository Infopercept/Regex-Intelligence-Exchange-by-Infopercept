# Regex Intelligence Exchange Web Interface

This directory contains the modern web interface and RESTful API for the Regex Intelligence Exchange project.

The application features a modern architecture with:
- RESTful API with automatic documentation using Flask-RESTX
- Web interface with responsive Bootstrap 5 design
- Proper separation of concerns with models, services, and utilities
- Security measures including input validation and sanitization
- Comprehensive logging and error handling
- Configuration management for different environments
- Caching for better performance

## Project Structure

```
web/
├── api/                    # RESTful API implementation
│   ├── v1/                 # API version 1
│   │   ├── __init__.py
│   │   ├── routes.py       # API route definitions
│   │   ├── controllers/    # API controllers
│   │   └── models/         # API data models
│   ├── __init__.py
│   └── app.py              # API application factory
├── app/                    # Web application
│   ├── __init__.py
│   ├── routes.py           # Web route definitions
│   ├── controllers/        # Web controllers
│   ├── models/             # Web data models
│   └── app.py              # Web application factory
├── config/                 # Configuration files
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── search.html
│   ├── pattern_detail.html
│   ├── analytics.html
│   └── partials/           # Template partials
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── pattern_loader.py
│   ├── pattern_matcher.py
│   └── version_utils.py
├── services/               # Business logic services
│   ├── __init__.py
│   └── pattern_service.py  # Pattern service implementation
├── models/                 # Data models
│   ├── __init__.py
│   └── pattern.py          # Pattern data models
├── deploy/                 # Deployment scripts
│   ├── __init__.py
│   └── deploy.py           # Deployment automation
├── docs/                   # Documentation
├── tests/                  # Web interface tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_web.py
│   └── conftest.py
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # Setup script
├── run.py                 # Main entry point
└── README.md              # This file
```

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

If you encounter any dependency issues, you may need to ensure you have compatible versions:

```bash
pip install "flask-restx>=1.3.0" "werkzeug>=3.0.0"
```

### Running the Applications

```bash
# Run both web interface and API (default)
python run.py

# Run only the web interface
python run.py --mode web

# Run only the RESTful API
python run.py --mode api

# Run with custom options
python run.py --mode both --port 8000 --api-port 8001 --debug
```

## API Documentation

API documentation is available at `/api/docs` when the API is running.

The API features:
- Automatic interactive documentation with Swagger UI
- Detailed endpoint descriptions and examples
- Request/response model definitions
- Error response documentation

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_api.py
```

## Features

- **Modern Web Interface**: Responsive Bootstrap 5 design with intuitive navigation
- **RESTful API**: Fully documented REST API with versioning
- **Pattern Search**: Advanced search capabilities with filtering by category, vendor, or text
- **Pattern Matcher**: Real-time pattern matching against custom text
- **Analytics Dashboard**: Insights and statistics about the pattern database
- **Security Features**: Input validation, sanitization, and secure API access
- **Performance Optimizations**: Caching and efficient pattern loading
- **Comprehensive Documentation**: Both user guides and API documentation

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Usage

### Running the Application

1. Start the application:
   ```bash
   python run.py
   ```

2. Access the web interface:
   Open http://localhost:5000 in your browser

3. Access the API documentation:
   Open http://localhost:5001/api/docs in your browser

### API Endpoints

All API endpoints are available at http://localhost:5001/api/v1/

- `GET /patterns` - Get all patterns with optional filtering
- `GET /patterns/<vendor_id>/<product_id>` - Get a specific pattern
- `POST /match` - Match patterns against input text
- `GET /categories` - Get all available categories
- `GET /vendors` - Get all available vendors
- `GET /stats` - Get database statistics
- `GET /health` - Health check endpoint

See the interactive API documentation at `/api/docs` for detailed information about each endpoint, parameters, and response formats.

### API Parameters

#### GET /patterns
- `limit` (int): Limit the number of results
- `offset` (int): Offset for pagination (default: 0)
- `category` (string): Filter by category
- `vendor` (string): Filter by vendor ID
- `q` (string): Search query

Example:
```
GET /api/v1/patterns?category=web&limit=10&offset=0
```

#### POST /match
```json
{
  "text": "Server: Apache/2.4.41 (Ubuntu)"
}
```

## API Response Formats

### Pattern List
```json
{
  "patterns": [
    {
      "vendor": "Apache",
      "vendor_id": "apache",
      "product": "HTTPD",
      "product_id": "apache-httpd",
      "category": "web",
      "subcategory": "web-server",
      "pattern_count": 3
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": null
}
```

### Pattern Detail
```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "HTTPD",
  "product_id": "apache-httpd",
  "category": "web",
  "subcategory": "web-server",
  "versions": {
    "2.4.x": [
      {
        "name": "Apache HTTPD Server 2.4 Banner",
        "pattern": "Server: Apache/2\\.4\\.([\\d]+)",
        "version_group": 1,
        "priority": 180,
        "confidence": 0.9
      }
    ]
  },
  "all_versions": [
    {
      "name": "Apache HTTPD Server Generic",
      "pattern": "Server: Apache/([\\d.]+)",
      "version_group": 1,
      "priority": 100,
      "confidence": 0.8
    }
  ]
}
```

### Match Results
```json
[
  {
    "vendor": "Apache",
    "product": "HTTPD",
    "vendor_id": "apache",
    "product_id": "apache-httpd",
    "pattern_name": "Apache HTTPD Server Generic",
    "matched_text": "Server: Apache/2.4.41 (Ubuntu)",
    "version": "2.4.41"
  }
]
```

## Security Considerations

- Input validation and sanitization on all endpoints
- CORS configuration for controlled API access
- Secure pattern ID validation
- Comprehensive logging of API access and security events
- No exposure of sensitive system information
- Protection against common web vulnerabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file in the main project directory for details.