# load.py
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

def insert_to_mongo(collection_name, data):
    """Insert data into MongoDB collection."""
    if not data:
        print("No data to insert.")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]

    collection.insert_many(data)
    print(f"Inserted {len(data)} records into '{collection_name}' collection.")
