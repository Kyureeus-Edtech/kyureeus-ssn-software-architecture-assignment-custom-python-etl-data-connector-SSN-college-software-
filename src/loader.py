from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from config import MONGO_URI, DB_NAME

logger = logging.getLogger(__name__)

def get_mongo_client() -> MongoClient | None:
    """
    Establishes a connection to the MongoDB server.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful.")
        return client
    except ConnectionFailure as e:
        logger.critical(f"MongoDB connection failed: {e}")
        return None

def load_data(client: MongoClient, collection_name: str, data: dict, unique_key: str):
    """
    Loads a single document into MongoDB using update_one with upsert.
    This prevents duplicate entries based on the unique_key.
    
    Args:
        client: The MongoClient instance.
        collection_name: The name of the collection (e.g., 'ip_info').
        data: The transformed data dictionary to load.
        unique_key: The field to check for uniqueness (e.g., 'ip_address').
    """
    if not client:
        logger.error("No MongoDB client provided. Cannot load data.")
        return

    try:
        db = client[DB_NAME]
        collection = db[collection_name]
        
        # Use update_one with upsert=True
        # This will update the record if one with the unique_key exists,
        # or insert a new one if it doesn't.
        key_value = data.get(unique_key)
        result = collection.update_one(
            {unique_key: key_value},
            {"$set": data},
            upsert=True
        )
        
        if result.upserted_id:
            logger.info(f"Inserted new record for {unique_key}: {key_value}")
        elif result.matched_count:
            logger.info(f"Updated existing record for {unique_key}: {key_value}")
            
    except OperationFailure as e:
        logger.error(f"Error loading data into MongoDB: {e}")