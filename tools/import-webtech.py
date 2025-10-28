#!/usr/bin/env python3
"""
Script to import patterns from WebTech technology definitions
"""

import json
import re
import sys
import os
from urllib.parse import urlparse


def load_webtech_technologies(file_path):
    """
    Load WebTech technology definitions from a JSON file.
    
    Args:
        file_path (str): Path to the WebTech apps JSON file
        
    Returns:
        dict: Technology definitions
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # WebTech format has technologies under the 'apps' key
        if isinstance(data, dict) and 'apps' in data:
            return data['apps']
        elif isinstance(data, dict):
            return data
        else:
            return {}
    except Exception as e:
        print(f"Error loading WebTech technologies: {e}")
        return {}


def convert_webtech_category(webtech_category):
    """
    Convert WebTech category to our category system.
    
    Args:
        webtech_category (int): WebTech category ID
        
    Returns:
        tuple: (category, subcategory)
    """
    # WebTech uses the same category IDs as Wappalyzer
    # This is a simplified mapping for common categories
    id_mapping = {
        1: ('cms', 'cms-platform'),      # CMS
        6: ('cms', 'ecommerce'),         # Ecommerce
        10: ('web', 'web-application'),   # Analytics
        12: ('web', 'web-application'),   # JavaScript frameworks
        18: ('framework', 'web-framework'),       # Web Frameworks
        22: ('web', 'web-server'),       # Web Servers
        25: ('framework', 'frontend-framework'),  # JavaScript graphics
        27: ('framework', 'web-framework'),        # Programming Languages (treated as frameworks)
        31: ('web', 'cdn'),              # CDN
        32: ('web', 'web-application'),   # Marketing automation
        36: ('web', 'web-application'),   # Advertising
        59: ('framework', 'frontend-framework'),   # JavaScript libraries
        62: ('web', 'web-application')   # PaaS
    }
    
    return id_mapping.get(webtech_category, ('web', 'web-application'))


def convert_webtech_pattern(webtech_pattern):
    """
    Convert WebTech pattern to our regex format.
    
    Args:
        webtech_pattern (str): WebTech pattern string
        
    Returns:
        str: Converted regex pattern
    """
    # Remove version capture group markers if present
    pattern = webtech_pattern
    pattern = re.sub(r'\\;version:\\\d+', '', pattern)
    pattern = re.sub(r'\\;version:', '', pattern)
    pattern = re.sub(r';version:\\\d+', '', pattern)
    pattern = re.sub(r';version:', '', pattern)
    pattern = re.sub(r'\\;confidence:\d+', '', pattern)
    
    # Unescape forward slashes that WebTech escapes
    pattern = pattern.replace('\\/', '/')
    
    return pattern


def extract_version_group(webtech_pattern):
    """
    Extract version group information from WebTech pattern.
    
    Args:
        webtech_pattern (str): WebTech pattern string
        
    Returns:
        int: Version group number (0 if no version capture)
    """
    # Look for version capture group markers
    match = re.search(r'\\;version:\\(\d+)', webtech_pattern)
    if match:
        return int(match.group(1))
    
    match = re.search(r';version:\\(\d+)', webtech_pattern)
    if match:
        return int(match.group(1))
        
    return 0


def create_pattern_structure(tech_name, tech_data):
    """
    Create our pattern structure from WebTech technology data.
    
    Args:
        tech_name (str): Technology name
        tech_data (dict): WebTech technology data
        
    Returns:
        dict: Our pattern structure
    """
    # Get category information
    categories = tech_data.get('cats', [])
    category = 'web'
    subcategory = 'web-application'
    
    if categories:
        # Use the first category for mapping
        webtech_cat = categories[0]  # Categories are numeric in WebTech
        category, subcategory = convert_webtech_category(webtech_cat)
    
    # Process headers
    headers = tech_data.get('headers', {})
    header_patterns = []
    for header_name, header_value in headers.items():
        if isinstance(header_value, str):
            pattern = f"{header_name}: {convert_webtech_pattern(header_value)}"
            version_group = extract_version_group(header_value)
            header_patterns.append({
                "name": f"{tech_name} Header Detection",
                "pattern": pattern,
                "version_group": version_group,
                "priority": 150,
                "confidence": 0.8,
                "metadata": {
                    "author": "WebTech Import",
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "description": f"Detects {tech_name} from {header_name} header",
                    "tags": ["webtech", "header", tech_name.lower().replace(' ', '-')],
                    "source": "WebTech",
                    "license": "MIT"
                }
            })
        elif isinstance(header_value, list):
            for header_val in header_value:
                if isinstance(header_val, str):
                    pattern = f"{header_name}: {convert_webtech_pattern(header_val)}"
                    version_group = extract_version_group(header_val)
                    header_patterns.append({
                        "name": f"{tech_name} Header Detection",
                        "pattern": pattern,
                        "version_group": version_group,
                        "priority": 150,
                        "confidence": 0.8,
                        "metadata": {
                            "author": "WebTech Import",
                            "created_at": "2025-01-01",
                            "updated_at": "2025-01-01",
                            "description": f"Detects {tech_name} from {header_name} header",
                            "tags": ["webtech", "header", tech_name.lower().replace(' ', '-')],
                            "source": "WebTech",
                            "license": "MIT"
                        }
                    })
    
    # Process HTML patterns
    html_patterns = []
    html = tech_data.get('html', [])
    if isinstance(html, str):
        html = [html]
    
    for html_pattern in html:
        pattern = convert_webtech_pattern(html_pattern)
        version_group = extract_version_group(html_pattern)
        html_patterns.append({
            "name": f"{tech_name} HTML Detection",
            "pattern": pattern,
            "version_group": version_group,
            "priority": 100,
            "confidence": 0.7,
            "metadata": {
                "author": "WebTech Import",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01",
                "description": f"Detects {tech_name} from HTML content",
                "tags": ["webtech", "html", tech_name.lower().replace(' ', '-')],
                "source": "WebTech",
                "license": "MIT"
            }
        })
    
    # Process meta tags
    meta_patterns = []
    meta = tech_data.get('meta', {})
    for meta_name, meta_content in meta.items():
        if isinstance(meta_content, str):
            pattern = f'<meta[^>]+name=["\']{meta_name}["\'][^>]+content=["\']{convert_webtech_pattern(meta_content)}["\']'
            version_group = extract_version_group(meta_content)
            meta_patterns.append({
                "name": f"{tech_name} Meta Tag Detection",
                "pattern": pattern,
                "version_group": version_group,
                "priority": 120,
                "confidence": 0.75,
                "metadata": {
                    "author": "WebTech Import",
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "description": f"Detects {tech_name} from meta tag with name '{meta_name}'",
                    "tags": ["webtech", "meta", tech_name.lower().replace(' ', '-')],
                    "source": "WebTech",
                    "license": "MIT"
                }
            })
        elif isinstance(meta_content, list):
            for meta_val in meta_content:
                if isinstance(meta_val, str):
                    pattern = f'<meta[^>]+name=["\']{meta_name}["\'][^>]+content=["\']{convert_webtech_pattern(meta_val)}["\']'
                    version_group = extract_version_group(meta_val)
                    meta_patterns.append({
                        "name": f"{tech_name} Meta Tag Detection",
                        "pattern": pattern,
                        "version_group": version_group,
                        "priority": 120,
                        "confidence": 0.75,
                        "metadata": {
                            "author": "WebTech Import",
                            "created_at": "2025-01-01",
                            "updated_at": "2025-01-01",
                            "description": f"Detects {tech_name} from meta tag with name '{meta_name}'",
                            "tags": ["webtech", "meta", tech_name.lower().replace(' ', '-')],
                            "source": "WebTech",
                            "license": "MIT"
                        }
                    })
    
    # Process scripts
    script_patterns = []
    scripts = tech_data.get('script', [])
    if isinstance(scripts, str):
        scripts = [scripts]
    
    for script_pattern in scripts:
        pattern = convert_webtech_pattern(script_pattern)
        version_group = extract_version_group(script_pattern)
        script_patterns.append({
            "name": f"{tech_name} Script Detection",
            "pattern": pattern,
            "version_group": version_group,
            "priority": 130,
            "confidence": 0.7,
            "metadata": {
                "author": "WebTech Import",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01",
                "description": f"Detects {tech_name} from script tags",
                "tags": ["webtech", "script", tech_name.lower().replace(' ', '-')],
                "source": "WebTech",
                "license": "MIT"
            }
        })
    
    # Process JavaScript variables
    js_patterns = []
    js = tech_data.get('js', {})
    for js_var, js_value in js.items():
        if isinstance(js_value, str):
            # For JavaScript detection, we'll create a pattern that looks for the variable
            pattern = f"window\\.{re.escape(js_var)}|{re.escape(js_var)}\\s*="
            version_group = extract_version_group(js_value)
            js_patterns.append({
                "name": f"{tech_name} JavaScript Detection",
                "pattern": pattern,
                "version_group": version_group,
                "priority": 140,
                "confidence": 0.7,
                "metadata": {
                    "author": "WebTech Import",
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "description": f"Detects {tech_name} from JavaScript variable '{js_var}'",
                    "tags": ["webtech", "javascript", tech_name.lower().replace(' ', '-')],
                    "source": "WebTech",
                    "license": "MIT"
                }
            })
    
    # Combine all patterns
    all_patterns = header_patterns + html_patterns + meta_patterns + script_patterns + js_patterns
    
    # Create the technology structure
    vendor_name = tech_name.split()[0] if ' ' in tech_name else tech_name
    tech_slug = tech_name.lower().replace(' ', '-').replace('.', '')
    
    return {
        "vendor": vendor_name,
        "vendor_id": vendor_name.lower(),
        "product": tech_name,
        "product_id": f"{vendor_name.lower()}-{tech_slug}",
        "category": category,
        "subcategory": subcategory,
        "versions": {},
        "all_versions": all_patterns
    }


def import_webtech_technologies(webtech_data, output_dir):
    """
    Import WebTech technologies and convert to our format.
    
    Args:
        webtech_data (dict): WebTech technology definitions
        output_dir (str): Output directory for converted patterns
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each technology
    count = 0
    skipped = 0
    for tech_name, tech_data in webtech_data.items():
        try:
            # Skip non-dict entries
            if not isinstance(tech_data, dict):
                continue
                
            # Create our pattern structure
            pattern_structure = create_pattern_structure(tech_name, tech_data)
            
            # Only save technologies that have patterns
            if pattern_structure['all_versions']:
                # Create vendor directory
                vendor_id = pattern_structure['vendor_id']
                vendor_dir = os.path.join(output_dir, vendor_id)
                os.makedirs(vendor_dir, exist_ok=True)
                
                # Check if pattern already exists
                filename = f"{pattern_structure['product_id']}.json"
                filepath = os.path.join(vendor_dir, filename)
                
                # Check if file already exists
                if os.path.exists(filepath):
                    print(f"Skipping {tech_name} - already exists at {filepath}")
                    skipped += 1
                    continue
                
                # Save pattern file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(pattern_structure, f, indent=2, ensure_ascii=False)
                
                print(f"Imported {tech_name} -> {filepath}")
                count += 1
            
        except Exception as e:
            print(f"Error processing {tech_name}: {e}")
    
    print(f"Imported {count} technologies, skipped {skipped} existing technologies")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python import-webtech.py <webtech-json-file> <output-directory>")
        print("Example: python import-webtech.py apps.json ./imported-webtech-patterns/")
        return
    
    webtech_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("Loading WebTech technologies...")
    webtech_data = load_webtech_technologies(webtech_file)
    
    if not webtech_data:
        print("Failed to load WebTech technologies")
        return
    
    print(f"Loaded {len(webtech_data)} technologies")
    
    print("Importing technologies...")
    import_webtech_technologies(webtech_data, output_dir)
    
    print("Import completed!")


if __name__ == "__main__":
    main()