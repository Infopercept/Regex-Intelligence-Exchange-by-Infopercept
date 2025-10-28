# Tools

This directory contains various tools for managing and enhancing the Regex Intelligence Exchange patterns.

## Import Tools

### import-wappalyzer.py
Imports technology patterns from Wappalyzer's technology definitions.

Usage:
```bash
python import-wappalyzer.py <wappalyzer-json-file> <output-directory>
```

### import-webtech.py
Imports technology patterns from WebTech's technology definitions.

Usage:
```bash
python import-webtech.py <webtech-json-file> <output-directory>
```

Note: These import scripts now check for existing patterns and will skip importing if a pattern with the same product ID already exists.

## Duplicate Management Tools

### check-duplicates.py
Checks the repository for duplicate patterns based on content similarity.

Usage:
```bash
python check-duplicates.py
```

### merge-patterns.py
Merges patterns from different sources, intelligently handling duplicates by combining metadata, test cases, and selecting the best values for confidence and priority.

Usage:
```bash
python merge-patterns.py <import-directory> <target-directory>
```

## Pattern Management Tools

### add-test-cases.py
Automatically adds test cases to patterns that are missing them.

Usage:
```bash
python add-test-cases.py
```

### update-patterns.py
Updates existing patterns to conform to the enhanced structure.

Usage:
```bash
python update-patterns.py
```

### validate-patterns.py
Validates all patterns in the repository for structural integrity and test coverage.

Usage:
```bash
python validate-patterns.py
```