import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CISA_KEV_URL = os.getenv("CISA_KEV_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "cisa_kev")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract(url: str) -> Any:
    logger.info(f"Extracting data from {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def sanitize_for_mongo(obj):
    if isinstance(obj, dict):
        return {k.replace(".", "_").replace("$", "_"): sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    return obj

def transform(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    logger.info("Transforming data...")
    vulnerabilities = raw_data.get("vulnerabilities", [])
    docs = []
    for item in vulnerabilities:
        doc = sanitize_for_mongo(item)
        doc["ingested_at"] = datetime.now(timezone.utc).isoformat()
        docs.append(doc)
    return docs

def load_to_mongo(docs: List[Dict[str, Any]]):
    if not docs:
        logger.warning("No documents to insert.")
        return
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    coll.insert_many(docs)
    logger.info(f"Inserted {len(docs)} documents into {MONGO_DB}.{MONGO_COLLECTION}")

def run():
    try:
        raw = extract(CISA_KEV_URL)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL failed: {e}")

if __name__ == "__main__":
    run()