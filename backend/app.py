from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId # IMPORTANTE: Necessario per cercare in Mongo
import os
import secrets
from zxcvbn import zxcvbn 
from datetime import timedelta

# 1. Configurazione Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32)) 

# --- CONFIGURAZIONE CRITICA PER LA GESTIONE DEI COOKIE/SESSIONE SU CLOUD ---
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True     # Manda il cookie solo via HTTPS (OBBLIGATORIO su Cloud Run)
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Consente l'invio cross-site con credenziali
# -------------------------------------------------------------------------

# L'URL del tuo frontend Cloud Run (usato per CORS)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://password-frontend-749522457256.us-central1.run.app")

# 1.2 Configurazione CORS per accettare richieste dal frontend di Cloud Run
CORS(
    app, 
    resources={r"/api/*": {"origins": [FRONTEND_URL, "http://localhost:3000"]}}, 
    supports_credentials=True, 
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "PUT", "DELETE"]
)

# 2. Configurazione Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Variabili globali per il database
db = None
users = None

# Modello utente per Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"]) 
        self.email = user_data["email"]

@login_manager.user_loader
def load_user(user_id):
    if users is not None:
        try:
            # CORREZIONE: Cerca l'ID come ObjectId, che è il tipo corretto in MongoDB
            user_data = users.find_one({"_id": ObjectId(user_id)}) 
            if user_data:
                return User(user_data)
        except Exception as e:
            print(f"Error loading user with ID {user_id}: {e}")
    return None

# 3. Connessione MongoDB
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    print("FATAL ERROR: MONGO_URI environment variable not set.")
else:
    try:
        client = MongoClient(MONGO_URI)
        db = client.password_health 
        users = db.users
        client.admin.command('ping') 
        print("MongoDB connection successful.")
    except PyMongoError as e: 
        print(f"MongoDB connection or operation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during DB connection: {e}")

# 4. Endpoints API (Resto del codice omesso per brevità, è lo stesso di prima)
# Endpoint di registrazione
@app.route("/api/signup", methods=["POST"])
def signup():
    if users is None:
        return jsonify({"message": "Database not available."}), 503
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing email or password."}), 400

    try:
        if users.find_one({"email": email}):
            return jsonify({"message": "User already exists."}), 409

        hashed_password = generate_password_hash(password)
        result = users.insert_one({"email": email, "password": hashed_password})
        
        user = User({"_id": result.inserted_id, "email": email})
        
        login_user(user, remember=True)

        return jsonify({"message": "User created and logged in successfully.", "email": email}), 201

    except PyMongoError as e:
        print(f"MongoDB Error during signup: {e}")
        return jsonify({"message": "Database error during registration."}), 500


# Endpoint di login
@app.route("/api/login", methods=["POST"])
def login():
    if users is None:
        return jsonify({"message": "Database not available."}), 503
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user_data = users.find_one({"email": email})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_data)
            login_user(user, remember=True) 
            return jsonify({"message": "Login successful.", "email": email}), 200
        
        return jsonify({"message": "Invalid email or password."}), 401

    except PyMongoError as e:
        print(f"MongoDB Error during login: {e}")
        return jsonify({"message": "Database error during login."}), 500


# Endpoint di logout
@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful."}), 200

# Endpoint protetto (Richiede il login)
@app.route("/api/dashboard", methods=["GET"])
@login_required
def dashboard():
    return jsonify({"message": f"Welcome back, {current_user.email}!"}), 200

# Nuovo Endpoint: Analisi della Forza della Password
@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze_password():
    data = request.get_json()
    password = data.get("password")

    if not password:
        return jsonify({"message": "Password is required for analysis."}), 400

    results = zxcvbn(password)

    security_score = results['score']

    if security_score <= 1:
        message = "Very weak. Easily guessable."
    elif security_score == 2:
        message = "Weak. Could be cracked quickly."
    elif security_score == 3:
        message = "Fair. Reasonably secure but could be improved."
    elif security_score == 4:
        message = "Strong! Excellent resistance to cracking."
    else:
        message = "Password strength is undetermined."

    return jsonify({
        "score": security_score,
        "feedback": results.get('feedback', {}).get('suggestions', []),
        "warning": results.get('feedback', {}).get('warning'),
        "message": message
    }), 200


# Entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)