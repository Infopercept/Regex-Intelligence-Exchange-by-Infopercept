# Migration Guide: Enhanced Pattern Structure

This guide explains how to migrate existing patterns to the enhanced pattern structure and how to contribute new patterns using the improved format.

## Overview

The enhanced pattern structure includes several improvements over the original format:

1. **Enhanced Categorization**: Added `subcategory` field for more granular classification
2. **Improved Metadata**: Additional metadata fields for better documentation
3. **Required Fields**: All patterns must include `version_group`, `priority`, and `confidence`
4. **Structured Format**: Consistent structure for all pattern files

## Migration Process

### Automated Migration

For existing patterns that were automatically extracted from WhatWeb, you can use the automated migration script:

```bash
python tools/update-patterns.py
```

This script will:
1. Add missing required fields (`version_group`, `priority`, `confidence`)
2. Ensure metadata contains all required fields
3. Add `subcategory` field based on the main category
4. Update all pattern files in the repository

To update a specific file:
```bash
python tools/update-patterns.py patterns/by-vendor/apache/apache.json
```

### Manual Migration

For manually migrating patterns, ensure each pattern includes:

#### Required Top-Level Fields
```json
{
  "vendor": "Vendor Name",
  "vendor_id": "vendor-id",
  "product": "Product Name",
  "product_id": "vendor-id-product-id",
  "category": "web",
  "subcategory": "web-server"
}
```

#### Required Pattern Fields
Each pattern in `all_versions` and `versions` must include:
```json
{
  "name": "Pattern Name",
  "pattern": "regex_pattern",
  "version_group": 1,
  "priority": 100,
  "confidence": 0.8,
  "metadata": {
    "author": "Author Name",
    "created_at": "YYYY-MM-DD",
    "updated_at": "YYYY-MM-DD",
    "description": "Pattern description",
    "tags": ["tag1", "tag2"]
  }
}
```

## Enhanced Pattern Structure

### New Fields

#### Subcategory
Added for more granular classification:
```json
"subcategory": "web-server"
```

#### Enhanced Metadata
Additional metadata fields for better documentation:
```json
"metadata": {
  "author": "Security Scanner Team",
  "created_at": "2024-01-01",
  "updated_at": "2024-01-01",
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
  "source": "WhatWeb",
  "license": "MIT",
  "test_cases": [
    {
      "input": "Server: Apache/2.4.41 (Ubuntu)",
      "expected_version": "41"
    }
  ]
}
```

## Integration with External Databases

### Wappalyzer Integration

To import patterns from Wappalyzer:

1. Obtain the Wappalyzer technologies.json file
2. Run the import script:
```bash
python tools/import-wappalyzer.py technologies.json imported-patterns
```

3. Review and validate the imported patterns:
```bash
python tools/test-patterns.py imported-patterns/vendor/product.json
```

4. Move validated patterns to the main patterns directory

### Duplicate Management

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

### Supported Import Sources

- **Wappalyzer**: Technology definitions in JSON format
- **WebTech**: Technology definitions in JSON format
- **WhatWeb**: Ruby plugin files (future enhancement)
- **Custom**: Any JSON format that can be converted

## Quality Assurance

### Validation Scripts

Use the enhanced validation framework to ensure pattern quality:

1. **Validate individual patterns**:
```bash
python tools/validate-new-pattern.py patterns/by-vendor/apache/httpd.json
```

2. **Validate all patterns**:
```bash
python tools/validate-all-patterns.py
```

3. **Comprehensive testing**:
```bash
python tools/test-patterns.py patterns/by-vendor/apache/httpd.json
```

4. **Test all patterns**:
```bash
python tools/test-patterns.py
```

### Test Cases

All patterns should include test cases:
```json
"test_cases": [
  {
    "input": "Server: Apache/2.4.41 (Ubuntu)",
    "expected_version": "41"
  },
  {
    "input": "Server: Apache/2.2.34 (Unix)",
    "expected_version": "34"
  }
]
```

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

## Example Enhanced Pattern

```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "HTTPD",
  "product_id": "apache-httpd",
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
          "author": "Security Scanner Team",
          "created_at": "2024-01-01",
          "updated_at": "2024-01-01",
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
          "source": "WhatWeb",
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
    {
      "name": "Apache HTTPD Server Generic",
      "pattern": "Server: Apache/([\\d.]+)",
      "version_group": 1,
      "priority": 100,
      "confidence": 0.8,
      "metadata": {
        "author": "Security Scanner Team",
        "created_at": "2024-01-01",
        "updated_at": "2024-01-01",
        "description": "Generic pattern for Apache HTTPD version detection",
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
        "affected_versions": [],
        "remediation": "Keep Apache HTTPD updated to the latest stable version",
        "source": "WhatWeb",
        "license": "MIT",
        "test_cases": [
          {
            "input": "Server: Apache/2.4.41 (Ubuntu)",
            "expected_version": "2.4.41"
          },
          {
            "input": "Server: Apache/2.2.34 (Unix)",
            "expected_version": "2.2.34"
          }
        ]
      }
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Missing required fields**: Ensure all required fields are present
2. **Invalid regex patterns**: Test regex compilation before committing
3. **Date format errors**: Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format
4. **Test case failures**: Verify test cases match expected behavior

### Validation Errors

If validation fails:
1. Check the error message for specific issues
2. Review the pattern against the template
3. Run individual validation scripts to isolate issues
4. Consult this guide for required fields and formats

## Contributing

To contribute enhanced patterns:

1. **Fork the repository**
2. **Create a new branch**:
```bash
git checkout -b add-my-new-pattern
```

3. **Add your pattern** following the enhanced structure
4. **Validate your pattern**:
```bash
python tools/validate-new-pattern.py patterns/by-vendor/vendor/product.json
python tools/test-patterns.py patterns/by-vendor/vendor/product.json
```

5. **Commit your changes** with a clear, descriptive message:
```bash
git commit -m "feat: Add enhanced Apache HTTPD patterns with version detection"
```

6. **Push to your fork**:
```bash
git push origin add-my-new-pattern
```

7. **Open a pull request** to the main repository

## Support

For questions about the enhanced pattern structure or migration process:

1. **Check existing documentation**: Review this guide and related documents
2. **Open an issue**: If you encounter problems or have questions
3. **Join the community**: Participate in discussions about pattern development