#!/usr/bin/env python3
"""
Setup script for Regex Intelligence Exchange Web Interface
"""

import os
import sys
import subprocess
import platform


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        return False
    return True


def install_dependencies():
    """Install required Python dependencies."""
    print("Installing Python dependencies...")
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Error: pip is not available")
        return False
    
    # Install requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def validate_setup():
    """Validate that the web interface setup is correct."""
    print("Validating web interface setup...")
    
    # Check if required directories exist
    required_dirs = [
        "templates",
        "static",
        "static/css",
        "static/js",
        "api",
        "api/v1",
        "app",
        "config",
        "utils",
        "tests"
    ]
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"Error: Required directory '{dir_name}' not found")
            return False
    
    # Check if required files exist
    required_files = [
        "app/app.py",
        "api/app.py",
        "app/routes.py",
        "api/v1/routes.py",
        "templates/base.html",
        "templates/index.html",
        "templates/search.html",
        "templates/analytics.html",
        "templates/pattern_detail.html",
        "static/css/style.css",
        "static/js/main.js",
        "config/__init__.py",
        "config/development.py",
        "config/production.py",
        "config/testing.py",
        "utils/__init__.py",
        "utils/pattern_loader.py",
        "utils/pattern_matcher.py",
        "utils/version_utils.py",
        "tests/__init__.py",
        "tests/test_api.py",
        "tests/test_web.py",
        "tests/conftest.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Error: Required file '{file_path}' not found")
            return False
    
    # Test importing Flask
    try:
        import flask
        print("Flask imported successfully")
    except ImportError as e:
        print(f"Error importing Flask: {e}")
        return False
    
    return True


def print_usage():
    """Print usage instructions."""
    print("""
Regex Intelligence Exchange Web Interface Setup Complete!

To run the web interface:

1. Start the main web application:
   python -m app.app

2. Start the RESTful API (in a separate terminal):
   python -m api.app

3. Access the web interface:
   Open http://localhost:5000 in your browser

4. Access the RESTful API:
   API endpoints available at http://localhost:5001/api/v1/

API Endpoints:
  GET  /api/v1/patterns              - Get all patterns
  GET  /api/v1/patterns/<vendor>/<product> - Get specific pattern
  POST /api/v1/match                 - Match patterns against text
  GET  /api/v1/categories            - Get all categories
  GET  /api/v1/vendors               - Get all vendors
  GET  /api/v1/stats                 - Get database statistics
  GET  /api/v1/health                - Health check

For more information, see the project documentation.
""")


def main():
    """Main setup function."""
    print("Setting up Regex Intelligence Exchange Web Interface...")
    
    # Change to web directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Validate setup
    if not validate_setup():
        return 1
    
    # Print usage instructions
    print_usage()
    
    print("Web interface setup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())