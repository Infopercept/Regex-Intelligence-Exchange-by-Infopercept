# Pattern Database

This directory contains the regex patterns used to detect software versions. Patterns are organized by vendor to make them easy to find and manage.

## Vendors

Patterns are organized by vendor name. Each vendor directory contains JSON files for each product.

## Getting Started

1. Use our [pattern template](../TEMPLATE.md) as a starting point for new patterns
2. Follow our [contribution guidelines](../../CONTRIBUTING.md)
3. Include comprehensive test cases
4. Validate your pattern with our tools

## Validation

All patterns are validated using our [pattern validation tool](../../tools/validate-pattern.py) which checks:

- JSON schema compliance
- Regex pattern compilation
- Test case execution
- Metadata completeness

Patterns that don't pass validation will not be accepted.

## Duplicate Management

To prevent duplicate entries:

1. **Import scripts now check for existing patterns** and skip importing if a pattern with the same product ID already exists
2. **Use the duplicate checker** to identify potential duplicates:
   ```bash
   python ../../tools/check-duplicates.py
   ```
3. **Use the merge tool** to intelligently combine patterns from different sources:
   ```bash
   python ../../tools/merge-patterns.py <import-directory> <target-directory>
   ```

## License

This pattern database is provided under the MIT License. See [LICENSE](../../LICENSE) file in the root directory for more information.