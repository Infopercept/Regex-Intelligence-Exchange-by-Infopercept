#!/usr/bin/env python3
"""
Script to extract regex patterns from WhatWeb plugins and convert them to Regex-Intelligence-Exchange format
"""

import os
import re
import json
import hashlib
from pathlib import Path

def normalize_string(s):
    """Normalize a string for use as an ID"""
    return re.sub(r'[^a-zA-Z0-9\-_]', '-', s.lower()).strip('-')

def extract_matches_section(content):
    """Extract the matches section from a WhatWeb plugin"""
    # Find the matches section manually
    lines = content.split('\n')
    in_matches = False
    matches_lines = []
    
    for line in lines:
        if '# Matches #' in line:
            in_matches = True
            continue
        elif in_matches and line.strip() == ']' and matches_lines:
            # End of matches section
            matches_lines.append(line)
            break
        elif in_matches:
            matches_lines.append(line)
    
    if matches_lines:
        return ''.join(matches_lines)
    else:
        # If we can't find the matches section, try to find any array of hashes
        return content

def extract_patterns_from_plugin(plugin_path):
    """Extract patterns from a WhatWeb plugin file"""
    with open(plugin_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract plugin name
    name_match = re.search(r'name\s+["\']([^"\']+)["\']', content)
    plugin_name = name_match.group(1) if name_match else "Unknown"
    
    # Extract website if available
    website_match = re.search(r'website\s+["\']([^"\']+)["\']', content)
    website = website_match.group(1) if website_match else ""
    
    # Extract version information
    version_match = re.search(r'version\s+["\']([^"\']+)["\']', content)
    version = version_match.group(1) if version_match else ""
    
    # Extract matches section
    matches_content = extract_matches_section(content)
    
    # Parse individual match patterns
    patterns = []
    
    # Extract regex patterns from matches
    # Look for patterns like {:regexp=>/.../, :version=>/.../, etc.}
    # Handle both {:key=>value} and { :key => value } formats
    match_patterns = re.findall(r'\{\s*[^}]+\s*\}', matches_content)
    
    for match in match_patterns:
        pattern_info = {}
        
        # Extract regex pattern (handle both /pattern/ and "pattern" formats)
        regexp_match = re.search(r':regexp\s*=>\s*(?:/((?:[^/]|(?<=\\)/)+)/|"([^"]+)"|\'([^\']+)\')', match)
        if regexp_match:
            pattern_info['pattern'] = regexp_match.group(1) or regexp_match.group(2) or regexp_match.group(3)
        
        # Extract version regex (handle both /pattern/ and "pattern" formats)
        version_regexp_match = re.search(r':version\s*=>\s*(?:/((?:[^/]|(?<=\\)/)+)/|"([^"]+)"|\'([^\']+)\')', match)
        if version_regexp_match:
            pattern_info['version_pattern'] = version_regexp_match.group(1) or version_regexp_match.group(2) or version_regexp_match.group(3)
        
        # Extract text match
        text_match = re.search(r':text\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if text_match:
            pattern_info['text'] = text_match.group(1) or text_match.group(2)
        
        # Extract MD5 hashes
        md5_match = re.search(r':md5\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if md5_match:
            pattern_info['md5'] = md5_match.group(1) or md5_match.group(2)
        
        # Extract URL
        url_match = re.search(r':url\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if url_match:
            pattern_info['url'] = url_match.group(1) or url_match.group(2)
        
        # Extract search type (headers, body, etc.)
        search_match = re.search(r':search\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if search_match:
            pattern_info['search'] = search_match.group(1) or search_match.group(2)
        
        # Extract status
        status_match = re.search(r':status\s*=>\s*(\d+)', match)
        if status_match:
            pattern_info['status'] = status_match.group(1)
        
        # Extract module
        module_match = re.search(r':module\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if module_match:
            pattern_info['module'] = module_match.group(1) or module_match.group(2)
        
        # Extract certainty
        certainty_match = re.search(r':certainty\s*=>\s*(\d+)', match)
        if certainty_match:
            pattern_info['certainty'] = int(certainty_match.group(1))
        
        # Extract name
        name_match = re.search(r':name\s*=>\s*(?:"([^"]*)"|\'([^\']*)\')', match)
        if name_match:
            pattern_info['pattern_name'] = name_match.group(1) or name_match.group(2)
        
        # Include patterns that have version detection, even if they don't have text or regexp
        if pattern_info:
            patterns.append(pattern_info)
    
    return {
        'plugin_name': plugin_name,
        'website': website,
        'version': version,
        'patterns': patterns
    }

def convert_to_regex_exchange_format(whatweb_data):
    """Convert WhatWeb data to Regex-Intelligence-Exchange format"""
    if not whatweb_data or not whatweb_data['patterns']:
        return None
    
    # Determine vendor and product from plugin name
    plugin_name = whatweb_data['plugin_name']
    
    # Simple heuristic to determine vendor/product
    if ' ' in plugin_name:
        parts = plugin_name.split(' ', 1)
        vendor = parts[0]
        product = parts[1] if len(parts) > 1 else plugin_name
    else:
        vendor = plugin_name
        product = plugin_name
    
    vendor_id = normalize_string(vendor)
    product_id = normalize_string(product)
    
    # Determine category based on common patterns
    category = 'web'
    if any(keyword in plugin_name.lower() for keyword in ['cms', 'content', 'wordpress', 'joomla', 'drupal']):
        category = 'cms'
    elif any(keyword in plugin_name.lower() for keyword in ['server', 'apache', 'nginx', 'iis']):
        category = 'web'
    elif any(keyword in plugin_name.lower() for keyword in ['database', 'mysql', 'postgresql', 'mongodb']):
        category = 'database'
    
    # Group patterns by version or put in all_versions
    versions = {}
    all_versions = []
    
    for pattern in whatweb_data['patterns']:
        pattern_entry = {
            'name': pattern.get('pattern_name', f"{whatweb_data['plugin_name']} Pattern"),
            'priority': pattern.get('certainty', 100),
            'confidence': pattern.get('certainty', 100) / 100.0 if 'certainty' in pattern else 0.8,
            'metadata': {
                'author': 'WhatWeb Project',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01',
                'description': f"Pattern extracted from WhatWeb plugin for {whatweb_data['plugin_name']}",
                'tags': ['whatweb', 'extracted']
            }
        }
        
        # Handle different pattern types
        if 'pattern' in pattern:
            # Convert WhatWeb regex to our format
            converted_pattern = pattern['pattern'].replace('\\/', '/').replace('\\\\', '\\')
            pattern_entry['pattern'] = converted_pattern
            
            # Handle version extraction
            if 'version_pattern' in pattern:
                version_pattern = pattern['version_pattern'].replace('\\/', '/').replace('\\\\', '\\')
                # Try to determine version group (simplified)
                pattern_entry['version_group'] = 1
                
        elif 'version_pattern' in pattern and 'search' in pattern:
            # Handle version patterns in headers
            version_pattern = pattern['version_pattern'].replace('\\/', '/').replace('\\\\', '\\')
            search_type = pattern['search']
            
            # Create appropriate pattern based on search type
            if 'headers[server]' in search_type.lower():
                # For server header version patterns, create the full pattern
                # Extract the actual regex part without delimiters
                pattern_entry['pattern'] = f"Server: {version_pattern}"
                pattern_entry['version_group'] = 1
            elif 'headers' in search_type.lower():
                # Extract header name
                header_match = re.search(r'headers\[([^\]]+)\]', search_type, re.IGNORECASE)
                if header_match:
                    header_name = header_match.group(1)
                    pattern_entry['pattern'] = f"{header_name}: {version_pattern}"
                    pattern_entry['version_group'] = 1
                
        elif 'text' in pattern:
            # Convert text match to regex
            escaped_text = re.escape(pattern['text'])
            pattern_entry['pattern'] = escaped_text
            
        elif 'md5' in pattern:
            # Skip MD5 patterns for now as they're not regex
            continue
            
        else:
            # Skip patterns that don't have recognizable types
            continue
        
        # Add test cases if possible
        if 'text' in pattern:
            pattern_entry['metadata']['test_cases'] = [{
                'input': pattern['text'],
                'expected_version': 'unknown'
            }]
        elif 'pattern' in pattern_entry and 'version_group' in pattern_entry:
            # For version detection patterns, create a sample test case
            sample_pattern = pattern_entry['pattern']
            # Extract the version pattern part
            if 'Server:' in sample_pattern:
                # This is a server header pattern
                version_part = re.search(r'Server:\s*(.*)', sample_pattern)
                if version_part:
                    pattern_entry['metadata']['test_cases'] = [{
                        'input': f"Server: {version_part.group(1).replace('([\\d\\.]+)', '8.5')}",
                        'expected_version': '8.5'
                    }]
            elif ':' in sample_pattern and 'version_group' in pattern_entry:
                # This is a header pattern with version capture
                pattern_entry['metadata']['test_cases'] = [{
                    'input': sample_pattern.replace('([\\d\\.]+)', '1.0'),
                    'expected_version': '1.0'
                }]
        
        # Add to all_versions since we don't have specific version info
        all_versions.append(pattern_entry)
    
    if not all_versions:
        return None
    
    return {
        'vendor': vendor,
        'vendor_id': vendor_id,
        'product': product,
        'product_id': product_id,
        'category': category,
        'versions': versions,
        'all_versions': all_versions
    }

def process_whatweb_plugins(whatweb_plugins_dir, output_dir):
    """Process all WhatWeb plugins and convert them"""
    # Check if directory exists
    if not os.path.exists(whatweb_plugins_dir):
        print(f"Directory {whatweb_plugins_dir} does not exist")
        return []
    
    plugin_files = list(Path(whatweb_plugins_dir).glob('*.rb'))
    print(f"Found {len(plugin_files)} plugin files")
    
    converted_patterns = []
    
    for plugin_file in plugin_files:
        try:
            print(f"Processing {plugin_file.name}...")
            whatweb_data = extract_patterns_from_plugin(plugin_file)
            
            # Debug: Print patterns for Microsoft-IIS
            if "microsoft-iis.rb" in plugin_file.name:
                print(f"Microsoft-IIS patterns: {whatweb_data['patterns']}")
            
            if whatweb_data and whatweb_data['patterns']:
                regex_exchange_data = convert_to_regex_exchange_format(whatweb_data)
                
                if regex_exchange_data:
                    converted_patterns.append({
                        'filename': plugin_file.name.replace('.rb', ''),
                        'data': regex_exchange_data
                    })
        except Exception as e:
            print(f"Error processing {plugin_file.name}: {e}")
            continue
    
    # Save converted patterns
    for pattern in converted_patterns:
        filename = pattern['filename']
        data = pattern['data']
        
        # Create vendor directory
        vendor_dir = Path(output_dir) / data['vendor_id']
        vendor_dir.mkdir(exist_ok=True)
        
        # Save JSON file
        output_file = vendor_dir / f"{data['product_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {output_file}")
    
    print(f"Processed {len(converted_patterns)} plugins")
    return converted_patterns

if __name__ == '__main__':
    # Configuration
    WHATWEB_PLUGINS_DIR = 'whatweb-repo/plugins'
    OUTPUT_DIR = 'patterns/by-vendor'
    
    # Process plugins
    process_whatweb_plugins(WHATWEB_PLUGINS_DIR, OUTPUT_DIR)