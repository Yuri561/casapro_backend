from flask import Flask
from routes.auth_routes import auth_routes
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Correct CORS Configuration (Allow Multiple Origins)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173",
                                         "https://casapro-pink.vercel.app",
                                         "https://casapro-backend-o0k1.onrender.com"]}})
# Register Blueprints
app.register_blueprint(auth_routes)

@app.route("/")
def home():
    return "Casa Pro Backend is running!"

if __name__ == "__main__":
    print("db is currently online")
    app.run(host="0.0.0.0", port=5000)
