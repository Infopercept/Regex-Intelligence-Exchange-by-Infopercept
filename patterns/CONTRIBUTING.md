# Contributing Patterns to Regex Intelligence Exchange by Infopercept

Thank you for your interest in contributing to the Regex Intelligence Exchange by Infopercept! This document provides guidelines and best practices for contributing new patterns or improving existing ones.

## Pattern Guidelines

### Accuracy and Reliability

Patterns should be thoroughly tested and validated to ensure they:
- Accurately detect the intended software versions
- Minimize false positives and false negatives
- Work across different environments and configurations

### Pattern Structure

Each pattern file should follow the [standard template](TEMPLATE.md) and include:

1. **Metadata**: Complete information about the software being detected
2. **Regex Pattern**: Well-crafted regular expression for version detection
3. **Test Cases**: Comprehensive examples covering positive and negative matches
4. **Documentation**: Clear descriptions of the pattern's purpose and usage

### Test Cases

Every pattern must include test cases that cover:
- Normal version formats for the software
- Edge cases and unusual version strings
- Examples that should NOT match (negative test cases)
- Various sources where the version might appear

## Submission Process

1. Fork the repository
2. Create a new branch for your pattern
3. Add your pattern file to the appropriate category directory
4. Include comprehensive test cases
5. Validate your pattern using our tools
6. Submit a pull request with a clear description

## Pattern Categories

Organize patterns in the appropriate subdirectory:
- `web/` - Web servers, applications, frameworks
- `database/` - Database systems
- `networking/` - Routers, switches, firewalls
- `cms/` - Content management systems
- `framework/` - Programming frameworks and libraries
- `os/` - Operating systems
- `other/` - Software that doesn't fit other categories

## Review Process

All pattern submissions go through a review process:
1. Automated validation checks
2. Manual review by maintainers
3. Testing against real-world samples
4. Feedback and revision requests
5. Approval and merge

## Questions?

If you have questions about pattern development, open an issue or contact the maintainers.
