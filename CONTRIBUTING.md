# Contributing to Regex Intelligence Exchange by Infopercept

Thank you for your interest in contributing to the Regex Intelligence Exchange by Infopercept! This document provides guidelines for contributing to this project.

## How to Contribute

1. **Report Issues**: If you find a bug or have a suggestion, please open an issue on GitHub
2. **Fix Issues**: Look for issues tagged with "good first issue" if you're new to the project
3. **Add Patterns**: Contribute new regex patterns following our template and guidelines
4. **Improve Documentation**: Help improve our documentation and guides

## Pattern Contribution Guidelines

### Pattern Structure

All patterns must follow our standardized JSON structure as defined in the [pattern template](https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept/blob/master/patterns/TEMPLATE.md).

### Pattern Requirements

1. **Accuracy**: Patterns must reliably detect the intended software versions
2. **Specificity**: Avoid false positives by making patterns specific to the target software
3. **Test Cases**: Include comprehensive test cases covering both positive and negative matches
4. **Documentation**: Provide clear metadata about the pattern's purpose and usage

### Testing

Before submitting a pattern, ensure it passes our validation tests:

```bash
python tools/validate-new-pattern.py patterns/by-vendor/vendor-name/product-name.json
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

### Keeping Your Fork Updated

To keep your fork updated with the main repository:

```bash
git remote add upstream https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git
git fetch upstream
git checkout master
git merge upstream/master
```

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Questions?

If you have any questions about contributing, feel free to open an issue or contact the maintainers.