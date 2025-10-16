# Automatic Data Updates

This repository automatically updates statistics and data files whenever new patterns are added.

## How It Works

1. **GitHub Actions Workflow**: Whenever changes are pushed to the `master` branch, a GitHub Actions workflow automatically runs to:
   - Validate all patterns
   - Update statistics in `PATTERNS_SUMMARY.md`
   - Update vendor and product data in the `data/` directory
   - Commit and push any changes

2. **Manual Updates**: You can also manually update all data by running:
   ```bash
   python tools/update-all-data.py
   ```

## Files That Are Automatically Updated

- `PATTERNS_SUMMARY.md` - Contains overall statistics about the pattern database
- `data/vendors.json` - List of all vendors with patterns in the database
- `data/products.json` - List of all products with patterns in the database

## Adding New Patterns

When you add new patterns to the `patterns/by-vendor/` directory, the statistics will automatically update the next time the GitHub Actions workflow runs (on push to master) or when you manually run the update script.

The update process:
1. Counts all patterns in the repository
2. Categorizes patterns by type, vendor, and product
3. Updates summary statistics
4. Ensures vendor and product data files are up to date

## Customizing Vendor/Product Information

While the automatic update process will create basic entries for new vendors and products, you may want to manually edit `data/vendors.json` and `data/products.json` to add:
- Website URLs
- Descriptions
- Other relevant information

These manual edits will be preserved when the automatic update process runs, as it only adds missing entries and doesn't overwrite existing information with websites and descriptions.