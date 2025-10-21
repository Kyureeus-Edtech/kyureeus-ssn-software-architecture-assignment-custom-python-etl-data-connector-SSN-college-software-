import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CERTAT_FEED_URL = os.getenv("CERTAT_FEED_URL", "https://threatintel.circl.lu/projects/certat/feeds/json/")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "certat_threatfeed")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract() -> List[Dict[str, Any]]:
    """Fetch JSON threat feed data from CERT.at."""
    logger.info(f"Extracting data from {CERTAT_FEED_URL}")
    response = requests.get(CERTAT_FEED_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data

def sanitize_for_mongo(obj):
    """Recursively sanitize keys for MongoDB (replace '.' and '$')."""
    if isinstance(obj, dict):
        return {k.replace('.', '_').replace('$', '_'): sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    else:
        return obj

def transform(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add metadata and prepare documents for MongoDB."""
    logger.info("Transforming CERT.at threat feed data...")
    docs = []
    for record in raw_data:
        doc = sanitize_for_mongo(record)
        doc["ingested_at"] = datetime.now(timezone.utc).isoformat()
        docs.append(doc)
    return docs

def load_to_mongo(docs: List[Dict[str, Any]]):
    """Insert documents into MongoDB collection."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not set in .env file.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    if docs:
        result = coll.insert_many(docs)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into {MONGO_DB}.{MONGO_COLLECTION}")
    else:
        logger.warning("No documents to insert.")

def run():
    """Main ETL pipeline."""
    try:
        raw = extract()
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("CERT.at ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
