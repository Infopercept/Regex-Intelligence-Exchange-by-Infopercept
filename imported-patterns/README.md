# Imported Patterns

This directory contains patterns imported from external fingerprinting databases, primarily Wappalyzer.

## Directory Structure

```
imported-patterns/
├── vendor-name/
│   ├── product-name.json
│   └── ...
├── another-vendor/
│   ├── product-name.json
│   └── ...
└── README.md
```

## Import Process

Patterns in this directory were imported using the [import-wappalyzer.py](file:///c%3A/code/Regex-Intelligence-Exchange-by-Infopercept/tools/import-wappalyzer.py) script:

```bash
python tools/import-wappalyzer.py technologies.json imported-patterns
```

## Validation Process

All imported patterns should be validated before moving to the main patterns directory:

```bash
# Validate individual pattern
python tools/validate-new-pattern.py imported-patterns/vendor/product.json

# Test individual pattern
python tools/test-patterns.py imported-patterns/vendor/product.json

# Validate all imported patterns
python tools/validate-all-patterns.py imported-patterns

# Test all imported patterns
python tools/test-patterns.py imported-patterns
```

## Integration Steps

1. Import patterns from external sources using the appropriate import script
2. Review and validate all imported patterns
3. Run tests to ensure patterns work correctly
4. Move validated patterns to the main patterns directory:
   ```bash
   mv imported-patterns/vendor-name/ patterns/by-vendor/
   ```
5. Update pattern metadata as needed for consistency

## Quality Assurance

Imported patterns should meet the same quality standards as manually created patterns:
- All required fields must be present
- Regex patterns must be valid
- Test cases should be included
- Metadata should be complete and accurate
- Patterns should follow the enhanced structure

## Source Tracking

Imported patterns retain information about their source in the metadata:
- `source`: Indicates the original source (e.g., "Wappalyzer")
- `license`: Indicates the licensing terms
- `author`: Indicates the original author or source project

This helps maintain proper attribution and ensures compliance with licensing requirements.