"""
AI-powered password recommendation routes
"""
from flask import Blueprint, request, jsonify, session
from utils.ai_recommender import generate_recommendations, generate_strong_password
from utils.password_analyzer import analyze_password_strength
import os

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Track password suggestion attempts per session
suggestion_attempts = {}

@bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get AI-generated password recommendations"""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'Password required'}), 400
    
    password = data.get('password')
    
    # Analyze password strength
    analysis = analyze_password_strength(password)
    
    # Generate AI recommendations
    ai_recommendations = generate_recommendations(password)
    
    # Combine with standard analysis recommendations
    all_recommendations = list(set(analysis.get('recommendations', []) + ai_recommendations))
    
    return jsonify({
        'strength': analysis['strength'],
        'score': analysis['score'],
        'entropy': analysis['entropy'],
        'crack_time': analysis['crack_time'],
        'characteristics': analysis['characteristics'],
        'recommendations': all_recommendations[:10]  # Top 10 recommendations
    }), 200

@bp.route('/generate', methods=['POST'])
def generate_password():
    """Generate a strong password using AI"""
    try:
        data = request.get_json() if request.get_json() else {}
        
        # Get session ID for tracking attempts
        client_id = request.remote_addr + str(request.headers.get('User-Agent', ''))
        
        # Track attempts per session
        if client_id not in suggestion_attempts:
            suggestion_attempts[client_id] = 0
        
        suggestion_attempts[client_id] += 1
        
        # Limit to 3 suggestions per session
        if suggestion_attempts[client_id] > 3:
            return jsonify({
                'error': 'Maximum suggestions reached (3 per session)',
                'message': 'Please refresh to reset suggestion limit'
            }), 429
        
        # Get requirements from request
        length = data.get('length', 16)
        use_special = data.get('use_special', True)
        use_numbers = data.get('use_numbers', True)
        
        # Validate length
        if length < 8 or length > 32:
            length = 16
        
        # Generate strong password
        new_password = generate_strong_password(
            length=length,
            use_special=use_special,
            use_numbers=use_numbers
        )
        
        # Analyze generated password
        analysis = analyze_password_strength(new_password)
        
        return jsonify({
            'generated_password': new_password,
            'strength_score': analysis['score'],
            'strength_level': analysis['strength'],
            'entropy': analysis['entropy'],
            'attempts_remaining': 3 - suggestion_attempts[client_id],
            'note': 'This password is displayed but not saved. Copy it to your preferred location.'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate password: {str(e)}'}), 500

@bp.route('/verify-strength', methods=['POST'])
def verify_strength():
    """Verify and analyze password strength in real-time"""
    try:
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({'error': 'Password required'}), 400
        
        password = data.get('password')
        
        # Comprehensive analysis
        analysis = analyze_password_strength(password)
        
        return jsonify({
            'password_length': len(password),
            'strength': analysis['strength'],
            'score': analysis['score'],
            'entropy': analysis['entropy'],
            'crack_time': analysis['crack_time'],
            'characteristics': analysis['characteristics'],
            'recommendations': analysis.get('recommendations', [])[:5]  # Top 5
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@bp.route('/reset-suggestions', methods=['POST'])
def reset_suggestions():
    """Reset suggestion counter for new session"""
    try:
        client_id = request.remote_addr + str(request.headers.get('User-Agent', ''))
        suggestion_attempts[client_id] = 0
        
        return jsonify({
            'message': 'Suggestion counter reset',
            'attempts_remaining': 3
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
