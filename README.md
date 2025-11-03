# 🔍 Complete Regex Intelligence Exchange

A comprehensive technology fingerprinting pattern database with **1500+ real patterns** and a complete web interface.

## ✨ Features

- **🎯 1500+ Technology Patterns** - Real patterns from Apache, Nginx, PHP, WordPress, and hundreds more
- **🔍 Advanced Search** - Search by vendor, category, or keyword with real-time filtering
- **🧪 Pattern Testing** - Test your text against all patterns to identify technologies
- **📊 Analytics Dashboard** - Comprehensive statistics and visualizations
- **🌐 Complete REST API** - Full API with interactive documentation
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🖥️ Cross-Platform** - Runs on Windows, macOS, and Linux
- **⚡ Zero Configuration** - No database setup required
- **🔄 Real-Time Integration** - Continuously updates with latest patterns from external sources

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ (tested on Python 3.8-3.13)
- pip (Python package manager)

### Installation & Setup

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or use the web directory runner:
   ```bash
   cd web
   python run.py
   ```

4. **Access the application:**
   - **Web Interface:** http://127.0.0.1:5000
   - **API Documentation:** http://127.0.0.1:5000/api/docs/
   - **Search:** http://127.0.0.1:5000/search
   - **Analytics:** http://127.0.0.1:5000/analytics
   - **Pattern Tester:** http://127.0.0.1:5000/test

## 🔄 Real-Time Data Integration

The Regex Intelligence Exchange includes a real-time integration system that continuously fetches and adds pattern data from external sources:

### Supported Sources
- **WhatWeb** - Web scanner with extensive technology detection
- **Wappalyzer** - Technology detection library
- **WebTech** - Web technology identification tool

### How to Use

To add all real-time data in your format:

1. **One-Time Integration:**
   ```bash
   # Run integration once
   python tools/integration-scripts/import-all-sources.py
   ```

2. **Scheduled Integration (Continuous):**
   ```bash
   # Run continuous integration (checks for updates every 24 hours)
   python tools/monitor-integration.py
   ```

### Integration Details

All data is automatically:
- Fetched from external repositories
- Converted to your standardized JSON format
- Stored in the `patterns/by-vendor` directory
- Standardized and validated for consistency

For detailed usage instructions, see the [tools directory README](tools/README.md)

## 🎯 Usage Examples

### Web Interface
1. **Dashboard** - Overview of all patterns and statistics
2. **Search** - Find patterns by vendor, category, or keyword
3. **Pattern Details** - View detailed regex patterns and test them
4. **Analytics** - Comprehensive charts and statistics
5. **Pattern Tester** - Test your text against all patterns

### API Usage

```bash
# Search for Apache patterns
curl "http://localhost:5000/api/v1/patterns?q=apache&limit=5"

# Get specific pattern
curl "http://localhost:5000/api/v1/patterns/apache/apache"

# Match patterns against text
curl -X POST "http://localhost:5000/api/v1/match" \
  -H "Content-Type: application/json" \
  -d '{"text": "Server: Apache/2.4.41 (Ubuntu)"}'

# Get analytics summary
curl "http://localhost:5000/api/v1/analytics/summary"

# Get all categories
curl "http://localhost:5000/api/v1/categories"

# Get all vendors
curl "http://localhost:5000/api/v1/vendors"
```

### Python Integration

```python
import requests

# Search patterns
response = requests.get('http://localhost:5000/api/v1/patterns?q=nginx')
patterns = response.json()

# Match text against patterns
response = requests.post('http://localhost:5000/api/v1/match', 
                        json={'text': 'Server: nginx/1.18.0'})
matches = response.json()

for match in matches:
    print(f"Found: {match['vendor']} {match['product']} {match.get('version', '')}")
```

## 📊 Pattern Database

The database includes patterns for:

- **Web Servers** - Apache, Nginx, IIS, Lighttpd, Cherokee, and more
- **Programming Languages** - PHP, Python, Java, Ruby, Node.js, and more  
- **Databases** - MySQL, PostgreSQL, MongoDB, Redis, and more
- **CMS Platforms** - WordPress, Drupal, Joomla, and hundreds more
- **Security Tools** - Firewalls, WAFs, security scanners
- **Network Devices** - Routers, switches, cameras, printers
- **And much more!**

### Statistics
- **Total Patterns:** 1500+
- **Categories:** 50+
- **Vendors:** 800+
- **Technologies:** Web, Security, Database, Network, CMS, and more

## 🛠️ Configuration

### Command Line Options

```bash
python main.py --help

Options:
  --mode {web,api,both}  Run mode: web interface, API only, or both (default: web)
  --host TEXT            Host to bind to (default: 127.0.0.1)
  --port INTEGER         Port to bind to (default: 5000)
  --debug                Enable debug mode
  --api-port INTEGER     API port (when running in "both" mode, default: 5001)
```

### Examples

```bash
# Run web interface only
python main.py --mode web

# Run API only
python main.py --mode api

# Run both web and API
python main.py --mode both

# Run on all interfaces
python main.py --host 0.0.0.0

# Use different port
python main.py --port 8080

# Enable debug mode
python main.py --debug

# Combine options
python main.py --mode both --host 0.0.0.0 --port 8080 --api-port 8081
```

## 🌐 API Documentation

The application includes interactive API documentation powered by Swagger UI:

- **URL:** http://localhost:5000/api/docs/
- **Features:** Interactive testing, request/response examples, schema documentation

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/patterns` | List all patterns with filtering |
| GET | `/api/v1/patterns/{vendor_id}/{product_id}` | Get specific pattern |
| POST | `/api/v1/match` | Match text against patterns |
| GET | `/api/v1/categories` | Get all categories |
| GET | `/api/v1/vendors` | Get all vendors |
| GET | `/api/v1/analytics/summary` | Get analytics data |
| GET | `/api/v1/health` | Health check |

## 🔧 Development

### Project Structure

```
web/
├── app.py                 # Main application
├── run.py                 # Simple startup script
├── requirements.txt       # Dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── search.html       # Search page
│   ├── pattern_detail.html # Pattern details
│   ├── analytics.html    # Analytics dashboard
│   ├── test.html         # Pattern tester
│   └── 404.html          # Error page
└── patterns/             # Pattern database
    └── by-vendor/        # Organized by vendor
```

### Adding Custom Patterns

Patterns are stored as JSON files in the `patterns/by-vendor/` directory. Each vendor has its own subdirectory with JSON files containing pattern definitions.

Example pattern structure:
```json
{
  "vendor": "Apache",
  "product": "Apache HTTP Server",
  "vendor_id": "apache",
  "product_id": "apache",
  "category": "web",
  "subcategory": "web-server",
  "all_versions": [
    {
      "name": "HTTP Server Header",
      "pattern": "Server:\\s*Apache/([\\d.]+)",
      "version_range": ">=1.0.0"
    }
  ]
}
```

## 🚀 Deployment

### Production Deployment

For production deployment, consider using a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Docker Deployment

Create a `Dockerfile`:

``dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY web/ .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t regex-intelligence-exchange .
docker run -p 5000:5000 regex-intelligence-exchange
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your patterns or improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Pattern data sourced from various open source projects
- Built with Flask, Bootstrap, and Chart.js
- Inspired by technology fingerprinting tools

---

**🎉 Enjoy using the Complete Regex Intelligence Exchange!**

For questions, issues, or contributions, please visit the project repository.