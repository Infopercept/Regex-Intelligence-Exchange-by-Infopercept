# Development Guide

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
├── tests/                  # Web interface tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_web.py
│   └── conftest.py
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── pattern_loader.py
│   ├── pattern_matcher.py
│   └── version_utils.py
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # Setup script
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git
   ```

2. Navigate to the web directory:
   ```bash
   cd Regex-Intelligence-Exchange-by-Infopercept/web
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. Run the setup script:
   ```bash
   python setup.py
   ```

### Running the Applications

#### Web Application

```bash
# Run the web application
python -m app.app
```

The web interface will be available at `http://localhost:5000`.

#### RESTful API

```bash
# Run the RESTful API
python -m api.app
```

The API will be available at `http://localhost:5001/api/v1`.

## Development Workflow

### Code Structure

The project follows a modular structure with clear separation of concerns:

1. **API Layer** (`api/`) - RESTful API implementation
2. **Web Layer** (`app/`) - Web application with HTML templates
3. **Configuration** (`config/`) - Environment-specific configuration
4. **Utilities** (`utils/`) - Shared utility functions
5. **Tests** (`tests/`) - Unit and integration tests

### Adding New Features

1. **API Endpoints**
   - Add new routes in `api/v1/routes.py`
   - Implement controller logic in `api/v1/controllers/`
   - Add data models in `api/v1/models/` if needed

2. **Web Pages**
   - Add new routes in `app/routes.py`
   - Create HTML templates in `templates/`
   - Add static assets in `static/` if needed

3. **Utilities**
   - Add utility functions in `utils/`
   - Ensure proper documentation and type hints

### Testing

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run tests with coverage
pytest --cov=app --cov=api tests/
```

#### Writing Tests

Tests should follow the Arrange-Act-Assert pattern:

```python
def test_example(client):
    # Arrange
    expected_result = "expected value"
    
    # Act
    response = client.get('/api/endpoint')
    data = response.get_json()
    
    # Assert
    assert response.status_code == 200
    assert data['result'] == expected_result
```

### Code Quality

#### Linting

```bash
# Run flake8
flake8 .

# Run black formatter
black .
```

#### Type Checking

```bash
# Run mypy (if configured)
mypy .
```

### Configuration

The application supports multiple environments:

- **Development** - `config/development.py`
- **Production** - `config/production.py`
- **Testing** - `config/testing.py`

Configuration can be selected by setting the `FLASK_ENV` environment variable or by passing the configuration name to the `create_app()` function.

## API Documentation

API documentation is automatically generated using Flask-RESTX and is available at `/api/docs` when the API is running.

To update the API documentation:

1. Add docstrings to your API resources
2. Use Flask-RESTX decorators for request/response models
3. The documentation will be automatically updated

## Frontend Development

### Templates

Templates use Jinja2 templating engine with Bootstrap 5 for styling.

### CSS

Custom CSS is located in `static/css/style.css`. Avoid inline styles and use CSS classes whenever possible.

### JavaScript

Custom JavaScript is located in `static/js/main.js`. The project uses vanilla JavaScript with Bootstrap 5 components.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request

### Code Review Process

All pull requests must be reviewed by at least one maintainer before merging.

### Style Guide

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for all public functions and classes
- Add type hints where possible
- Keep functions small and focused
- Write tests for new functionality

## Deployment

See [Deployment Guide](deployment.md) for deployment instructions.