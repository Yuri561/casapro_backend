from functools import wraps
from flask import request, jsonify
import jwt
from utils.config import TOKEN_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing!"}), 400

        try:
            decoded = jwt.decode(token, TOKEN_KEY, algorithms=["HS256"])
            current_user_id = decoded['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated
