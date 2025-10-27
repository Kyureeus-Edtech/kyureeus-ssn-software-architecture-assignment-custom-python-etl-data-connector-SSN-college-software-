import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "hibp_etl")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def insert_data(collection, data):
    if not data:
        print(f"⚠️ Skipping load: No data for {collection}")
        return

    # If data is a list of non-dict items, wrap them
    if isinstance(data, list):
        if not all(isinstance(d, dict) for d in data):
            data = [{"value": d} for d in data]
    elif isinstance(data, dict):
        data = [data]
    else:
        # Single value (string, int, etc)
        data = [{"value": data}]

    db[collection].insert_many(data)
    print(f"✅ Inserted into {collection}, count={len(data)}")
