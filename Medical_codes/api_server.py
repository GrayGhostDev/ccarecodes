#!/usr/bin/env python3
"""
Companion Care Medical Billing Code API Server

This script provides a REST API for the front-end application to interact with
the medical billing code automation system.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from medical_code_automation import MedicalCodeAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_server")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize the medical code automation
automation = MedicalCodeAutomation()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "healthy", "service": "medical-code-api"})

@app.route('/api/codes/search', methods=['GET'])
def search_codes():
    """
    Search for medical billing codes based on a query string.
    
    Query parameters:
    - q: The search query (required)
    - max_results: Maximum number of results to return (optional, default=20)
    
    Returns:
        JSON response with search results
    """
    query = request.args.get('q')
    max_results = request.args.get('max_results', default=20, type=int)
    
    if not query:
        return jsonify({"error": "Missing required parameter 'q'"}), 400
    
    logger.info(f"API search request: query='{query}', max_results={max_results}")
    
    results = automation.search_codes(query, max_results)
    return jsonify({
        "query": query,
        "count": len(results),
        "results": results
    })

@app.route('/api/codes/<code>', methods=['GET'])
def get_code_details(code):
    """
    Get detailed information for a specific medical code.
    
    Path parameters:
    - code: The medical code to look up
    
    Returns:
        JSON response with code details or error
    """
    logger.info(f"API code details request: code='{code}'")
    
    details = automation.get_code_details(code)
    
    if details:
        return jsonify(details)
    else:
        return jsonify({"error": f"Code '{code}' not found"}), 404

@app.route('/api/codes/bulk', methods=['POST'])
def bulk_code_lookup():
    """
    Look up multiple codes at once.
    
    Request body:
    - codes: List of codes to look up
    
    Returns:
        JSON response with details for all requested codes
    """
    data = request.json
    
    if not data or 'codes' not in data or not isinstance(data['codes'], list):
        return jsonify({"error": "Request must include a 'codes' list"}), 400
    
    codes = data['codes']
    logger.info(f"API bulk lookup request: {len(codes)} codes")
    
    results = automation.bulk_update_codes(codes)
    return jsonify({
        "count": len(results),
        "results": results
    })

@app.route('/api/codes/estimate', methods=['POST'])
def estimate_cost():
    """
    Estimate the total cost for a set of medical codes.
    
    Request body:
    - codes: List of codes to include in the estimate
    - quantities: Optional dictionary mapping codes to quantities (default is 1 for each code)
    
    Returns:
        JSON response with cost estimate breakdown
    """
    data = request.json
    
    if not data or 'codes' not in data or not isinstance(data['codes'], list):
        return jsonify({"error": "Request must include a 'codes' list"}), 400
    
    codes = data['codes']
    quantities = data.get('quantities', {})
    
    logger.info(f"API cost estimate request: {len(codes)} codes")
    
    # Get details for all codes
    code_details = automation.bulk_update_codes(codes)
    
    # Calculate the estimate
    items = []
    total = 0.0
    
    for code in codes:
        if code in code_details:
            details = code_details[code]
            quantity = quantities.get(code, 1)
            
            # Get price (default to 0 if not available)
            price = details.get('price')
            if price is None:
                price = 0.0
            else:
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    price = 0.0
            
            item_total = price * quantity
            total += item_total
            
            items.append({
                "code": code,
                "description": details.get('description', ''),
                "price": price,
                "quantity": quantity,
                "item_total": item_total
            })
    
    return jsonify({
        "items": items,
        "total": total,
        "currency": "USD"
    })

def main():
    """Run the API server."""
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Medical Code API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main() 