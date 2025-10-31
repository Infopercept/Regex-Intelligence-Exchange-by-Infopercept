#!/usr/bin/env python3
"""
AI-Powered Pattern Generation for Regex Intelligence Exchange
"""

import json
import os
import sys
import re
from pathlib import Path
import random
from datetime import datetime


def generate_pattern_name(vendor, product, version_range=None):
    """Generate a descriptive pattern name."""
    if version_range:
        return f"{vendor} {product} {version_range} Detection"
    else:
        return f"{vendor} {product} Generic Detection"


def generate_regex_pattern(vendor, product, pattern_type="generic"):
    """Generate a regex pattern based on vendor and product names."""
    # Normalize vendor and product names for regex
    vendor_clean = re.sub(r'[^a-zA-Z0-9]', '', vendor)
    product_clean = re.sub(r'[^a-zA-Z0-9]', '', product)
    
    # Different pattern types for variety
    if pattern_type == "header":
        return f"(?i){vendor_clean}[/-]([\\d.]+)"
    elif pattern_type == "banner":
        return f"(?i){vendor_clean}[ /]([\\d.]+)"
    elif pattern_type == "html":
        return f"(?i){product_clean}[ /]v([\\d.]+)"
    else:  # generic
        return f"(?i)({vendor_clean}|{product_clean})[ /-]([\\d.]+)"


def generate_test_cases(vendor, product, pattern):
    """Generate test cases for a pattern."""
    # Extract potential version numbers from vendor/product names
    versions = ["1.0.0", "2.0.0", "2.4.41", "3.1.0", "latest"]
    
    test_cases = []
    for version in versions:
        # Generate realistic test input based on pattern type
        if "Server:" in pattern:
            test_input = f"Server: {vendor}/{version}"
        elif "header" in pattern.lower():
            test_input = f"{vendor}-header: {version}"
        elif "banner" in pattern.lower():
            test_input = f"{vendor} banner: {version}"
        else:
            test_input = f"{vendor}/{product} version {version}"
        
        test_cases.append({
            "input": test_input,
            "expected_version": version
        })
    
    return test_cases


def generate_ai_pattern(vendor, product, vendor_id=None, product_id=None):
    """Generate an AI-powered pattern."""
    if not vendor_id:
        vendor_id = vendor.lower().replace(' ', '-').replace('.', '')
    if not product_id:
        product_id = product.lower().replace(' ', '-').replace('.', '')
    
    # Determine category based on product type
    web_products = ["http", "web", "server", "apache", "nginx", "iis"]
    cms_products = ["wordpress", "drupal", "joomla", "magento"]
    database_products = ["mysql", "postgresql", "mongodb", "oracle", "sql"]
    
    product_lower = product.lower()
    if any(wp in product_lower for wp in web_products):
        category = "web"
        subcategory = "web-server"
    elif any(cp in product_lower for cp in cms_products):
        category = "cms"
        subcategory = "cms-platform"
    elif any(dp in product_lower for dp in database_products):
        category = "database"
        subcategory = "database-engine"
    else:
        category = "web"
        subcategory = "web-application"
    
    # Generate multiple patterns for different contexts
    patterns = {
        "all_versions": [],
        "versions": {}
    }
    
    # Generate all-versions patterns
    pattern_types = ["generic", "header", "banner"]
    for i, ptype in enumerate(pattern_types):
        pattern_obj = {
            "name": generate_pattern_name(vendor, product),
            "pattern": generate_regex_pattern(vendor, product, ptype),
            "version_group": 2 if ptype == "generic" else 1,
            "priority": 100 - (i * 10),
            "confidence": round(0.8 - (i * 0.1), 2),
            "metadata": {
                "author": "AI Pattern Generator",
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "updated_at": datetime.now().strftime("%Y-%m-%d"),
                "description": f"AI-generated pattern for {vendor} {product}",
                "tags": ["ai-generated", vendor.lower(), product.lower(), ptype],
                "test_cases": generate_test_cases(vendor, product, ptype)
            }
        }
        patterns["all_versions"].append(pattern_obj)
    
    # Generate version-specific patterns for common versions
    common_versions = ["1.x", "2.x", "3.x"]
    for version in common_versions:
        patterns["versions"][version] = []
        for i, ptype in enumerate(pattern_types[:2]):  # Limit to 2 types for version-specific
            pattern_obj = {
                "name": generate_pattern_name(vendor, product, version),
                "pattern": generate_regex_pattern(vendor, product, ptype),
                "version_group": 2 if ptype == "generic" else 1,
                "priority": 150 - (i * 20),
                "confidence": round(0.9 - (i * 0.1), 2),
                "metadata": {
                    "author": "AI Pattern Generator",
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                    "description": f"AI-generated pattern for {vendor} {product} version {version}",
                    "tags": ["ai-generated", vendor.lower(), product.lower(), ptype, f"version-{version}"],
                    "test_cases": generate_test_cases(vendor, product, ptype)
                }
            }
            patterns["versions"][version].append(pattern_obj)
    
    # Create the complete pattern structure
    pattern_data = {
        "vendor": vendor,
        "vendor_id": vendor_id,
        "product": product,
        "product_id": product_id,
        "category": category,
        "subcategory": subcategory,
        "versions": patterns["versions"],
        "all_versions": patterns["all_versions"]
    }
    
    return pattern_data


def save_pattern(pattern_data, output_dir="ai-generated-patterns"):
    """Save a pattern to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename
    filename = f"{pattern_data['vendor_id']}_{pattern_data['product_id']}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save pattern
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(pattern_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated pattern saved to: {filepath}")
    return filepath


def generate_batch_patterns(vendor_product_list, output_dir="ai-generated-patterns"):
    """Generate patterns for a list of vendor/product pairs."""
    generated_patterns = []
    
    for vendor, product in vendor_product_list:
        try:
            print(f"Generating pattern for {vendor} - {product}...")
            pattern = generate_ai_pattern(vendor, product)
            filepath = save_pattern(pattern, output_dir)
            generated_patterns.append({
                "vendor": vendor,
                "product": product,
                "filepath": filepath
            })
        except Exception as e:
            print(f"Error generating pattern for {vendor} - {product}: {e}")
    
    return generated_patterns


def main():
    """Main function."""
    # Example vendor/product pairs
    example_pairs = [
        ("Acme Corp", "WebServer Pro"),
        ("BetaSoft", "ContentManager"),
        ("GammaTech", "Database Engine"),
        ("Delta Systems", "Messaging Platform"),
        ("Epsilon Solutions", "Network Monitor")
    ]
    
    print("AI-Powered Pattern Generation for Regex Intelligence Exchange")
    print("=" * 60)
    
    # Generate example patterns
    print("\nGenerating example patterns...")
    generated = generate_batch_patterns(example_pairs)
    
    print(f"\nGenerated {len(generated)} patterns:")
    for pattern in generated:
        print(f"  - {pattern['vendor']} {pattern['product']}: {pattern['filepath']}")
    
    # Show an example pattern
    if generated:
        example_file = generated[0]['filepath']
        print(f"\nExample pattern content from {example_file}:")
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:500] + "..." if len(content) > 500 else content)
        except Exception as e:
            print(f"Error reading example file: {e}")
    
    print("\nTo generate patterns for your own vendor/product pairs:")
    print("  python ai-pattern-generator.py --vendor 'Your Vendor' --product 'Your Product'")
    print("  python ai-pattern-generator.py --batch 'vendors.txt'")


if __name__ == "__main__":
    main()