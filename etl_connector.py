#!/usr/bin/env python3
"""
DShield ETL Connector - topips + ipinfo
----------------------------------------
Extracts the top attacking IPs from DShield's REST API, retrieves detailed info for each,
transforms it, and loads into MongoDB.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
import json

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, errors as pymongo_errors

# Config & Setup
load_dotenv()

BASE_URL = os.getenv("DSHIELD_BASE_URL", "https://www.dshield.org/api")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION") 
SESSION = requests.Session()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dshield_topips_raw")


def get_headers() -> Dict[str, str]:
    ua_email = os.getenv("USER_AGENT_EMAIL") 
    return {
        "User-Agent": f"SSN-CSE-ETL/1.0 (+{ua_email})",
        "Accept": "application/json",
    }


def with_json(url: str) -> str:
    return f"{url}{'&' if '?' in url else '?'}json"


def http_get(path: str, max_retries: int = 3) -> Tuple[int, Any]:
    url = with_json(f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}")
    attempt = 0
    while True:
        attempt += 1
        resp = SESSION.get(url, headers=get_headers(), timeout=30)
        if resp.status_code == 429:
            wait_s = int(resp.headers.get("Retry-After", "300"))
            logger.warning("Rate-limited: sleeping %ss", wait_s)
            if attempt >= max_retries:
                break
            time.sleep(wait_s)
            continue
        if 200 <= resp.status_code < 300:
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, resp.text
        else:
            logger.error("HTTP %s from %s", resp.status_code, url)
            if attempt >= max_retries:
                break
            time.sleep(min(2**attempt, 10))
    return resp.status_code, None


# Mongo connection
def get_mongo() -> Tuple[MongoClient, str]:
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB")
    client = MongoClient(mongodb_uri)
    return client, db_name


def load_to_mongo(rows: List[Dict[str, Any]], collection_name: str) -> int:
    if not rows:
        logger.info("No rows to insert into %s", collection_name)
        return 0
    client, db_name = get_mongo()
    try:
        coll = client[db_name][collection_name]
        coll.create_index("_ingested_at")
        result = coll.insert_many(rows, ordered=False)
        count = len(result.inserted_ids)
        logger.info("Inserted %s docs into %s.%s", count, db_name, collection_name)
        return count
    except pymongo_errors.PyMongoError as e:
        logger.exception("MongoDB insert failed: %s", e)
        return 0
    finally:
        client.close()


# Transform function
def transform_topips_with_details(topips_payload: Any) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    results = []
    ip_list = topips_payload.get("topips", []) if isinstance(topips_payload, dict) else []
    for ip_entry in ip_list:
        ip_addr = ip_entry.get("ip") or ip_entry.get("source")
        if not ip_addr:
            continue

        # Fetch IP details
        code, ip_details = http_get(f"ip/{ip_addr}")
        if code != 200 or not isinstance(ip_details, dict):
            logger.warning("No details for IP %s", ip_addr)
            continue

        # Merge IP rank info + details
        merged = {
            "ip": ip_addr,
            "rank_info": ip_entry,
            "ip_details": ip_details.get("ip", ip_details),
            "_ingested_at": now,
            "_source": "dshield:topips+ipinfo"
        }
        results.append(merged)
    return results


def main() -> int:
    # Early Test Mongo
    try:
        client, db = get_mongo()
        client[db].command("ping")
        client.close()
        logger.info("MongoDB ping OK (db=%s)", db)
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        return 2

    # Fetch topips
    code, payload = http_get("topips")
    if code != 200:
        logger.error("topips fetch failed: HTTP %s", code)
        return 1

    # Normalize payload so we can sample it
    if isinstance(payload, dict) and "topips" in payload:
        sample_before = payload["topips"][:3]
    elif isinstance(payload, list):
        sample_before = payload[:3]
        payload = {"topips": payload}
    else:
        sample_before = [payload]
        payload = {"topips": [payload]}

    logger.info("Sample BEFORE transform (topips):\n%s",
                json.dumps(sample_before, indent=2, default=str))

    # After transform
    enriched_rows = transform_topips_with_details(payload)
    logger.info("Sample AFTER transform:\n%s",
                json.dumps(enriched_rows[:2], indent=2, default=str))

    # Load into Mongo
    inserted = load_to_mongo(enriched_rows, COLLECTION_NAME)
    logger.info("Done. Inserted %s documents.", inserted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
