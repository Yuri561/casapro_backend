from flask import Flask
from routes.auth_routes import auth_routes
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://casapro-pink.vercel.app",
    "https://casapro-backend-o0k1.onrender.com"
]}}, supports_credentials=True)

app.register_blueprint(auth_routes)

@app.route("/")
def home():
    return "Casa Pro Backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
