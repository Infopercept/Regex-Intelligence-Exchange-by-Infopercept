"""
API v1 routes for Regex Intelligence Exchange
"""

from flask_restx import Namespace, Resource, fields
from flask import request
import json
import os
import re
from datetime import datetime
from utils.security import security_manager, validate_pattern_id, validate_search_input
from utils.logging import log_manager
from services.pattern_service import pattern_service
from models.pattern import PatternSearchResult

# Create namespace with detailed description
api = Namespace('patterns', description='Technology fingerprinting pattern operations')

# Define API models for documentation
pattern_model = api.model('Pattern', {
    'vendor': fields.String(description='Vendor name', example='Apache'),
    'vendor_id': fields.String(description='Vendor ID', example='apache'),
    'product': fields.String(description='Product name', example='Apache'),
    'product_id': fields.String(description='Product ID', example='apache'),
    'category': fields.String(description='Category', example='web'),
    'subcategory': fields.String(description='Subcategory', example='web-server'),
    'pattern_count': fields.Integer(description='Number of patterns', example=5)
})

pattern_list_model = api.model('PatternList', {
    'patterns': fields.List(fields.Nested(pattern_model), description='List of patterns'),
    'total': fields.Integer(description='Total number of patterns matching criteria', example=1577),
    'offset': fields.Integer(description='Offset for pagination', example=0),
    'limit': fields.Integer(description='Limit for pagination', example=20)
})

pattern_detail_model = api.model('PatternDetail', {
    'vendor': fields.String(description='Vendor name'),
    'vendor_id': fields.String(description='Vendor ID'),
    'product': fields.String(description='Product name'),
    'product_id': fields.String(description='Product ID'),
    'category': fields.String(description='Category'),
    'subcategory': fields.String(description='Subcategory'),
    'versions': fields.Raw(description='Version-specific patterns'),
    'all_versions': fields.List(fields.Raw, description='Patterns for all versions')
})

match_request_model = api.model('MatchRequest', {
    'text': fields.String(required=True, description='Text to match against patterns', example='Server: Apache/2.4.41 (Ubuntu)')
})

match_result_model = api.model('MatchResult', {
    'vendor': fields.String(description='Vendor name', example='Apache'),
    'product': fields.String(description='Product name', example='Apache'),
    'vendor_id': fields.String(description='Vendor ID', example='apache'),
    'product_id': fields.String(description='Product ID', example='apache'),
    'pattern_name': fields.String(description='Pattern name', example='HTTP Server Header'),
    'matched_text': fields.String(description='Matched text', example='Server: Apache/2.4.41 (Ubuntu)'),
    'version': fields.String(description='Detected version', example='2.4.41'),
    'version_range': fields.String(description='Version range', example='>=2.4.0,<3.0.0')
})

category_list_model = api.model('CategoryList', {
    'categories': fields.List(fields.String, description='List of categories', example=['web', 'security', 'database'])
})

vendor_list_model = api.model('VendorList', {
    'vendors': fields.List(fields.String, description='List of vendors', example=['Apache', 'Microsoft', 'Oracle'])
})

stats_model = api.model('Stats', {
    'total_patterns': fields.Integer(description='Total number of patterns', example=1577),
    'categories': fields.Raw(description='Category counts', example={'web': 800, 'security': 200}),
    'subcategories': fields.Raw(description='Subcategory counts', example={'web-server': 300, 'firewall': 150}),
    'last_updated': fields.String(description='Last updated timestamp', example='2025-01-01T12:00:00Z')
})

health_model = api.model('Health', {
    'status': fields.String(description='Health status', example='healthy'),
    'timestamp': fields.String(description='Timestamp', example='2025-01-01T12:00:00Z'),
    'pattern_count': fields.Integer(description='Number of patterns', example=1577)
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message'),
    'status_code': fields.Integer(description='HTTP status code')
})

