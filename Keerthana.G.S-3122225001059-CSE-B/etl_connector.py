#!/usr/bin/env python3
import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load config from env
OTX_API_KEY = os.getenv("OTX_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://otx.alienvault.com/api/v1/pulses/subscribed")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "api_testing")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "otx_pulses_raw")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
MAX_PAGES = 5

# Validate API key
if not OTX_API_KEY:
    logging.error("OTX_API_KEY not found in environment. Please set it in .env")
    sys.exit(1)

HEADERS = {"X-OTX-API-KEY": OTX_API_KEY}


def fetch_with_retries(url, headers, timeout, retries=3, backoff_factor=2):
    """Fetch JSON data with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = backoff_factor * (2 ** attempt)
                logging.warning(f"Rate limit hit (429). Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                logging.error(f"HTTP {resp.status_code}: {resp.text[:200]}")
                break
        except requests.RequestException as e:
            wait = backoff_factor * (2 ** attempt)
            logging.warning(f"Network error: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    logging.error(f"Failed to fetch after {retries} attempts.")
    return None


def extract_pulses():
    """Generator that yields pulse results page by page."""
    url = BASE_URL
    page_count = 0

    while url and page_count < MAX_PAGES:
        logging.info(f"Fetching page {page_count + 1} from {url}")
        data = fetch_with_retries(url, HEADERS, REQUEST_TIMEOUT)

        if not isinstance(data, dict):
            logging.error("Invalid response structure. Stopping ETL.")
            break

        results = data.get("results")
        if not isinstance(results, list):
            logging.error("'results' is missing or not a list. Stopping ETL.")
            break

        yield results
        url = data.get("next")
        page_count += 1

    logging.info(f"Stopped after {page_count} pages.")


def transform_pulse(pulse):
    """Transform raw pulse data for Mongo storage."""
    return {
        "_id": pulse.get("id"),
        "name": pulse.get("name"),
        "description": pulse.get("description"),
        "author_name": pulse.get("author_name"),
        "created": pulse.get("created"),
        "modified": pulse.get("modified"),
        "tags": pulse.get("tags", []),
        "references": pulse.get("references", [])
    }


def load_pulses(pulses, collection):
    """Upsert transformed pulses into MongoDB."""
    upserts = 0
    for pulse in pulses:
        transformed = transform_pulse(pulse)
        if not transformed["_id"]:
            logging.warning("Skipping pulse with no ID.")
            continue
        result = collection.update_one(
            {"_id": transformed["_id"]},
            {"$set": transformed},
            upsert=True
        )
        if result.upserted_id is not None:
            upserts += 1
    return upserts


def run_etl():
    client = MongoClient(MONGO_URI)
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        total_upserts = 0
        for pulses in extract_pulses():
            upserts = load_pulses(pulses, collection)
            total_upserts += upserts
            logging.info(f"Upserted {upserts} pulses this page.")

        logging.info(f"ETL finished. Total new pulses inserted: {total_upserts}")
    finally:
        client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    run_etl()
