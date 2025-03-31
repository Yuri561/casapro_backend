from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["casaprodb"]

    # Get a list of collections to test the connection
    collections = db.list_collection_names()
    print("✅ Connection Successful!")
    print("Collections:", collections)

except Exception as e:
    print(f"❌ Error: {e}")
