#!/usr/bin/env python3
"""
CyberGreen ETL Connector
Extracts CSV data from CyberGreen, transforms it, and loads into MongoDB.
"""

import os
import csv
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pymongo import MongoClient, errors as pymongo_errors

# --- Load environment variables ---
load_dotenv()

# Pull all config from .env only (no defaults here)
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
CYBERGREEN_BASE = os.getenv("CYBERGREEN_BASE")
CYBERGREEN_ENDPOINT = os.getenv("CYBERGREEN_ENDPOINT")
CYBERGREEN_BULK_URL = os.getenv("CYBERGREEN_BULK_URL")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
BATCH_SIZE = int(os.getenv("BATCH_SIZE"))

# --- Mandatory env check ---
required_vars = [
    "MONGODB_URI", "MONGODB_DB", "CYBERGREEN_BASE",
    "CYBERGREEN_ENDPOINT", "CYBERGREEN_BULK_URL",
    "OUTPUT_FILE", "BATCH_SIZE"
]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise SystemExit(f"ERROR: Missing required environment variables in .env: {', '.join(missing)}")

# --- MongoDB client setup ---
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
collection = db["data_collection"]
metadata_collection = db["connector_metadata"]

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cybergreen_etl")

# --- HTTP Session with retries ---
session = requests.Session()
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1,
    allowed_methods=["GET", "HEAD", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def normalize_key(k: str) -> str:
    """Normalize header keys to lowercase with underscores."""
    return k.strip().lower().replace(" ", "_") if k else k

def transform_row(row: dict) -> dict:
    """Normalize keys, cast numeric fields, and add ingestion timestamp."""
    normalized = {}
    for k, v in row.items():
        if k is None:
            continue
        key = normalize_key(k)
        val = v.strip() if isinstance(v, str) else v
        normalized[key] = val

    # Cast numeric fields
    for num_field in ("count", "count_amplified", "asn"):
        if num_field in normalized:
            try:
                normalized[num_field] = int(normalized[num_field])
            except (ValueError, TypeError):
                normalized[num_field] = None

    # Normalize date
    if "date" in normalized:
        try:
            normalized["date"] = datetime.fromisoformat(normalized["date"]).date().isoformat()
        except Exception:
            pass

    normalized["ingestion_timestamp"] = datetime.utcnow().isoformat()
    return normalized

def stream_csv(url: str, limit=None):
    """Stream CSV from a URL and yield transformed rows."""
    logger.info("Fetching CSV from %s", url)
    with session.get(url, stream=True, timeout=(10, 120)) as r:
        r.raise_for_status()
        lines = (line.decode("utf-8") if isinstance(line, bytes) else line for line in r.iter_lines())
        reader = csv.DictReader(lines)
        count = 0
        for row in reader:
            yield transform_row(row)
            count += 1
            if limit and count >= limit:
                break

def load_to_mongo(rows):
    """Insert rows into MongoDB in batches."""
    batch = []
    total_inserted = 0
    for row in rows:
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            try:
                collection.insert_many(batch, ordered=False)
                total_inserted += len(batch)
                logger.info("Inserted %d rows so far...", total_inserted)
            except pymongo_errors.BulkWriteError as bwe:
                logger.warning("Bulk write error: %s", bwe.details)
            batch.clear()

    if batch:
        try:
            collection.insert_many(batch, ordered=False)
            total_inserted += len(batch)
        except pymongo_errors.BulkWriteError as bwe:
            logger.warning("Bulk write error on final batch: %s", bwe.details)

    # Save metadata
    metadata_collection.update_one(
        {"connector": "cybergreen"},
        {"$set": {
            "last_run": datetime.utcnow().isoformat(),
            "rows_ingested": total_inserted
        }},
        upsert=True
    )
    logger.info("ETL completed. Total rows inserted: %d", total_inserted)

def run_etl(limit=None):
    """Main ETL runner."""
    rows = stream_csv(CYBERGREEN_BULK_URL, limit)
    load_to_mongo(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["bulk", "api"], default="bulk",
                        help="bulk: use CYBERGREEN_BULK_URL, api: use base+endpoint")
    parser.add_argument("--limit", type=int, default=None, help="Limit rows for testing")
    args = parser.parse_args()

    if args.mode == "bulk":
        rows = stream_csv(CYBERGREEN_BULK_URL, args.limit)
    else:
        url = f"{CYBERGREEN_BASE.rstrip('/')}/{CYBERGREEN_ENDPOINT.lstrip('/')}"
        rows = stream_csv(url, args.limit)

    load_to_mongo(rows)

