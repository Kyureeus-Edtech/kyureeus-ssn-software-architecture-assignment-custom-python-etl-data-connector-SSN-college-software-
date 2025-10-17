from pymongo import MongoClient
from config import settings

def get_mongo_collection():
    """Connect to MongoDB and return the target collection."""
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    return db[settings.MONGO_COLLECTION]
