"""
Web routes for Regex Intelligence Exchange
"""

from flask import Blueprint, render_template, request, jsonify
import json
import os
import sys
import importlib.util
from pathlib import Path
from utils.security import security_manager, validate_pattern_id, validate_search_input
from utils.logging import log_manager, log_request_info
from services.pattern_service import pattern_service

# Add tools directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

# Import our utilities
tools_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tools')

# Import version utilities
spec = importlib.util.spec_from_file_location("version_utils", os.path.join(tools_dir, "version_utils.py"))
if spec is not None and spec.loader is not None:
    version_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_utils)

# Import pattern matcher
spec2 = importlib.util.spec_from_file_location("pattern_matcher", os.path.join(tools_dir, "pattern-matcher.py"))
if spec2 is not None and spec2.loader is not None:
    pattern_matcher = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(pattern_matcher)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Main dashboard page"""
    # Log the request
    log_request_info(request, 200)
    return render_template('index.html')

@main.route('/editor')
def pattern_editor():
    """Pattern editor page"""
    # Log the request
    log_request_info(request, 200)
    return render_template('pattern_editor.html')

@main.route('/api/patterns')
def api_patterns():
    """API endpoint to get all patterns"""
    # Log the API call
    log_manager.log_api_call('/api/patterns', 'GET')
    
    patterns = pattern_service.get_all_patterns()
    patterns_dict = [pattern.to_dict() for pattern in patterns]
    return jsonify(patterns_dict)

@main.route('/api/patterns/search')
@validate_search_input
def api_patterns_search():
    """API endpoint to search patterns"""
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    vendor = request.args.get('vendor', '')
    
    # Sanitize inputs
    query = security_manager.sanitize_input(query)
    category = security_manager.sanitize_input(category)
    vendor = security_manager.sanitize_input(vendor)
    
    # Log the search
    log_manager.log_search_query(query, category, vendor)
    
    # Search patterns
    search_result = pattern_service.search_patterns(query=query, category=category, vendor=vendor)
    patterns_dict = [pattern.to_dict() for pattern in search_result.patterns]
    
    return jsonify(patterns_dict)

@main.route('/api/patterns/<vendor>/<product>')
@validate_pattern_id
def api_pattern_detail(vendor, product):
    """API endpoint to get a specific pattern"""
    # Log pattern access
    log_manager.log_pattern_access(vendor, product, request.headers.get('User-Agent'))
    
    pattern = pattern_service.get_pattern_by_id(vendor, product)
    
    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404
    
    return jsonify(pattern.to_dict())

@main.route('/api/match', methods=['POST'])
def api_match():
    """API endpoint to match patterns against input text"""
    data = request.get_json()
    input_text = data.get('text', '')
    
    if not input_text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Sanitize input text
    input_text = security_manager.sanitize_input(input_text)
    
    # Log the API call
    log_manager.log_api_call('/api/match', 'POST')
    
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
    
    return jsonify(matches_dict)

@main.route('/search')
def search():
    """Search page"""
    # Log the request
    log_request_info(request, 200)
    return render_template('search.html')

@main.route('/pattern/<vendor>/<product>')
@validate_pattern_id
def pattern_detail(vendor, product):
    """Pattern detail page"""
    # Log pattern access
    log_manager.log_pattern_access(vendor, product, request.headers.get('User-Agent'))
    return render_template('pattern_detail.html', vendor=vendor, product=product)

@main.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Log the request
    log_request_info(request, 200)
    return render_template('analytics.html')

@main.route('/api/analytics/summary')
def api_analytics_summary():
    """API endpoint for analytics summary"""
    # Log the API call
    log_manager.log_api_call('/api/analytics/summary', 'GET')
    
    stats = pattern_service.get_statistics()
    
    return jsonify({
        'total_patterns': stats.total_patterns,
        'categories': stats.categories,
        'subcategories': stats.subcategories
    })