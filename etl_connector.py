import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CISA_KEV_URL = os.getenv("CISA_KEV_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "cisa_kev")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def extract(url: str) -> Any:
    """Fetch JSON data from the given URL."""
    logger.info(f"Extracting data from {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def sanitize_for_mongo(obj):
    """Replace problematic keys for MongoDB."""
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


def transform(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Clean and prepare data for MongoDB."""
    logger.info("Transforming data...")
    vulnerabilities = raw_data.get("vulnerabilities", [])
    docs = []
    for item in vulnerabilities:
        doc = sanitize_for_mongo(item)
        doc["ingested_at"] = datetime.now(timezone.utc).isoformat()
        docs.append(doc)
    return docs


def load_to_mongo(docs: List[Dict[str, Any]]):
    """Insert documents into MongoDB."""
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
        raw = extract(CISA_KEV_URL)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")


if __name__ == "__main__":
    run()
