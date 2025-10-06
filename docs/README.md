# Regex Intelligence Exchange by Invinsense

This repository contains a collection of regex patterns used to detect software versions from various sources like HTTP headers, file contents, network responses, and more.

## Repository Structure

- `patterns/` - JSON files containing version detection patterns
- `docs/` - Static HTML documentation site
- `tools/` - Validation and utility scripts
- `patterns/TEMPLATE.md` - Template for creating new patterns
- `patterns/CONTRIBUTING.md` - Contribution guidelines

## Pattern Categories

- Web servers and applications
- Networking equipment and services
- Database systems
- Messaging systems
- Content management systems
- Operating systems
- Frameworks and libraries

## Documentation

The documentation site is available at:
- GitHub Pages: https://invinsense.github.io/regex-intelligence-exchange/

## Contributing

Please see our [contribution guidelines](patterns/CONTRIBUTING.md) for details on how to contribute new patterns or improve existing ones.

Last updated: 2025-10-01

# Regex Intelligence Exchange by Invinsense Documentation

Welcome to the documentation for the Regex Intelligence Exchange by Invinsense!

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [User Guides](#user-guides)
- [Community Resources](#community-resources)
- [Development](#development)

## Introduction

The Regex Intelligence Exchange by Invinsense is an open-source collection of regex patterns designed to help security researchers, penetration testers, and developers identify software versions through service banners, HTTP responses, and other network protocol responses.

Our database provides:
- Community-driven version detection patterns
- Structured regex pattern data in JSON format
- Machine-readable data for tool integration
- Open-source collaboration under MIT license
- Comprehensive test cases for pattern validation

## Getting Started

If you're new to the Regex Intelligence Exchange by Invinsense, start here:

- [Getting Started Guide](community/beginners-guide.html) - Introduction for new contributors and users
- [Pattern Database Guide](community/pattern-development.html) - Understanding our pattern structure and organization
- [Contribution Guidelines](../patterns/CONTRIBUTING.md) - How to contribute to the project

## User Guides

### For Security Researchers
- [Contributing Patterns](../patterns/CONTRIBUTING.md) - How to submit new version detection patterns
- [Pattern Development](community/pattern-development.html) - Creating effective regex patterns for version detection

### For Security Teams
- [Using Pattern Data](../patterns/README.md) - How to integrate our patterns with security tools
- [Pattern Categories](../patterns/README.md) - Understanding pattern organization by service type

### For Developers
- [Validation Tools](../tools/README.md) - Tools for validating pattern files
- [Pattern Testing](../tools/README.md) - How to test patterns against real service responses

## Community Resources

### Participation
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Our community standards
- [Community Discussions](https://github.com/Invinsense/regex-intelligence-exchange/discussions) - Engage with other community members
- [Issue Tracker](https://github.com/Invinsense/regex-intelligence-exchange/issues) - Report bugs and request features

### Contribution
- [Good First Issues](https://github.com/Invinsense/regex-intelligence-exchange/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - Issues suitable for newcomers
- [Help Wanted](https://github.com/Invinsense/regex-intelligence-exchange/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) - Opportunities for more experienced contributors
- [Governance](#) - How the project is managed

## Development

### Project Information
- [Changelog](../RELEASE.md) - History of changes to the database
- [Roadmap](#) - (Coming Soon) Future development plans
- [Security Policy](../SECURITY.md) - How to report security vulnerabilities

### Technical Documentation
- [Pattern Validation](../tools/validate-pattern.py) - Scripts for validating pattern files
- [JSON Schema](#) - (Coming Soon) Detailed schema documentation
- [API Reference](#) - (Coming Soon) Programmatic interface documentation

## Support

If you need help with the Regex Intelligence Exchange by Invinsense:

1. Check the documentation in this directory
2. Review existing issues and discussions
3. Ask questions in [GitHub Discussions](https://github.com/Invinsense/regex-intelligence-exchange/discussions)
4. Contact maintainers directly for complex issues

## License

The Regex Intelligence Exchange by Invinsense documentation is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

# Documentation

This directory contains the documentation for the Regex Intelligence Exchange by Invinsense.

## Deployment

This site is manually deployed. When new changes are pushed to the master branch, follow the manual deployment steps outlined in the [DEPLOYMENT.md](../DEPLOYMENT.md) file in the main repository.

## Files

- [index.html](index.html) - Main documentation site
- [community/](community/) - Community resources
  - [beginners-guide.html](community/beginners-guide.html) - Getting started guide
  - [good-first-issues.html](community/good-first-issues.html) - Easy contribution opportunities
  - [pattern-development.html](community/pattern-development.html) - Advanced pattern development guide