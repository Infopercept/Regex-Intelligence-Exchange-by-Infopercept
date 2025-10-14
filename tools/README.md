# Tools

This directory contains utility scripts for working with the pattern database.

## Validation Tools

### validate-new-pattern.py

Validates a pattern file in the new by-vendor format.

Usage:
```bash
python validate-new-pattern.py ../patterns/by-vendor/apache/httpd.json
```

## Pattern Discovery Tools

### list-vendors-products.py

Lists all vendors and products in the new by-vendor structure.

Usage:
```bash
python list-vendors-products.py
```

### search-patterns.py

Searches for patterns by vendor or product name in the new by-vendor structure.

Usage:
```bash
python search-patterns.py <search-term>
```

## Summary Tools

### generate-pattern-summary.py

Generates a summary report of all patterns in the database.

Usage:
```bash
python generate-pattern-summary.py
```

## Tool Requirements

All tools are written in Python and require:
- Python 3.6 or higher

No additional Python packages are required for the validation tools.

## Contributing to Tools

When adding new tools or modifying existing ones:

1. Ensure the tool is well-documented with usage examples
2. Include error handling for common failure cases
3. Follow Python best practices and coding standards
4. Test the tool thoroughly before submitting
5. Update this README with information about new tools

## Tool Descriptions

### Pattern Validation

The validation tools check:

1. JSON schema compliance
2. Regex pattern compilation
3. Test case execution
4. Metadata completeness
5. Priority and confidence score ranges

These tools help ensure that all patterns in the database meet our quality standards and function correctly.