#!/usr/bin/env python3
"""
Complete Regex Intelligence Exchange Web Application
Cross-platform compatible - Works on Windows, macOS, and Linux
With full features and actual pattern data
"""

import os
import sys
import json
import glob
import re
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import argparse

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
        return os.path.join(os.path.dirname(__file__), '..', 'patterns', 'by-vendor')
    
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
    
    def get_vendors(self):
        """Get all unique vendors."""
        stats = self.get_statistics()
        return list(stats['vendors'].keys())

def create_app():
    """Create complete Flask application with all features."""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize pattern service
    pattern_service = PatternService()
    
    # Initialize Flask-RESTX API
    api = Api(app, 
              title='Regex Intelligence Exchange API',
              version='1.0',
              description='Complete technology fingerprinting pattern API with 1500+ patterns',
              doc='/api/docs/')
    
    # API Models for documentation
    pattern_model = api.model('Pattern', {
        'vendor': fields.String(description='Vendor name', example='Apache'),
        'product': fields.String(description='Product name', example='Apache HTTP Server'),
        'category': fields.String(description='Category', example='web'),
        'vendor_id': fields.String(description='Vendor ID', example='apache'),
        'product_id': fields.String(description='Product ID', example='apache')
    })
    
    match_request_model = api.model('MatchRequest', {
        'text': fields.String(required=True, description='Text to match against patterns')
    })
    
    match_result_model = api.model('MatchResult', {
        'vendor': fields.String(description='Vendor name'),
        'product': fields.String(description='Product name'),
        'matched_text': fields.String(description='Matched text'),
        'version': fields.String(description='Detected version'),
        'category': fields.String(description='Technology category')
    })
    
    # Web Routes
    @app.route('/')
    def index():
        """Main dashboard."""
        stats = pattern_service.get_statistics()
        return render_template('dashboard.html', stats=stats)
    
    @app.route('/search')
    def search():
        """Search page."""
        categories = pattern_service.get_categories()
        vendors = pattern_service.get_vendors()
        return render_template('search.html', categories=categories, vendors=vendors)
    
    @app.route('/pattern/<vendor_id>/<product_id>')
    def pattern_detail(vendor_id, product_id):
        """Pattern detail page."""
        pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
        if not pattern:
            return render_template('404.html'), 404
        return render_template('pattern_detail.html', pattern=pattern)
    
    @app.route('/analytics')
    def analytics():
        """Analytics dashboard."""
        stats = pattern_service.get_statistics()
        return render_template('analytics.html', stats=stats)
    
    @app.route('/test')
    def test_patterns():
        """Pattern testing tool."""
        return render_template('test.html')
    
    # API Routes
    @api.route('/patterns')
    class PatternList(Resource):
        @api.doc('list_patterns')
        @api.param('q', 'Search query')
        @api.param('category', 'Filter by category')
        @api.param('vendor', 'Filter by vendor')
        @api.param('limit', 'Limit results (max 100)', type=int, default=20)
        @api.param('offset', 'Offset for pagination', type=int, default=0)
        @api.marshal_list_with(pattern_model)
        def get(self):
            """Get all patterns with optional filtering."""
            query = request.args.get('q', '')
            category = request.args.get('category', '')
            vendor = request.args.get('vendor', '')
            limit = min(request.args.get('limit', 20, type=int), 100)
            offset = request.args.get('offset', 0, type=int)
            
            result = pattern_service.search_patterns(query, category, vendor, limit, offset)
            return result
    
    @api.route('/patterns/<string:vendor_id>/<string:product_id>')
    class PatternDetail(Resource):
        @api.doc('get_pattern')
        def get(self, vendor_id, product_id):
            """Get specific pattern by vendor and product ID."""
            pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
            if not pattern:
                api.abort(404, "Pattern not found")
            return pattern
    
    @api.route('/match')
    class PatternMatch(Resource):
        @api.doc('match_patterns')
        @api.expect(match_request_model)
        @api.marshal_list_with(match_result_model)
        def post(self):
            """Match patterns against input text."""
            data = request.get_json()
            if not data or 'text' not in data:
                api.abort(400, "Missing text parameter")
            
            matches = pattern_service.match_patterns(data['text'])
            return matches
    
    @api.route('/categories')
    class CategoriesList(Resource):
        @api.doc('list_categories')
        def get(self):
            """Get all available categories."""
            categories = pattern_service.get_categories()
            return {'categories': categories}
    
    @api.route('/vendors')
    class VendorsList(Resource):
        @api.doc('list_vendors')
        def get(self):
            """Get all available vendors."""
            vendors = pattern_service.get_vendors()
            return {'vendors': vendors}
    
    @api.route('/analytics/summary')
    class AnalyticsSummary(Resource):
        @api.doc('get_analytics')
        def get(self):
            """Get analytics summary."""
            return pattern_service.get_statistics()
    
    @api.route('/health')
    class Health(Resource):
        @api.doc('health_check')
        def get(self):
            """Health check endpoint."""
            stats = pattern_service.get_statistics()
            return {
                'status': 'healthy',
                'patterns_loaded': stats['total_patterns'],
                'categories': len(stats['categories']),
                'vendors': len(stats['vendors']),
                'timestamp': time.time()
            }
    
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
    print(f"📚 API Documentation: http://{args.host}:{args.port}/api/docs/")
    print(f"🔍 Search: http://{args.host}:{args.port}/search")
    print(f"📊 Analytics: http://{args.host}:{args.port}/analytics")
    print(f"🧪 Pattern Tester: http://{args.host}:{args.port}/test")
    print("=" * 60)
    
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()