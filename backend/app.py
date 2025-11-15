import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

app = Flask(__name__)
CORS(app)

# ----------------------------
# MongoDB Connection
# ----------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["myapp"]
users = db["users"]

# ----------------------------
# Email Validation Regex
# ----------------------------
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# ----------------------------
# Password Strength Check
# ----------------------------
def valid_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

# ----------------------------
# Signup API Route
# ----------------------------
@app.post("/api/signup", strict_slashes=False)
def signup():
    print("Signup route hit")
    data = request.get_json()
    print("Received data:", data)

    if not data or "email" not in data or "password" not in data:
        return jsonify({"status": "error", "message": "Email and password are required"}), 422

    email = data["email"].strip().lower()
    password = data["password"]

    # Validate email format
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400

    # Validate password strength
    if not valid_password(password):
        return jsonify({"status": "error", "message": "Password does not meet security requirements"}), 400

    # Check if user already exists
    if users.find_one({"email": email}):
        return jsonify({"status": "error", "message": "Email already registered"}), 400

    # Hash the password
    hashed_pw = generate_password_hash(password)

    # Insert into MongoDB
    new_user = {
        "email": email,
        "password": hashed_pw
    }

    result = users.insert_one(new_user)

    return jsonify({
        "status": "success",
        "message": "Account created successfully",
        "userId": str(result.inserted_id)
    }), 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)