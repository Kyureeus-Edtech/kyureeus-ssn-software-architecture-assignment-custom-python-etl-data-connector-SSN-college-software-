# database/mongo_loader.py
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

class MongoLoader:
    """Handles loading data into MongoDB."""

    def __init__(self, uri):
        """Initializes the MongoDB connection."""
        try:
            self.client = MongoClient(uri)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            logging.info("MongoDB connection successful.")
            self.db = self.client['threat_intelligence'] # Database name
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB: {e}")
            self.client = None

    def upsert_data(self, collection_name, data):
        """
        Inserts or updates data in a specified collection.
        'upsert=True' creates a new document if one doesn't exist.
        This prevents creating duplicate records on repeated runs.
        """
        if not self.client or not data:
            logging.warning("No data to load or database not connected.")
            return

        collection = self.db[collection_name]
        count = 0
        for record in data:
            try:
                # Update the record if _id matches, otherwise insert it
                collection.update_one(
                    {'_id': record['_id']},
                    {'$set': record},
                    upsert=True
                )
                count += 1
            except OperationFailure as e:
                logging.error(f"Error upserting data: {e}")
        logging.info(f"Upserted {count} records into '{collection_name}' collection.")

    def close_connection(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")