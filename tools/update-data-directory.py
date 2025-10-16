#!/usr/bin/env python3
"""
Update Data Directory Script

This script updates the data directory (vendors.json and products.json) 
based on the current patterns in the repository.
"""

import json
import os
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
    
    # Find all pattern files
    pattern_files = find_pattern_files(repo_root)
    
    if not pattern_files:
        print("No pattern files found!")
        return
    
    print(f"Found {len(pattern_files)} pattern files to analyze")
    
    # Extract vendors and products
    vendors, products = extract_vendors_and_products(pattern_files)
    
    # Update data files
    update_vendors_file(vendors, data_dir)
    update_products_file(products, data_dir)
    
    print("Data directory updated successfully!")

if __name__ == "__main__":
    main()