from pymongo import MongoClient
import os

# MongoDB URI (Replace with the correct connection string)
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://yuri561:Houbenove561$@homebase.5zmgu59.mongodb.net/casaprodb?retryWrites=true&w=majority"
)

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Correct database name
db = client["casaprodb"]

# Collections
users_collection = db["users"]
