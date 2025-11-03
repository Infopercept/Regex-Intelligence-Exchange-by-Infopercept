# Usage Guide for Regex Intelligence Exchange

## Overview

This guide explains how to use the Regex Intelligence Exchange repository, including both the traditional category-based structure and the new vendor-based structure.

## Directory Structure

```
.
├── data/                 # Vendor and product information
├── docs/                 # Documentation files
├── patterns/             # Pattern files in two structures:
│   ├── by-vendor/        # New vendor-based structure (recommended)
│   │   ├── apache/
│   │   │   ├── httpd.json
│   │   │   └── ...
│   │   └── ...
│   ├── web/              # Traditional category-based structure
│   ├── database/
│   └── ...
├── tools/                # Utility scripts
└── README.md             # Main documentation
```

## Using the New Vendor-Based Structure (Recommended)

The new structure organizes patterns by vendor and product, making it easier to find and manage patterns.

### Finding Patterns

1. **Browse by vendor**: Navigate to `patterns/by-vendor/[vendor-name]/` to see all products for a vendor
2. **Use the search tool**:
   ```bash
   python tools/search-patterns.py [search-term]
   ```
3. **List all vendors and products**:
   ```bash
   python tools/list-vendors-products.py
   ```

### Pattern File Format

Each product file contains all patterns for that product:

```json
{
  "vendor": "Vendor Name",
  "vendor_id": "vendor-id",
  "product": "Product Name",
  "product_id": "vendor-id-product-id",
  "category": "product-category",
  "subcategory": "product-subcategory",
  "versions": {
    "version-range": [
      {
        "name": "Pattern Name",
        "pattern": "regex_pattern",
        "version_group": 1,
        "priority": 100,
        "confidence": 0.9,
        "metadata": {
          "author": "Author Name",
          "created_at": "YYYY-MM-DD",
          "updated_at": "YYYY-MM-DD",
          "description": "Pattern description",
          "tags": ["tag1", "tag2"],
          "references": [
            {
              "title": "Reference Title",
              "url": "https://example.com/reference"
            }
          ],
          "severity": "medium",
          "cvss_score": 0.0,
          "cwe_ids": ["CWE-XXX"],
          "affected_versions": ["1.0.0-2.0.0"],
          "remediation": "Remediation steps",
          "source": "WhatWeb",
          "license": "MIT",
          "test_cases": [
            {
              "input": "Test input",
              "expected_version": "Expected version"
            }
          ]
        }
      }
    ]
  },
  "all_versions": [
    {
      "name": "Generic Pattern Name",
      "pattern": "generic_regex_pattern",
      "version_group": 1,
      "priority": 100,
      "confidence": 0.8,
      "metadata": {
        "author": "Author Name",
        "created_at": "YYYY-MM-DD",
        "updated_at": "YYYY-MM-DD",
        "description": "Generic pattern description",
        "tags": ["tag1", "tag2"],
        "references": [
          {
            "title": "Reference Title",
            "url": "https://example.com/reference"
          }
        ],
        "severity": "medium",
        "cvss_score": 0.0,
        "cwe_ids": ["CWE-XXX"],
        "affected_versions": ["1.0.0-2.0.0"],
        "remediation": "Remediation steps",
        "source": "WhatWeb",
        "license": "MIT",
        "test_cases": [
          {
            "input": "Test input",
            "expected_version": "Expected version"
          }
        ]
      }
    }
  ]
}
```

## Using the Traditional Category-Based Structure

The traditional structure organizes patterns by category.

### Finding Patterns

1. **Browse by category**: Navigate to `patterns/[category]/` to see all products in that category
2. **Each product has its own JSON file** with one or more patterns

## Contributing New Patterns

### Using the New Structure (Recommended)

1. **Create a new product file** in `patterns/by-vendor/[vendor-name]/[product-name].json`
2. **Follow the format** shown in the example above
3. **Include comprehensive test cases**
4. **Validate your pattern**:
   ```bash
   python tools/validate-new-pattern.py patterns/by-vendor/[vendor-name]/[product-name].json
   ```

### Using the Traditional Structure

1. **Add your pattern** to the appropriate category directory
2. **Follow the template** in `patterns/TEMPLATE.md`
3. **Validate your pattern**:
   ```bash
   python tools/validate-pattern.py patterns/[category]/[product-name].json
   ```

## Duplicate Management

To prevent duplicate entries when importing patterns from external sources:

1. **Import scripts now check for existing patterns** and skip importing if a pattern with the same product ID already exists
2. **Use the duplicate checker** to identify potential duplicates:
   ```bash
   python tools/check-duplicates.py
   ```

## Tools

### Validation Tools

- `validate-pattern.py`: Validates patterns in the traditional structure
- `validate-new-pattern.py`: Validates patterns in the new structure
- `validate-all-patterns.py`: Validates all patterns in the traditional structure
- `validate-imported-patterns.py`: Validates Wappalyzer imported patterns
- `validate-webtech-patterns.py`: Validates WebTech imported patterns

### Utility Tools

- `list-vendors-products.py`: Lists all vendors and products in the new structure
- `search-patterns.py`: Searches for patterns by vendor or product name
- `add-test-cases.py`: Automatically adds test cases to patterns
- `check-duplicates.py`: Checks for duplicate patterns

### Integration Tools

- `import-wappalyzer.py`: Imports patterns from Wappalyzer (now skips existing patterns)
- `import-webtech.py`: Imports patterns from WebTech (now skips existing patterns)