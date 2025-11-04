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
from flask import Flask, render_template, jsonify, request, send_from_directory, current_app, Blueprint
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
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        patterns_dir = os.path.join(base_dir, 'patterns', 'by-vendor')
        if not os.path.exists(patterns_dir):
            raise Exception(f"Patterns directory not found at {patterns_dir}")
        return patterns_dir
    
    def _load_patterns(self):
        """Load all patterns from files with progress indicator."""
        if self._patterns_cache is not None:
            return self._patterns_cache
        
        if not os.path.exists(self.patterns_dir):
            # Try to find patterns directory relative to the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)
            alt_patterns_dir = os.path.join(base_dir, 'patterns', 'by-vendor')
            
            if os.path.exists(alt_patterns_dir):
                self.patterns_dir = alt_patterns_dir
            else:
                raise Exception(f"Patterns directory not found at: {self.patterns_dir} or {alt_patterns_dir}")
        
        patterns = []
        pattern_files = glob.glob(os.path.join(self.patterns_dir, '**', '*.json'), recursive=True)
        
        if not pattern_files:
            raise Exception(f"No pattern files found in: {self.patterns_dir}")
        
        print(f"📂 Loading patterns from {len(pattern_files)} files in {self.patterns_dir}...")
        
        for i, file_path in enumerate(pattern_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                    
                    # Get vendor/product from file path
                    rel_path = os.path.relpath(file_path, self.patterns_dir)
                    parts = rel_path.split(os.sep)
                    
                    # Extract meaningful data from path
                    if len(parts) >= 2:
                        vendor_id = parts[0]
                        product_id = os.path.splitext(parts[1])[0]
                        
                        # Set vendor and product IDs
                        pattern_data['vendor_id'] = vendor_id
                        pattern_data['product_id'] = product_id
                        
                        # Set vendor/product names if not present
                        if not pattern_data.get('vendor'):
                            pattern_data['vendor'] = vendor_id.replace('-', ' ').title()
                        if not pattern_data.get('product'):
                            pattern_data['product'] = product_id.replace('-', ' ').title()
                    
                    # Ensure all required fields with proper defaults
                    pattern_data.setdefault('vendor', pattern_data.get('vendor_id', 'Unknown'))
                    pattern_data.setdefault('product', pattern_data.get('product_id', 'Unknown'))
                    pattern_data.setdefault('category', 'Web')  # Default to Web category
                    pattern_data.setdefault('subcategory', '')
                    pattern_data.setdefault('description', '')
                    pattern_data.setdefault('notes', '')
                    
                    # Validate required fields
                    if not pattern_data.get('vendor') or not pattern_data.get('product'):
                        print(f"⚠️  Skipping {file_path}: Missing vendor or product name")
                        continue
                        
                    # Validate patterns
                    all_versions = pattern_data.get('all_versions', [])
                    versions = pattern_data.get('versions', {})
                    
                    if not all_versions and not versions:
                        print(f"⚠️  Warning: No patterns found in {file_path}")
                        continue
                        
                    # Validate and compile patterns
                    for pattern_entry in all_versions:
                        try:
                            if pattern_entry.get('pattern'):
                                re.compile(pattern_entry['pattern'])
                        except re.error as e:
                            print(f"⚠️  Invalid regex in {file_path}: {e}")
                            continue
                    
                    patterns.append(pattern_data)
                    
                    # Progress indicator
                    if (i + 1) % 100 == 0:
                        print(f"   Loaded {i + 1}/{len(pattern_files)} files...")
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON Error in {file_path}: {e}")
                continue
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
                continue
        
        if not patterns:
            raise Exception("No valid patterns were loaded!")
        
        self._patterns_cache = patterns
        print(f"✅ Successfully loaded {len(patterns)} patterns!")
        print(f"   Categories: {len(set(p.get('category', '') for p in patterns))}")
        print(f"   Vendors: {len(set(p.get('vendor', '') for p in patterns))}")
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
        try:
            print(f"\n🔍 Search request - Query: '{query}', Category: '{category}', Vendor: '{vendor}'")
            
            # Ensure patterns are loaded
            patterns = self._load_patterns()
            if not patterns:
                print("❌ No patterns loaded in cache")
                return {
                    'patterns': [],
                    'total': 0,
                    'offset': offset,
                    'limit': limit or 20
                }
            
            print(f"📊 Total patterns in cache: {len(patterns)}")
            
            # Apply filters
            filtered = []
            for pattern in patterns:
                match = True
                
                # Category filter
                if category and category.lower() not in ('all categories', 'all'):
                    pattern_category = str(pattern.get('category', '')).lower()
                    if not pattern_category:
                        match = False
                    elif category.lower() != pattern_category:
                        # Try partial match for subcategories
                        pattern_subcategory = str(pattern.get('subcategory', '')).lower()
                        if not (category.lower() in pattern_category or 
                              category.lower() in pattern_subcategory):
                            match = False
                
                # Vendor filter
                if vendor and vendor.lower() not in ('all vendors', 'all'):
                    pattern_vendor = str(pattern.get('vendor', '')).lower()
                    vendor_id = str(pattern.get('vendor_id', '')).lower()
                    if not (vendor.lower() in pattern_vendor or 
                           vendor.lower() in vendor_id):
                        match = False
                
                # Text search
                if query and match:
                    query_parts = query.lower().split()
                    searchable_fields = {
                        'vendor': str(pattern.get('vendor', '')).lower(),
                        'vendor_id': str(pattern.get('vendor_id', '')).lower(),
                        'product': str(pattern.get('product', '')).lower(),
                        'product_id': str(pattern.get('product_id', '')).lower(),
                        'category': str(pattern.get('category', '')).lower(),
                        'subcategory': str(pattern.get('subcategory', '')).lower(),
                        'description': str(pattern.get('description', '')).lower(),
                        'notes': str(pattern.get('notes', '')).lower(),
                    }
                    
                    # Check each query part against all fields
                    for query_part in query_parts:
                        found_part = False
                        for field_value in searchable_fields.values():
                            if query_part in field_value:
                                found_part = True
                                break
                        if not found_part:
                            match = False
                            break
                
                if match:
                    filtered.append(pattern)
            
            # Get total before pagination
            total = len(filtered)
            
            # Apply pagination
            offset = max(0, int(offset))
            if limit:
                limit = max(1, int(limit))
                filtered = filtered[offset:offset + limit]
            
            return {
                'patterns': filtered,
                'total': total,
                'offset': offset,
                'limit': limit or len(filtered)
            }
            
        except Exception as e:
            raise Exception(f"Error searching patterns: {str(e)}")
    
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

from flask import Blueprint

# Initialize Flask-RESTX API
api = Api(
    title='Regex Intelligence Exchange API',
    version='1.0',
    description='Complete technology fingerprinting pattern API with 1500+ patterns',
    doc='/api/docs/',
    prefix='/api'
)

# Create namespaces
ns = api.namespace('', description='Pattern operations')

# Create blueprints
web_bp = Blueprint('web', __name__, url_prefix='')
api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_web_routes(bp, pattern_service):
    @bp.route('/')
    def index():
        """Main dashboard."""
        try:
            stats = pattern_service.get_statistics()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            current_app.logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('errors/500.html'), 500

    @bp.route('/search')
    def search():
        """Search page."""
        categories = pattern_service.get_categories()
        vendors = pattern_service.get_vendors()
        return render_template('search.html', categories=categories, vendors=vendors)

    @bp.route('/analytics')
    def analytics():
        """Analytics dashboard."""
        stats = pattern_service.get_statistics()
        return render_template('analytics.html', stats=stats)

    @bp.route('/test')
    def test():
        """Pattern testing tool."""
        return render_template('test.html')
    
    @bp.route('/pattern/<string:vendor_id>/<string:product_id>')
    def pattern_detail(vendor_id, product_id):
        """Pattern detail page."""
        pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
        if not pattern:
            return render_template('errors/404.html'), 404
        return render_template('pattern_detail.html', pattern=pattern)

def create_app():
    """Create complete Flask application with all features."""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize pattern service
    pattern_service = PatternService()
    
    # Register static folder
    app.static_folder = 'static'
    app.template_folder = 'templates'
    
    # Add favicon handler
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon'
        )
    
    # Initialize routes
    init_web_routes(web_bp, pattern_service)
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    
    # Initialize API with app
    api.init_app(app)
    
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
        try:
            stats = pattern_service.get_statistics()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            app.logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('errors/500.html'), 500
    
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
    @ns.route('/patterns')
    class PatternList(Resource):
        @ns.doc('list_patterns')
        @ns.param('q', 'Search query')
        @ns.param('category', 'Filter by category')
        @ns.param('vendor', 'Filter by vendor')
        @ns.param('limit', 'Limit results (max 100)', type=int, default=20)
        @ns.param('offset', 'Offset for pagination', type=int, default=0)
        @ns.marshal_list_with(pattern_model)
        def get(self):
            """Get all patterns with optional filtering."""
            # Get and clean search parameters
            query = request.args.get('q', '').strip()
            category = request.args.get('category', '').strip()
            vendor = request.args.get('vendor', '').strip()
            limit = min(request.args.get('limit', 20, type=int), 100)
            offset = request.args.get('offset', 0, type=int)
            
            try:
                # Log the request parameters
                print(f"\n📥 API Request - Params: q='{query}', category='{category}', vendor='{vendor}', limit={limit}, offset={offset}")
                
                # If all filters are empty, return the first page of all patterns
                if not query and not category and not vendor:
                    result = pattern_service.get_all_patterns(limit=limit, offset=offset)
                    total = len(pattern_service._load_patterns())
                    response_data = {
                        'patterns': result,
                        'total': total,
                        'offset': offset,
                        'limit': limit,
                        'has_more': (offset + limit) < total
                    }
                else:
                    # Do filtered search
                    result = pattern_service.search_patterns(query, category, vendor, limit, offset)
                    response_data = {
                        'patterns': result['patterns'],
                        'total': result['total'],
                        'offset': result['offset'],
                        'limit': result['limit'],
                        'has_more': (result['offset'] + result['limit']) < result['total']
                    }
                
                print(f"📤 API Response - Total matches: {response_data['total']}, Returned: {len(response_data['patterns'])}")
                
                if not response_data['patterns']:
                    print("⚠️ Warning: No patterns found for the given criteria")
                    print(f"   Available categories: {pattern_service.get_categories()}")
                
                return response_data
            except Exception as e:
                app.logger.error(f"Search error: {str(e)}")
                return {'error': str(e)}, 500
    
    @ns.route('/patterns/<string:vendor_id>/<string:product_id>')
    @ns.response(404, 'Pattern not found')
    class PatternDetail(Resource):
        @ns.doc('get_pattern')
        def get(self, vendor_id, product_id):
            """Get specific pattern by vendor and product ID."""
            pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
            if not pattern:
                api.abort(404, "Pattern not found")
            return pattern
    
    @ns.route('/match')
    class PatternMatch(Resource):
        @ns.doc('match_patterns')
        @ns.expect(match_request_model)
        @ns.marshal_list_with(match_result_model)
        def post(self):
            """Match patterns against input text."""
            try:
                data = request.get_json()
                if not data or 'text' not in data:
                    api.abort(400, "Missing text parameter")
                
                matches = pattern_service.match_patterns(data['text'])
                return matches
            except Exception as e:
                app.logger.error(f"Error in pattern matching: {str(e)}")
                api.abort(500, f"Error processing pattern match request: {str(e)}")
    
    @ns.route('/categories')
    class CategoriesList(Resource):
        @ns.doc('list_categories')
        def get(self):
            """Get all available categories."""
            categories = pattern_service.get_categories()
            return {'categories': categories}
    
    @ns.route('/vendors')
    class VendorsList(Resource):
        @ns.doc('list_vendors')
        def get(self):
            """Get all available vendors."""
            vendors = pattern_service.get_vendors()
            return {'vendors': vendors}
    
    @ns.route('/analytics/summary')
    class AnalyticsSummary(Resource):
        @ns.doc('get_analytics')
        def get(self):
            """Get analytics summary."""
            return pattern_service.get_statistics()
    
    @app.route('/health')
    class Health(Resource):
        @ns.doc('health_check')
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
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error(f'Unhandled Exception: {str(error)}')
        return render_template('errors/500.html'), 500
    
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