#!/usr/bin/env python3
"""
ETL connector for FilterLists API
- Extracts data from endpoints
- Transforms by adding ingestion metadata
- Loads documents into MongoDB collections (one collection per endpoint)
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# ---- Load env ----
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.filterlists.com")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "filterlists_db")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))  # seconds

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("filterlists-etl")

# ---- HTTP session with retry ----
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "HEAD"],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ---- MongoDB client ----
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # quick server check
    mongo_client.server_info()
    db = mongo_client[DB_NAME]
except errors.ServerSelectionTimeoutError as e:
    logger.error("Could not connect to MongoDB: %s", e)
    raise SystemExit(1)

# ---- Endpoints list ----
ENDPOINTS = [
    "/languages",
    "/licenses",
    "/maintainers",
    "/software",
    "/syntaxes",
    "/tags",
]

# ---- Utilities ----
import time
import logging
import requests

REQUEST_TIMEOUT = 10  # seconds

def safe_get_json(url, params=None):
    for attempt in range(3):
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout while fetching {url} (attempt {attempt+1}/3)")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error fetching {url}: {e}")
        time.sleep(2)
    logging.error(f"Failed to fetch {url} after 3 attempts — skipping.")
    return {}


# ---- ETL steps ----
def extract(endpoint: str) -> List[dict]:
    """Extract data from the API endpoint. Handles /lists/{id} detail fetch."""
    url = BASE_URL.rstrip("/") + endpoint
    logger.info("Extracting %s", endpoint)

    data = safe_get_json(url)
    if data is None:
        logger.warning("No data returned from %s", endpoint)
        return []

    # Special handling: if endpoint == "/lists", also fetch details for each list
    if endpoint == "/lists":
        lists = data if isinstance(data, list) else []
        detailed = []
        for item in lists:
            # The API returns objects with 'id' (integer) in lists
            list_id = item.get("id")
            if list_id is None:
                detailed.append(item)
                continue
            detail_url = f"{BASE_URL.rstrip('/')}/lists/{list_id}"
            logger.debug("Fetching detail for list id=%s", list_id)
            detail = safe_get_json(detail_url)
            # if detail is None, fallback to original item
            detailed.append(detail if detail is not None else item)
            # small delay to avoid overwhelming server
            time.sleep(0.1)
        return detailed
    else:
        # For other endpoints, return list or wrap single objects in list
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Some endpoints may return object with a top-level key (rare); try to extract reasonable list
            # If it has 'data' key, use it; otherwise wrap dict
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            return [data]
        return []

def transform(records: List[dict], endpoint: str) -> List[dict]:
    """Enhanced transform: cleans, flattens, and adds metadata."""
    logger.info("Transforming %d records from %s", len(records), endpoint)
    transformed = []
    now = datetime.now().astimezone()

    def clean_record(d: dict) -> dict:
        return {k: v for k, v in d.items() if v not in [None, "", [], {}, "null"]}

    for i, rec in enumerate(records, start=1):
        rec = clean_record(rec)
        doc = {
            "_source_id": rec.get("id") or rec.get("_id"),
            "record_index": i,
            "endpoint": endpoint.strip("/"),
            "ingestion_time": now,
            "schema_version": 1.0,
            "source": {
                "api_base": BASE_URL,
                "endpoint": endpoint,
                "retrieved_at": now.isoformat(),
            },
            "data": rec,  # original record
        }

        # Endpoint-specific flattening for easier queries
        if endpoint == "/languages":
            doc["name"] = rec.get("name")
            doc["iso_code"] = rec.get("iso6391")
        elif endpoint == "/licenses":
            doc["license_name"] = rec.get("name")
            doc["license_url"] = rec.get("url")
        elif endpoint == "/maintainers":
            doc["maintainer_name"] = rec.get("name")
            doc["maintainer_url"] = rec.get("url")
        elif endpoint == "/software":
            doc["software_name"] = rec.get("name")
            doc["software_home"] = rec.get("homeUrl")
        elif endpoint == "/syntaxes":
            doc["syntax_name"] = rec.get("name")
        elif endpoint == "/tags":
            doc["tag_name"] = rec.get("name")

        transformed.append(doc)

    return transformed


def load(docs: List[dict], collection_name: str) -> None:
    """Load transformed docs into MongoDB collection."""
    if not docs:
        logger.info("No documents to load into %s", collection_name)
        return
    try:
        col = db[collection_name]
        result = col.insert_many(docs)
        logger.info("Inserted %d documents into %s (sample inserted id: %s)", len(result.inserted_ids), collection_name, result.inserted_ids[0])
    except Exception as e:
        logger.error("Failed to insert into %s: %s", collection_name, e)

def endpoint_to_collection(endpoint: str) -> str:
    # e.g. "/languages" -> "languages_raw"
    name = endpoint.strip("/").replace("/", "_")
    if name == "":
        name = "root"
    return f"{name}_raw"

def run_etl(selected_endpoints: Optional[List[str]] = None) -> None:
    """Main ETL runner. If selected_endpoints provided, process only those."""
    endpoints = selected_endpoints if selected_endpoints else ENDPOINTS
    for ep in endpoints:
        try:
            raw = extract(ep)
            transformed = transform(raw, ep)
            collection = endpoint_to_collection(ep)
            load(transformed, collection)
            # small sleep to be polite
            time.sleep(0.2)
        except Exception as e:
            logger.exception("Unhandled error processing %s: %s", ep, e)

# ---- CLI-ish entrypoint ----
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FilterLists API ETL connector")
    parser.add_argument("--endpoints", nargs="+", help="List of endpoints to fetch (e.g. /lists /languages). If omitted, all endpoints are processed.")
    args = parser.parse_args()

    if args.endpoints:
        # validate provided endpoints (must start with '/')
        normalized = [ep if ep.startswith("/") else f"/{ep}" for ep in args.endpoints]
        run_etl(normalized)
    else:
        run_etl()
