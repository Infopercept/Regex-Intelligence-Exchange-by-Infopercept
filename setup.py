#!/usr/bin/env python3
"""
Setup script for Regex Intelligence Exchange
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        return False
    return True


def install_dependencies():
    """Install required Python dependencies."""
    print("Installing Python dependencies...")
    
    # Required packages
    required_packages = [
        "packaging"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"Package '{package}' already installed")
        except ImportError:
            print(f"Installing '{package}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed '{package}'")
            except subprocess.CalledProcessError:
                print(f"Failed to install '{package}'")
                return False
    
    return True


def validate_setup():
    """Validate that the setup is correct."""
    print("Validating setup...")
    
    # Check if required directories exist
    required_dirs = [
        "patterns",
        "tools",
        "tests"
    ]
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"Error: Required directory '{dir_name}' not found")
            return False
    
    # Check if required files exist
    required_files = [
        "tools/version_utils.py",
        "tools/enhanced-validation.py",
        "tools/test-patterns.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Error: Required file '{file_path}' not found")
            return False
    
    # Test importing version utilities
    try:
        sys.path.insert(0, "tools")
        import importlib
        version_utils = importlib.import_module("version_utils")
        print("Version utilities imported successfully")
    except ImportError as e:
        print(f"Error importing version utilities: {e}")
        return False
    
    return True


def run_initial_tests():
    """Run initial tests to verify setup."""
    print("Running initial tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/run_tests.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("Initial tests passed")
            return True
        else:
            print("Initial tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Initial tests timed out")
        return False
    except Exception as e:
        print(f"Error running initial tests: {e}")
        return False


def create_sample_config():
    """Create a sample configuration file."""
    print("Creating sample configuration...")
    
    config = {
        "version": "1.0.0",
        "last_updated": "2025-10-28",
        "pattern_directories": [
            "patterns/by-vendor"
        ],
        "default_category": "web",
        "performance": {
            "cache_enabled": True,
            "precompile_patterns": True
        }
    }
    
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("Sample configuration created")
        return True
    except Exception as e:
        print(f"Error creating sample configuration: {e}")
        return False


def print_usage():
    """Print usage instructions."""
    print("""
Regex Intelligence Exchange Setup Complete!

Usage:
  # Run tests
  python tests/run_tests.py

  # Validate all patterns
  python tools/validate-all-patterns.py

  # Test pattern matching
  python tools/test-patterns.py

  # Add new patterns
  python tools/validate-new-pattern.py <pattern_file>

  # Import external patterns
  python tools/import-wappalyzer.py
  python tools/import-webtech.py

  # Check for duplicates
  python tools/check-duplicates.py

  # Optimize patterns
  python tools/optimize-patterns.py

For more information, see the README.md file.
""")


def main():
    """Main setup function."""
    print("Setting up Regex Intelligence Exchange...")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Validate setup
    if not validate_setup():
        return 1
    
    # Run initial tests
    if not run_initial_tests():
        return 1
    
    # Create sample configuration
    if not create_sample_config():
        return 1
    
    # Print usage instructions
    print_usage()
    
    print("Setup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())