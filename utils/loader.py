import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_many(docs):
    if not docs:
        print("[Warning] No documents to insert.")
        return
    try:
        result = collection.insert_many(docs)
        print(f"[Info] Inserted {len(result.inserted_ids)} documents.")
    except Exception as e:
        print(f"[Error] MongoDB insert failed: {e}")
