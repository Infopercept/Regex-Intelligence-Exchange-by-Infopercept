# Regex Intelligence Exchange by Infopercept Documentation

Welcome to the documentation for the Regex Intelligence Exchange by Infopercept!

## Overview

The Regex Intelligence Exchange by Infopercept is an open-source collection of regex patterns designed to help security researchers, penetration testers, and developers identify software versions through service banners, HTTP responses, and other network protocol responses.

Our database now includes:
- Community-driven version detection patterns
- Structured regex pattern data in JSON format
- Machine-readable data for tool integration
- Open-source collaboration under MIT license
- Comprehensive test cases for pattern validation
- **Web-based interface** for non-technical users
- **RESTful API** for integration with security tools

## Getting Started

If you're new to the Regex Intelligence Exchange by Infopercept, start here:

- [Contribution Guidelines](../CONTRIBUTING.md) - How to contribute to the project
- [Pattern Template](../patterns/TEMPLATE.md) - Understanding our pattern structure

## Web Interface

The project now includes a user-friendly web interface:

1. Navigate to the `web/` directory
2. Run `python setup.py` to install dependencies
3. Start the web application with `python app.py`
4. Start the RESTful API with `python api.py`
5. Access the web interface at `http://localhost:5000`

## API Access

For programmatic access, use our RESTful API:

- Base URL: `http://localhost:5001/api/v1/`
- Endpoints:
  - `GET /patterns` - Get all patterns
  - `GET /patterns/<vendor>/<product>` - Get specific pattern
  - `POST /match` - Match patterns against text
  - `GET /categories` - Get all categories
  - `GET /vendors` - Get all vendors
  - `GET /stats` - Get database statistics
  - `GET /health` - Health check

## User Guides

### For Security Researchers
- [Contributing Patterns](../CONTRIBUTING.md) - How to submit new version detection patterns
- [Pattern Development](../patterns/TEMPLATE.md) - Creating effective regex patterns for version detection

### For Security Teams
- [Using Pattern Data](../patterns/README.md) - How to integrate our patterns with security tools
- [Pattern Categories](../PATTERN_CATEGORIZATION.md) - Understanding pattern organization by service type

### For Developers
- [Validation Tools](../tools/README.md) - Tools for validating pattern files
- [Pattern Testing](../tools/README.md) - How to test patterns against real service responses
- [Duplicate Management](../tools/README.md) - Tools for managing duplicate patterns

## Community Resources

### Participation
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Our community standards
- [Community Discussions](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/discussions) - Engage with other community members
- [Issue Tracker](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/issues) - Report bugs and request features

### Contribution
- [Good First Issues](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - Issues suitable for newcomers
- [Help Wanted](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) - Opportunities for more experienced contributors

## Development

### Project Information
- [Changelog](../RELEASE.md) - History of changes to the database
- [Security Policy](../SECURITY.md) - How to report security vulnerabilities

### Technical Documentation
- [Pattern Validation](../tools/README.md) - Scripts for validating pattern files
- [Enhanced Validation](../ENHANCED_VALIDATION.md) - Advanced validation features
- [Pattern Categorization](../PATTERN_CATEGORIZATION.md) - Pattern classification system
- [Metadata Enhancements](../METADATA_ENHANCEMENTS.md) - Additional metadata fields
- [Version Extraction](../VERSION_EXTRACTION.md) - Version processing utilities

## Support

If you need help with the Regex Intelligence Exchange by Infopercept:

1. Check the documentation in this directory
2. Review existing issues and discussions
3. Ask questions in [GitHub Discussions](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/discussions)
4. Contact maintainers directly for complex issues

## License

The Regex Intelligence Exchange by Infopercept documentation is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

## Deployment

This site is manually deployed. When new changes are pushed to the master branch, follow the manual deployment steps outlined in the [DEPLOYMENT.md](../DEPLOYMENT.md) file in the main repository.