#!/usr/bin/env python3
"""
Script to enhance metadata in pattern files with additional information
"""

import json
import os
import sys
import re
from datetime import datetime


def enhance_pattern_metadata(file_path):
    """Enhance metadata in a pattern file with additional information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Enhance top-level metadata if needed
        if 'subcategory' not in data:
            # Add subcategory based on category
            category = data.get('category', 'web')
            subcategory_map = {
                'web': 'web-application',
                'cms': 'cms-platform',
                'database': 'database-engine',
                'framework': 'web-framework',
                'messaging': 'message-queue',
                'networking': 'network-device',
                'os': 'linux-distribution'
            }
            data['subcategory'] = subcategory_map.get(category, 'web-application')
        
        # Get vendor and product for reference creation
        vendor = data.get('vendor', '')
        product = data.get('product', '')
        
        # Enhance pattern metadata
        all_patterns = []
        pattern_paths = []
        
        if 'all_versions' in data:
            all_patterns.extend(data['all_versions'])
            pattern_paths.extend([('all_versions', i) for i in range(len(data['all_versions']))])
        
        if 'versions' in data:
            for version, version_patterns in data['versions'].items():
                all_patterns.extend(version_patterns)
                pattern_paths.extend([('versions', version, i) for i in range(len(version_patterns))])
        
        enhanced_count = 0
        for i, pattern in enumerate(all_patterns):
            if 'metadata' in pattern:
                metadata = pattern['metadata']
                enhanced = False
                
                # Add source if missing
                if 'source' not in metadata:
                    metadata['source'] = 'WhatWeb'
                    enhanced = True
                
                # Add license if missing
                if 'license' not in metadata:
                    metadata['license'] = 'MIT'
                    enhanced = True
                
                # Add references if missing and we can infer them
                if 'references' not in metadata:
                    # Create references based on vendor/product
                    references = []
                    if vendor.lower() == 'apache' and product.lower() == 'httpd':
                        references.append({
                            "title": "Apache HTTP Server Documentation",
                            "url": "https://httpd.apache.org/docs/"
                        })
                    elif vendor.lower() == 'nginx':
                        references.append({
                            "title": "nginx Documentation",
                            "url": "https://nginx.org/en/docs/"
                        })
                    elif vendor.lower() == 'wordpress':
                        references.append({
                            "title": "WordPress Developer Resources",
                            "url": "https://developer.wordpress.org/"
                        })
                    
                    if references:
                        metadata['references'] = references
                        enhanced = True
                
                # Add severity if missing and we can infer it
                if 'severity' not in metadata:
                    # Default to low severity for most patterns
                    metadata['severity'] = 'low'
                    enhanced = True
                
                # Add CVSS score if missing
                if 'cvss_score' not in metadata:
                    metadata['cvss_score'] = 0.0
                    enhanced = True
                
                # Add CWE IDs if missing
                if 'cwe_ids' not in metadata:
                    metadata['cwe_ids'] = []
                    enhanced = True
                
                # Add affected versions if missing
                if 'affected_versions' not in metadata:
                    metadata['affected_versions'] = []
                    enhanced = True
                
                # Add remediation if missing
                if 'remediation' not in metadata:
                    if vendor.lower() == 'apache' and product.lower() == 'httpd':
                        metadata['remediation'] = 'Keep Apache HTTPD updated to the latest stable version'
                    elif vendor.lower() == 'nginx':
                        metadata['remediation'] = 'Keep nginx updated to the latest stable version'
                    elif vendor.lower() == 'wordpress':
                        metadata['remediation'] = 'Keep WordPress updated to the latest stable version'
                    else:
                        metadata['remediation'] = 'Keep the software updated to the latest stable version'
                    enhanced = True
                
                if enhanced:
                    enhanced_count += 1
        
        # Write the enhanced data back to the file
        if enhanced_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Enhanced metadata in {file_path}: {enhanced_count} patterns updated")
            return True
        else:
            print(f"No metadata enhancements needed for {file_path}")
            return False
    
    except Exception as e:
        print(f"Error enhancing {file_path}: {e}")
        return False


def enhance_all_patterns(patterns_dir, limit=None):
    """Enhance metadata in all pattern files."""
    enhanced_files = 0
    error_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                processed_files += 1
                
                if enhance_pattern_metadata(file_path):
                    enhanced_files += 1
                
                # Limit processing if specified
                if limit and processed_files >= limit:
                    break
        
        if limit and processed_files >= limit:
            break
    
    print(f"\nSummary: {enhanced_files} files enhanced, {error_files} errors, {processed_files} processed")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
        limit = None
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    enhance_all_patterns(patterns_dir, limit)