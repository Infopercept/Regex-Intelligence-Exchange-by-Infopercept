#!/usr/bin/env python3
"""
Simple startup script for Regex Intelligence Exchange
Cross-platform compatible
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the main application
from app import main

if __name__ == '__main__':
    main()