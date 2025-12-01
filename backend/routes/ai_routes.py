"""
AI-powered password recommendation routes
"""
from flask import Blueprint, request, jsonify, session
from utils.ai_recommender import (
    generate_recommendations, 
    generate_strong_password,
    validate_password_meets_security_rules,
    generate_ai_password_suggestions
)
from utils.password_analyzer import analyze_password_strength
from utils.auth_helper import token_required
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
@token_required
def generate_password(current_user):
    """Generate a strong password using AI"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f'🔄 Generate password request started')
        
        data = request.get_json() if request.get_json() else {}
        
        # Get requirements from request
        length = data.get('length', 16)
        use_special = data.get('use_special', True)
        use_numbers = data.get('use_numbers', True)
        
        logger.info(f'🔄 Parameters: length={length}, special={use_special}, numbers={use_numbers}')
        
        # Validate length (12-32)
        if length < 12 or length > 32:
            length = 16
        
        try:
            logger.info(f'🔄 Calling generate_strong_password...')
            # Generate strong password meeting security rules
            new_password = generate_strong_password(
                length=length,
                use_special=use_special,
                use_numbers=use_numbers
            )
            logger.info(f'🔄 Password generated: {len(new_password)} chars')
        except Exception as e:
            logger.error(f'🔄 Error in generate_strong_password: {str(e)}', exc_info=True)
            raise
        
        try:
            logger.info(f'🔄 Validating password...')
            # Validate password meets security rules
            is_valid, validation_errors = validate_password_meets_security_rules(
                new_password,
                min_length=12,
                require_special=use_special,
                require_numbers=use_numbers
            )
            logger.info(f'🔄 Validation result: {is_valid}')
        except Exception as e:
            logger.error(f'🔄 Error in validate_password_meets_security_rules: {str(e)}', exc_info=True)
            raise
        
        try:
            logger.info(f'🔄 Analyzing password strength...')
            # Analyze generated password
            analysis = analyze_password_strength(new_password)
            logger.info(f'✅ Password analysis complete - score={analysis["score"]}')
        except Exception as e:
            logger.error(f'🔄 Error in analyze_password_strength: {str(e)}', exc_info=True)
            raise
        
        logger.info(f'✅ Password generation successful')
        
        return jsonify({
            'generated_password': new_password,
            'strength_score': analysis['score'],
            'strength_level': analysis['strength'],
            'entropy': analysis['entropy'],
            'meets_security_rules': is_valid,
            'validation_errors': validation_errors if not is_valid else [],
            'note': 'This password is displayed but not saved. Copy it to your preferred location.'
        }), 200
    
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'🔄 Password generation error: {str(e)}')
        logger.error(f'Stack trace: {traceback.format_exc()}')
        return jsonify({'error': f'Failed to generate password: {str(e)}'}), 500

@bp.route('/ai-suggestions', methods=['POST'])
@token_required
def get_ai_suggestions(current_user):
    """Get multiple AI-driven password suggestions"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        data = request.get_json() if request.get_json() else {}
        
        # Get user ID for tracking attempts (per-user, not per-session)
        user_id = str(current_user.get('user_id', 'anonymous'))
        session_key = f"{user_id}_suggestions"
        
        # Track attempts per user per session
        if session_key not in suggestion_attempts:
            suggestion_attempts[session_key] = 0
        
        suggestion_attempts[session_key] += 1
        current_attempt = suggestion_attempts[session_key]
        
        logger.info(f'🤖 AI suggestions request - attempt {current_attempt} for user {user_id}')
        
        # Limit to 3 suggestion requests per session
        if current_attempt > 3:
            logger.warning(f'🤖 Attempt limit exceeded: {current_attempt}')
            return jsonify({
                'error': 'Maximum suggestions reached (3 per session)',
                'message': 'Refresh the page to reset your attempts'
            }), 429
        
        # Get parameters
        count = data.get('count', 3)
        length = data.get('length', 16)
        
        logger.info(f'🤖 AI parameters - count={count}, length={length}')
        
        # Validate count and length
        if count < 1 or count > 5:
            count = 3
        if length < 12 or length > 32:
            length = 16
        
        # Generate AI-driven suggestions
        suggestions = generate_ai_password_suggestions(count=count, length=length)
        
        logger.info(f'🤖 Generated {len(suggestions)} suggestions')
        
        # Analyze each suggestion
        analyzed_suggestions = []
        for pwd in suggestions:
            analysis = analyze_password_strength(pwd)
            is_valid, errors = validate_password_meets_security_rules(pwd, min_length=12)
            
            analyzed_suggestions.append({
                'password': pwd,
                'strength_score': analysis['score'],
                'strength_level': analysis['strength'],
                'entropy': analysis['entropy'],
                'meets_security_rules': is_valid,
                'validation_errors': errors if not is_valid else []
            })
        
        logger.info(f'✅ AI suggestions completed successfully')
        
        return jsonify({
            'suggestions': analyzed_suggestions,
            'count': len(analyzed_suggestions),
            'attempts_remaining': 3 - current_attempt,
            'note': 'Passwords are AI-generated and not saved. Copy to your password manager or save securely.',
            'security_requirements': {
                'minimum_length': 12,
                'requires_uppercase': True,
                'requires_lowercase': True,
                'requires_numbers': True,
                'requires_special': True
            }
        }), 200
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'🤖 AI suggestions error: {str(e)}', exc_info=True)
        return jsonify({'error': f'Failed to generate AI suggestions: {str(e)}'}), 500

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
        
        # Validate against security rules
        is_valid, validation_errors = validate_password_meets_security_rules(password, min_length=12)
        
        return jsonify({
            'password_length': len(password),
            'strength': analysis['strength'],
            'score': analysis['score'],
            'entropy': analysis['entropy'],
            'crack_time': analysis['crack_time'],
            'characteristics': analysis['characteristics'],
            'recommendations': analysis.get('recommendations', [])[:5],  # Top 5
            'meets_security_rules': is_valid,
            'validation_errors': validation_errors if not is_valid else [],
            'security_requirements': {
                'minimum_length': 12,
                'requires_uppercase': True,
                'requires_lowercase': True,
                'requires_numbers': True,
                'requires_special': True
            }
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
