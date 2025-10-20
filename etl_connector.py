#!/usr/bin/env python3
"""
NetworkCalc ETL Connector
Extract -> Transform -> Load for NetworkCalc public APIs:
 - /api/ip/{subnet}
 - /api/binary/{number}
 - /api/security/certificate/{hostname}

Usage:
    export MONGO_URI="mongodb://localhost:27017"
    python etl_connector.py --mode ip --input "192.168.1.0/24"
    python etl_connector.py --mode binary --input "255"
    python etl_connector.py --mode certificate --input "example.com"
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("NETWORKCALC_BASE_URL", "https://networkcalc.com/api")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "networkcalc_etl")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))  # seconds

# Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)-8s %(message)s",
)

logger = logging.getLogger("networkcalc_etl")

# HTTP session with retry/backoff
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))


def get_mongo_client(uri: str = MONGO_URI) -> MongoClient:
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform a GET request and return a JSON-decoded dict.
    Raises RuntimeError on non-JSON or unsuccessful responses.
    """
    logger.info("GET %s", url)
    try:
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        logger.error("Request failed: %s", e)
        raise RuntimeError(f"HTTP request failed: {e}") from e

    if resp.status_code == 204:
        return {}

    content_type = resp.headers.get("Content-Type", "")
    if not resp.ok:
        # Try to capture error detail
        text = resp.text.strip()
        logger.error("HTTP error %s: %s", resp.status_code, text[:300])
        raise RuntimeError(f"HTTP {resp.status_code}: {text}")

    if "application/json" not in content_type:
        # Some endpoints may return text/html; try to parse JSON anyway
        try:
            return resp.json()
        except ValueError:
            logger.error("Non-JSON response (content-type=%s).", content_type)
            raise RuntimeError("Non-JSON response received")

    try:
        return resp.json()
    except ValueError as e:
        logger.error("JSON decode error: %s", e)
        raise RuntimeError("Failed to decode JSON response") from e


def transform_record(raw: Dict[str, Any], source: str, input_value: str) -> Dict[str, Any]:
    """
    Normalize record before inserting to MongoDB.
    Adds metadata fields for auditing.
    """
    record = {
        "source": source,
        "input": input_value,
        "fetched_at": datetime.utcnow(),
        "raw": raw
    }
    # Optionally normalize some fields here if desired.
    return record


def load_to_mongo(collection_name: str, document: Dict[str, Any]) -> None:
    client = get_mongo_client()
    db = client[MONGO_DB]
    coll = db[collection_name]
    # Use upsert logic if you want idempotency. Here we insert a new doc for every fetch.
    res = coll.insert_one(document)
    logger.info("Inserted document id=%s into %s.%s", res.inserted_id, MONGO_DB, collection_name)


# ETL job implementations for each endpoint
def etl_ip(subnet: str) -> Dict[str, Any]:
    endpoint = f"{BASE_URL}/ip/{subnet}"
    raw = safe_get(endpoint)
    doc = transform_record(raw, "ip", subnet)
    load_to_mongo("networkcalc_ip_raw", doc)
    return raw


def etl_binary(number: str) -> Dict[str, Any]:
    endpoint = f"{BASE_URL}/binary/{number}"
    raw = safe_get(endpoint)
    doc = transform_record(raw, "binary", number)
    load_to_mongo("networkcalc_binary_raw", doc)
    return raw


def etl_certificate(hostname: str) -> Dict[str, Any]:
    endpoint = f"{BASE_URL}/security/certificate/{hostname}"
    raw = safe_get(endpoint)
    doc = transform_record(raw, "certificate", hostname)
    load_to_mongo("networkcalc_certificate_raw", doc)
    return raw


def parse_args():
    p = argparse.ArgumentParser(description="NetworkCalc ETL Connector")
    p.add_argument("--mode", required=True, choices=["ip", "binary", "certificate", "all"],
                   help="Which connector to run")
    p.add_argument("--input", required=False, help="Input value (subnet, number, hostname). If mode=all, provide a JSON string map.")
    return p.parse_args()


def main():
    args = parse_args()
    try:
        if args.mode == "ip":
            if not args.input:
                raise SystemExit("mode=ip requires --input like '192.168.1.0/24'")
            result = etl_ip(args.input)
            print(result)
        elif args.mode == "binary":
            if not args.input:
                raise SystemExit("mode=binary requires --input like '255'")
            result = etl_binary(args.input)
            print(result)
        elif args.mode == "certificate":
            if not args.input:
                raise SystemExit("mode=certificate requires --input like 'example.com'")
            result = etl_certificate(args.input)
            print(result)
        elif args.mode == "all":
            # Expect a JSON map: {"ip":"192.168.1.0/24","binary":"255","certificate":"example.com"}
            if not args.input:
                raise SystemExit("mode=all requires --input JSON map")
            job_map = json.loads(args.input)
            outputs = {}
            if "ip" in job_map:
                outputs["ip"] = etl_ip(job_map["ip"])
            if "binary" in job_map:
                outputs["binary"] = etl_binary(job_map["binary"])
            if "certificate" in job_map:
                outputs["certificate"] = etl_certificate(job_map["certificate"])
            print(json.dumps(outputs, indent=2))
    except Exception as e:
        logger.exception("ETL failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    import json
    main()
