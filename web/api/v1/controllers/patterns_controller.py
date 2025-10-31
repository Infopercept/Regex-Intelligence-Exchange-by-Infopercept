"""
Patterns controller for Regex Intelligence Exchange API v1.
"""

from flask import request
from flask_restx import Resource
from api.v1.routes import api
from utils.pattern_loader import load_patterns, get_pattern_by_id, search_patterns
import re

# Global pattern data
PATTERNS = load_patterns()

@api.route('/patterns')
class PatternsList(Resource):
    @api.doc('list_patterns')
    @api.param('limit', 'Limit the number of patterns returned')
    @api.param('offset', 'Offset for pagination', default=0)
    @api.param('category', 'Filter by category')
    @api.param('vendor', 'Filter by vendor')
    @api.param('q', 'Search query')
    def get(self):
        """Get all patterns with optional filtering"""
        # Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        category = request.args.get('category', '')
        vendor = request.args.get('vendor', '')
        query = request.args.get('q', '')
        
        # Filter patterns
        filtered_patterns = search_patterns(query=query, category=category, vendor=vendor, patterns=PATTERNS)
        
        # Apply pagination
        if limit:
            filtered_patterns = filtered_patterns[offset:offset + limit]
        
        # Return patterns without the actual regex patterns for security
        safe_patterns = []
        for pattern in filtered_patterns:
            safe_pattern = {
                'vendor': pattern.get('vendor'),
                'vendor_id': pattern.get('vendor_id'),
                'product': pattern.get('product'),
                'product_id': pattern.get('product_id'),
                'category': pattern.get('category'),
                'subcategory': pattern.get('subcategory'),
                'pattern_count': 0
            }
            
            # Count patterns
            if 'all_versions' in pattern:
                safe_pattern['pattern_count'] += len(pattern['all_versions'])
            
            if 'versions' in pattern:
                for version_patterns in pattern['versions'].values():
                    safe_pattern['pattern_count'] += len(version_patterns)
            
            safe_patterns.append(safe_pattern)
        
        return {
            'patterns': safe_patterns,
            'total': len(filtered_patterns),
            'offset': offset,
            'limit': limit
        }

@api.route('/patterns/<vendor_id>/<product_id>')
@api.param('vendor_id', 'Vendor ID')
@api.param('product_id', 'Product ID')
class PatternDetail(Resource):
    @api.doc('get_pattern')
    def get(self, vendor_id, product_id):
        """Get a specific pattern by vendor and product ID"""
        pattern = get_pattern_by_id(vendor_id, product_id, PATTERNS)
        
        if not pattern:
            return {'error': 'Pattern not found'}, 404
        
        return pattern

@api.route('/match')
class PatternMatch(Resource):
    @api.doc('match_patterns')
    def post(self):
        """Match patterns against input text"""
        from utils.pattern_matcher import find_matches
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return {'error': 'Missing text parameter'}, 400
        
        input_text = data['text']
        matches = find_matches(input_text, PATTERNS)
        
        return matches

@api.route('/categories')
class CategoriesList(Resource):
    @api.doc('list_categories')
    def get(self):
        """Get all available categories"""
        from utils.pattern_loader import get_categories
        categories = get_categories(PATTERNS)
        return {'categories': categories}

@api.route('/vendors')
class VendorsList(Resource):
    @api.doc('list_vendors')
    def get(self):
        """Get all available vendors"""
        from utils.pattern_loader import get_vendors
        vendors = get_vendors(PATTERNS)
        return {'vendors': vendors}

@api.route('/stats')
class Stats(Resource):
    @api.doc('get_stats')
    def get(self):
        """Get database statistics"""
        from utils.pattern_loader import get_statistics
        stats = get_statistics(PATTERNS)
        return stats

@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    def get(self):
        """Health check endpoint"""
        from datetime import datetime
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'pattern_count': len(PATTERNS)
        }