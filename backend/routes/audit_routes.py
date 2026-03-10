"""
Security Audit Routes
Endpoints for scanning and auditing password security
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.password_analyzer import analyze_password_strength
import jwt
import os
from bson.objectid import ObjectId
import logging
import traceback

logger = logging.getLogger(__name__)
bp = Blueprint('audit', __name__, url_prefix='/api/audit')

mongo = None
limiter = None


def set_mongo(mongo_instance):
    global mongo
    mongo = mongo_instance


def set_limiter(limiter_instance):
    global limiter
    limiter = limiter_instance


@bp.route('/scan', methods=['POST'])
def scan_credentials():
    """
    Scan all user credentials for security issues
    Returns audit report with weak, breached, and duplicate passwords
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401

        # Extract and verify token
        token = auth_header.split('Bearer ')[-1]
        jwt_secret = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Invalid token payload'}), 401

        # Get all credentials
        db = mongo.db
        credentials = list(db.credentials.find({'user_id': ObjectId(user_id)}))

        if not credentials:
            return jsonify({
                'audit_report': {
                    'total_credentials': 0,
                    'weak_passwords': [],
                    'breached_passwords': [],
                    'duplicate_passwords': [],
                    'strong_passwords': [],
                    'reused_passwords': [],
                    'summary': {
                        'total': 0,
                        'strong': 0,
                        'weak': 0,
                        'breached': 0,
                        'duplicates': 0,
                        'security_score': 0
                    }
                }
            }), 200

        weak_passwords = []
        strong_passwords = []
        breached_passwords = []
        password_counts = {}
        duplicate_passwords = []

        # Analyze each credential
        for cred in credentials:
            website = cred.get('website_name', 'Unknown')
            password = cred.get('password', '')
            username = cred.get('username', '')

            try:
                # Calculate strength
                strength = analyze_password_strength(password)
                strength_level = strength.get('strength', 'Unknown')

                # Check for weak passwords
                if strength_level in ['Weak', 'Fair', 'Very Weak']:
                    weak_passwords.append({
                        'id': str(cred.get('_id', '')),
                        'website': website,
                        'username': username,
                        'strength': strength_level,
                        'score': int((strength.get('score', 0) / 4) * 100),  # Convert 0-4 scale to 0-100
                        'feedback': strength.get('recommendations', [])
                    })
                else:
                    strong_passwords.append({
                        'website': website,
                        'strength': strength_level,
                        'score': int((strength.get('score', 0) / 4) * 100)  # Convert 0-4 scale to 0-100
                    })
            except Exception as cred_error:
                logger.error(f'Error analyzing password for {website}: {str(cred_error)}')
                # Continue with next credential
                continue

            # Check for breached passwords
            if cred.get('breach_status') == True:
                breached_passwords.append({
                    'id': str(cred.get('_id', '')),
                    'website': website,
                    'username': username,
                    'breach_count': cred.get('breach_count', 0)
                })

            # Check for duplicate/reused passwords
            pwd_hash = hash(password)
            if pwd_hash not in password_counts:
                password_counts[pwd_hash] = []
            password_counts[pwd_hash].append({
                'website': website,
                'username': username,
                'credential_id': str(cred.get('_id', ''))
            })

        # Find duplicate passwords
        for pwd_hash, occurrences in password_counts.items():
            if len(occurrences) > 1:
                duplicate_passwords.append({
                    'count': len(occurrences),
                    'credentials': occurrences
                })

        # Calculate security score (0-100)
        total = len(credentials)
        weak_count = len(weak_passwords)
        breached_count = len(breached_passwords)
        duplicate_count = sum(len(d['credentials']) - 1 for d in duplicate_passwords)

        score = 100
        score -= (weak_count / total) * 30 if total > 0 else 0
        score -= (breached_count / total) * 40 if total > 0 else 0
        score -= (duplicate_count / total) * 20 if total > 0 else 0
        score = max(0, int(score))

        audit_report = {
            'total_credentials': total,
            'weak_passwords': weak_passwords,
            'breached_passwords': breached_passwords,
            'duplicate_passwords': duplicate_passwords,
            'strong_passwords': strong_passwords,
            'summary': {
                'total': total,
                'strong': len(strong_passwords),
                'weak': weak_count,
                'breached': breached_count,
                'duplicates': len(duplicate_passwords),
                'security_score': score
            }
        }

        return jsonify({'audit_report': audit_report}), 200

    except Exception as e:
        logger.error(f'Audit scan error: {str(e)}')
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to scan credentials: {str(e)}'}), 500
