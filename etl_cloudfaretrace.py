import os
import logging
from datetime import datetime, timezone
from typing import Dict

import requests
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLOUDFLARE_TRACE_URL = os.getenv("CLOUDFLARE_TRACE_URL", "https://www.cloudflare.com/cdn-cgi/trace")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "cloudflare_trace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract_trace_data() -> Dict[str, str]:
    """Fetch raw Cloudflare trace data and parse key-value pairs."""
    logger.info(f"Fetching Cloudflare trace data from {CLOUDFLARE_TRACE_URL}")
    resp = requests.get(CLOUDFLARE_TRACE_URL, timeout=20)
    resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    trace_dict = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            trace_dict[key.strip()] = value.strip()
    return trace_dict

def transform(trace_dict: Dict[str, str]) -> Dict[str, str]:
    """Add ingestion timestamp and sanitize data."""
    logger.info("Transforming trace data...")
    trace_dict["ingested_at"] = datetime.now(timezone.utc).isoformat()
    return trace_dict

def load_to_mongo(trace_data: Dict[str, str]):
    """Insert trace data into MongoDB."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not set.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION]
    result = coll.insert_one(trace_data)
    logger.info(f"Inserted Cloudflare trace document with ID: {result.inserted_id}")

def run():
    try:
        data = extract_trace_data()
        doc = transform(data)
        load_to_mongo(doc)
        logger.info("Cloudflare Trace ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run()
