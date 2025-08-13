import os
import logging
from datetime import datetime, timezone
from typing import Any, List, Dict

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

THREATFOX_JSON_URL = os.getenv("THREATFOX_JSON_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "threatfox_recent")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract(url: str) -> Any:
    """Fetch JSON data from the ThreatFox API."""
    logger.info(f"Extracting data from {url}")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()

def sanitize_for_mongo(obj):
    """Recursively replace keys containing '.' or starting with '$'."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new_key = k.replace(".", "_").replace("$", "_")
            new[new_key] = sanitize_for_mongo(v)
        return new
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    else:
        return obj

def transform(raw_data: dict) -> List[Dict[str, Any]]:
    """Transform raw JSON into Mongo-ready documents."""
    logger.info("Transforming data...")
    docs = []
    for _id, records in raw_data.items():
        if isinstance(records, list):
            for record in records:
                doc = sanitize_for_mongo(record)
                doc["threatfox_id"] = _id  # keep the original key
                doc["ingested_at"] = datetime.now(timezone.utc).isoformat()
                docs.append(doc)
    return docs


def load_to_mongo(docs: List[Dict[str, Any]]):
    """Load documents into MongoDB."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not set in environment variables.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    if docs:
        result = coll.insert_many(docs)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into {MONGO_DB}.{MONGO_COLLECTION}")
    else:
        logger.warning("No documents to insert.")

def run():
    try:
        raw = extract(THREATFOX_JSON_URL)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
