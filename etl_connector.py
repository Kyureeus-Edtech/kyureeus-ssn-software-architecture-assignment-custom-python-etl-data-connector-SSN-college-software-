#!/usr/bin/env python3
"""
ETL Connector for OTX IPv4 General Endpoint
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def get_env(name: str, required: bool = True, default: Optional[str] = None) -> str:
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

OTX_BASE = get_env("OTX_BASE")
OTX_API_KEY = get_env("OTX_API_KEY")
MONGO_URI = get_env("MONGO_URI", default="mongodb://localhost:27017")
MONGO_DB = get_env("MONGO_DB")
COLLECTION_NAME = get_env("COLLECTION_NAME")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_headers(api_key: str) -> Dict[str, str]:
    return {
        "X-OTX-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "custom-etl-connector/1.0"
    }

def fetch_ipv4_general(ip: str, headers: Dict[str, str], retries: int = 5, backoff_factor: int = 2) -> Dict[str, Any]:
    url = OTX_BASE.format(ip=ip)
    delay = 1

    for attempt in range(1, retries + 1):
        print(f"[INFO] Fetching data for IP: {ip} (attempt {attempt}/{retries})")
        try:
            resp = requests.get(url, headers=headers, timeout=20)

            if resp.status_code == 429:
                print(f"[WARN] Rate limited (429). Waiting {delay}s before retry...")
                time.sleep(delay)
                delay *= backoff_factor
                continue
            if resp.status_code == 404:
                print(f"[WARN] No data found for {ip}")
                return {"indicator": ip, "indicator_type": "IPv4", "otx_found": False}
            if not resp.ok:
                raise Exception(f"OTX error {resp.status_code}: {resp.text[:200]}")

            data = resp.json()
            data["otx_found"] = True
            return data

        except (requests.RequestException, json.JSONDecodeError, Exception) as e:
            print(f"[ERROR] Attempt {attempt} failed for {ip}: {e}")
            if attempt == retries:
                raise
            print(f"[INFO] Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= backoff_factor

    raise Exception(f"Failed to fetch data for {ip} after {retries} attempts.")

def transform(doc: Dict[str, Any], ip: str) -> Dict[str, Any]:
    print(f"[INFO] Transforming data for {ip}")
    out = {
        "source": "OTX",
        "indicator_type": "IPv4",
        "indicator": ip,
        "fetched_at": utc_now_iso(),
        "raw": doc
    }

    if "pulse_info" in doc and isinstance(doc["pulse_info"], dict):
        pc = doc["pulse_info"].get("count")
        if pc is not None:
            out["pulse_count"] = int(pc)

    for key in ["reputation", "validation", "base_indicator", "geo", "whois", "asn", "city", "country_name"]:
        if key in doc:
            out[key] = doc[key]

    for arr_key in ["passive_dns", "url_list", "detections"]:
        if arr_key in doc and isinstance(doc[arr_key], list):
            out[arr_key] = doc[arr_key][:100]

    return out

def connect_mongo() -> MongoClient:
    print(f"[INFO] Connecting to MongoDB at {MONGO_URI}")
    return MongoClient(MONGO_URI, uuidRepresentation="standard")

def load_docs(client: MongoClient, db_name: str, coll_name: str, doc: Dict[str, Any], upsert_latest: bool = True):
    print(f"[INFO] Loading document for IP: {doc['indicator']} into {db_name}.{coll_name}")
    coll = client[db_name][coll_name]

    if upsert_latest:
        filter_ = {"source": "OTX", "indicator_type": "IPv4", "indicator": doc["indicator"]}
        update = {
            "$set": {
                "latest": doc,
                "updated_at": utc_now_iso()
            },
            "$push": {
                "history": {
                    "$each": [doc],
                    "$position": 0,
                    "$slice": 20
                }
            }
        }
        coll.update_one(filter_, update, upsert=True)
    else:
        coll.insert_one(doc)

def main():
    print("[START] OTX IPv4 General ETL Connector")
    try:
        headers = build_headers(OTX_API_KEY)
        ips = sys.argv[1:] or ["8.8.8.8"]

        client = connect_mongo()
        try:
            for ip in ips:
                try:
                    raw = fetch_ipv4_general(ip, headers)

                    doc = transform(raw, ip)

                    load_docs(client, MONGO_DB, COLLECTION_NAME, doc, upsert_latest=True)
                    print(f"[SUCCESS] Ingested {ip} (otx_found={raw.get('otx_found')})")
                except Exception as e:
                    print(f"[ERROR] Failed for IP {ip}: {e}", file=sys.stderr)
        finally:
            client.close()
            print("[INFO] MongoDB connection closed.")

    except RuntimeError as e:
        print(f"[CONFIG ERROR] {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[FATAL ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print("[END] ETL process completed successfully.")


if __name__ == "__main__":
    main()
