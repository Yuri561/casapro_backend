from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB URI
MONGO_URI = os.getenv("MONGODB_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["casaprodb"]

# Collections
users_collection = db["users"]
inventory_collection = db["inventory"]
inventory_history_collection = db["inventory_history"]
budget_collection = db["budget_goal"]

# JWT secret
TOKEN_KEY = os.getenv("TOKEN_KEY")
