import logging
from pymongo import MongoClient
from config import MONGO_URL, MONGO_DB, MONGO_COLLECTION

def load_to_mongo(transformed_data):
    """Load transformed Abuse.ch data into MongoDB."""
    logging.info("--------PHASE 3 : Connecting to MongoDB--------")
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    total_inserted = 0
    for source, records in transformed_data.items():
        if not records:
            continue
        logging.info(f"Inserting {len(records)} records from {source}...")
        result = collection.insert_many(records)
        total_inserted += len(result.inserted_ids)

    logging.info(f"Inserted {total_inserted} total documents into MongoDB.")
    client.close()
