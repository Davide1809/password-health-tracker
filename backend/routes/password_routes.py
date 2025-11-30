"""
Password analysis and strength scoring routes
"""
from flask import Blueprint, request, jsonify
from utils.password_analyzer import analyze_password_strength
from utils.breach_checker import check_breach

bp = Blueprint('password', __name__, url_prefix='/api/passwords')

@bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze password strength"""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'Password required'}), 400
    
    password = data.get('password')
    
    # Analyze strength
    strength_analysis = analyze_password_strength(password)
    
    # Check for breaches
    breach_data = check_breach(password)
    
    response = {
        'strength': strength_analysis,
        'breached': breach_data['breached'],
        'breach_count': breach_data.get('breach_count', 0),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(response), 200

@bp.route('/history', methods=['GET'])
def get_history():
    """Get password analysis history for authenticated user"""
    # TODO: Implement history retrieval from database
    return jsonify({'history': []}), 200

@bp.route('/save-result', methods=['POST'])
def save_result():
    """Save password analysis result"""
    data = request.get_json()
    
    # TODO: Save to database
    return jsonify({'message': 'Result saved'}), 201

from datetime import datetime
