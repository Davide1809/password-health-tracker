"""
Password Health Tracker - Flask Backend
Main application entry point
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from datetime import datetime
import logging

# Import route blueprints
from routes import auth_routes, password_routes, breach_routes, ai_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/password_health')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['AI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

# Initialize extensions
CORS(app)
mongo = PyMongo(app)

# Register blueprints with error handling
try:
    app.register_blueprint(auth_routes.bp)
except Exception as e:
    logger.warning(f"Could not register auth routes: {e}")
try:
    app.register_blueprint(password_routes.bp)
except Exception as e:
    logger.warning(f"Could not register password routes: {e}")
try:
    app.register_blueprint(breach_routes.bp)
except Exception as e:
    logger.warning(f"Could not register breach routes: {e}")
try:
    app.register_blueprint(ai_routes.bp)
except Exception as e:
    logger.warning(f"Could not register AI routes: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/version', methods=['GET'])
def version():
    """API version endpoint"""
    return jsonify({
        'version': '1.0.0',
        'name': 'Password Health Tracker API'
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_ENV', 'production') == 'development'
    )
