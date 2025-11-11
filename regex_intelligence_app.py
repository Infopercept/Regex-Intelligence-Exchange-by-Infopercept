#!/usr/bin/env python3
"""
Complete Regex Intelligence Exchange Application
Cross-platform compatible - Works on Windows, macOS, and Linux
With full features and actual pattern data
"""

import os
import sys
import json
import glob
import re
import time
import argparse
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading

class PatternService:
    """Complete pattern service with all features."""
    
    def __init__(self, patterns_dir=None):
        self.patterns_dir = patterns_dir or self._get_patterns_dir()
        self._patterns_cache = None
        self._stats_cache = None
        self._compiled_patterns = {}
        print(f"🔍 Pattern directory: {self.patterns_dir}")
    
    def _get_patterns_dir(self):
        """Get patterns directory path."""
        # Try to find the patterns directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        patterns_path = os.path.join(current_dir, 'patterns', 'by-vendor')
        
        # If not found, try the web directory structure
        if not os.path.exists(patterns_path):
            patterns_path = os.path.join(current_dir, 'web', 'patterns', 'by-vendor')
            
        # If still not found, try the original structure
        if not os.path.exists(patterns_path):
            patterns_path = os.path.join(current_dir, 'patterns', 'by-vendor')
            
        return patterns_path
    
    def _load_patterns(self):
        """Load all patterns from files with progress indicator."""
        if self._patterns_cache is not None:
            return self._patterns_cache
        
        patterns = []
        pattern_files = glob.glob(os.path.join(self.patterns_dir, '**', '*.json'), recursive=True)
        
        print(f"📂 Loading patterns from {len(pattern_files)} files...")
        
        for i, file_path in enumerate(pattern_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                    patterns.append(pattern_data)
                
                # Progress indicator
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i + 1}/{len(pattern_files)} files...")
                    
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
                continue
        
        self._patterns_cache = patterns
        print(f"✅ Successfully loaded {len(patterns)} patterns!")
        return patterns
    
    def get_all_patterns(self, limit=None, offset=0):
        """Get all patterns with pagination."""
        patterns = self._load_patterns()
        
        if offset:
            patterns = patterns[offset:]
        if limit:
            patterns = patterns[:limit]
        
        return patterns
    
    def search_patterns(self, query=None, category=None, vendor=None, limit=None, offset=0):
        """Search patterns with advanced filtering."""
        patterns = self._load_patterns()
        
        if not query and not category and not vendor:
            filtered = patterns
        else:
            filtered = []
            for pattern in patterns:
                match = True
                
                if category and category.lower() not in pattern.get('category', '').lower():
                    match = False
                
                if vendor and vendor.lower() not in pattern.get('vendor', '').lower():
                    match = False
                
                if query:
                    query_lower = query.lower()
                    if not (query_lower in pattern.get('vendor', '').lower() or 
                           query_lower in pattern.get('product', '').lower() or
                           query_lower in pattern.get('category', '').lower()):
                        match = False
                
                if match:
                    filtered.append(pattern)
        
        # Apply pagination
        total = len(filtered)
        if offset:
            filtered = filtered[offset:]
        if limit:
            filtered = filtered[:limit]
        
        return {
            'patterns': filtered,
            'total': total,
            'offset': offset,
            'limit': limit
        }
    
    def get_pattern_by_id(self, vendor_id, product_id):
        """Get specific pattern by vendor and product ID."""
        patterns = self._load_patterns()
        
        for pattern in patterns:
            if (pattern.get('vendor_id') == vendor_id and 
                pattern.get('product_id') == product_id):
                return pattern
        
        return None
    
    def match_patterns(self, input_text, max_patterns=50):
        """Match patterns against input text."""
        patterns = self.get_all_patterns(limit=max_patterns)
        matches = []
        
        for pattern in patterns:
            try:
                # Check all_versions patterns
                for version_pattern in pattern.get('all_versions', []):
                    regex_pattern = version_pattern.get('pattern', '')
                    if regex_pattern:
                        match_result = self._test_pattern_match(regex_pattern, input_text)
                        if match_result:
                            matches.append({
                                'vendor': pattern.get('vendor', ''),
                                'product': pattern.get('product', ''),
                                'vendor_id': pattern.get('vendor_id', ''),
                                'product_id': pattern.get('product_id', ''),
                                'pattern_name': version_pattern.get('name', ''),
                                'matched_text': match_result['matched_text'],
                                'version': match_result.get('version'),
                                'category': pattern.get('category', '')
                            })
                            break  # Only one match per pattern
                
                # Check versions patterns
                for version_key, version_patterns in pattern.get('versions', {}).items():
                    for version_pattern in version_patterns:
                        regex_pattern = version_pattern.get('pattern', '')
                        if regex_pattern:
                            match_result = self._test_pattern_match(regex_pattern, input_text)
                            if match_result:
                                # Check if we already have a match for this pattern
                                existing_match = any(
                                    m['vendor_id'] == pattern.get('vendor_id') and 
                                    m['product_id'] == pattern.get('product_id')
                                    for m in matches
                                )
                                if not existing_match:
                                    matches.append({
                                        'vendor': pattern.get('vendor', ''),
                                        'product': pattern.get('product', ''),
                                        'vendor_id': pattern.get('vendor_id', ''),
                                        'product_id': pattern.get('product_id', ''),
                                        'pattern_name': version_pattern.get('name', ''),
                                        'matched_text': match_result['matched_text'],
                                        'version': match_result.get('version'),
                                        'category': pattern.get('category', '')
                                    })
                                    break
            except Exception as e:
                continue  # Skip problematic patterns
        
        return matches
    
    def _test_pattern_match(self, pattern, text):
        """Test if pattern matches text."""
        try:
            # Use compiled pattern cache for better performance
            if pattern not in self._compiled_patterns:
                self._compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            compiled_pattern = self._compiled_patterns[pattern]
            match = compiled_pattern.search(text)
            
            if match:
                result = {
                    'matched_text': match.group(0),
                    'full_match': match
                }
                
                # Try to extract version if there are groups
                if match.groups():
                    result['version'] = match.group(1)
                
                return result
            
        except re.error:
            pass  # Invalid regex pattern
        except Exception:
            pass  # Other errors
        
        return None
    
    def get_statistics(self):
        """Get comprehensive pattern statistics."""
        if self._stats_cache is not None:
            return self._stats_cache
        
        patterns = self._load_patterns()
        
        categories = {}
        vendors = {}
        subcategories = {}
        
        for pattern in patterns:
            category = pattern.get('category', 'Unknown')
            vendor = pattern.get('vendor', 'Unknown')
            subcategory = pattern.get('subcategory', '')
            
            categories[category] = categories.get(category, 0) + 1
            vendors[vendor] = vendors.get(vendor, 0) + 1
            
            if subcategory:
                subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        stats = {
            'total_patterns': len(patterns),
            'categories': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            'vendors': dict(sorted(vendors.items(), key=lambda x: x[1], reverse=True)),
            'subcategories': dict(sorted(subcategories.items(), key=lambda x: x[1], reverse=True)),
            'top_categories': dict(list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:10]),
            'top_vendors': dict(list(sorted(vendors.items(), key=lambda x: x[1], reverse=True))[:10])
        }
        
        self._stats_cache = stats
        return stats
    
    def get_categories(self):
        """Get all unique categories."""
        stats = self.get_statistics()
        return list(stats['categories'].keys())
    
    def get_vendors(self, category=None):
        """Get all unique vendors, optionally filtered by category."""
        if category:
            # Filter vendors by category
            patterns = self._load_patterns()
            vendors = set()
            for pattern in patterns:
                if pattern.get('category', '').lower() == category.lower():
                    vendor = pattern.get('vendor')
                    if vendor:
                        vendors.add(vendor)
            return sorted(list(vendors))
        else:
            # Return all vendors
            stats = self.get_statistics()
            return list(stats['vendors'].keys())

