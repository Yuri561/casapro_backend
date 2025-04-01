from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["casaprodb"]
    inventory_collection = db["inventory"]

    print("✅ Connection Successful!")
    print("Collections:", db.list_collection_names())


except Exception as e:
    print(f"Error: {e}")
