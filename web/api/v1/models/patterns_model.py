"""
Pattern models for Regex Intelligence Exchange API v1.
"""

from flask_restx import fields
from api.v1.routes import api

# API models
pattern_model = api.model('Pattern', {
    'vendor': fields.String(description='Vendor name'),
    'vendor_id': fields.String(description='Vendor ID'),
    'product': fields.String(description='Product name'),
    'product_id': fields.String(description='Product ID'),
    'category': fields.String(description='Category'),
    'subcategory': fields.String(description='Subcategory'),
    'pattern_count': fields.Integer(description='Number of patterns')
})

pattern_list_model = api.model('PatternList', {
    'patterns': fields.List(fields.Nested(pattern_model)),
    'total': fields.Integer(description='Total number of patterns'),
    'offset': fields.Integer(description='Offset for pagination'),
    'limit': fields.Integer(description='Limit for pagination')
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
    'text': fields.String(required=True, description='Text to match against patterns')
})

match_result_model = api.model('MatchResult', {
    'vendor': fields.String(description='Vendor name'),
    'product': fields.String(description='Product name'),
    'vendor_id': fields.String(description='Vendor ID'),
    'product_id': fields.String(description='Product ID'),
    'pattern_name': fields.String(description='Pattern name'),
    'matched_text': fields.String(description='Matched text'),
    'version': fields.String(description='Detected version'),
    'version_range': fields.String(description='Version range')
})

category_list_model = api.model('CategoryList', {
    'categories': fields.List(fields.String, description='List of categories')
})

vendor_list_model = api.model('VendorList', {
    'vendors': fields.List(fields.String, description='List of vendors')
})

stats_model = api.model('Stats', {
    'total_patterns': fields.Integer(description='Total number of patterns'),
    'categories': fields.Raw(description='Category counts'),
    'subcategories': fields.Raw(description='Subcategory counts'),
    'last_updated': fields.String(description='Last updated timestamp')
})

health_model = api.model('Health', {
    'status': fields.String(description='Health status'),
    'timestamp': fields.String(description='Timestamp'),
    'pattern_count': fields.Integer(description='Number of patterns')
})