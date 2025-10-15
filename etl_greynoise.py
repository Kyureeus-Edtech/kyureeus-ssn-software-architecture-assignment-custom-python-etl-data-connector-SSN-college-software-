import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GREYNOISE_API_KEY = os.getenv("GREYNOISE_API_KEY")
GREYNOISE_BASE_URL = os.getenv("GREYNOISE_BASE_URL", "https://api.greynoise.io/v3/community/")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "greynoise_data")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {"key": GREYNOISE_API_KEY}

def extract(ip_list: List[str]) -> List[Dict[str, Any]]:
    """Fetch GreyNoise data for a list of IP addresses."""
    results = []
    for ip in ip_list:
        url = f"{GREYNOISE_BASE_URL}{ip}"
        try:
            logger.info(f"Fetching GreyNoise data for IP: {ip}")
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                data["ip"] = ip
                results.append(data)
            else:
                logger.warning(f"Failed for {ip}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {ip}: {e}")
    return results

def sanitize_for_mongo(obj):
    """Replace invalid MongoDB characters in keys."""
    if isinstance(obj, dict):
        return {k.replace('.', '_').replace('$', '_'): sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    else:
        return obj

def transform(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add metadata and sanitize data."""
    logger.info("Transforming GreyNoise data...")
    docs = []
    for record in raw_data:
        doc = sanitize_for_mongo(record)
        doc["ingested_at"] = datetime.now(timezone.utc).isoformat()
        docs.append(doc)
    return docs

def load_to_mongo(docs: List[Dict[str, Any]]):
    """Insert documents into MongoDB."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not set.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    if docs:
        result = coll.insert_many(docs)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into {MONGO_DB}.{MONGO_COLLECTION}")
    else:
        logger.warning("No documents to insert.")

def run():
    ip_list = ["8.8.8.8", "1.1.1.1", "103.15.67.4"]
    try:
        raw = extract(ip_list)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("GreyNoise ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
