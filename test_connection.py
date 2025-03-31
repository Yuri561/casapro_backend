from pymongo import MongoClient

MONGO_URI = "mongodb+srv://yuri561:Houbenove561$@homebase.5zmgu59.mongodb.net/casaprodb?retryWrites=true&w=majority"

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
