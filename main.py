from flask import Flask
from routes.auth_routes import auth_routes
# from utils.config import SECRET_KEY

app = Flask(__name__)
# app.config["SECRET_KEY"] = SECRET_KEY

# Register blueprints
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
