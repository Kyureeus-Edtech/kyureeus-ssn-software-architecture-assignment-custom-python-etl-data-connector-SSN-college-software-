import os
import sys
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()  
MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGO_DB", "ssn_etl")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "threatfox_raw")
THREATFOX_AUTH_KEY = os.getenv("THREATFOX_AUTH_KEY", "a5f2b65f597d8aeca7558550edcee95d2d21797818a452d5")
API_URL = "https://threatfox-api.abuse.ch/api/v1/"

if not MONGODB_URI:
    print("MONGODB_URI not set in environment. Exiting.")
    sys.exit(1)


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


client = MongoClient(MONGODB_URI)
db = client[MONGO_DB]
collection = db[COLLECTION_NAME]

collection.create_index([("doc_hash", ASCENDING)], unique=True)


def fetch_json_with_retries(url: str, data: dict, headers: dict, tries: int = 3, backoff: int = 2) -> Any:
    for attempt in range(1, tries + 1):
        try:
            r = requests.post(url, headers=headers, data=data, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logging.warning("Fetch attempt %d failed: %s", attempt, e)
            if attempt < tries:
                time.sleep(backoff ** attempt)
            else:
                raise

def clean_item(item: Any) -> Any:
    if isinstance(item, dict):
        return {k: clean_item(v) for k, v in item.items() if v is not None}
    if isinstance(item, list):
        return [clean_item(x) for x in item]
    return item

def compute_hash(doc: Dict[str, Any]) -> str:
    s = json.dumps(doc, sort_keys=True, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def upsert_documents(docs: List[Dict[str, Any]]) -> int:
    inserted = 0
    for doc in docs:
        cleaned = clean_item(doc)
        if not isinstance(cleaned, dict):
            # wrap non-dict items in a dict
            cleaned = {"value": cleaned}
        # Use timezone-aware UTC timestamp
        cleaned["ingested_at"] = datetime.now(timezone.utc).isoformat()
        h = compute_hash(cleaned)
        cleaned["doc_hash"] = h
        try:
            res = collection.update_one({"doc_hash": h}, {"$set": cleaned}, upsert=True)
            if getattr(res, "upserted_id", None):
                inserted += 1
        except Exception as e:
            logging.exception("Error writing to MongoDB for doc_hash=%s: %s", h, e)
    return inserted

def main():
    logging.info("Starting ETL for ThreatFox API")
    
    headers = {"Auth-Key": THREATFOX_AUTH_KEY}
    post_data = {"query": "get_iocs", "days": 7}  # past 7 days
    
    data = fetch_json_with_retries(API_URL, data=post_data, headers=headers, tries=4, backoff=2)

    # Normalize response
    docs = data.get("data", []) if isinstance(data, dict) else []

    logging.info("Fetched %d items; beginning upsert...", len(docs))
    inserted = upsert_documents(docs)
    logging.info("ETL finished: %d new documents inserted.", inserted)

if __name__ == "__main__":
    main()
