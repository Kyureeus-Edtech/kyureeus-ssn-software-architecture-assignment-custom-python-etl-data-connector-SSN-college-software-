import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def load_to_mongo(collection_name, data):
    """Insert data into MongoDB collection."""
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[collection_name]

    if not data:
        print(f"⚠️ No data to insert into {collection_name}. Skipping.")
        return

    if isinstance(data, list):
        for d in data:
            d["ingested_at"] = datetime.utcnow()
        collection.insert_many(data)
        print(f"✅ Inserted into {collection_name}: {len(data)} documents")
    else:
        data["ingested_at"] = datetime.utcnow()
        collection.insert_one(data)
        print(f"✅ Inserted into {collection_name}: 1 document")
