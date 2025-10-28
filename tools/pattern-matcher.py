#!/usr/bin/env python3
"""
Simple pattern matcher that demonstrates using patterns from the new structure
"""

import os
import json
import re
import sys
from pathlib import Path

# Import our version utilities
from version_utils import extract_and_normalize_version


def load_patterns(patterns_dir, vendor=None, product=None):
    """Load patterns from the new by-vendor structure"""
    by_vendor_dir = os.path.join(patterns_dir, 'by-vendor')
    patterns = []
    
    if not os.path.exists(by_vendor_dir):
        print("Error: by-vendor directory not found")
        return patterns
    
    # If specific vendor/product specified, load only those
    if vendor and product:
        product_path = os.path.join(by_vendor_dir, vendor, f"{product}.json")
        if os.path.exists(product_path):
            try:
                with open(product_path, 'r') as f:
                    data = json.load(f)
                patterns.extend(extract_patterns(data))
            except Exception as e:
                print(f"Error loading {product_path}: {e}")
        else:
            print(f"Product file not found: {product_path}")
    elif vendor:
        # Load all products for a vendor
        vendor_path = os.path.join(by_vendor_dir, vendor)
        if os.path.exists(vendor_path):
            for product_file in os.listdir(vendor_path):
                if product_file.endswith('.json'):
                    product_path = os.path.join(vendor_path, product_file)
                    try:
                        with open(product_path, 'r') as f:
                            data = json.load(f)
                        patterns.extend(extract_patterns(data))
                    except Exception as e:
                        print(f"Error loading {product_path}: {e}")
        else:
            print(f"Vendor directory not found: {vendor_path}")
    else:
        # Load all patterns
        for vendor_name in os.listdir(by_vendor_dir):
            vendor_path = os.path.join(by_vendor_dir, vendor_name)
            if os.path.isdir(vendor_path) and vendor_name != 'README.md':
                for product_file in os.listdir(vendor_path):
                    if product_file.endswith('.json'):
                        product_path = os.path.join(vendor_path, product_file)
                        try:
                            with open(product_path, 'r') as f:
                                data = json.load(f)
                            patterns.extend(extract_patterns(data))
                        except Exception as e:
                            print(f"Error loading {product_path}: {e}")
    
    return patterns


def extract_patterns(data):
    """Extract all patterns from a product file"""
    patterns = []
    
    # Extract all_versions patterns
    for pattern_data in data.get('all_versions', []):
        patterns.append({
            'vendor': data.get('vendor', 'Unknown'),
            'product': data.get('product', 'Unknown'),
            'name': pattern_data.get('name', 'Unknown'),
            'pattern': pattern_data.get('pattern', ''),
            'version_group': pattern_data.get('version_group', 0),
            'priority': pattern_data.get('priority', 0),
            'confidence': pattern_data.get('confidence', 0.0),
            'category': data.get('category', 'Unknown'),
            'subcategory': data.get('subcategory', 'Unknown')
        })
    
    # Extract version-specific patterns
    versions = data.get('versions', {})
    for version_range, version_patterns in versions.items():
        for pattern_data in version_patterns:
            patterns.append({
                'vendor': data.get('vendor', 'Unknown'),
                'product': data.get('product', 'Unknown'),
                'name': pattern_data.get('name', 'Unknown'),
                'pattern': pattern_data.get('pattern', ''),
                'version_group': pattern_data.get('version_group', 0),
                'priority': pattern_data.get('priority', 0),
                'confidence': pattern_data.get('confidence', 0.0),
                'category': data.get('category', 'Unknown'),
                'subcategory': data.get('subcategory', 'Unknown'),
                'version_range': version_range
            })
    
    return patterns


def match_patterns(patterns, text):
    """Match patterns against text and return results"""
    results = []
    
    for pattern_data in patterns:
        try:
            regex = re.compile(pattern_data['pattern'])
            match = regex.search(text)
            
            if match:
                # Extract and normalize version if version_group is specified
                version = None
                normalized_version = None
                if pattern_data['version_group'] > 0 and pattern_data['version_group'] <= len(match.groups()):
                    version = match.group(pattern_data['version_group'])
                    normalized_version = extract_and_normalize_version(match, pattern_data['version_group'])
                
                results.append({
                    'vendor': pattern_data['vendor'],
                    'product': pattern_data['product'],
                    'name': pattern_data['name'],
                    'matched_text': match.group(0),
                    'version': version,
                    'normalized_version': normalized_version,
                    'priority': pattern_data['priority'],
                    'confidence': pattern_data['confidence'],
                    'category': pattern_data['category'],
                    'subcategory': pattern_data['subcategory']
                })
        except re.error as e:
            print(f"Invalid regex pattern: {pattern_data['pattern']} - {e}")
    
    # Sort by priority (highest first)
    results.sort(key=lambda x: x['priority'], reverse=True)
    return results


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python pattern-matcher.py <text-to-match> [vendor] [product]")
        print("Examples:")
        print("  python pattern-matcher.py 'Server: Apache/2.4.41 (Ubuntu)'")
        print("  python pattern-matcher.py 'Server: Apache/2.4.41 (Ubuntu)' apache httpd")
        print("  python pattern-matcher.py 'Server: nginx/1.18.0' f5-networks nginx")
        return
    
    text = sys.argv[1]
    vendor = sys.argv[2] if len(sys.argv) > 2 else None
    product = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Define paths
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    patterns_dir = os.path.join(workspace_dir, 'patterns')
    
    print(f"Matching patterns against: '{text}'")
    print("=" * 50)
    
    # Load patterns
    patterns = load_patterns(patterns_dir, vendor, product)
    print(f"Loaded {len(patterns)} patterns")
    
    # Match patterns
    results = match_patterns(patterns, text)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} matching patterns:")
        for result in results:
            print(f"\nVendor: {result['vendor']}")
            print(f"Product: {result['product']}")
            print(f"Pattern: {result['name']}")
            print(f"Matched: {result['matched_text']}")
            if result['version']:
                print(f"Raw Version: {result['version']}")
            if result['normalized_version']:
                print(f"Normalized Version: {result['normalized_version']}")
            print(f"Priority: {result['priority']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Category: {result['category']}")
            print(f"Subcategory: {result['subcategory']}")
    else:
        print("\nNo matching patterns found.")


if __name__ == "__main__":
    main()