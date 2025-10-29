import os
from pymongo import MongoClient
from dotenv import load_dotenv

class TorExitNodeLoader:
    """Loads transformed data into a MongoDB collection."""

    def __init__(self):
        load_dotenv()  # Load environment variables
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME", "tor_data")
        self.collection_name = os.getenv("MONGO_COLLECTION", "exit_nodes")

        if not self.mongo_uri:
            raise ValueError("MONGO_URI not set in environment variables.")

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def save_to_mongodb(self, data):
        """Insert the transformed data into MongoDB."""
        if not data:
            return 0
        result = self.collection.insert_many(data)
        return len(result.inserted_ids)
