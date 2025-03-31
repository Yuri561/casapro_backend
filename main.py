from flask import Flask, request, jsonify
from routes.auth_routes import auth_routes
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env
load_dotenv()

# ✅ Get MongoDB URI from .env
MONGO_URI = os.getenv("MONGODB_URI")

# ✅ Establish MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client["casaprodb"]
    users_collection = db["users"]

    # Print collections for confirmation
    collections = db.list_collection_names()
    print("✅ Connection Successful!")
    print("Collections:", collections)

except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    exit(1)  # Exit the application if MongoDB fails

# Initialize Flask app
app = Flask(__name__)

# Correct CORS Configuration (Allow Multiple Origins)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173",
                                         "https://casapro-pink.vercel.app",
                                         "https://casapro-backend-o0k1.onrender.com"]}})

# Register Blueprints
app.register_blueprint(auth_routes)

# Handle Preflight CORS Requests
@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
        return response

@app.route("/")
def home():
    return "Casa Pro Backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
