import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RDAP_BASE_URL = os.getenv("RDAP_BASE_URL", "https://rdap.org/")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "rdap_data")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract(domain_list: List[str]) -> List[Dict[str, Any]]:
    """Fetch RDAP data for multiple domains."""
    results = []
    for domain in domain_list:
        url = f"{RDAP_BASE_URL.rstrip('/')}/domain/{domain}"
        try:
            logger.info(f"Fetching RDAP data for {domain}")
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                results.append({"domain": domain, "data": resp.json()})
            else:
                logger.warning(f"Failed to fetch {domain}: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error fetching {domain}: {e}")
    return results

def sanitize_for_mongo(obj):
    """Recursively replace '.' or '$' in keys."""
    if isinstance(obj, dict):
        return {k.replace('.', '_').replace('$', '_'): sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(i) for i in obj]
    else:
        return obj

def transform(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform and prepare for MongoDB."""
    logger.info("Transforming data...")
    docs = []
    for record in raw_data:
        doc = {
            "domain": record["domain"],
            "rdap_data": sanitize_for_mongo(record["data"]),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }
        docs.append(doc)
    return docs

def load_to_mongo(docs: List[Dict[str, Any]]):
    """Insert into MongoDB."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not set in environment variables.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    if docs:
        result = coll.insert_many(docs)
        logger.info(f"Inserted {len(result.inserted_ids)} RDAP records into {MONGO_DB}.{MONGO_COLLECTION}")
    else:
        logger.warning("No documents to insert.")

def run():
    domains = ["example.com", "google.com", "openai.com"]  # you can change these
    try:
        raw = extract(domains)
        docs = transform(raw)
        load_to_mongo(docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
