# Regex Intelligence Exchange by Infopercept

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Pattern Count](https://img.shields.io/badge/patterns-1577-blue.svg)](#)

## Overview

The Regex Intelligence Exchange is a comprehensive repository of regex patterns for technology fingerprinting. Originally derived from the WhatWeb project, this enhanced database provides accurate detection of web technologies, software versions, and security-related information.

The project now includes both a **web-based interface** for non-technical users and a **RESTful API** for integration with other security tools. It also features a **database-backed storage system** for improved performance and scalability.

## Repository Structure

```
Regex-Intelligence-Exchange/
├── patterns/                 # Main pattern database (1,577 files)
├── imported-patterns/        # Wappalyzer imported patterns (1,243 files)
├── imported-webtech-patterns/ # WebTech imported patterns (1,081 files)
├── tools/                    # Tools for pattern development and management
├── web/                      # Web interface and RESTful API
│   ├── models/               # Data models (file-based and database)
│   ├── services/             # Business logic services
│   ├── utils/                # Utility functions
│   ├── scripts/              # Migration and utility scripts
│   └── ...
├── data/                     # Supporting data files
├── docs/                     # Documentation
└── README.md                 # This file
```

## Pattern Database

### Main Patterns (`patterns/`)
The core pattern database organized by vendor containing 1,577 technology detection patterns with enhanced structure including:
- Category and subcategory classification
- Version detection capabilities
- Rich metadata with security information
- Comprehensive test cases

### Wappalyzer Integration (`imported-patterns/`)
1,243 technology patterns imported from Wappalyzer with:
- HTTP header detection
- HTML content analysis
- Meta tag identification
- JavaScript framework detection

### WebTech Integration (`imported-webtech-patterns/`)
1,081 technology patterns imported from WebTech with:
- Comprehensive technology coverage
- Multiple detection methods
- Standardized format

## Database Migration

The project now supports database-backed storage for improved performance and scalability:

### Migration Process
To migrate existing file-based patterns to the database:
```bash
cd web
python scripts/migrate_all_patterns.py
```

### Database Configuration
Configure your database connection in the environment:
```bash
# For PostgreSQL
export DATABASE_URL=postgresql://user:password@localhost/regex_exchange

# For SQLite (development)
export DATABASE_URL=sqlite:///patterns.db

# Enable database mode
export USE_DATABASE=true
```

### Switching Between Storage Modes
The application can operate in two modes:
1. **File-based mode** (default) - Reads patterns directly from JSON files
2. **Database mode** - Reads patterns from a database for better performance

To switch to database mode, set the `USE_DATABASE` environment variable to `true`.

## Web Interface

The project now includes a user-friendly web interface built with Flask:

### Features
- **Dashboard** with pattern overview and statistics
- **Search functionality** with advanced filtering by category, vendor, and keywords
- **Pattern matcher** for testing patterns against custom text
- **Analytics dashboard** with visualizations
- **Pattern detail pages** with comprehensive information
- **Responsive design** that works on desktop and mobile devices
- **Enhanced security** with CSRF protection and rate limiting
- **Improved caching** with Redis support

### Access
```bash
# Navigate to the web directory
cd web

# Install dependencies
pip install -r requirements.txt

# (Optional) Install PostgreSQL support
# pip install psycopg2-binary

# (Optional) Migrate patterns to database
python scripts/migrate_all_patterns.py

# (Optional) Enable database mode
export USE_DATABASE=true

# Start the web application
python run.py

# Access the web interface at http://localhost:5000
# Access the API documentation at http://localhost:5001/api/docs/
```

## RESTful API

The project includes a comprehensive RESTful API for integration with other security tools:

### Endpoints
- `GET /api/v1/patterns` - Get all patterns with filtering and pagination
- `GET /api/v1/patterns/<vendor>/<product>` - Get specific pattern details
- `POST /api/v1/match` - Match patterns against input text
- `GET /api/v1/categories` - Get all available categories
- `GET /api/v1/vendors` - Get all available vendors
- `GET /api/v1/stats` - Get database statistics
- `GET /api/v1/health` - Health check endpoint

### Usage
```bash
# Get all patterns
curl http://localhost:5001/api/v1/patterns

# Search for patterns
curl "http://localhost:5001/api/v1/patterns?category=web&limit=10"

# Match patterns against text
curl -X POST http://localhost:5001/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"text": "Server: Apache/2.4.41 (Ubuntu)"}'
```

## Tools

The `tools/` directory contains utilities for pattern development and management:

### Validation Tools
- `validate-new-pattern.py` - Validate individual patterns
- `validate-all-patterns.py` - Validate all patterns
- `validate-imported-patterns.py` - Validate Wappalyzer imported patterns
- `validate-webtech-patterns.py` - Validate WebTech imported patterns

### Testing Tools
- `test-patterns.py` - Test pattern functionality
- `monitor-quality.py` - Monitor pattern quality metrics

### Development Tools
- `update-patterns.py` - Update existing patterns to enhanced structure
- `add-test-cases.py` - Automatically add test cases to patterns
- `search-patterns.py` - Search patterns by various criteria
- `generate-pattern-summary.py` - Generate pattern summary reports

### Integration Tools
- `import-wappalyzer.py` - Import patterns from Wappalyzer (now skips existing patterns)
- `import-webtech.py` - Import patterns from WebTech (now skips existing patterns)
- `check-duplicates.py` - Check for duplicate patterns based on content similarity
- `merge-patterns.py` - Merge patterns from different sources intelligently

### Advanced Tools
- `ai-pattern-generator.py` - AI-powered pattern generation
- `threat-intel-integration.py` - Threat intelligence integration
- `advanced-analytics.py` - Advanced analytics and reporting
- `realtime-detection.py` - Real-time pattern detection
- `pattern-composition.py` - Pattern composition engine

## Getting Started

### For Users

To use the pattern database in your projects:

```bash
# Clone the repository
git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git

# Explore patterns
ls patterns/by-vendor/

# Use patterns in your tools
import json
with open('patterns/by-vendor/apache/apache.json', 'r') as f:
    pattern_data = json.load(f)
```

### For Web Interface Users

```bash
# Navigate to the web directory
cd web

# Install dependencies
pip install -r requirements.txt

# (Optional) Install PostgreSQL support
# pip install psycopg2-binary

# (Optional) Migrate patterns to database
python scripts/migrate_all_patterns.py

# (Optional) Enable database mode
export USE_DATABASE=true

# Start the web application
python run.py

# Access the web interface at http://localhost:5000
# Access the API documentation at http://localhost:5001/api/docs/
```

### For API Users

```bash
# Navigate to the web directory
cd web

# Install dependencies
pip install -r requirements.txt

# (Optional) Install PostgreSQL support
# pip install psycopg2-binary

# (Optional) Migrate patterns to database
python scripts/migrate_all_patterns.py

# (Optional) Enable database mode
export USE_DATABASE=true

# Start only the API
python run.py --mode api

# Access API endpoints at http://localhost:5001/api/v1/
# Access API documentation at http://localhost:5001/api/docs/
```

### Production Deployment

For production deployment, see the detailed [Production Setup Guide](PRODUCTION_SETUP.md).

Key production considerations:
- Use a production WSGI server like Gunicorn or uWSGI
- Configure a reverse proxy like Nginx or Apache
- Enable Redis for caching (recommended)
- Use PostgreSQL for database storage (recommended for production)
- Configure proper SSL/TLS certificates
- Set up process management with systemd or similar

### For Contributors

We welcome contributions from the community:

1. **Read our contribution guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Use our pattern template**: [patterns/TEMPLATE.md](patterns/TEMPLATE.md)
3. **Validate your patterns**: 
   ```bash
   python tools/validate-new-pattern.py patterns/by-vendor/my-vendor/my-product.json
   ```
4. **Test your patterns**:
   ```bash
   python tools/test-patterns.py patterns/by-vendor/my-vendor/my-product.json
   ```

## Duplicate Management

To prevent duplicate entries when importing patterns from external sources:

1. **Import scripts now check for existing patterns** and skip importing if a pattern with the same product ID already exists
2. **Use the duplicate checker** to identify potential duplicates:
   ```bash
   python tools/check-duplicates.py
   ```
3. **Use the merge tool** to intelligently combine patterns from different sources:
   ```bash
   python tools/merge-patterns.py <import-directory> <target-directory>
   ```

## Quality Assurance

We maintain high quality standards:
- **100% Test Coverage** - Every pattern has comprehensive test cases
- **Automated Validation** - Patterns are validated against strict criteria
- **Regular Quality Monitoring** - Continuous quality assessment

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The pattern database includes content derived from the WhatWeb project, which is also available under the MIT License.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- **WhatWeb Project** - Original source of many patterns
- **Wappalyzer** - Additional patterns through integration
- **WebTech** - Additional patterns through integration
- **All Contributors** - Community members who help improve the database

## Project Status

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Quality Score](https://img.shields.io/badge/quality-A+-brightgreen.svg)](#)
[![Last Commit](https://img.shields.io/github/last-commit/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.svg)](#)

This project is actively maintained with regular updates and improvements. We're constantly working to expand the pattern database, improve quality, and enhance the contributor experience.

---

*Made with ❤️ by Infopercept and the open source community*