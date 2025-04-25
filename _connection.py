from pymongo import MongoClient
from dotenv import load_dotenv
import os
import secrets

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

from bson import ObjectId
from utils.config import inventory_collection

old_object_id = ObjectId("661fda7811cb8949c0233d99")

result = inventory_collection.update_many(
    {"user_id": old_object_id},
    {"$set": {"user_id": "yuri"}}
)

print(f"Modified {result.modified_count} documents.")