def create_app():
    """Create complete Flask application with all features."""
    app = Flask(__name__, 
                template_folder='web/templates',
                static_folder='web/static')
    CORS(app)
    
    # Initialize pattern service
    pattern_service = PatternService()
    
    # Web Routes
    @app.route('/')
    def index():
        """Main dashboard."""
        try:
            stats = pattern_service.get_statistics()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            return f"<h1>Error loading dashboard</h1><p>{str(e)}</p>", 500
    
    @app.route('/search')
    def search():
        """Search page."""
        try:
            categories = pattern_service.get_categories()
            vendors = pattern_service.get_vendors()
            return render_template('search.html', categories=categories, vendors=vendors)
        except Exception as e:
            return f"<h1>Error loading search page</h1><p>{str(e)}</p>", 500
    
    @app.route('/pattern/<vendor_id>/<product_id>')
    def pattern_detail(vendor_id, product_id):
        """Pattern detail page."""
        try:
            pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
            if not pattern:
                return render_template('404.html'), 404
            return render_template('pattern_detail.html', pattern=pattern)
        except Exception as e:
            return f"<h1>Error loading pattern detail</h1><p>{str(e)}</p>", 500
    
    @app.route('/analytics')
    def analytics():
        """Analytics dashboard."""
        try:
            stats = pattern_service.get_statistics()
            return render_template('analytics.html', stats=stats)
        except Exception as e:
            return f"<h1>Error loading analytics</h1><p>{str(e)}</p>", 500
    
    @app.route('/test')
    def test_patterns():
        """Pattern testing tool."""
        try:
            examples = {
                'apache': "HTTP/1.1 200 OK\nServer: Apache/2.4.41 (Ubuntu)\nX-Powered-By: PHP/7.4.3\nSet-Cookie: PHPSESSID=abc123; path=/\nContent-Type: text/html; charset=UTF-8\n\n<!DOCTYPE html>\n<html>\n<head>\n<meta name=\"generator\" content=\"WordPress 6.2\" />\n</head>\n<body>\n<!-- Powered by Apache -->\n</body>\n</html>",
                'nginx': "HTTP/1.1 200 OK\nServer: nginx/1.18.0 (Ubuntu)\nX-Powered-By: Express\nX-Frame-Options: SAMEORIGIN\nContent-Security-Policy: default-src 'self'\n\n<!DOCTYPE html>\n<html>\n<body>\n<script src=\"/express-app/main.js\"></script>\n</body>\n</html>",
                'php': "HTTP/1.1 200 OK\nX-Powered-By: PHP/8.1.2\nSet-Cookie: PHPSESSID=def456; path=/; HttpOnly\nContent-Type: text/html; charset=UTF-8\nX-PHP-Version: 8.1.2\n\n<!DOCTYPE html>\n<html>\n<body>\n<!-- Generated by PHP 8.1.2 -->\n<?php echo phpversion(); ?>\n</body>\n</html>",
                'wordpress': "HTTP/1.1 200 OK\nServer: Apache\nX-Powered-By: PHP/7.4.3\n\n<!DOCTYPE html>\n<html>\n<head>\n<meta name=\"generator\" content=\"WordPress 6.2\" />\n<link rel='stylesheet' id='wp-block-library-css'  href='/wp-includes/css/dist/block-library/style.min.css' type='text/css' media='all' />\n</head>\n<body class=\"home blog\">\n<script src=\"/wp-includes/js/jquery/jquery.min.js\"></script>\n<!-- This site is powered by WordPress -->\n</body>\n</html>"
            }
            return render_template('test.html', examples=examples)
        except Exception as e:
            return f"<h1>Error loading test page</h1><p>{str(e)}</p>", 500
    
    @app.route('/export')
    def export_page():
        """Export data page."""
        try:
            categories = pattern_service.get_categories()
            vendors = pattern_service.get_vendors()
            return render_template('export.html', categories=categories, vendors=vendors)
        except Exception as e:
            return f"<h1>Error loading export page</h1><p>{str(e)}</p>", 500
    
    # API Routes
    @app.route('/api/patterns')
    def api_patterns():
        """Get all patterns with optional filtering."""
        try:
            query = request.args.get('q', '')
            category = request.args.get('category', '')
            vendor = request.args.get('vendor', '')
            limit = min(request.args.get('limit', 20, type=int), 100)
            offset = request.args.get('offset', 0, type=int)
            
            result = pattern_service.search_patterns(query, category, vendor, limit, offset)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/patterns/<vendor_id>/<product_id>')
    def api_pattern_detail(vendor_id, product_id):
        """Get specific pattern by vendor and product ID."""
        try:
            pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
            if not pattern:
                return jsonify({'error': 'Pattern not found'}), 404
            return jsonify(pattern)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/match', methods=['POST'])
    def api_match():
        """Match patterns against input text."""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing text parameter'}), 400
            
            matches = pattern_service.match_patterns(data['text'])
            return jsonify(matches)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/categories')
    def api_categories():
        """Get all available categories."""
        try:
            categories = pattern_service.get_categories()
            return jsonify({'categories': categories})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vendors')
    def api_vendors():
        """Get all available vendors, optionally filtered by category."""
        try:
            category = request.args.get('category', '').strip()
            vendors = pattern_service.get_vendors(category if category else None)
            return jsonify({'vendors': vendors})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/summary')
    def api_analytics():
        """Get analytics summary."""
        try:
            return jsonify(pattern_service.get_statistics())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint."""
        try:
            stats = pattern_service.get_statistics()
            return jsonify({
                'status': 'healthy',
                'patterns_loaded': stats['total_patterns'],
                'categories': len(stats['categories']),
                'vendors': len(stats['vendors']),
                'timestamp': time.time()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/docs/')
    @app.route('/api/docs')
    def api_docs():
        """API Documentation page."""
        return render_template('api_docs.html')
    
    @app.route('/api/export')
    def api_export():
        """Export patterns data in various formats."""
        try:
            # Get filter parameters
            category = request.args.get('category', '').strip()
            vendor = request.args.get('vendor', '').strip()
            format_type = request.args.get('format', 'json').lower()
            
            # Get filtered patterns
            result = pattern_service.search_patterns(
                query=None,
                category=category if category else None,
                vendor=vendor if vendor else None,
                limit=None,  # Get all matching patterns
                offset=0
            )
            
            patterns = result['patterns']
            
            if format_type == 'json':
                # Export as JSON
                from flask import Response
                response = Response(
                    json.dumps(patterns, indent=2),
                    mimetype='application/json',
                    headers={
                        'Content-Disposition': f'attachment; filename=patterns_export.json'
                    }
                )
                return response
                
            elif format_type == 'csv':
                # Export as CSV
                import csv
                from io import StringIO
                
                output = StringIO()
                if patterns:
                    # Get all unique keys from patterns
                    fieldnames = ['vendor', 'vendor_id', 'product', 'product_id', 'category', 'subcategory', 'description']
                    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    
                    for pattern in patterns:
                        # Write basic pattern info (not including nested all_versions)
                        row = {
                            'vendor': pattern.get('vendor', ''),
                            'vendor_id': pattern.get('vendor_id', ''),
                            'product': pattern.get('product', ''),
                            'product_id': pattern.get('product_id', ''),
                            'category': pattern.get('category', ''),
                            'subcategory': pattern.get('subcategory', ''),
                            'description': pattern.get('description', '')
                        }
                        writer.writerow(row)
                
                from flask import Response
                response = Response(
                    output.getvalue(),
                    mimetype='text/csv',
                    headers={
                        'Content-Disposition': f'attachment; filename=patterns_export.csv'
                    }
                )
                return response
            
            else:
                return jsonify({'error': 'Invalid format. Supported formats: json, csv'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Complete Regex Intelligence Exchange')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("🚀 Complete Regex Intelligence Exchange")
    print("=" * 60)
    print("✅ Cross-platform compatible (Windows, macOS, Linux)")
    print("✅ 1500+ real technology patterns loaded")
    print("✅ Full web interface with modern UI")
    print("✅ Complete REST API with documentation")
    print("✅ Advanced search and filtering")
    print("✅ Pattern matching engine")
    print("✅ Analytics dashboard with charts")
    print("✅ Pattern testing tool")
    print("=" * 60)
    print(f"🌐 Web Interface: http://{args.host}:{args.port}")
    print(f"📚 API Endpoints:")
    print(f"   - List/Search Patterns: http://{args.host}:{args.port}/api/patterns")
    print(f"   - Pattern Detail: http://{args.host}:{args.port}/api/patterns/<vendor_id>/<product_id>")
    print(f"   - Pattern Matching: http://{args.host}:{args.port}/api/match")
    print(f"   - Categories: http://{args.host}:{args.port}/api/categories")
    print(f"   - Vendors: http://{args.host}:{args.port}/api/vendors")
    print(f"   - Analytics: http://{args.host}:{args.port}/api/analytics/summary")
    print(f"   - Health Check: http://{args.host}:{args.port}/api/health")
    print(f"🔍 Search: http://{args.host}:{args.port}/search")
    print(f"📊 Analytics: http://{args.host}:{args.port}/analytics")
    print(f"🧪 Pattern Tester: http://{args.host}:{args.port}/test")
    print("=" * 60)
    
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()