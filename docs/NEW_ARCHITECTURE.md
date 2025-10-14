# New Architecture for Regex Pattern Organization

## Overview

This document explains the new architecture for organizing regex patterns in the Regex Intelligence Exchange repository. The new structure organizes patterns by vendor and product, with all versions consolidated in a single file per product.

## Traditional vs. New Structure

### Traditional Structure (patterns/)

The traditional structure organizes patterns by category:
```
patterns/
├── cms/
├── database/
├── framework/
├── messaging/
├── networking/
├── os/
└── web/
```

Each category directory contains JSON files, one per product.

### New Structure (patterns/by-vendor/)

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

## Benefits of the New Structure

1. **Clear Organization**: Patterns grouped by vendor and product
2. **Version Management**: All version-specific patterns in one place
3. **Reduced Redundancy**: Single file per product
4. **Easier Maintenance**: Updates only require modifying one file
5. **Better Overview**: Complete view of all available patterns for a product

## Implementation Details

### Migration Process

All existing patterns have been migrated to the new structure using the `migrate-patterns.py` tool. The migration process:

1. Reads existing pattern files from the traditional structure
2. Extracts vendor and product information
3. Creates vendor directories in the new structure
4. Consolidates patterns into product files
5. Preserves all existing pattern data and metadata

### File Format

Each product file in the new structure contains:

- Vendor information (name, ID)
- Product information (name, ID, category)
- Version-specific patterns organized by version range
- Generic patterns that work across all versions
- Complete metadata for each pattern

### Tools

Several new tools have been created to work with the new structure:

- `validate-new-pattern.py`: Validates pattern files in the new format
- `migrate-patterns.py`: Converts existing patterns to the new format
- `list-vendors-products.py`: Lists all vendors and products
- `search-patterns.py`: Searches for patterns by vendor or product name
- `compare-structures.py`: Compares pattern counts between structures

## Usage

### Finding Patterns

To find patterns in the new structure:

1. Browse the `patterns/by-vendor/` directory
2. Navigate to the vendor directory of interest
3. Open the product JSON file

Alternatively, use the search tool:
```bash
python tools/search-patterns.py [search-term]
```

Or list all vendors and products:
```bash
python tools/list-vendors-products.py
```

### Contributing New Patterns

When contributing new patterns, we recommend using the new structure:

1. Create a new product file in `patterns/by-vendor/[vendor-name]/[product-name].json`
2. Follow the format shown in existing files
3. Include comprehensive test cases
4. Validate your pattern with the new validation tool

### Validation

Validate patterns in the new structure with:
```bash
python tools/validate-new-pattern.py patterns/by-vendor/[vendor-name]/[product-name].json
```

## Backward Compatibility

The traditional structure is maintained for backward compatibility. All existing tools that work with the traditional structure continue to function.

## Future Development

The new structure is the recommended approach for future development. New patterns should be added to the new structure when possible, though contributions to either structure will be accepted.