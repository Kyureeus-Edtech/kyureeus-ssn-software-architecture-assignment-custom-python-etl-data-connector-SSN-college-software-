#!/usr/bin/env python3
"""
GreyNoise ETL: read IPs from ips_to_enrich.txt (one per line),
query GreyNoise Community API for each IP, transform and upsert into MongoDB.

Requirements:
    pip install requests pymongo python-dotenv
"""
import os
import time
import requests
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne, errors
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

# Load environment
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "greynoise")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "raw_data")
GREYNOISE_API_KEY = os.getenv("GREYNOISE_API_KEY")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 200))
SLEEP_BETWEEN = float(os.getenv("SLEEP_BETWEEN", 0.5))

if not MONGO_URI:
    raise SystemExit("MONGODB_URI missing in .env")
if not GREYNOISE_API_KEY:
    raise SystemExit("GREYNOISE_API_KEY missing in .env")

# Community endpoint base (use enterprise endpoints if you have those credentials)
BASE_URL = "https://api.greynoise.io/v3/community"

# Configure session with simple retries for transient errors
session = requests.Session()
retries = Retry(total=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.headers.update({"key": GREYNOISE_API_KEY, "Accept": "application/json"})

def get_mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[COLLECTION_NAME]
    try:
        coll.create_index("ip", unique=True, sparse=True)
    except Exception as e:
        print("Index creation warning:", e)
    return coll

def load_ips_from_file(path="ips_to_enrich.txt"):
    """Return list of IPs; fallback to sample list if file missing."""
    if os.path.exists(path):
        with open(path, "r") as f:
            ips = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(ips)} IPs from {path}")
            return ips
    sample = ["8.8.8.8", "1.1.1.1"]
    print(f"No {path} found — using sample IPs: {sample}")
    return sample

def lookup_ip(ip, max_retries=3):
    """Query GreyNoise community IP endpoint, with backoff on 429."""
    url = f"{BASE_URL}/{ip}"
    wait = 1
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 429:
                print(f"[{ip}] Rate limited (429). Backing off {wait}s (attempt {attempt})")
                time.sleep(wait)
                wait *= 2
                continue
            # 404 means GreyNoise has no record for this IP; return not_found record
            if resp.status_code == 404:
                return {"ip": ip, "message": "not_found"}
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as he:
            # if status code available, print & break/raise accordingly
            status = getattr(he.response, "status_code", None)
            print(f"[{ip}] HTTPError {status}: {he}")
            raise
        except Exception as e:
            print(f"[{ip}] Error: {e} (attempt {attempt})")
            time.sleep(wait)
            wait *= 2
    raise RuntimeError(f"Failed to fetch {ip} after {max_retries} attempts")

def transform_record(raw):
    """Normalize result for Mongo ingestion and add metadata."""
    if isinstance(raw, dict):
        rec = dict(raw)  # shallow copy
    else:
        rec = {"raw": raw}
    # unify ip field names (some endpoints differ)
    rec["ip"] = rec.get("ip") or rec.get("ip_address") or rec.get("query")
    rec["ingested_at"] = datetime.utcnow()
    return rec

def bulk_upsert(collection, ops):
    if not ops:
        return
    try:
        res = collection.bulk_write(ops, ordered=False)
        # bulk_write returns matched_count and upserted_ids (a dict-like)
        upserted_count = len(res.upserted_ids) if getattr(res, "upserted_ids", None) else 0
        print(f"Bulk write: matched={res.matched_count}, upserted={upserted_count}")
    except errors.BulkWriteError as bwe:
        print("BulkWriteError: some operations failed. Sample errors:", bwe.details.get("writeErrors", [])[:3])
    except Exception as e:
        print("Bulk upsert failed:", e)

def main():
    coll = get_mongo_collection()
    ips = load_ips_from_file()

    ops = []
    processed = 0
    for ip in ips:
        try:
            raw = lookup_ip(ip)
            rec = transform_record(raw)
            ip_key = rec.get("ip") or ip
            ops.append(UpdateOne({"ip": ip_key}, {"$set": rec}, upsert=True))
            processed += 1
        except Exception as e:
            print(f"Skipping {ip} due to error: {e}")

        # flush batch
        if len(ops) >= BATCH_SIZE:
            bulk_upsert(coll, ops)
            ops = []

        time.sleep(SLEEP_BETWEEN)

    # final flush
    if ops:
        bulk_upsert(coll, ops)

    print(f"ETL finished. Processed {processed} IP(s).")

if __name__ == "__main__":
    main()
