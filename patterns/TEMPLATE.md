# Pattern Template

Use this template when creating new pattern files for the database.

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

## Field Descriptions

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

## Example Pattern

```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "HTTPD",
  "product_id": "apache-httpd",
  "category": "web",
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
```