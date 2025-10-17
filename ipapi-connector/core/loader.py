from pymongo.errors import PyMongoError
from utils.logger import logger

def load_to_mongo(collection, records):
    if not records:
        logger.warning("No records to insert.")
        return

    try:
        result = collection.insert_many(records)
        logger.info(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
    except PyMongoError as e:
        logger.error(f"MongoDB insertion failed: {e}")
