import os
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

if not all([MONGO_URI, DB_NAME, COLLECTION_NAME]):
    raise RuntimeError("Missing one or more MongoDB environment variables.")

def get_db_col():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION_NAME]
    col.create_index("ip", unique=True)
    return col

def save_results(col, docs, batch_size=100):
    if not docs:
        return 0
    ops = [
        UpdateOne(
            {"ip": doc["ip"]},
            {"$set": doc},
            upsert=True
        )
        for doc in docs
    ]
    result = col.bulk_write(ops, ordered=False)
    return result.upserted_count + result.modified_count