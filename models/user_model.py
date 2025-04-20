from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from utils.config import TOKEN_KEY


class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = self.generate_password(password)
        self.email = email

    # Save user to MongoDB
    def save_to_db(self, users_collection):
        user_data = {"username": self.username, "password": self.password_hash, "email": self.email}
        users_collection.insert_one(user_data)

    # Generate hashed password
    @staticmethod
    def generate_password(password):
        return generate_password_hash(password)

    # Verify hashed password
    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)

    # Find user by username
    @staticmethod
    def find_by_username(username, users_collection):
        return users_collection.find_one({"username": username})


    #jwt token being created
    @staticmethod
    def encode_auth_token(user_id):
        try:
            payload = {
                'exp': datetime.now(timezone.utc) + timedelta(days=1),
                'iat': datetime.now(timezone.utc),
                'sub': str(user_id)
            }
            token = jwt.encode(payload, TOKEN_KEY, algorithm='HS256')



        except Exception as e:
            print("Token generation error:", str(e))
            return None

        return token