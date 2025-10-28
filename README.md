# Regex Intelligence Exchange by Infopercept

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Pattern Count](https://img.shields.io/badge/patterns-1577-blue.svg)](#)

## Overview

The Regex Intelligence Exchange is a comprehensive repository of regex patterns for technology fingerprinting. Originally derived from the WhatWeb project, this enhanced database provides accurate detection of web technologies, software versions, and security-related information.

## Repository Structure

```
Regex-Intelligence-Exchange/
├── patterns/                 # Main pattern database (1,577 files)
├── imported-patterns/        # Wappalyzer imported patterns (1,243 files)
├── imported-webtech-patterns/ # WebTech imported patterns (1,081 files)
├── tools/                    # Tools for pattern development and management
├── data/                     # Supporting data files
├── docs/                     # Documentation
└── README.md                 # This file
```

## Pattern Database

### Main Patterns (`patterns/`)
The core pattern database organized by vendor containing 1,577 technology detection patterns with enhanced structure including:
- Category and subcategory classification
- Version detection capabilities
- Rich metadata with security information
- Comprehensive test cases

### Wappalyzer Integration (`imported-patterns/`)
1,243 technology patterns imported from Wappalyzer with:
- HTTP header detection
- HTML content analysis
- Meta tag identification
- JavaScript framework detection

### WebTech Integration (`imported-webtech-patterns/`)
1,081 technology patterns imported from WebTech with:
- Comprehensive technology coverage
- Multiple detection methods
- Standardized format

## Tools

The `tools/` directory contains utilities for pattern development and management:

### Validation Tools
- `validate-new-pattern.py` - Validate individual patterns
- `validate-all-patterns.py` - Validate all patterns
- `validate-imported-patterns.py` - Validate Wappalyzer imported patterns
- `validate-webtech-patterns.py` - Validate WebTech imported patterns

### Testing Tools
- `test-patterns.py` - Test pattern functionality
- `monitor-quality.py` - Monitor pattern quality metrics

### Development Tools
- `update-patterns.py` - Update existing patterns to enhanced structure
- `add-test-cases.py` - Automatically add test cases to patterns
- `search-patterns.py` - Search patterns by various criteria
- `generate-pattern-summary.py` - Generate pattern summary reports

### Integration Tools
- `import-wappalyzer.py` - Import patterns from Wappalyzer (now skips existing patterns)
- `import-webtech.py` - Import patterns from WebTech (now skips existing patterns)
- `check-duplicates.py` - Check for duplicate patterns based on content similarity
- `merge-patterns.py` - Merge patterns from different sources intelligently

## Getting Started

### For Users

To use the pattern database in your projects:

```bash
# Clone the repository
git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git

# Explore patterns
ls patterns/by-vendor/

# Use patterns in your tools
import json
with open('patterns/by-vendor/apache/apache.json', 'r') as f:
    pattern_data = json.load(f)
```

### For Contributors

We welcome contributions from the community:

1. **Read our contribution guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Use our pattern template**: [patterns/TEMPLATE.md](patterns/TEMPLATE.md)
3. **Validate your patterns**: 
   ```bash
   python tools/validate-new-pattern.py patterns/by-vendor/my-vendor/my-product.json
   ```
4. **Test your patterns**:
   ```bash
   python tools/test-patterns.py patterns/by-vendor/my-vendor/my-product.json
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

## Quality Assurance

We maintain high quality standards:
- **100% Test Coverage** - Every pattern has comprehensive test cases
- **Automated Validation** - Patterns are validated against strict criteria
- **Regular Quality Monitoring** - Continuous quality assessment

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The pattern database includes content derived from the WhatWeb project, which is also available under the MIT License.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- **WhatWeb Project** - Original source of many patterns
- **Wappalyzer** - Additional patterns through integration
- **WebTech** - Additional patterns through integration
- **All Contributors** - Community members who help improve the database

## Project Status

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Quality Score](https://img.shields.io/badge/quality-A+-brightgreen.svg)](#)
[![Last Commit](https://img.shields.io/github/last-commit/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.svg)](#)

This project is actively maintained with regular updates and improvements. We're constantly working to expand the pattern database, improve quality, and enhance the contributor experience.

---

*Made with ❤️ by Infopercept and the open source community*