@api.route('/')
class PatternsList(Resource):
    @api.doc('list_patterns')
    @api.param('limit', 'Limit the number of patterns returned (max 100)', type=int, default=20)
    @api.param('offset', 'Offset for pagination', type=int, default=0)
    @api.param('category', 'Filter by category', type=str)
    @api.param('vendor', 'Filter by vendor ID', type=str)
    @api.param('q', 'Search query', type=str)
    @api.response(200, 'Success', pattern_list_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @validate_search_input
    def get(self):
        """Get all patterns with optional filtering
        
        Returns a list of technology patterns with optional filtering by category, vendor, or search query.
        Results are paginated with a maximum of 100 items per page.
        """
        # Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        category = request.args.get('category', '')
        vendor = request.args.get('vendor', '')
        query = request.args.get('q', '')
        
        # Sanitize inputs
        query = security_manager.sanitize_input(query)
        category = security_manager.sanitize_input(category)
        vendor = security_manager.sanitize_input(vendor)
        
        # Log the search
        log_manager.log_search_query(query, category, vendor)
        
        # Search patterns
        search_result = pattern_service.search_patterns(query=query, category=category, vendor=vendor)
        
        # Apply pagination
        if limit:
            # Ensure reasonable limits
            limit = min(limit, 100)  # Max 100 items per page
            start_idx = offset
            end_idx = offset + limit
            search_result.patterns = search_result.patterns[start_idx:end_idx]
            search_result.limit = limit
        
        # Return safe pattern representations
        safe_patterns = [pattern.get_safe_dict() for pattern in search_result.patterns]
        
        return {
            'patterns': safe_patterns,
            'total': search_result.total,
            'offset': offset,
            'limit': search_result.limit
        }

@api.route('/<vendor_id>/<product_id>')
@api.param('vendor_id', 'Vendor ID', type=str, required=True)
@api.param('product_id', 'Product ID', type=str, required=True)
class PatternDetail(Resource):
    @api.doc('get_pattern')
    @api.response(200, 'Success', pattern_detail_model)
    @api.response(404, 'Pattern not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @validate_pattern_id
    def get(self, vendor_id, product_id):
        """Get a specific pattern by vendor and product ID
        
        Returns detailed information about a specific technology pattern including all regex patterns
        and metadata associated with different versions of the technology.
        """
        # Log pattern access
        log_manager.log_pattern_access(vendor_id, product_id, request.headers.get('User-Agent'))
        
        pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
        
        if not pattern:
            api.abort(404, "Pattern not found")
        
        # Return pattern without sensitive metadata
        if pattern is not None and hasattr(pattern, 'to_dict'):
            return pattern.to_dict()
        else:
            # This should not happen, but provide a fallback
            api.abort(500, "Error processing pattern data")

@api.route('/match')
class PatternMatch(Resource):
    @api.doc('match_patterns')
    @api.expect(match_request_model)
    @api.response(200, 'Success', [match_result_model])
    @api.response(400, 'Bad Request', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Match patterns against input text
        
        Takes a text input and returns all technology patterns that match against it.
        This is useful for identifying technologies in HTTP responses, HTML content, or other text.
        """
        data = request.get_json()
        
        if not data or 'text' not in data:
            api.abort(400, "Missing text parameter")
        
        input_text = data['text']
        
        # Sanitize input text
        input_text = security_manager.sanitize_input(input_text)
        
        # Log the API call
        log_manager.log_api_call('/match', 'POST')
        
        # Match patterns
        matches = pattern_service.match_patterns(input_text)
        
        # Convert to dictionary format
        matches_dict = []
        for match in matches:
            matches_dict.append({
                'vendor': match.vendor,
                'product': match.product,
                'vendor_id': match.vendor_id,
                'product_id': match.product_id,
                'pattern_name': match.pattern_name,
                'matched_text': match.matched_text,
                'version': match.version,
                'version_range': match.version_range
            })
        
        return matches_dict

@api.route('/categories')
class CategoriesList(Resource):
    @api.doc('list_categories')
    @api.response(200, 'Success', category_list_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all available categories
        
        Returns a list of all technology categories available in the pattern database.
        """
        # Log the API call
        log_manager.log_api_call('/categories', 'GET')
        
        categories = pattern_service.get_categories()
        
        return {
            'categories': categories
        }

@api.route('/vendors')
class VendorsList(Resource):
    @api.doc('list_vendors')
    @api.response(200, 'Success', vendor_list_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all available vendors
        
        Returns a list of all technology vendors available in the pattern database.
        """
        # Log the API call
        log_manager.log_api_call('/vendors', 'GET')
        
        vendors = pattern_service.get_vendors()
        
        return {
            'vendors': vendors
        }

@api.route('/stats')
class Stats(Resource):
    @api.doc('get_stats')
    @api.response(200, 'Success', stats_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get database statistics
        
        Returns statistics about the pattern database including total pattern count,
        category distribution, and subcategory distribution.
        """
        # Log the API call
        log_manager.log_api_call('/stats', 'GET')
        
        stats = pattern_service.get_statistics()
        
        return {
            'total_patterns': stats.total_patterns,
            'categories': stats.categories,
            'subcategories': stats.subcategories,
            'last_updated': stats.last_updated
        }

@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.response(200, 'Success', health_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Health check endpoint
        
        Returns the health status of the API service including uptime information
        and the number of patterns loaded in memory.
        """
        # Log the API call
        log_manager.log_api_call('/health', 'GET')
        
        patterns = pattern_service.get_all_patterns()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'pattern_count': len(patterns)
        }