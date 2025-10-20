"""
etl_connector.py
Custom ETL connector using Cloudflare Trace API.
Assignment: Software Architecture – Custom Python ETL Data Connector
Student: Anandharaj D (3122225001009, CSE A)

This script extracts diagnostic trace data from three Cloudflare endpoints,
transforms the plain-text key=value format into structured JSON, and loads it
into a MongoDB collection for auditing and analysis.
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List

import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# ---------------- Environment Setup ----------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "cloudflare_trace_raw")

# Multiple Cloudflare Trace endpoints
TRACE_ENDPOINTS = [
    "https://www.cloudflare.com/cdn-cgi/trace",
    "https://1.1.1.1/cdn-cgi/trace",
    "https://cloudflare-dns.com/cdn-cgi/trace"
]

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cloudflare-trace-etl")


# ---------------- ETL Functions ----------------
def extract_trace(url: str) -> str:
    """Extract raw data from the Cloudflare Trace endpoint."""
    try:
        logger.info(f"Extracting from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return ""


def transform_trace(raw_text: str, source_url: str) -> Dict:
    """Transform key=value pairs into a structured dictionary."""
    if not raw_text:
        return {}

    data = {}
    for line in raw_text.strip().split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()

    # Add ingestion metadata
    data["_source"] = source_url
    data["_ingested_at"] = datetime.utcnow().isoformat()
    data["_timestamp"] = time.time()

    return data


def load_to_mongo(records: List[Dict]):
    """Insert transformed records into MongoDB."""
    if not records:
        logger.warning("No records to insert.")
        return

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        coll = db[COLLECTION_NAME]

        result = coll.insert_many(records)
        logger.info(f"Inserted {len(result.inserted_ids)} records into {COLLECTION_NAME}.")
    except Exception as e:
        logger.error(f"MongoDB insertion error: {e}")


def run_etl():
    """Main ETL pipeline runner."""
    all_records = []

    for url in TRACE_ENDPOINTS:
        raw = extract_trace(url)
        record = transform_trace(raw, url)
        if record:
            all_records.append(record)

        # short delay to be polite
        time.sleep(1)

    load_to_mongo(all_records)
    logger.info("✅ ETL pipeline completed successfully.")


# ---------------- Entry Point ----------------
if __name__ == "__main__":
    run_etl()
