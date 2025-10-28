# Pattern Template

Use this template when creating new pattern files for the database.

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

## Field Descriptions

- `vendor`: The company or organization that creates the product
- `vendor_id`: A normalized identifier for the vendor
- `product`: The specific product name
- `product_id`: A normalized identifier for the product
- `category`: Product category (web, cms, database, framework, messaging, networking, os)
- `subcategory`: Product subcategory for more granular classification (web-server, cms-platform, database-engine, etc.)
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

### Metadata Fields

- `author`: The person or team who created the pattern
- `created_at`: Date when the pattern was created (YYYY-MM-DD)
- `updated_at`: Date when the pattern was last updated (YYYY-MM-DD)
- `description`: Detailed description of what the pattern detects
- `tags`: Array of tags for categorization and searching
- `references`: Array of references to documentation, advisories, or related resources
- `severity`: Security severity level (low, medium, high, critical)
- `cvss_score`: Common Vulnerability Scoring System score (0.0-10.0)
- `cwe_ids`: Array of Common Weakness Enumeration IDs
- `affected_versions`: Array of version ranges that are affected
- `remediation`: Steps to remediate issues detected by this pattern
- `source`: Source of the pattern (WhatWeb, manual, etc.)
- `license`: License under which the pattern is provided
- `test_cases`: Array of test cases for validating the pattern

## Example Pattern

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
          }
        ]
      }
    }
  ]
}