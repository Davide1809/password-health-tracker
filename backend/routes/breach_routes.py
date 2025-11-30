"""
Breach detection routes using Have I Been Pwned API
"""
from flask import Blueprint, request, jsonify
from utils.breach_checker import check_breach, get_breach_details

bp = Blueprint('breach', __name__, url_prefix='/api/breaches')

@bp.route('/check', methods=['POST'])
def check():
    """Check if password has been breached"""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'Password required'}), 400
    
    password = data.get('password')
    result = check_breach(password)
    
    return jsonify(result), 200

@bp.route('/search', methods=['POST'])
def search():
    """Search for breaches by email"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    email = data.get('email')
    
    # TODO: Use HIBP API to search for breaches associated with email
    breaches = []
    
    return jsonify({
        'email': email,
        'breaches': breaches,
        'breach_count': len(breaches)
    }), 200
