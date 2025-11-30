"""
Password analysis and strength scoring routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.password_analyzer import analyze_password_strength
from utils.breach_checker import check_breach
from utils.auth_helper import token_required

bp = Blueprint('password', __name__, url_prefix='/api/passwords')


@bp.route('/analyze', methods=['POST'])
@token_required
def analyze(current_user):
    """
    Analyze password strength and check for breaches
    
    Requires: Authentication token
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if len(password) > 128:
            return jsonify({'error': 'Password is too long'}), 400
        
        # Analyze strength
        strength_analysis = analyze_password_strength(password)
        
        # Check for breaches
        try:
            breach_data = check_breach(password)
        except Exception as e:
            # If breach check fails, continue without it
            breach_data = {'breached': False, 'breach_count': 0}
        
        response = {
            'strength': strength_analysis,
            'breached': breach_data.get('breached', False),
            'breach_count': breach_data.get('breach_count', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': f'Password analysis failed: {str(e)}'}), 500


@bp.route('/history', methods=['GET'])
@token_required
def get_history(current_user):
    """
    Get password analysis history for authenticated user
    
    Requires: Authentication token
    """
    try:
        # TODO: Implement history retrieval from database
        # For now, return empty list
        return jsonify({'history': []}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve history: {str(e)}'}), 500


@bp.route('/save-result', methods=['POST'])
@token_required
def save_result(current_user):
    """
    Save password analysis result to user history
    
    Requires: Authentication token
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # TODO: Save to database
        return jsonify({'message': 'Result saved'}), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to save result: {str(e)}'}), 500

