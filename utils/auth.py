from flask import request, jsonify
import jwt
from utils.config import TOKEN_KEY

def token_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Token is missing"}), 400

        try:
            data = jwt.decode(token, TOKEN_KEY, algorithms=["HS256"])
            current_user_id = data["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated
