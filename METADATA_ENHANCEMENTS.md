# Additional Metadata Fields

This document describes the enhanced metadata fields added to the Regex Intelligence Exchange patterns for better documentation and tracking.

## Overview

The additional metadata fields provide more comprehensive information about each pattern, including security-related data, references, and tracking information. These fields enhance the utility of the pattern database for security professionals and researchers.

## New Metadata Fields

### 1. References

An array of references to documentation, security advisories, or related resources:

```json
"references": [
  {
    "title": "Apache HTTP Server Documentation",
    "url": "https://httpd.apache.org/docs/"
  }
]
```

### 2. Severity

Security severity level with values: `low`, `medium`, `high`, `critical`

```json
"severity": "medium"
```

### 3. CVSS Score

Common Vulnerability Scoring System score (0.0-10.0):

```json
"cvss_score": 7.5
```

### 4. CWE IDs

Array of Common Weakness Enumeration IDs:

```json
"cwe_ids": ["CWE-79", "CWE-89"]
```

### 5. Affected Versions

Array of version ranges that are affected:

```json
"affected_versions": ["1.0.0-2.0.0", "2.1.0-2.1.5"]
```

### 6. Remediation

Steps to remediate issues detected by this pattern:

```json
"remediation": "Update to version 2.0.0 or later"
```

### 7. Source

Source of the pattern (WhatWeb, manual, etc.):

```json
"source": "WhatWeb"
```

### 8. License

License under which the pattern is provided:

```json
"license": "MIT"
```

## Benefits

1. **Enhanced Documentation**: More detailed information about each pattern
2. **Security Context**: Security severity and vulnerability information
3. **Traceability**: References to documentation and sources
4. **Remediation Guidance**: Clear steps for addressing detected issues
5. **Version Tracking**: Specific information about affected versions
6. **Compliance**: License information for legal compliance

## Usage Guidelines

When creating or updating patterns:

1. Include relevant references to official documentation or security advisories
2. Set appropriate severity levels based on the potential impact
3. Provide CVSS scores when known vulnerabilities are associated with the pattern
4. List CWE IDs when applicable
5. Specify affected version ranges when known
6. Include remediation steps for addressing detected issues
7. Always specify the source of the pattern
8. Include appropriate license information

## Example Pattern with Enhanced Metadata

```json
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
      },
      {
        "title": "Apache HTTP Server Security Advisories",
        "url": "https://httpd.apache.org/security/"
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
```

## Validation

All new metadata fields are validated by the pattern validation scripts to ensure data quality and consistency.