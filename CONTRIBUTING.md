# Contributing to Regex Intelligence Exchange by Infopercept

Thank you for your interest in contributing to the Regex Intelligence Exchange by Infopercept! This document provides comprehensive guidelines for contributing to this project.

## How to Contribute

1. **Report Issues**: If you find a bug or have a suggestion, please open an issue on GitHub
2. **Fix Issues**: Look for issues tagged with "good first issue" if you're new to the project
3. **Add Patterns**: Contribute new regex patterns following our template and guidelines
4. **Improve Documentation**: Help improve our documentation and guides
5. **Enhance Existing Patterns**: Add test cases, metadata, or improve accuracy of existing patterns
6. **Integrate New Sources**: Help integrate patterns from other fingerprinting databases

## Pattern Contribution Guidelines

### Pattern Structure

All patterns must follow our standardized JSON structure as defined in the [pattern template](patterns/TEMPLATE.md).

Example pattern structure:
```json
{
  "vendor": "Vendor Name",
  "vendor_id": "vendor-id",
  "product": "Product Name",
  "product_id": "vendor-id-product-id",
  "category": "web",
  "subcategory": "web-server",
  "versions": {
    "2.4.x": [
      {
        "name": "Apache HTTPD Server 2.4 Banner",
        "pattern": "Server: Apache/2\\.4\\.([\\d]+)",
        "version_group": 1,
        "priority": 180,
        "confidence": 0.9,
        "metadata": {
          "author": "Your Name",
          "created_at": "2025-01-01",
          "updated_at": "2025-01-01",
          "description": "Detects Apache HTTPD 2.4.x version from HTTP server banner",
          "tags": ["http", "apache", "webserver"],
          "references": [
            {
              "title": "Apache HTTP Server Documentation",
              "url": "https://httpd.apache.org/docs/"
            }
          ],
          "severity": "low",
          "cvss_score": 0.0,
          "cwe_ids": [],
          "affected_versions": ["2.4.0-2.4.99"],
          "remediation": "Keep Apache HTTPD updated to the latest stable version",
          "source": "Manual",
          "license": "MIT",
          "test_cases": [
            {
              "input": "Server: Apache/2.4.41 (Ubuntu)",
              "expected_version": "41"
            }
          ]
        }
      }
    ]
  },
  "all_versions": [
    // ... additional patterns
  ]
}
```

### Pattern Requirements

1. **Accuracy**: Patterns must reliably detect the intended software versions
2. **Specificity**: Avoid false positives by making patterns specific to the target software
3. **Test Cases**: Include comprehensive test cases covering both positive and negative matches
4. **Documentation**: Provide clear metadata about the pattern's purpose and usage
5. **Version Handling**: Use appropriate version_group values for version extraction
6. **Priority Setting**: Set appropriate priority values (0-200) based on pattern reliability
7. **Confidence Levels**: Set confidence values (0.0-1.0) reflecting pattern accuracy

### Required Fields

Each pattern must include these required fields:
- `name`: Descriptive name of the pattern
- `pattern`: Valid regex pattern
- `version_group`: Integer indicating version capture group (0 if no version)
- `priority`: Integer between 0-200 (higher = more reliable)
- `confidence`: Float between 0.0-1.0 (accuracy level)
- `metadata`: Object containing author, dates, description, and tags

### Metadata Requirements

Each pattern's metadata must include:
- `author`: Your name or organization
- `created_at`: Date in YYYY-MM-DD format
- `updated_at`: Date in YYYY-MM-DD format
- `description`: Clear description of what the pattern detects
- `tags`: Array of relevant tags
- `test_cases`: Array of test cases (at least one)

### Optional Metadata Fields

Enhance your patterns with these optional fields:
- `references`: Array of reference URLs
- `severity`: Security impact (low, medium, high, critical)
- `cvss_score`: CVSS score (0.0-10.0)
- `cwe_ids`: Array of CWE identifiers
- `affected_versions`: Array of affected version ranges
- `remediation`: Guidance for addressing issues
- `source`: Origin of the pattern
- `license`: Licensing information

## Testing

Before submitting a pattern, ensure it passes our validation tests:

### Validate Individual Patterns
```bash
python tools/validate-new-pattern.py patterns/by-vendor/vendor-name/product-name.json
```

### Test Pattern Functionality
```bash
python tools/test-patterns.py patterns/by-vendor/vendor-name/product-name.json
```

### Validate All Patterns
```bash
python tools/validate-all-patterns.py
```

