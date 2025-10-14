# Patterns Architecture

## Overview

This document describes the architecture for organizing regex patterns in this repository. All patterns are now organized in a single simplified structure:

**Simplified Structure** (in [patterns/by-vendor/](patterns/by-vendor/)): Organized by vendor and product

The old category-based structure has been removed to simplify the organization and reduce redundancy.

## New Simplified Structure

The new structure organizes patterns by vendor and product:
```
patterns/by-vendor/
├── apache/
│   ├── httpd.json
│   ├── pulsar.json
│   ├── answer.json
│   └── traffic-server.json
├── microsoft/
│   └── internet-information-services.json
├── f5-networks/
│   └── nginx.json
└── ... (other vendors)
```

### File Format

Each product file contains all regex patterns for that product:

```json
{
  "vendor": "Vendor Name",
  "vendor_id": "vendor-id",
  "product": "Product Name",
  "product_id": "vendor-id-product-id",
  "category": "product-category",
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

### Fields Explanation

- `vendor`: The company or organization that creates the product
- `vendor_id`: A normalized identifier for the vendor
- `product`: The specific product name
- `product_id`: A normalized identifier for the product
- `category`: Product category (web, database, networking, etc.)
- `versions`: Object containing version-specific patterns
  - Keys are version ranges (e.g., "2.4.x")
  - Values are arrays of patterns for that version range
- `all_versions`: Array of patterns that work across all versions

Each pattern contains:
- `name`: Descriptive name of the pattern
- `pattern`: The regex pattern with capture groups
- `version_group`: The capture group number containing the version
- `priority`: Priority score (0-200) indicating reliability
- `confidence`: Confidence level (0.0-1.0) in accuracy
- `metadata`: Additional information about the pattern

## Benefits of the New Structure

1. **Clear Organization**: Patterns grouped by vendor and product
2. **Version Management**: All version-specific patterns in one place
3. **Reduced Redundancy**: Single file per product
4. **Easier Maintenance**: Updates only require modifying one file
5. **Better Overview**: Complete view of all available patterns for a product

## Tools

- [validate-new-pattern.py](tools/validate-new-pattern.py): Validates pattern files in the new format

## Migration Status

All existing patterns have been migrated to the new structure. The old category-based structure has been removed to simplify the organization.