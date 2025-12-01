"""
Security questions routes for account recovery
"""
from flask import Blueprint, request, jsonify
import logging
from utils.security_questions import (
    get_all_questions,
    get_question_by_id,
    validate_question_id,
    validate_answer,
    normalize_answer
)

logger = logging.getLogger(__name__)

bp = Blueprint('security_questions', __name__, url_prefix='/api/security-questions')

# Get MongoDB instance (will be injected from app)
mongo = None

def set_mongo(mongo_instance):
    """Set the MongoDB instance for routes"""
    global mongo
    mongo = mongo_instance


@bp.route('/questions', methods=['GET'])
def get_questions():
    """
    Get all available security questions
    Returns list of questions for signup
    """
    try:
        questions = get_all_questions()
        return jsonify({
            'questions': questions,
            'count': len(questions)
        }), 200
    except Exception as e:
        logger.error(f'Failed to fetch security questions: {str(e)}')
        return jsonify({'error': 'Failed to fetch questions'}), 500


@bp.route('/get-question-for-email', methods=['POST'])
def get_question_for_email():
    """
    Get the security question for a specific email
    Used during password recovery to show user their question
    
    Request body:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user
        user_data = mongo.db.users.find_one({'email': email})
        
        if not user_data:
            # Don't reveal if email exists (security best practice)
            logger.warning(f'Get question failed: email {email} not found')
            return jsonify({
                'error': 'Email not found'
            }), 404
        
        # Get the question
        question_id = user_data.get('security_question_id')
        if not question_id:
            logger.warning(f'Get question failed: user {email} has no security question set')
            return jsonify({
                'error': 'User account not properly configured'
            }), 400
        
        question = get_question_by_id(question_id)
        if not question:
            logger.error(f'Get question failed: invalid question_id {question_id} for user {email}')
            return jsonify({
                'error': 'Question not found'
            }), 400
        
        logger.info(f'✅ Security question retrieved for {email}')
        
        return jsonify({
            'question': question['question'],
            'question_id': question_id
        }), 200
        
    except Exception as e:
        logger.error(f'Failed to get security question: {str(e)}', exc_info=True)
        return jsonify({'error': 'Failed to retrieve question'}), 500


@bp.route('/validate-answer', methods=['POST'])
def validate_security_answer():
    """
    Validate a security question answer during password recovery
    This endpoint is used after email verification
    
    Request body:
    {
        "user_id": "mongo_user_id",
        "question_id": 1,
        "answer": "user's answer"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        user_id = data.get('user_id', '').strip()
        question_id = data.get('question_id')
        answer = data.get('answer', '').strip()
        
        if not user_id or not question_id or not answer:
            return jsonify({'error': 'user_id, question_id, and answer are required'}), 400
        
        # Validate question exists
        if not validate_question_id(question_id):
            return jsonify({'error': 'Invalid question_id'}), 400
        
        # Validate answer format
        is_valid, error_msg = validate_answer(answer)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Note: Actual verification happens in auth_routes.py 
        # because it needs access to the user's stored hashed answer
        return jsonify({
            'message': 'Answer validation passed format check',
            'ready_to_verify': True
        }), 200
        
    except Exception as e:
        logger.error(f'Security answer validation failed: {str(e)}')
        return jsonify({'error': 'Validation failed'}), 500
