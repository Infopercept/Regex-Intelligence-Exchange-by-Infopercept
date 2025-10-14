#!/usr/bin/env python3
"""
Generate a comprehensive report of all patterns in the new by-vendor structure
"""

import os
import json
from collections import defaultdict


def generate_patterns_report(patterns_dir):
    """Generate a comprehensive report of all patterns"""
    by_vendor_dir = os.path.join(patterns_dir, 'by-vendor')
    
    if not os.path.exists(by_vendor_dir):
        print("Error: by-vendor directory not found")
        return
    
    # Statistics
    total_patterns = 0
    total_vendors = 0
    total_products = 0
    categories = defaultdict(int)
    vendors_with_most_patterns = []
    
    # Report data
    report_data = {
        'vendors': {},
        'categories': {},
        'summary': {}
    }
    
    print("Generating Patterns Report...")
    print("=" * 50)
    
    # Walk through vendor directories
    for vendor in os.listdir(by_vendor_dir):
        vendor_path = os.path.join(by_vendor_dir, vendor)
        
        if not os.path.isdir(vendor_path) or vendor == 'README.md':
            continue
            
        total_vendors += 1
        vendor_patterns = 0
        vendor_products = 0
        vendor_categories = set()
        
        # Process product files
        for product_file in os.listdir(vendor_path):
            if not product_file.endswith('.json'):
                continue
                
            product_path = os.path.join(vendor_path, product_file)
            vendor_products += 1
            total_products += 1
            
            try:
                with open(product_path, 'r') as f:
                    data = json.load(f)
                
                # Extract information
                product_name = data.get('product', 'Unknown')
                category = data.get('category', 'Unknown')
                vendor_name = data.get('vendor', 'Unknown')
                
                # Count patterns
                all_versions_count = len(data.get('all_versions', []))
                version_patterns_count = 0
                versions = data.get('versions', {})
                for version_patterns_list in versions.values():
                    version_patterns_count += len(version_patterns_list)
                
                product_patterns = all_versions_count + version_patterns_count
                vendor_patterns += product_patterns
                total_patterns += product_patterns
                categories[category] += product_patterns
                vendor_categories.add(category)
                
                # Store product data
                if vendor not in report_data['vendors']:
                    report_data['vendors'][vendor] = {
                        'name': vendor_name,
                        'products': {},
                        'total_patterns': 0,
                        'categories': set()
                    }
                
                report_data['vendors'][vendor]['products'][product_file] = {
                    'name': product_name,
                    'category': category,
                    'patterns': product_patterns,
                    'version_specific_patterns': version_patterns_count,
                    'generic_patterns': all_versions_count
                }
                
                report_data['vendors'][vendor]['total_patterns'] += product_patterns
                report_data['vendors'][vendor]['categories'].add(category)
                
            except Exception as e:
                print(f"Error reading {product_path}: {e}")
        
        # Store vendor data
        vendors_with_most_patterns.append((vendor, vendor_patterns))
    
    # Sort vendors by pattern count
    vendors_with_most_patterns.sort(key=lambda x: x[1], reverse=True)
    
    # Generate report
    print("REGEX INTELLIGENCE EXCHANGE - PATTERNS REPORT")
    print("=" * 50)
    print(f"Generated on: {os.popen('date /t').read().strip()}")
    print()
    
    print("SUMMARY")
    print("-" * 20)
    print(f"Total Patterns: {total_patterns}")
    print(f"Total Vendors: {total_vendors}")
    print(f"Total Products: {total_products}")
    print()
    
    print("PATTERNS BY CATEGORY")
    print("-" * 20)
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"{category}: {count}")
        report_data['categories'][category] = count
    print()
    
    print("TOP VENDORS BY PATTERN COUNT")
    print("-" * 30)
    for vendor, count in vendors_with_most_patterns[:10]:  # Top 10
        vendor_name = report_data['vendors'][vendor]['name']
        print(f"{vendor_name} ({vendor}): {count}")
    print()
    
    print("VENDORS WITH MULTIPLE PRODUCTS")
    print("-" * 30)
    multi_product_vendors = []
    for vendor, data in report_data['vendors'].items():
        if len(data['products']) > 1:
            multi_product_vendors.append((vendor, len(data['products']), data['total_patterns']))
    
    multi_product_vendors.sort(key=lambda x: x[1], reverse=True)
    for vendor, product_count, pattern_count in multi_product_vendors:
        vendor_name = report_data['vendors'][vendor]['name']
        print(f"{vendor_name} ({vendor}): {product_count} products, {pattern_count} patterns")
    print()
    
    print("PATTERNS WITH VERSION-SPECIFIC MATCHING")
    print("-" * 40)
    version_specific_products = []
    for vendor, data in report_data['vendors'].items():
        for product_file, product_data in data['products'].items():
            if product_data['version_specific_patterns'] > 0:
                version_specific_products.append((
                    product_data['name'],
                    product_data['version_specific_patterns'],
                    product_data['generic_patterns']
                ))
    
    version_specific_products.sort(key=lambda x: x[1], reverse=True)
    for product_name, version_patterns, generic_patterns in version_specific_products[:10]:  # Top 10
        print(f"{product_name}: {version_patterns} version-specific, {generic_patterns} generic")
    print()
    
    # Store summary data
    report_data['summary'] = {
        'total_patterns': total_patterns,
        'total_vendors': total_vendors,
        'total_products': total_products,
        'categories': dict(categories),
        'top_vendors': vendors_with_most_patterns[:10]
    }
    
    # Save report data to JSON file
    report_file = os.path.join(os.path.dirname(patterns_dir), 'docs', 'patterns-report.json')
    try:
        # Convert sets to lists for JSON serialization
        for vendor_data in report_data['vendors'].values():
            vendor_data['categories'] = list(vendor_data['categories'])
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"Full report data saved to: {report_file}")
    except Exception as e:
        print(f"Error saving report data: {e}")
    
    return report_data


if __name__ == "__main__":
    # Define paths
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    patterns_dir = os.path.join(workspace_dir, 'patterns')
    
    generate_patterns_report(patterns_dir)