#!/usr/bin/env python3
"""
Update All Data Script

This script updates all data files and statistics in the repository:
- PATTERNS_SUMMARY.md
- data/vendors.json
- data/products.json

It should be run after adding new patterns to automatically update all related files.
"""

import json
import os
import subprocess
from pathlib import Path
from collections import defaultdict

def find_pattern_files(root_dir):
    """Find all pattern files in the repository."""
    pattern_files = []
    patterns_dir = os.path.join(root_dir, 'patterns')
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files

def analyze_patterns(pattern_files):
    """Analyze all patterns and generate statistics."""
    # Statistics counters
    total_patterns = 0
    patterns_by_category = defaultdict(int)
    patterns_by_vendor = defaultdict(int)
    patterns_by_product = defaultdict(int)
    total_test_cases = 0
    patterns_with_test_cases = 0
    
    # Process each pattern file
    for pattern_file in pattern_files:
        with open(pattern_file, 'r') as f:
            try:
                pattern_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {pattern_file}: {e}")
                continue
        
        # Extract vendor and product information
        vendor = pattern_data.get('vendor', 'unknown')
        product = pattern_data.get('product', 'unknown')
        category = pattern_data.get('category', 'unknown')
        
        # Process patterns in all_versions
        for pattern in pattern_data.get('all_versions', []):
            total_patterns += 1
            
            # Count by category
            patterns_by_category[category] += 1
            
            # Count by vendor
            patterns_by_vendor[vendor] += 1
            
            # Count by product
            patterns_by_product[product] += 1
            
            # Count test cases
            test_cases = pattern.get('metadata', {}).get('test_cases', [])
            total_test_cases += len(test_cases)
            if len(test_cases) > 0:
                patterns_with_test_cases += 1
        
        # Process patterns in versions (version-specific patterns)
        for version_range, patterns in pattern_data.get('versions', {}).items():
            for pattern in patterns:
                total_patterns += 1
                
                # Count by category
                patterns_by_category[category] += 1
                
                # Count by vendor
                patterns_by_vendor[vendor] += 1
                
                # Count by product
                patterns_by_product[product] += 1
                
                # Count test cases
                test_cases = pattern.get('metadata', {}).get('test_cases', [])
                total_test_cases += len(test_cases)
                if len(test_cases) > 0:
                    patterns_with_test_cases += 1
    
    return {
        'total_patterns': total_patterns,
        'patterns_by_category': dict(patterns_by_category),
        'patterns_by_vendor': dict(patterns_by_vendor),
        'patterns_by_product': dict(patterns_by_product),
        'total_test_cases': total_test_cases,
        'patterns_with_test_cases': patterns_with_test_cases
    }

def generate_report(stats):
    """Generate a formatted report from statistics."""
    report = []
    report.append("# Pattern Database Summary")
    report.append("")
    report.append(f"Total Patterns: {stats['total_patterns']}")
    report.append(f"Patterns with Test Cases: {stats['patterns_with_test_cases']}")
    report.append(f"Total Test Cases: {stats['total_test_cases']}")
    report.append("")
    
    # Patterns by category
    report.append("## Patterns by Category")
    report.append("")
    for category, count in sorted(stats['patterns_by_category'].items()):
        report.append(f"- {category}: {count}")
    report.append("")
    
    # Patterns by vendor
    report.append("## Patterns by Vendor")
    report.append("")
    for vendor, count in sorted(stats['patterns_by_vendor'].items()):
        report.append(f"- {vendor}: {count}")
    report.append("")
    
    # Patterns by product
    report.append("## Patterns by Product")
    report.append("")
    for product, count in sorted(stats['patterns_by_product'].items()):
        report.append(f"- {product}: {count}")
    report.append("")
    
    return "\n".join(report)

def extract_vendors_and_products(pattern_files):
    """Extract unique vendors and products from pattern files."""
    vendors = {}
    products = {}
    
    # Process each pattern file
    for pattern_file in pattern_files:
        with open(pattern_file, 'r') as f:
            try:
                pattern_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {pattern_file}: {e}")
                continue
        
        # Extract vendor information
        vendor_id = pattern_data.get('vendor_id', 'unknown')
        vendor_name = pattern_data.get('vendor', 'Unknown')
        
        # Create a basic vendor entry if it doesn't exist
        if vendor_id not in vendors:
            vendors[vendor_id] = {
                "id": vendor_id,
                "name": vendor_name,
                "website": "",
                "description": ""
            }
        
        # Extract product information
        product_id = pattern_data.get('product_id', 'unknown')
        product_name = pattern_data.get('product', 'Unknown')
        category = pattern_data.get('category', 'unknown')
        
        # Create a basic product entry if it doesn't exist
        if product_id not in products:
            products[product_id] = {
                "id": product_id,
                "vendor_id": vendor_id,
                "name": product_name,
                "category": category,
                "website": "",
                "description": ""
            }
    
    return list(vendors.values()), list(products.values())

def update_summary_file(stats, repo_root):
    """Update the PATTERNS_SUMMARY.md file."""
    report = generate_report(stats)
    report_file = os.path.join(repo_root, 'PATTERNS_SUMMARY.md')
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Updated {report_file}")
    return report_file

def update_vendors_file(vendors, data_dir):
    """Update the vendors.json file."""
    vendors_file = os.path.join(data_dir, 'vendors.json')
    
    # Read existing vendors file if it exists
    existing_vendors = {}
    if os.path.exists(vendors_file):
        with open(vendors_file, 'r') as f:
            try:
                existing_data = json.load(f)
                for vendor in existing_data.get('vendors', []):
                    existing_vendors[vendor['id']] = vendor
            except json.JSONDecodeError:
                pass
    
    # Merge with existing data, preserving existing information
    updated_vendors = []
    for vendor in vendors:
        vendor_id = vendor['id']
        if vendor_id in existing_vendors:
            # Preserve existing website and description if they exist
            existing_vendor = existing_vendors[vendor_id]
            updated_vendor = vendor.copy()
            if existing_vendor.get('website'):
                updated_vendor['website'] = existing_vendor['website']
            if existing_vendor.get('description'):
                updated_vendor['description'] = existing_vendor['description']
            updated_vendors.append(updated_vendor)
        else:
            updated_vendors.append(vendor)
    
    # Write updated vendors file
    vendors_data = {
        "vendors": updated_vendors
    }
    
    with open(vendors_file, 'w') as f:
        json.dump(vendors_data, f, indent=2)
    
    print(f"Updated {vendors_file} with {len(updated_vendors)} vendors")

def update_products_file(products, data_dir):
    """Update the products.json file."""
    products_file = os.path.join(data_dir, 'products.json')
    
    # Read existing products file if it exists
    existing_products = {}
    if os.path.exists(products_file):
        with open(products_file, 'r') as f:
            try:
                existing_data = json.load(f)
                for product in existing_data.get('products', []):
                    existing_products[product['id']] = product
            except json.JSONDecodeError:
                pass
    
    # Merge with existing data, preserving existing information
    updated_products = []
    for product in products:
        product_id = product['id']
        if product_id in existing_products:
            # Preserve existing website and description if they exist
            existing_product = existing_products[product_id]
            updated_product = product.copy()
            if existing_product.get('website'):
                updated_product['website'] = existing_product['website']
            if existing_product.get('description'):
                updated_product['description'] = existing_product['description']
            updated_products.append(updated_product)
        else:
            updated_products.append(product)
    
    # Write updated products file
    products_data = {
        "products": updated_products
    }
    
    with open(products_file, 'w') as f:
        json.dump(products_data, f, indent=2)
    
    print(f"Updated {products_file} with {len(updated_products)} products")

def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    data_dir = os.path.join(repo_root, 'data')
    
    print("Updating all data files and statistics...")
    
    # Find all pattern files
    pattern_files = find_pattern_files(repo_root)
    
    if not pattern_files:
        print("No pattern files found!")
        return
    
    print(f"Found {len(pattern_files)} pattern files to analyze")
    
    # Analyze patterns for statistics
    stats = analyze_patterns(pattern_files)
    
    # Update summary file
    summary_file = update_summary_file(stats, repo_root)
    
    # Extract vendors and products
    vendors, products = extract_vendors_and_products(pattern_files)
    
    # Update data files
    update_vendors_file(vendors, data_dir)
    update_products_file(products, data_dir)
    
    print("\nAll data files updated successfully!")
    print(f"Total patterns: {stats['total_patterns']}")
    print(f"Vendors: {len(vendors)}")
    print(f"Products: {len(products)}")

if __name__ == "__main__":
    main()