### Run Quality Checks
```bash
python tools/monitor-quality.py
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

## Development Workflow

1. Fork the repository
2. Create a new branch for your work:
   ```bash
   git checkout -b add-my-new-pattern
   ```
3. Add your pattern and test cases
4. Validate your pattern using our tools
5. Commit your changes with a clear, descriptive message
6. Push to your fork:
   ```bash
   git push origin add-my-new-pattern
   ```
7. Open a pull request to the main repository

### Pull Request Guidelines

When submitting a pull request:

1. **Clear Title**: Use a descriptive title that summarizes your changes
2. **Detailed Description**: Explain what your changes do and why they're needed
3. **Link Issues**: Reference any related issues using #issue-number
4. **Pass Tests**: Ensure all tests pass before submitting
5. **Follow Guidelines**: Adhere to all contribution guidelines

### Keeping Your Fork Updated

To keep your fork updated with the main repository:

```bash
git remote add upstream https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git
git fetch upstream
git checkout master
git merge upstream/master
```

## Pattern Categories

We use a standardized category system:

### Main Categories
- `web`: Web applications and servers
- `cms`: Content Management Systems
- `database`: Database systems
- `framework`: Development frameworks
- `messaging`: Messaging systems
- `networking`: Networking tools and services
- `os`: Operating systems

### Subcategories
- `web`: web-application, web-server, cdn, webmail
- `cms`: cms-platform, ecommerce, blog
- `database`: database-engine, database-management
- `framework`: web-framework, frontend-framework
- `messaging`: message-queue, chat-system
- `networking`: network-device, firewall
- `os`: linux-distribution, windows-version

## Best Practices

### Pattern Creation
1. **Use descriptive names**: Make pattern names clearly indicate what they detect
2. **Set appropriate priorities**: Higher priority (150-200) for reliable patterns
3. **Set realistic confidence**: Reflect actual accuracy (0.0-1.0)
4. **Include version groups**: Set to 0 if no version capture, or the capture group number
5. **Add comprehensive metadata**: Include all relevant information
6. **Write test cases**: Include positive and negative test cases

### Version Handling
1. **Normalize versions**: Use the version_utils module for consistency
2. **Handle prefixes**: Account for "v", "V", "r" prefixes in versions
3. **Validate ranges**: Specify affected version ranges when known

### Categorization
1. **Choose appropriate categories**: Use the defined category system
2. **Select specific subcategories**: Use the most specific applicable subcategory
3. **Maintain consistency**: Follow existing categorization patterns

### Regex Best Practices
1. **Escape special characters**: Properly escape regex special characters
2. **Avoid catastrophic backtracking**: Write efficient regex patterns
3. **Test thoroughly**: Validate patterns with various inputs
4. **Be specific**: Avoid overly broad patterns that cause false positives

## Tools and Scripts

We provide several tools to help with pattern development:

### Validation Tools
- `validate-new-pattern.py`: Validate individual patterns
- `validate-all-patterns.py`: Validate all patterns
- `test-patterns.py`: Test pattern functionality
- `monitor-quality.py`: Monitor pattern quality metrics

### Development Tools
- `update-patterns.py`: Update existing patterns to enhanced structure
- `generate-pattern-summary.py`: Generate pattern summary reports
- `search-patterns.py`: Search patterns by various criteria
- `add-test-cases.py`: Automatically add test cases to patterns

### Integration Tools
- `import-wappalyzer.py`: Import patterns from Wappalyzer (now skips existing patterns)
- `import-webtech.py`: Import patterns from WebTech (now skips existing patterns)
- `check-duplicates.py`: Check for duplicate patterns based on content similarity
- `merge-patterns.py`: Merge patterns from different sources intelligently

## Community Resources

### Documentation
- [Migration Guide](MIGRATION_GUIDE.md): Guide for migrating to enhanced pattern structure
- [Pattern Template](patterns/TEMPLATE.md): Template for new patterns
- [Pattern Categorization](PATTERN_CATEGORIZATION.md): Category and subcategory system
- [Metadata Enhancements](METADATA_ENHANCEMENTS.md): Metadata field documentation
- [Version Extraction](VERSION_EXTRACTION.md): Version processing improvements
- [Enhanced Validation](ENHANCED_VALIDATION.md): Validation framework documentation

### Reports
- [Pattern Summary](PATTERNS_SUMMARY.md): Summary of all patterns
- [Quality Report](QUALITY_IMPROVEMENT_REPORT.md): Quality metrics and improvements
- [Wappalyzer Integration Report](WAPPALYZER_INTEGRATION_REPORT.md): Wappalyzer integration details
- [WebTech Integration Report](WEBTECH_INTEGRATION_REPORT.md): WebTech integration details

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Questions?

If you have any questions about contributing, feel free to:
1. Open an issue on GitHub
2. Contact the maintainers
3. Join our community discussions
4. Check the documentation and guides

Thank you for contributing to the Regex Intelligence Exchange!