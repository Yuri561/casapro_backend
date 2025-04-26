from flask import request, jsonify
import jwt
from utils.config import TOKEN_KEY
from functools import wraps

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if 'access_token' in request.cookies:
            token = request.cookies.get('access_token')
        if not token:
            return jsonify({"error": "Token is missing"}),
        try:
            data = jwt.decode(token, TOKEN_KEY, algorithms=["HS256"])
            # print("[DEBUG] JWT Payload:", data)
            current_user_id = data.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(current_user_id, *args, **kwargs)

    return decorated
