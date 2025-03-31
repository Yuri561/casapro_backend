from flask import Flask
from routes.auth_routes import auth_routes
# from utils.config import SECRET_KEY
from flask import Flask
from routes.auth_routes import auth_routes

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_routes)

@app.route("/")
def home():
    return "Casa Pro Backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
