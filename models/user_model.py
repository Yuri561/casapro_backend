from werkzeug.security import generate_password_hash, check_password_hash

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
