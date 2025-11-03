#!/usr/bin/env python3
"""
Script to import regex patterns from Wappalyzer database and convert them to Regex-Intelligence-Exchange format
"""

import os
import re
import json
import hashlib
from pathlib import Path

def normalize_string(s):
    """Normalize a string for use as an ID"""
    return re.sub(r'[^a-zA-Z0-9\-_]', '-', s.lower()).strip('-')

def extract_patterns_from_wappalyzer(wappalyzer_data):
    """Extract patterns from Wappalyzer database"""
    patterns = []
    
    # Wappalyzer data is typically in a JSON format with apps
    if 'apps' in wappalyzer_data:
        for app_name, app_data in wappalyzer_data['apps'].items():
            pattern_info = {
                'app_name': app_name,
                'cats': app_data.get('cats', []),
                'website': app_data.get('website', ''),
                'implies': app_data.get('implies', []),
                'patterns': []
            }
            
            # Extract different types of patterns
            for pattern_type in ['html', 'headers', 'meta', 'script', 'url', 'cookies', 'js']:
                if pattern_type in app_data:
                    patterns_data = app_data[pattern_type]
                    
                    # Handle different pattern formats
                    if isinstance(patterns_data, dict):
                        # Dict format: { "pattern": "version" }
                        for pattern, version in patterns_data.items():
                            pattern_info['patterns'].append({
                                'type': pattern_type,
                                'pattern': pattern,
                                'version': version if version else ''
                            })
                    elif isinstance(patterns_data, list):
                        # List format: ["pattern1", "pattern2"]
                        for pattern in patterns_data:
                            pattern_info['patterns'].append({
                                'type': pattern_type,
                                'pattern': pattern,
                                'version': ''
                            })
                    elif isinstance(patterns_data, str):
                        # String format: "pattern"
                        pattern_info['patterns'].append({
                            'type': pattern_type,
                            'pattern': patterns_data,
                            'version': ''
                        })
            
            patterns.append(pattern_info)
    
    return patterns

def convert_to_regex_exchange_format(wappalyzer_pattern):
    """Convert Wappalyzer pattern to Regex-Intelligence-Exchange format"""
    if not wappalyzer_pattern or not wappalyzer_pattern['patterns']:
        return None
    
    app_name = wappalyzer_pattern['app_name']
    
    # Determine vendor and product from app name
    if ' ' in app_name:
        parts = app_name.split(' ', 1)
        vendor = parts[0]
        product = parts[1] if len(parts) > 1 else app_name
    else:
        vendor = app_name
        product = app_name
    
    vendor_id = normalize_string(vendor)
    product_id = normalize_string(product)
    
    # Determine category based on Wappalyzer categories
    category = 'web'
    if any(cat in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for cat in wappalyzer_pattern['cats']):
        category = 'web'
    elif any(cat in [11, 12, 13, 14] for cat in wappalyzer_pattern['cats']):
        category = 'cms'
    elif any(cat in [15, 16, 17, 18, 19, 20] for cat in wappalyzer_pattern['cats']):
        category = 'database'
    
    # Convert patterns
    all_versions = []
    
    for pattern in wappalyzer_pattern['patterns']:
        pattern_entry = {
            'name': f"{app_name} {pattern['type'].title()} Pattern",
            'priority': 100,
            'confidence': 0.8,
            'metadata': {
                'author': 'Wappalyzer Project',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01',
                'description': f"Pattern extracted from Wappalyzer for {app_name}",
                'tags': ['wappalyzer', 'extracted'],
                'source': 'Wappalyzer',
                'license': 'MIT',
                'severity': 'low',
                'cvss_score': 0.0,
                'cwe_ids': [],
                'affected_versions': [],
                'remediation': 'Keep the software updated to the latest stable version'
            }
        }
        
        # Convert Wappalyzer pattern to regex
        wappalyzer_pattern_str = pattern['pattern']
        
        # Handle different pattern types
        if pattern['type'] == 'headers':
            # For headers, we need to create a full header pattern
            # Example: "Server" -> "Server: .*"
            if ':' not in wappalyzer_pattern_str:
                pattern_entry['pattern'] = f"{wappalyzer_pattern_str}: .*"
            else:
                pattern_entry['pattern'] = wappalyzer_pattern_str
        elif pattern['type'] == 'html':
            # Escape HTML patterns for regex
            pattern_entry['pattern'] = re.escape(wappalyzer_pattern_str)
        elif pattern['type'] == 'meta':
            # Meta patterns are usually attribute-based
            pattern_entry['pattern'] = re.escape(wappalyzer_pattern_str)
        elif pattern['type'] == 'script':
            # Script patterns are usually URLs or content
            pattern_entry['pattern'] = re.escape(wappalyzer_pattern_str)
        elif pattern['type'] == 'url':
            # URL patterns might need regex conversion
            pattern_entry['pattern'] = wappalyzer_pattern_str
        else:
            # For other types, escape the pattern
            pattern_entry['pattern'] = re.escape(wappalyzer_pattern_str)
        
        # Handle version extraction
        if pattern['version']:
            # If version is specified, try to create a version capture group
            version_pattern = pattern['version']
            if '\\1' in version_pattern:
                # This indicates a capture group reference
                pattern_entry['version_group'] = 1
            else:
                # Try to extract version from the pattern itself
                version_match = re.search(r'v([0-9.]+)', wappalyzer_pattern_str)
                if version_match:
                    pattern_entry['version_group'] = 1
        
        # Add test cases
        pattern_entry['metadata']['test_cases'] = [{
            'input': wappalyzer_pattern_str,
            'expected_version': pattern['version'] if pattern['version'] else 'unknown'
        }]
        
        all_versions.append(pattern_entry)
    
    if not all_versions:
        return None
    
    return {
        'vendor': vendor,
        'vendor_id': vendor_id,
        'product': product,
        'product_id': product_id,
        'category': category,
        'versions': {},
        'all_versions': all_versions
    }

