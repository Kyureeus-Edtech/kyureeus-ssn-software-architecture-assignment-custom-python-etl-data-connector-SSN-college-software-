#!/usr/bin/env python3
"""
OTX IOC IPv4 ETL Connector
--------------------------
Extracts "general" IOC metadata for IPv4s from AlienVault OTX and loads it into MongoDB.

- Extract: GET https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general
- Transform: add metadata (source, fetched_at, ip), keep payload under "raw"
- Load: insert into MongoDB collection (configurable via env)

Usage:
    python etl_connector.py --ips 8.8.8.8,1.1.1.1
    python etl_connector.py --ips-file ip_list.txt
    python etl_connector.py --dry-run --ips 8.8.8.8

Environment (use ENV_TEMPLATE as a reference):
    MONGO_URI=mongodb://localhost:27017
    MONGO_DB=otx
    MONGO_COLLECTION=otx_ipv4_raw
    OTX_API_KEY=optional_api_key            # optional
    OTX_USER_AGENT=SSN-SA-ETL/1.0 (+https://example.edu)  # optional
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, Iterable, List, Optional

import requests
from pymongo import MongoClient, errors as pymongo_errors
from dotenv import load_dotenv

OTX_URL_TEMPLATE = "https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"


def load_env() -> Dict[str, str]:
    load_dotenv()  # loads from .env if present
    env = {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "otx"),
        "MONGO_COLLECTION": os.getenv("MONGO_COLLECTION", "otx_ipv4_raw"),
        "OTX_API_KEY": os.getenv("OTX_API_KEY", ""),
        "OTX_USER_AGENT": os.getenv("OTX_USER_AGENT", "SSN-SA-ETL/1.0"),
        "REQUEST_TIMEOUT": os.getenv("REQUEST_TIMEOUT", "20"),
        "MAX_RETRIES": os.getenv("MAX_RETRIES", "3"),
        "RETRY_BACKOFF_SECONDS": os.getenv("RETRY_BACKOFF_SECONDS", "2"),
    }
    return env


def iter_ips_from_args(ips_arg: Optional[str], ips_file: Optional[str]) -> List[str]:
    ips: List[str] = []
    if ips_arg:
        ips.extend([x.strip() for x in ips_arg.split(",") if x.strip()])
    if ips_file:
        with open(ips_file, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    ips.append(s)
    # de-duplicate, preserve order
    seen = set()
    ordered = []
    for ip in ips:
        if ip not in seen:
            ordered.append(ip)
            seen.add(ip)
    return ordered


def fetch_otx_general(ip: str, headers: Dict[str, str], timeout: int, max_retries: int, backoff: int) -> Dict[str, Any]:
    url = OTX_URL_TEMPLATE.format(ip=ip)
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                # rate limited: exponential backoff
                sleep_for = backoff * attempt
                print(f"[WARN] Rate limited on attempt {attempt}. Sleeping {sleep_for}s...", file=sys.stderr)
                time.sleep(sleep_for)
                continue
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            if attempt == max_retries:
                raise
            sleep_for = backoff * attempt
            print(f"[WARN] Error fetching {ip} (attempt {attempt}/{max_retries}): {e}. Retrying in {sleep_for}s...", file=sys.stderr)
            time.sleep(sleep_for)
    # Should not reach here
    raise RuntimeError("Exhausted retries unexpectedly")


def transform(ip: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "ip": ip,
        "source": "AlienVault OTX",
        "endpoint": "IPv4/general",
        "fetched_at": now,
        "raw": payload,
        # Convenience fields (if present in payload)
        "indicator": payload.get("indicator"),
        "alexa_rank": payload.get("alexa", {}).get("rank") if isinstance(payload.get("alexa"), dict) else None,
        "pulse_count": payload.get("pulse_info", {}).get("count") if isinstance(payload.get("pulse_info"), dict) else None,
    }


def get_mongo_collection(mongo_uri: str, db_name: str, coll_name: str):
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=8000)
    # Test connection
    client.admin.command("ping")
    db = client[db_name]
    coll = db[coll_name]
    # Useful index for idempotent upserts
    try:
        coll.create_index([("ip", 1), ("fetched_at", 1)])
    except pymongo_errors.PyMongoError as e:
        print(f"[WARN] Could not create index: {e}", file=sys.stderr)
    return coll


def upsert_document(coll, doc: Dict[str, Any], upsert_key: Optional[str] = None):
    """Insert or upsert the document.

    If upsert_key is provided and exists in doc, we upsert by that key; otherwise, we insert.
    """
    if upsert_key and upsert_key in doc and doc[upsert_key] is not None:
        coll.update_one({upsert_key: doc[upsert_key]}, {"$set": doc}, upsert=True)
        return "upserted"
    else:
        coll.insert_one(doc)
        return "inserted"


def run(ips: List[str], dry_run: bool = False, upsert_key: Optional[str] = "indicator") -> int:
    env = load_env()
    timeout = int(env["REQUEST_TIMEOUT"])
    max_retries = int(env["MAX_RETRIES"])
    backoff = int(env["RETRY_BACKOFF_SECONDS"])

    headers = {
        "Accept": "application/json",
        "User-Agent": env["OTX_USER_AGENT"] or "SSN-SA-ETL/1.0"
    }
    if env["OTX_API_KEY"]:
        headers["X-OTX-API-KEY"] = env["OTX_API_KEY"]

    if not dry_run:
        try:
            coll = get_mongo_collection(env["MONGO_URI"], env["MONGO_DB"], env["MONGO_COLLECTION"])
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}", file=sys.stderr)
            return 2
    else:
        coll = None

    successes = 0
    for ip in ips:
        try:
            payload = fetch_otx_general(ip, headers=headers, timeout=timeout, max_retries=max_retries, backoff=backoff)
            doc = transform(ip, payload)
            if dry_run:
                print(json.dumps(doc, indent=2))
            else:
                status = upsert_document(coll, doc, upsert_key=upsert_key)
                print(f"[INFO] {ip}: {status}")
            successes += 1
        except Exception as e:
            print(f"[ERROR] Failed for {ip}: {e}", file=sys.stderr)
    return 0 if successes == len(ips) else 1


def main():
    parser = argparse.ArgumentParser(description="ETL: OTX IOC IPv4 'general' into MongoDB")
    parser.add_argument("--ips", type=str, help="Comma-separated list of IPv4 addresses")
    parser.add_argument("--ips-file", type=str, help="Path to a file containing IPv4s (one per line)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to Mongo; print transformed docs instead")
    parser.add_argument("--upsert-key", type=str, default="indicator", help="Key to upsert on (default: indicator)")
    args = parser.parse_args()

    ips = iter_ips_from_args(args.ips, args.ips_file)
    if not ips:
        print("No IPs provided. Use --ips or --ips-file.", file=sys.stderr)
        return 1
    return run(ips, dry_run=args.dry_run, upsert_key=args.upsert_key)


if __name__ == "__main__":
    sys.exit(main())
