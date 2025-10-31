import os
import json

# Search for patterns with single characters or very short patterns
patterns_dir = r"c:\code\Regex-Intelligence-Exchange-by-Infopercept\patterns\by-vendor"

short_patterns = []

for root, dirs, files in os.walk(patterns_dir):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check all_versions patterns
                for pattern in data.get('all_versions', []):
                    pattern_str = pattern.get('pattern', '')
                    if len(pattern_str) <= 2 and pattern_str not in ['^', '$']:
                        short_patterns.append({
                            'file': file_path,
                            'vendor': data.get('vendor', ''),
                            'product': data.get('product', ''),
                            'pattern': pattern_str
                        })
                        
                # Check version-specific patterns
                for version, patterns in data.get('versions', {}).items():
                    for pattern in patterns:
                        pattern_str = pattern.get('pattern', '')
                        if len(pattern_str) <= 2 and pattern_str not in ['^', '$']:
                            short_patterns.append({
                                'file': file_path,
                                'vendor': data.get('vendor', ''),
                                'product': data.get('product', ''),
                                'pattern': pattern_str
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

print(f"Found {len(short_patterns)} short patterns:")
for p in short_patterns:
    print(f"  {p['file']}: {p['pattern']} (Vendor: {p['vendor']}, Product: {p['product']})")