def process_wappalyzer_data(wappalyzer_file, output_dir):
    """Process Wappalyzer data and convert it"""
    # Check if file exists
    if not os.path.exists(wappalyzer_file):
        print(f"File {wappalyzer_file} does not exist")
        return []
    
    # Load Wappalyzer data
    with open(wappalyzer_file, 'r', encoding='utf-8') as f:
        wappalyzer_data = json.load(f)
    
    print(f"Loaded Wappalyzer data with {len(wappalyzer_data.get('apps', {}))} apps")
    
    converted_patterns = []
    
    # Process each app
    for app_name, app_data in wappalyzer_data.get('apps', {}).items():
        try:
            print(f"Processing {app_name}...")
            
            # Create pattern info structure
            pattern_info = {
                'app_name': app_name,
                'cats': app_data.get('cats', []),
                'website': app_data.get('website', ''),
                'implies': app_data.get('implies', []),
                'patterns': []
            }
            
            # Extract different types of patterns
            for pattern_type in ['html', 'headers', 'meta', 'script', 'url', 'cookies', 'js']:
                if pattern_type in app_data:
                    patterns_data = app_data[pattern_type]
                    
                    # Handle different pattern formats
                    if isinstance(patterns_data, dict):
                        # Dict format: { "pattern": "version" }
                        for pattern, version in patterns_data.items():
                            pattern_info['patterns'].append({
                                'type': pattern_type,
                                'pattern': pattern,
                                'version': version if version else ''
                            })
                    elif isinstance(patterns_data, list):
                        # List format: ["pattern1", "pattern2"]
                        for pattern in patterns_data:
                            pattern_info['patterns'].append({
                                'type': pattern_type,
                                'pattern': pattern,
                                'version': ''
                            })
                    elif isinstance(patterns_data, str):
                        # String format: "pattern"
                        pattern_info['patterns'].append({
                            'type': pattern_type,
                            'pattern': patterns_data,
                            'version': ''
                        })
            
            if pattern_info['patterns']:
                regex_exchange_data = convert_to_regex_exchange_format(pattern_info)
                
                if regex_exchange_data:
                    converted_patterns.append({
                        'app_name': app_name,
                        'data': regex_exchange_data
                    })
        except Exception as e:
            print(f"Error processing {app_name}: {e}")
            continue
    
    # Save converted patterns
    for pattern in converted_patterns:
        app_name = pattern['app_name']
        data = pattern['data']
        
        # Create vendor directory
        vendor_dir = Path(output_dir) / data['vendor_id']
        vendor_dir.mkdir(exist_ok=True)
        
        # Save JSON file
        output_file = vendor_dir / f"{data['product_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {output_file}")
    
    print(f"Processed {len(converted_patterns)} apps")
    return converted_patterns

if __name__ == '__main__':
    # Configuration
    WAPPALYZER_FILE = 'external/wappalyzer/apps.json'
    OUTPUT_DIR = 'patterns/by-vendor'
    
    # Process Wappalyzer data
    process_wappalyzer_data(WAPPALYZER_FILE, OUTPUT_DIR)