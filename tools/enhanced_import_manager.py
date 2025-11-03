#!/usr/bin/env python3
"""
Enhanced import manager that adds all regex data from different tools into a single folder
in a structured way while preventing data duplication
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

class EnhancedImportManager:
    """Enhanced import manager for pattern integration without duplication"""
    
    def __init__(self, patterns_dir='patterns/by-vendor'):
        self.patterns_dir = patterns_dir
        self.pattern_index = {}  # Index to track existing patterns
        self.stats = {
            'patterns_processed': 0,
            'patterns_added': 0,
            'patterns_updated': 0,
            'patterns_skipped': 0,
            'duplicates_found': 0
        }
        self._build_pattern_index()
    
    def _build_pattern_index(self):
        """Build an index of existing patterns to detect duplicates"""
        if not os.path.exists(self.patterns_dir):
            return
        
        for root, dirs, files in os.walk(self.patterns_dir):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Handle both single pattern files and multi-version files
                        vendor_id = data.get('vendor_id', '')
                        product_id = data.get('product_id', '')
                        
                        # Index each pattern version
                        if 'all_versions' in data:
                            for i, pattern in enumerate(data['all_versions']):
                                pattern_key = self._generate_pattern_key(pattern, vendor_id, product_id)
                                self.pattern_index[pattern_key] = {
                                    'file': filepath,
                                    'pattern_index': i,
                                    'data': data
                                }
                        else:
                            pattern_key = self._generate_pattern_key(data, vendor_id, product_id)
                            self.pattern_index[pattern_key] = {
                                'file': filepath,
                                'pattern_index': 0,
                                'data': data
                            }
                    except Exception as e:
                        print(f"Warning: Could not process {filepath}: {e}")
    
    def _generate_pattern_key(self, pattern_data, vendor_id, product_id):
        """
        Generate a unique key for a pattern to detect duplicates
        """
        # Create a signature based on key pattern characteristics
        signature_data = {
            'vendor_id': vendor_id,
            'product_id': product_id,
            'pattern_name': pattern_data.get('name', ''),
            'pattern_regex': pattern_data.get('pattern', ''),
            'priority': pattern_data.get('priority', 100)
        }
        
        # Create a hash of the signature
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.md5(signature_str.encode('utf-8')).hexdigest()
    
    def _is_duplicate(self, pattern_data, vendor_id, product_id):
        """
        Check if a pattern is a duplicate
        """
        pattern_key = self._generate_pattern_key(pattern_data, vendor_id, product_id)
        return pattern_key in self.pattern_index
    
    def _merge_patterns(self, existing_data, new_pattern_data):
        """
        Merge new pattern data with existing pattern data
        """
        # If existing data is single pattern, convert to multi-version format
        if 'all_versions' not in existing_data:
            existing_data = {
                'vendor': existing_data.get('vendor', ''),
                'vendor_id': existing_data.get('vendor_id', ''),
                'product': existing_data.get('product', ''),
                'product_id': existing_data.get('product_id', ''),
                'category': existing_data.get('category', 'unknown'),
                'versions': {},
                'all_versions': [existing_data]
            }
        
        # Add new pattern to all_versions
        existing_data['all_versions'].append(new_pattern_data)
        
        # Update metadata to reflect multiple sources
        for pattern in existing_data['all_versions']:
            if 'metadata' in pattern:
                source = pattern['metadata'].get('source', 'Unknown')
                if source not in pattern['metadata'].get('tags', []):
                    pattern['metadata']['tags'].append(source.lower())
        
        return existing_data
    
    def add_pattern(self, pattern_data, source_name):
        """
        Add a pattern to the repository, handling duplicates appropriately
        
        Args:
            pattern_data (dict): Pattern data in standardized format
            source_name (str): Name of the source tool
            
        Returns:
            bool: True if pattern was added/updated, False if skipped
        """
        self.stats['patterns_processed'] += 1
        
        # Extract key information
        vendor = pattern_data.get('vendor', 'unknown')
        product = pattern_data.get('product', 'unknown')
        vendor_id = pattern_data.get('vendor_id', vendor.lower().replace(' ', '-'))
        product_id = pattern_data.get('product_id', product.lower().replace(' ', '-'))
        
        # Ensure vendor and product IDs are valid
        vendor_id = "".join(c for c in vendor_id if c.isalnum() or c in ['-', '_']).strip('-')
        product_id = "".join(c for c in product_id if c.isalnum() or c in ['-', '_']).strip('-')
        
        # Create pattern directory
        vendor_dir = Path(self.patterns_dir) / vendor_id
        vendor_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern file path
        pattern_file = vendor_dir / f"{product_id}.json"
        
        # Check if pattern already exists
        if pattern_file.exists():
            try:
                # Load existing pattern
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                # Check if this specific pattern version already exists
                if self._is_duplicate(pattern_data, vendor_id, product_id):
                    self.stats['patterns_skipped'] += 1
                    self.stats['duplicates_found'] += 1
                    return False
                
                # Merge with existing pattern
                merged_data = self._merge_patterns(existing_data, pattern_data)
                self.stats['patterns_updated'] += 1
                
            except Exception as e:
                print(f"Error reading existing pattern {pattern_file}: {e}")
                merged_data = pattern_data
                self.stats['patterns_added'] += 1
        else:
            # New pattern
            merged_data = pattern_data
            self.stats['patterns_added'] += 1
        
        # Save the pattern
        try:
            with open(pattern_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving pattern {pattern_file}: {e}")
            return False
    
    def import_from_source(self, patterns_list, source_name):
        """
        Import patterns from a source
        
        Args:
            patterns_list (list): List of pattern data dictionaries
            source_name (str): Name of the source tool
        """
        print(f"Importing {len(patterns_list)} patterns from {source_name}...")
        
        for pattern_data in patterns_list:
            self.add_pattern(pattern_data, source_name)
        
        print(f"Completed importing from {source_name}")
        print(f"  - Processed: {self.stats['patterns_processed']}")
        print(f"  - Added: {self.stats['patterns_added']}")
        print(f"  - Updated: {self.stats['patterns_updated']}")
        print(f"  - Skipped (duplicates): {self.stats['patterns_skipped']}")
    
    def get_statistics(self):
        """
        Get import statistics
        
        Returns:
            dict: Statistics about the import process
        """
        return self.stats
    
    def consolidate_patterns(self):
        """
        Consolidate all patterns in the repository to ensure consistent format
        """
        print("Consolidating patterns...")
        consolidated_count = 0
        
        for root, dirs, files in os.walk(self.patterns_dir):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Ensure consistent format
                        if 'all_versions' not in data:
                            # Convert single pattern to multi-version format
                            consolidated_data = {
                                'vendor': data.get('vendor', ''),
                                'vendor_id': data.get('vendor_id', ''),
                                'product': data.get('product', ''),
                                'product_id': data.get('product_id', ''),
                                'category': data.get('category', 'unknown'),
                                'subcategory': data.get('subcategory', ''),
                                'versions': data.get('versions', {}),
                                'all_versions': [data]
                            }
                        else:
                            # Ensure all required fields are present
                            consolidated_data = data
                            if 'versions' not in consolidated_data:
                                consolidated_data['versions'] = {}
                            if 'subcategory' not in consolidated_data:
                                consolidated_data['subcategory'] = ''
                        
                        # Save consolidated data
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
                        
                        consolidated_count += 1
                        
                    except Exception as e:
                        print(f"Error consolidating {filepath}: {e}")
        
        print(f"Consolidated {consolidated_count} pattern files")

def main():
    """Main function to demonstrate usage"""
    print("Enhanced Import Manager for Regex Intelligence Exchange")
    print("=" * 55)
    
    # Create import manager
    import_manager = EnhancedImportManager()
    
    # Example usage:
    # import_manager.import_from_source(patterns_list, "WhatWeb")
    # import_manager.import_from_source(patterns_list, "Wappalyzer")
    # import_manager.import_from_source(patterns_list, "WebTech")
    
    print("Import manager ready. Use import_from_source() to add patterns.")
    print("Statistics:", import_manager.get_statistics())

if __name__ == '__main__':
    main()