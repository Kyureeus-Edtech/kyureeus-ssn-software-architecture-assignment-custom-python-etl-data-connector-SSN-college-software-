#!/usr/bin/env python3
"""
Spamhaus DROP List ETL Connector
- Extracts the DROP (Don't Route Or Peer) list from Spamhaus
- Transforms lines into JSON records
- Loads/upserts into MongoDB
Secure settings are pulled from .env

Author: <Your Name>
Roll No.: <Your Roll Number>
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

# ---------- Logging Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("spamhaus_drop_etl")


def load_settings() -> Dict[str, str]:
    """Load environment variables from .env and validate required keys."""
    load_dotenv()

    required_keys = [
        "BASE_URL",
        "ENDPOINT",
        "MONGO_URI",
        "DB_NAME",
        "COLLECTION_NAME",
        "CONNECTOR_NAME",
        # Optional:
        # "REQUEST_TIMEOUT",
        # "USER_AGENT",
        # "VERIFY_TLS"
    ]

    cfg = {}
    missing = []
    for k in required_keys:
        v = os.getenv(k)
        if not v:
            missing.append(k)
        else:
            cfg[k] = v

    # Optional configs with defaults
    cfg["REQUEST_TIMEOUT"] = float(os.getenv("REQUEST_TIMEOUT", "20"))
    cfg["USER_AGENT"] = os.getenv("USER_AGENT", f"{cfg.get('CONNECTOR_NAME','SpamhausConnector')}/1.0 (+student-etl)")
    cfg["VERIFY_TLS"] = os.getenv("VERIFY_TLS", "true").lower() not in ("0", "false", "no")
    cfg["BATCH_SIZE"] = int(os.getenv("BATCH_SIZE", "500"))
    cfg["METADATA_COLLECTION"] = os.getenv("METADATA_COLLECTION", f"{cfg['CONNECTOR_NAME'].lower().replace(' ', '_')}_meta")

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return cfg


def get_metadata_col(client: MongoClient, db_name: str, meta_col: str):
    return client[db_name][meta_col]


def get_saved_fetch_headers(meta_col, key: str) -> Dict[str, str]:
    """Return conditional request headers based on last ETag / Last-Modified we saw."""
    doc = meta_col.find_one({"_id": key}) or {}
    headers = {}
    etag = doc.get("etag")
    last_modified = doc.get("last_modified")
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    return headers


def save_fetch_headers(meta_col, key: str, response: requests.Response) -> None:
    """Persist ETag / Last-Modified for incremental pulls."""
    etag = response.headers.get("ETag")
    last_modified = response.headers.get("Last-Modified")
    meta_col.update_one(
        {"_id": key},
        {"$set": {"etag": etag, "last_modified": last_modified, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def fetch_drop_text(url: str, headers: Dict[str, str], timeout: float, verify_tls: bool) -> Optional[str]:
    """GET the DROP list; return text or None if not modified."""
    base_headers = {
        "Accept": "text/plain",
        "User-Agent": headers.pop("User-Agent", "SpamhausConnector/1.0"),
    }
    base_headers.update(headers)

    resp = requests.get(url, headers=base_headers, timeout=timeout, verify=verify_tls)
    if resp.status_code == 304:
        logger.info("No changes since last fetch (HTTP 304 Not Modified).")
        return None
    resp.raise_for_status()
    return resp.text, resp


def parse_drop_lines(text: str, connector_name: str, source_url: str) -> List[Dict]:
    """
    Parse DROP lines.
    Typical line: '1.2.3.0/24 ; some reason' or comments beginning with ';' or '#'
    """
    records = []
    fetched_at = datetime.now(timezone.utc)
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        cidr, note = (line.split(";", 1) + [""])[:2]
        cidr = cidr.strip()
        note = note.strip()
        records.append(
            {
                "cidr": cidr,
                "note": note if note else None,
                "source": source_url,
                "connector": connector_name,
                "fetched_at": fetched_at,
            }
        )
    return records


def upsert_records(col, records: List[Dict], batch_size: int = 500) -> int:
    """
    Upsert by CIDR. Keep latest fetched_at and note.
    """
    if not records:
        return 0

    total = 0
    for i in range(0, len(records), batch_size):
        chunk = records[i : i + batch_size]
        ops = []
        for r in chunk:
            ops.append(
                UpdateOne(
                    {"cidr": r["cidr"]},
                    {"$set": {
                        "note": r["note"],
                        "source": r["source"],
                        "connector": r["connector"],
                        "fetched_at": r["fetched_at"],
                    }},
                    upsert=True,
                )
            )
        res = col.bulk_write(ops, ordered=False)
        total += res.upserted_count + res.modified_count
    return total


def main() -> int:
    cfg = load_settings()
    url = cfg["BASE_URL"].rstrip("/") + "/" + cfg["ENDPOINT"].lstrip("/")
    logger.info("Starting ETL for %s", cfg["CONNECTOR_NAME"])
    logger.info("Fetching from: %s", url)

    # --- Mongodb ---
    try:
        client = MongoClient(cfg["MONGO_URI"])
        db = client[cfg["DB_NAME"]]
        col = db[cfg["COLLECTION_NAME"]]
        meta_col = get_metadata_col(client, cfg["DB_NAME"], cfg["METADATA_COLLECTION"])
        # Helpful index
        col.create_index("cidr", unique=True)
    except PyMongoError as e:
        logger.exception("MongoDB connection/index error: %s", e)
        return 2

    # --- HTTP fetch with conditional headers ---
    conditional = get_saved_fetch_headers(meta_col, key="spamhaus_drop")
    # Ensureing that user agent is from config
    conditional["User-Agent"] = cfg["USER_AGENT"]

    try:
        result = fetch_drop_text(url, headers=conditional, timeout=cfg["REQUEST_TIMEOUT"], verify_tls=cfg["VERIFY_TLS"])
        if result is None:
            logger.info("Nothing to load. Exiting.")
            return 0
        text, resp = result
    except requests.exceptions.HTTPError as e:
        logger.exception("HTTP error: %s", e)
        return 3
    except requests.exceptions.RequestException as e:
        logger.exception("Request failed: %s", e)
        return 4

    # Saving the ETag/Last-Modified for next run
    try:
        save_fetch_headers(meta_col, key="spamhaus_drop", response=resp)
    except PyMongoError as e:
        logger.warning("Failed to save fetch headers to metadata: %s", e)

    # --- Transforming the data ---
    records = parse_drop_lines(text, cfg["CONNECTOR_NAME"], url)
    logger.info("Parsed %d records.", len(records))

    # --- Loading transformed data to the db ---
    try:
        upserted = upsert_records(col, records, batch_size=cfg["BATCH_SIZE"])
        logger.info("Upserted/Modified %d records into %s.%s", upserted, cfg["DB_NAME"], cfg["COLLECTION_NAME"])
    except PyMongoError as e:
        logger.exception("MongoDB write error: %s", e)
        return 5

    logger.info("ETL completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
