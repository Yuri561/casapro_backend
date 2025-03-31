from flask import Flask, request, jsonify
from routes.auth_routes import auth_routes
from models.user_model import User
from utils.config import users_collection
from flask_cors import CORS
import logging

app = Flask(__name__)

# ✅ Correct CORS Configuration - Allow Multiple Origins
CORS(app, resources={
    r"/register": {"origins": ["http://localhost:5173", "https://casapro-pink.vercel.app"]},
    r"/login": {"origins": ["http://localhost:5173", "https://casapro-pink.vercel.app"]},
    r"/*": {"origins": ["http://localhost:5173", "https://casapro-pink.vercel.app"]}
})

# ✅ Register Blueprints
app.register_blueprint(auth_routes)

# ✅ Handle Preflight Requests Properly
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
    app.run(host="0.0.0.0", port=5000, debug=True)
