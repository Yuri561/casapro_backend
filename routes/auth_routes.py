
from flask import Blueprint, request, jsonify, Flask
from models.user_model import User
from utils.config import users_collection
import logging
from flask_cors import CORS

app = Flask(__name__)
auth_routes = Blueprint("auth_routes", __name__)

# Correct CORS Configuration (Allow Multiple Origins)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173",
                                         "https://casapro-pink.vercel.app",
                                         "https://casapro-backend-o0k1.onrender.com"]}})


# Register Route
@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if User.find_by_username(username, users_collection):
        return jsonify({"error": "Username already exists"}), 400

    user = User(username, password)
    user.save_to_db(users_collection)
    return jsonify({"message": "User registered successfully"}), 201

# Login Route
@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user_data = User.find_by_username(username, users_collection)

    if user_data and User.verify_password(user_data["password"], password):
        return jsonify({"message": "Login successful"}), 200
    else:
        logging.error(f"Error in login route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
