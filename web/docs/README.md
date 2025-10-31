# Regex Intelligence Exchange Web Interface Documentation

## Overview

This directory contains documentation for the web interface and RESTful API of the Regex Intelligence Exchange project.

## Documentation Files

- [API Documentation](api_comprehensive.md) - Complete API reference with endpoints, parameters, and examples
- [Web Interface Guide](web-interface.md) - User guide for the web interface
- [Development Guide](development.md) - Guide for developers working on the web interface
- [Deployment Guide](deployment_guide.md) - Instructions for deploying the web interface

## Web Interface

The web interface provides a user-friendly way to explore the pattern database, search for specific patterns, and test pattern matching capabilities.

### Features

- **Dashboard** - Overview of the pattern database with key statistics
- **Search** - Advanced search functionality with filtering options
- **Pattern Details** - Detailed view of individual patterns with metadata
- **Analytics** - Visualizations and statistics about the pattern database
- **Pattern Testing** - Ability to test patterns against custom input text

### Access

The web interface is available at `http://localhost:5000` when running locally.

## RESTful API

The RESTful API provides programmatic access to the pattern database and pattern matching capabilities.

### Features

- **Pattern Retrieval** - Get information about patterns with filtering and pagination
- **Pattern Matching** - Match patterns against input text
- **Metadata Access** - Get information about categories, vendors, and statistics
- **Health Monitoring** - Check the health status of the API

### Access

The RESTful API is available at `http://localhost:5001/api/v1` when running locally.

See [API Documentation](api_comprehensive.md) for detailed information about endpoints and usage.

## Development

For developers working on the web interface, see [Development Guide](development.md) for setup instructions, coding standards, and contribution guidelines.

## Deployment

For deployment instructions, see [Deployment Guide](deployment_guide.md).