# loader.py
from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo.errors import BulkWriteError
import logging

logger = logging.getLogger(__name__)

class MongoLoader:
    def __init__(self, uri=MONGO_URI, dbname=MONGO_DB, collname=MONGO_COLLECTION):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.collection = self.db[collname]
        self._ensure_indexes()

    def _ensure_indexes(self):
        self.collection.create_index([("ip", ASCENDING)])
        self.collection.create_index([("query_original", ASCENDING)])
        self.collection.create_index([("meta.fetched_at", ASCENDING)])
        self.collection.create_index([("location", "2dsphere")])

    def upsert_one(self, doc):
        query = {"ip": doc.get("ip")} if doc.get("ip") else {"query_original": doc.get("query_original")}
        doc["meta"]["loaded_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
        self.collection.update_one(query, {"$set": doc}, upsert=True)

    def bulk_insert(self, docs):
        if not docs:
            return
        try:
            self.collection.insert_many(docs, ordered=False)
        except BulkWriteError as e:
            logger.warning("Bulk write issue: %s", e.details)
