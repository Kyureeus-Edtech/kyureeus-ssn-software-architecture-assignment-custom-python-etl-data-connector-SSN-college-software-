import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import pymongo
from dotenv import load_dotenv

# Load env variables
load_dotenv()

NETWORKCALC_BASE_URL = os.getenv("NETWORKCALC_BASE_URL", "https://networkcalc.com/api/ip/")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "networkcalc_data")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract(ip_list: List[str]) -> List[Dict[str, Any]]:
    """Extract subnet details for multiple IP addresses."""
    data = []
    for ip in ip_list:
        url = f"{NETWORKCALC_BASE_URL}{ip}/24"  # CIDR /24 for simplicity
        try:
            logger.info(f"Fetching data for {ip}")
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                info = resp.json()
                data.append({"ip": ip, "data": info})
            else:
                logger.warning(f"Failed for {ip}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {ip}: {e}")
    return data

def sanitize_for_mongo(obj):
    """Recursively replace '.' or '$' in keys."""
    if isinstance(obj, dict):
        return {k.replace('.', '_').replace('$', '_'): sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    else:
        return obj

def transform(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform and prepare data for MongoDB."""
    logger.info("Transforming data...")
    docs = []
    for record in raw_data:
        doc = {
            "ip": record["ip"],
            "networkcalc_data": sanitize_for_mongo(record["data"]),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }
        docs.append(doc)
    return docs

def load_to_mongo(docs: List[Dict[str, Any]]):
    """Insert data into MongoDB."""
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
    ip_list = ["192.168.1.10", "10.0.0.5", "8.8.8.8"]
    try:
        raw = extract(ip_list)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
