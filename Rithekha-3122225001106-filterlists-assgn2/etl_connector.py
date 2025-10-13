#!/usr/bin/env python3
"""
ETL connector for FilterLists Directory API
Author: Rithekha (Roll No: 3122225001106)
"""

import os
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ================= Load environment variables =================
load_dotenv()

BASE_URL = os.getenv("FILTERLISTS_BASE_URL", "https://api.filterlists.com")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "filter_lists_assgn")
COLLECTION_PREFIX = os.getenv("COLLECTION_PREFIX", "filterlists")

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "1.5"))

# ================= Logging =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("FilterLists-ETL")

# ================= Helper: URL Builder =================
def build_url(path: str) -> str:
    """Builds full API URL safely without prefix."""
    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"

# ================= HTTP GET with Retry =================
def http_get(url: str) -> Optional[Any]:
    """Performs GET with retry and error handling."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"Accept": "application/json"})
            if resp.status_code == 404:
                logger.warning(f"404 Not Found: {url}")
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Invalid JSON from {url}. Body preview: {resp.text[:200]}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
    logger.error(f"Failed after {MAX_RETRIES} attempts: {url}")
    return None

# ================= MongoDB Helper =================
class MongoStore:
    def __init__(self, uri: str, db_name: str):
        logger.info(f"Connecting to MongoDB at {uri}")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        logger.info(f"Connected to database '{db_name}'")

    def insert_raw(self, collection: str, payload: Any):
        """Insert full API payload into raw collection."""
        doc = {
            "data": payload,
            "ingested_at": datetime.now(timezone.utc)
        }
        res = self.db[collection].insert_one(doc)
        logger.info(f"Inserted raw doc into {collection} (id={res.inserted_id})")

    def bulk_upsert_by_id(self, collection: str, records: List[Dict], id_field: str = "id"):
        """Upsert a batch of records by ID field."""
        if not records:
            return
        ops = []
        for r in records:
            if id_field in r:
                ops.append(UpdateOne(
                    {id_field: r[id_field]},
                    {"$set": {**r, "last_ingested_at": datetime.now(timezone.utc)}},
                    upsert=True
                ))
        if ops:
            res = self.db[collection].bulk_write(ops, ordered=False)
            logger.info(f"Upserted {res.upserted_count + res.modified_count} docs in {collection}")

    def close(self):
        logger.info("Closing MongoDB connection.")
        self.client.close()

# ================= ETL Logic =================
def etl_endpoint(store: MongoStore, path: str, collection_suffix: str):
    """Extract data from API and load into MongoDB."""
    url = build_url(path)
    logger.info(f"Extracting {url}")
    data = http_get(url)
    if not data:
        logger.error(f"No data returned for {path}")
        return None
    coll_name = f"{COLLECTION_PREFIX}_{collection_suffix}_raw"
    store.insert_raw(coll_name, data)
    return data

def etl_lists_and_details(store: MongoStore):
    """Fetch /lists and then /lists/{id} details for each entry."""
    data = etl_endpoint(store, "/lists", "lists")
    if not data or not isinstance(data, list):
        logger.error("No lists data to process details.")
        return

    # Bulk upsert summaries
    store.bulk_upsert_by_id(f"{COLLECTION_PREFIX}_lists_summaries", data)

    # Fetch details for each list
    details_coll = f"{COLLECTION_PREFIX}_lists_details"
    count = 0
    for item in data[:50]:  # Limit for demo
        list_id = item.get("id")
        if not list_id:
            continue
        detail = http_get(build_url(f"/lists/{list_id}"))
        if not detail:
            continue
        store.bulk_upsert_by_id(details_coll, [detail])
        count += 1
        time.sleep(0.3)
    logger.info(f"Fetched detailed info for {count} lists.")

# ================= Main ETL Flow =================
def main():
    logger.info("🚀 Starting FilterLists ETL Pipeline")
    store = MongoStore(MONGODB_URI, DATABASE_NAME)
    try:
        etl_endpoint(store, "/languages", "languages")
        etl_endpoint(store, "/licenses", "licenses")
        etl_lists_and_details(store)
        etl_endpoint(store, "/maintainers", "maintainers")
        etl_endpoint(store, "/software", "software")
        etl_endpoint(store, "/syntaxes", "syntaxes")
        etl_endpoint(store, "/tags", "tags")
        logger.info("✅ ETL completed successfully.")
    except Exception as e:
        logger.exception(f"❌ ETL failed: {e}")
    finally:
        store.close()

if __name__ == "__main__":
    main()
