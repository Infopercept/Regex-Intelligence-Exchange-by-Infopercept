#!/usr/bin/env python3
"""
Script to import regex patterns from WebTech database and convert them to Regex-Intelligence-Exchange format
"""

import os
import re
import json
import hashlib
from pathlib import Path

def normalize_string(s):
    """Normalize a string for use as an ID"""
    return re.sub(r'[^a-zA-Z0-9\-_]', '-', s.lower()).strip('-')

def extract_patterns_from_webtech(webtech_data):
    """Extract patterns from WebTech database"""
    patterns = []
    
    # WebTech data format may vary, but typically has tech entries with patterns
    for tech_name, tech_data in webtech_data.items():
        pattern_info = {
            'tech_name': tech_name,
            'cats': tech_data.get('cats', []),
            'website': tech_data.get('website', ''),
            'implies': tech_data.get('implies', []),
            'patterns': []
        }
        
        # Extract different types of patterns
        for pattern_type in ['html', 'headers', 'meta', 'script', 'url', 'cookies', 'js']:
            if pattern_type in tech_data:
                patterns_data = tech_data[pattern_type]
                
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

def convert_to_regex_exchange_format(webtech_pattern):
    """Convert WebTech pattern to Regex-Intelligence-Exchange format"""
    if not webtech_pattern or not webtech_pattern['patterns']:
        return None
    
    tech_name = webtech_pattern['tech_name']
    
    # Determine vendor and product from tech name
    if ' ' in tech_name:
        parts = tech_name.split(' ', 1)
        vendor = parts[0]
        product = parts[1] if len(parts) > 1 else tech_name
    else:
        vendor = tech_name
        product = tech_name
    
    vendor_id = normalize_string(vendor)
    product_id = normalize_string(product)
    
    # Determine category based on WebTech categories
    category = 'web'
    if any(cat in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for cat in webtech_pattern['cats']):
        category = 'web'
    elif any(cat in [11, 12, 13, 14] for cat in webtech_pattern['cats']):
        category = 'cms'
    elif any(cat in [15, 16, 17, 18, 19, 20] for cat in webtech_pattern['cats']):
        category = 'database'
    
    # Convert patterns
    all_versions = []
    
    for pattern in webtech_pattern['patterns']:
        pattern_entry = {
            'name': f"{tech_name} {pattern['type'].title()} Pattern",
            'priority': 100,
            'confidence': 0.8,
            'metadata': {
                'author': 'WebTech Project',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01',
                'description': f"Pattern extracted from WebTech for {tech_name}",
                'tags': ['webtech', 'extracted'],
                'source': 'WebTech',
                'license': 'MIT',
                'severity': 'low',
                'cvss_score': 0.0,
                'cwe_ids': [],
                'affected_versions': [],
                'remediation': 'Keep the software updated to the latest stable version'
            }
        }
        
        # Convert WebTech pattern to regex
        webtech_pattern_str = pattern['pattern']
        
        # Handle different pattern types
        if pattern['type'] == 'headers':
            # For headers, we need to create a full header pattern
            # Example: "Server" -> "Server: .*"
            if ':' not in webtech_pattern_str:
                pattern_entry['pattern'] = f"{webtech_pattern_str}: .*"
            else:
                pattern_entry['pattern'] = webtech_pattern_str
        elif pattern['type'] == 'html':
            # Escape HTML patterns for regex
            pattern_entry['pattern'] = re.escape(webtech_pattern_str)
        elif pattern['type'] == 'meta':
            # Meta patterns are usually attribute-based
            pattern_entry['pattern'] = re.escape(webtech_pattern_str)
        elif pattern['type'] == 'script':
            # Script patterns are usually URLs or content
            pattern_entry['pattern'] = re.escape(webtech_pattern_str)
        elif pattern['type'] == 'url':
            # URL patterns might need regex conversion
            pattern_entry['pattern'] = webtech_pattern_str
        else:
            # For other types, escape the pattern
            pattern_entry['pattern'] = re.escape(webtech_pattern_str)
        
        # Handle version extraction
        if pattern['version']:
            # If version is specified, try to create a version capture group
            version_pattern = pattern['version']
            if '\\1' in version_pattern:
                # This indicates a capture group reference
                pattern_entry['version_group'] = 1
            else:
                # Try to extract version from the pattern itself
                version_match = re.search(r'v([0-9.]+)', webtech_pattern_str)
                if version_match:
                    pattern_entry['version_group'] = 1
        
        # Add test cases
        pattern_entry['metadata']['test_cases'] = [{
            'input': webtech_pattern_str,
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

def process_webtech_data(webtech_file, output_dir):
    """Process WebTech data and convert it"""
    # Check if file exists
    if not os.path.exists(webtech_file):
        print(f"File {webtech_file} does not exist")
        return []
    
    # Load WebTech data
    with open(webtech_file, 'r', encoding='utf-8') as f:
        webtech_data = json.load(f)
    
    print(f"Loaded WebTech data with {len(webtech_data)} tech entries")
    
    converted_patterns = []
    
    # Process each tech
    for tech_name, tech_data in webtech_data.items():
        try:
            print(f"Processing {tech_name}...")
            
            # Create pattern info structure
            pattern_info = {
                'tech_name': tech_name,
                'cats': tech_data.get('cats', []),
                'website': tech_data.get('website', ''),
                'implies': tech_data.get('implies', []),
                'patterns': []
            }
            
            # Extract different types of patterns
            for pattern_type in ['html', 'headers', 'meta', 'script', 'url', 'cookies', 'js']:
                if pattern_type in tech_data:
                    patterns_data = tech_data[pattern_type]
                    
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
                        'tech_name': tech_name,
                        'data': regex_exchange_data
                    })
        except Exception as e:
            print(f"Error processing {tech_name}: {e}")
            continue
    
    # Save converted patterns
    for pattern in converted_patterns:
        tech_name = pattern['tech_name']
        data = pattern['data']
        
        # Create vendor directory
        vendor_dir = Path(output_dir) / data['vendor_id']
        vendor_dir.mkdir(exist_ok=True)
        
        # Save JSON file
        output_file = vendor_dir / f"{data['product_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {output_file}")
    
    print(f"Processed {len(converted_patterns)} tech entries")
    return converted_patterns

if __name__ == '__main__':
    # Configuration
    WEBTECH_FILE = 'external/webtech/webtech.json'
    OUTPUT_DIR = 'patterns/by-vendor'
    
    # Process WebTech data
    process_webtech_data(WEBTECH_FILE, OUTPUT_DIR)