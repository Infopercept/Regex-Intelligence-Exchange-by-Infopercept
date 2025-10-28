#!/usr/bin/env python3
"""
Script to import patterns from Wappalyzer technology definitions
"""

import json
import re
import sys
import os
from urllib.parse import urlparse
import requests


def load_wappalyzer_technologies(file_path):
    """
    Load Wappalyzer technology definitions from a JSON file.
    
    Args:
        file_path (str): Path to the Wappalyzer technologies JSON file
        
    Returns:
        dict: Technology definitions
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # The new format has technologies under a "technologies" key
        # But our file seems to have them at the root level
        # Let's check if it's the new format or old format
        if isinstance(data, dict) and 'technologies' in data:
            return data['technologies']
        elif isinstance(data, dict):
            # Remove the $schema entry if it exists
            if '$schema' in data:
                del data['$schema']
            if 'categories' in data:
                del data['categories']
            return data
        else:
            return {}
    except Exception as e:
        print(f"Error loading Wappalyzer technologies: {e}")
        return {}


def convert_wappalyzer_category(wappalyzer_category):
    """
    Convert Wappalyzer category to our category system.
    
    Args:
        wappalyzer_category (str): Wappalyzer category name
        
    Returns:
        tuple: (category, subcategory)
    """
    # Category mapping based on our research
    category_mapping = {
        'CMS': ('cms', 'cms-platform'),
        'Blogs': ('cms', 'cms-platform'),
        'Ecommerce': ('cms', 'ecommerce'),
        'Web Frameworks': ('framework', 'web-framework'),
        'Web Servers': ('web', 'web-server'),
        'JavaScript Frameworks': ('framework', 'frontend-framework'),
        'Databases': ('database', 'database-engine'),
        'Advertising': ('web', 'web-application'),
        'Analytics': ('web', 'web-application'),
        'Security': ('web', 'web-application'),
        'Servers': ('web', 'web-server'),
        'CDN': ('web', 'cdn'),
        'Marketing Automation': ('web', 'web-application'),
        'Rich Text Editors': ('web', 'web-application'),
        'Video Players': ('web', 'web-application'),
        'Comment Systems': ('web', 'web-application'),
        'Captchas': ('web', 'web-application'),
        'Font Scripts': ('web', 'web-application'),
        'Webmail': ('web', 'web-application'),
        'SSH Servers': ('networking', None),
        'Issue Trackers': ('web', 'web-application'),
        'Miscellaneous': ('web', 'web-application')
    }
    
    # Wappalyzer uses numeric category IDs, so we need to map those
    # This is a simplified mapping for common categories
    id_mapping = {
        '1': ('cms', 'cms-platform'),      # CMS
        '6': ('cms', 'ecommerce'),         # Ecommerce
        '11': ('cms', 'cms-platform'),     # Blogs
        '12': ('framework', 'frontend-framework'),  # JavaScript Frameworks
        '18': ('framework', 'web-framework'),       # Web Frameworks
        '22': ('web', 'web-server'),       # Web Servers
        '27': ('framework', 'web-framework'),        # Programming Languages (treated as frameworks)
        '59': ('framework', 'frontend-framework')   # JavaScript libraries
    }
    
    if isinstance(wappalyzer_category, int) or (isinstance(wappalyzer_category, str) and wappalyzer_category.isdigit()):
        return id_mapping.get(str(wappalyzer_category), ('web', 'web-application'))
    
    return category_mapping.get(wappalyzer_category, ('web', 'web-application'))


def convert_wappalyzer_pattern(wappalyzer_pattern):
    """
    Convert Wappalyzer pattern to our regex format.
    
    Args:
        wappalyzer_pattern (str): Wappalyzer pattern string
        
    Returns:
        str: Converted regex pattern
    """
    # Remove version capture group markers if present
    pattern = wappalyzer_pattern
    pattern = re.sub(r'\\;version:\\\d+', '', pattern)
    pattern = re.sub(r'\\;version:', '', pattern)
    pattern = re.sub(r';version:\\\d+', '', pattern)
    pattern = re.sub(r';version:', '', pattern)
    
    # Unescape forward slashes that Wappalyzer escapes
    pattern = pattern.replace('\\/', '/')
    
    return pattern


def extract_version_group(wappalyzer_pattern):
    """
    Extract version group information from Wappalyzer pattern.
    
    Args:
        wappalyzer_pattern (str): Wappalyzer pattern string
        
    Returns:
        int: Version group number (0 if no version capture)
    """
    # Look for version capture group markers
    match = re.search(r'\\;version:\\(\d+)', wappalyzer_pattern)
    if match:
        return int(match.group(1))
    
    match = re.search(r';version:\\(\d+)', wappalyzer_pattern)
    if match:
        return int(match.group(1))
        
    return 0


def create_pattern_structure(tech_name, tech_data):
    """
    Create our pattern structure from Wappalyzer technology data.
    
    Args:
        tech_name (str): Technology name
        tech_data (dict): Wappalyzer technology data
        
    Returns:
        dict: Our pattern structure
    """
    # Get category information
    categories = tech_data.get('cats', [])
    category = 'web'
    subcategory = 'web-application'
    
    if categories:
        # Use the first category for mapping
        wappalyzer_cat = categories[0]  # Categories are numeric in Wappalyzer
        category, subcategory = convert_wappalyzer_category(wappalyzer_cat)
    
    # Process headers
    headers = tech_data.get('headers', {})
    header_patterns = []
    for header_name, header_value in headers.items():
        if isinstance(header_value, str):
            pattern = f"{header_name}: {convert_wappalyzer_pattern(header_value)}"
            version_group = extract_version_group(header_value)
            header_patterns.append({
                "name": f"{tech_name} Header Detection",
                "pattern": pattern,
                "version_group": version_group,
                "priority": 150,
                "confidence": 0.8,
                "metadata": {
                    "author": "Wappalyzer Import",
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "description": f"Detects {tech_name} from {header_name} header",
                    "tags": ["wappalyzer", "header", tech_name.lower().replace(' ', '-')],
                    "source": "Wappalyzer",
                    "license": "MIT"
                }
            })
        elif isinstance(header_value, list):
            for header_val in header_value:
                if isinstance(header_val, str):
                    pattern = f"{header_name}: {convert_wappalyzer_pattern(header_val)}"
                    version_group = extract_version_group(header_val)
                    header_patterns.append({
                        "name": f"{tech_name} Header Detection",
                        "pattern": pattern,
                        "version_group": version_group,
                        "priority": 150,
                        "confidence": 0.8,
                        "metadata": {
                            "author": "Wappalyzer Import",
                            "created_at": "2025-01-01",
                            "updated_at": "2025-01-01",
                            "description": f"Detects {tech_name} from {header_name} header",
                            "tags": ["wappalyzer", "header", tech_name.lower().replace(' ', '-')],
                            "source": "Wappalyzer",
                            "license": "MIT"
                        }
                    })
    
    # Process HTML patterns
    html_patterns = []
    html = tech_data.get('html', [])
    if isinstance(html, str):
        html = [html]
    
    for html_pattern in html:
        pattern = convert_wappalyzer_pattern(html_pattern)
        version_group = extract_version_group(html_pattern)
        html_patterns.append({
            "name": f"{tech_name} HTML Detection",
            "pattern": pattern,
            "version_group": version_group,
            "priority": 100,
            "confidence": 0.7,
            "metadata": {
                "author": "Wappalyzer Import",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01",
                "description": f"Detects {tech_name} from HTML content",
                "tags": ["wappalyzer", "html", tech_name.lower().replace(' ', '-')],
                "source": "Wappalyzer",
                "license": "MIT"
            }
        })
    
    # Process meta tags
    meta_patterns = []
    meta = tech_data.get('meta', {})
    for meta_name, meta_content in meta.items():
        if isinstance(meta_content, str):
            pattern = f'<meta[^>]+name=["\']{meta_name}["\'][^>]+content=["\']{convert_wappalyzer_pattern(meta_content)}["\']'
            version_group = extract_version_group(meta_content)
            meta_patterns.append({
                "name": f"{tech_name} Meta Tag Detection",
                "pattern": pattern,
                "version_group": version_group,
                "priority": 120,
                "confidence": 0.75,
                "metadata": {
                    "author": "Wappalyzer Import",
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "description": f"Detects {tech_name} from meta tag with name '{meta_name}'",
                    "tags": ["wappalyzer", "meta", tech_name.lower().replace(' ', '-')],
                    "source": "Wappalyzer",
                    "license": "MIT"
                }
            })
        elif isinstance(meta_content, list):
            for meta_val in meta_content:
                if isinstance(meta_val, str):
                    pattern = f'<meta[^>]+name=["\']{meta_name}["\'][^>]+content=["\']{convert_wappalyzer_pattern(meta_val)}["\']'
                    version_group = extract_version_group(meta_val)
                    meta_patterns.append({
                        "name": f"{tech_name} Meta Tag Detection",
                        "pattern": pattern,
                        "version_group": version_group,
                        "priority": 120,
                        "confidence": 0.75,
                        "metadata": {
                            "author": "Wappalyzer Import",
                            "created_at": "2025-01-01",
                            "updated_at": "2025-01-01",
                            "description": f"Detects {tech_name} from meta tag with name '{meta_name}'",
                            "tags": ["wappalyzer", "meta", tech_name.lower().replace(' ', '-')],
                            "source": "Wappalyzer",
                            "license": "MIT"
                        }
                    })
    
    # Process scripts
    script_patterns = []
    scripts = tech_data.get('scripts', [])
    if isinstance(scripts, str):
        scripts = [scripts]
    
    for script_pattern in scripts:
        pattern = convert_wappalyzer_pattern(script_pattern)
        version_group = extract_version_group(script_pattern)
        script_patterns.append({
            "name": f"{tech_name} Script Detection",
            "pattern": pattern,
            "version_group": version_group,
            "priority": 130,
            "confidence": 0.7,
            "metadata": {
                "author": "Wappalyzer Import",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01",
                "description": f"Detects {tech_name} from script tags",
                "tags": ["wappalyzer", "script", tech_name.lower().replace(' ', '-')],
                "source": "Wappalyzer",
                "license": "MIT"
            }
        })
    
    # Combine all patterns
    all_patterns = header_patterns + html_patterns + meta_patterns + script_patterns
    
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


def import_wappalyzer_technologies(wappalyzer_data, output_dir):
    """
    Import Wappalyzer technologies and convert to our format.
    
    Args:
        wappalyzer_data (dict): Wappalyzer technology definitions
        output_dir (str): Output directory for converted patterns
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each technology
    count = 0
    for tech_name, tech_data in wappalyzer_data.items():
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
                
                # Save pattern file
                filename = f"{pattern_structure['product_id']}.json"
                filepath = os.path.join(vendor_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(pattern_structure, f, indent=2, ensure_ascii=False)
                
                print(f"Imported {tech_name} -> {filepath}")
                count += 1
            
        except Exception as e:
            print(f"Error processing {tech_name}: {e}")
    
    print(f"Imported {count} technologies")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python import-wappalyzer.py <wappalyzer-json-file> <output-directory>")
        print("Example: python import-wappalyzer.py technologies.json ./imported-patterns/")
        return
    
    wappalyzer_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("Loading Wappalyzer technologies...")
    wappalyzer_data = load_wappalyzer_technologies(wappalyzer_file)
    
    if not wappalyzer_data:
        print("Failed to load Wappalyzer technologies")
        return
    
    print(f"Loaded {len(wappalyzer_data)} technologies")
    
    print("Importing technologies...")
    import_wappalyzer_technologies(wappalyzer_data, output_dir)
    
    print("Import completed!")


if __name__ == "__main__":
    main()