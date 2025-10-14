# Regex Intelligence Exchange Architecture

## Current Structure
The current structure organizes patterns by category (web, database, networking, etc.) with separate JSON files for each product.

## Proposed Simplified Architecture
To make the project more understandable and maintainable, we propose a new structure that organizes patterns by vendor and product, with all versions consolidated in a single file per product.

### New Directory Structure
```
patterns/
├── by-vendor/
│   ├── apache/
│   │   ├── httpd.json
│   │   └── traffic-server.json
│   ├── microsoft/
│   │   └── iis.json
│   ├── nginx/
│   │   └── nginx.json
│   └── ... (other vendors)
└── README.md
```

### Pattern File Structure
Each product file will contain all regex patterns for all versions of that product:

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
    ],
    "2.2.x": [
      {
        "name": "Apache HTTPD Server 2.2 Banner",
        "pattern": "Server: Apache/2\\.2\\.([\\d]+)",
        "version_group": 1,
        "priority": 170,
        "confidence": 0.85,
        "metadata": {
          "author": "Security Scanner Team",
          "created_at": "2024-01-01",
          "updated_at": "2024-01-01",
          "description": "Detects Apache HTTPD 2.2.x version from HTTP server banner",
          "tags": ["http", "apache", "webserver"],
          "test_cases": [
            {
              "input": "Server: Apache/2.2.34 (Unix)",
              "expected_version": "34"
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

### Benefits of This Approach
1. **Clear Organization**: Patterns are grouped by vendor and product, making it easier to locate specific patterns
2. **Version Management**: All version-specific patterns are in one place for each product
3. **Reduced Redundancy**: Eliminates the need for multiple files for the same product
4. **Easier Maintenance**: Updates to a product's patterns only require modifying one file
5. **Better Overview**: Provides a complete view of all available patterns for a product

### Migration Process
1. Create the new directory structure
2. Consolidate existing patterns into the new format
3. Update validation tools to work with the new structure
4. Update documentation to reflect the new organization