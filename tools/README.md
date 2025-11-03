# Tools

This directory contains various tools for managing and enhancing the Regex Intelligence Exchange patterns.

## Import Tools

### extract-whatweb-patterns.py
Extracts patterns from WhatWeb plugins and converts them to Regex-Intelligence-Exchange format.

Usage:
```bash
python extract-whatweb-patterns.py
```

### import-wappalyzer.py
Imports technology patterns from Wappalyzer's technology definitions.

Usage:
```bash
python import-wappalyzer.py
```

### import-webtech.py
Imports technology patterns from WebTech's technology definitions.

Usage:
```bash
python import-webtech.py
```

Note: These import scripts now check for existing patterns and will skip importing if a pattern with the same product ID already exists.

## Integration Tools

### realtime-integration.py
Real-time integration system that continuously fetches and integrates pattern data from all available regex tools and databases.

Usage:
```bash
# Run integration once
python realtime-integration.py

# Run in scheduled mode (continuous integration)
python realtime-integration.py --schedule

# Show integration statistics
python realtime-integration.py --stats
```

### enhanced_import_manager.py
Enhanced import manager that adds all regex data from different tools into a single folder in a structured way while preventing data duplication.

Usage:
```bash
# This is a library module used by other tools
```

### monitor-integration.py
Monitoring dashboard that displays real-time status of the integration process.

Usage:
```bash
python monitor-integration.py
```

## Validation Tools

### validate-all-patterns.py
Validates all patterns in the repository for structural integrity.

Usage:
```bash
python validate-all-patterns.py
```

### validate-imported-patterns.py
Validates Wappalyzer imported patterns.

Usage:
```bash
python validate-imported-patterns.py
```

### validate-new-pattern.py
Validates patterns in the new vendor-based structure.

Usage:
```bash
python validate-new-pattern.py <pattern-file>
```

### validate-webtech-patterns.py
Validates WebTech imported patterns.

Usage:
```bash
python validate-webtech-patterns.py
```

## Pattern Enhancement Tools

### add-test-cases.py
Automatically adds test cases to patterns that are missing them.

Usage:
```bash
python add-test-cases.py
```

### analyze-metadata.py
Analyzes pattern metadata for quality and completeness.

Usage:
```bash
python analyze-metadata.py
```

### enhance-metadata.py
Enhances pattern metadata with additional information.

Usage:
```bash
python enhance-metadata.py
```

### standardize-patterns.py
Standardizes all patterns to ensure consistent format.

Usage:
```bash
python standardize-patterns.py
```

### optimize-patterns.py
Optimizes patterns for better performance.

Usage:
```bash
python optimize-patterns.py
```

## Duplicate Management Tools

### check-duplicates.py
Checks the repository for duplicate patterns based on content similarity.

Usage:
```bash
python check-duplicates.py
```

### check-pattern-structure.py
Checks pattern structure for consistency.

Usage:
```bash
python check-pattern-structure.py
```

### fix-pattern-structure.py
Fixes pattern structure issues.

Usage:
```bash
python fix-pattern-structure.py
```

## Search and Analysis Tools

### search-patterns.py
Searches for patterns by vendor or product name.

Usage:
```bash
python search-patterns.py [search-term]
```

### list-vendors-products.py
Lists all vendors and products in the new structure.

Usage:
```bash
python list-vendors-products.py
```

### generate-pattern-summary.py
Generates a summary of all patterns.

Usage:
```bash
python generate-pattern-summary.py
```

## Testing Tools

### test-patterns.py
Tests patterns against sample data.

Usage:
```bash
python test-patterns.py
```

### test-pattern-service.py
Tests the pattern service functionality.

Usage:
```bash
python test-pattern-service.py
```

### pattern-matcher.py
Matches patterns against text input.

Usage:
```bash
python pattern-matcher.py
```

## Deployment Tools

### deploy.py
Deployment script for the application.

Usage:
```bash
python deploy.py
```

## Utility Tools

### update-patterns.py
Updates existing patterns to conform to the enhanced structure.

Usage:
```bash
python update-patterns.py
```

### version_utils.py
Utility functions for version handling.

Usage:
```bash
# This is a library module used by other tools
```