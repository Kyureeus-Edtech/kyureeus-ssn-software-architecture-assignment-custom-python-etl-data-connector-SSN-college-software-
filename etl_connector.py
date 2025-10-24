import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def fetch_api(url: str, params: Dict[str, Any], log_id: str):
    delay = 1
    for attempt in range(1, 6):
        try:
            print(f"[INFO] Fetching {url} params={params} [Attempt {attempt}]")
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code == 429:
                print(f"[ERROR] Rate limited (429) on {log_id}. Retrying in {delay}s")
                time.sleep(delay)
                delay *= 2
                continue
            resp.raise_for_status()
            if resp.headers.get('Content-Type', '').startswith('application/json'):
                print(f"[INFO] Got JSON response from {log_id}")
                return resp.json()
            print(f"[INFO] Got raw response from {log_id}")
            return resp.text
        except Exception as e:
            print(f"[ERROR] Attempt {attempt} failed for {url}: {e}")
            if attempt == 5:
                print(f"[ERROR] Giving up on {url} after {attempt} tries")
                raise
            print(f"[INFO] Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2

def transform_available(doc, params):
    closest = doc.get("archived_snapshots", {}).get("closest", {})
    return {
        "url": params["url"],
        "endpoint": "available",
        "closest_snapshot_url": closest.get("url"),
        "closest_timestamp": closest.get("timestamp"),
        "snapshot_available": closest.get("available"),
        "status": closest.get("status"),
        "fetched_at": utc_now_iso(),
        "raw": doc
    }

def transform_cdx(doc, params):
    try:
        rows = doc if isinstance(doc, list) else json.loads(doc)
    except:
        rows = []
    columns = rows[0] if rows else []
    captures = rows[1:] if len(rows) > 1 else []
    total_snapshots = len(captures)
    timestamps = [c[0] for c in captures] if total_snapshots else []
    latest_timestamp = max(timestamps) if timestamps else None
    latest_url = None
    if captures:
        latest_row = max(captures, key=lambda r: r[0])
        latest_url = f"https://web.archive.org/web/{latest_row[0]}/{latest_row[1]}"
    return {
        "url": params["url"],
        "endpoint": "cdx",
        "total_snapshots": total_snapshots,
        "latest_snapshot_url": latest_url,
        "latest_timestamp": latest_timestamp,
        "fetched_at": utc_now_iso(),
        "raw": doc
    }

def transform_timemap(doc, params):
    try:
        rows = doc if isinstance(doc, list) else json.loads(doc)
    except:
        rows = []
    captures = [r for r in rows if r and isinstance(r, list) and r[0] == "memento"]
    total_snapshots = len(captures)
    timestamps = [c[1] for c in captures] if total_snapshots else []
    latest_memento_url = None
    latest_memento_timestamp = None
    if captures:
        latest_capture = max(captures, key=lambda v: v[1])
        latest_memento_url = latest_capture[2]
        latest_memento_timestamp = latest_capture[1]
    return {
        "url": params["url"],
        "endpoint": "timemap",
        "total_snapshots": total_snapshots,
        "latest_snapshot_url": latest_memento_url,
        "latest_timestamp": latest_memento_timestamp,
        "fetched_at": utc_now_iso(),
        "raw": doc
    }

def connect_mongo():
    print(f"[INFO] Connecting to MongoDB {MONGO_URI}")
    return MongoClient(MONGO_URI, uuidRepresentation="standard")

def load_docs(client, db_name, coll_name, doc):
    coll = client[db_name][coll_name]
    print(f"[INFO] Inserting document for {doc['endpoint']}:{doc.get('url')}")
    coll.insert_one(doc)

def main():
    urls = sys.argv[1:]
    if not urls:
        urls = ["https://example.com"]
    endpoints = [
        {
            "name": "available",
            "url": "http://archive.org/wayback/available",
            "params_func": lambda u: {"url": u},
            "transform": transform_available
        },
        {
            "name": "cdx",
            "url": "https://web.archive.org/cdx/search/cdx",
            "params_func": lambda u: {"url": u, "output": "json", "limit": 10},
            "transform": transform_cdx
        },
        {
            "name": "timemap",
            "url_func": lambda u: f"https://web.archive.org/web/timemap/json/{u}",
            "params_func": lambda u: {"url": u},
            "transform": transform_timemap
        }
    ]
    client = connect_mongo()
    try:
        for url in urls:
            print(f"[INFO] Processing URL: {url}")
            for ep in endpoints:
                print(f"[INFO] Endpoint: {ep['name']}")
                if ep["name"] == "timemap":
                    req_url = ep["url_func"](url)
                else:
                    req_url = ep["url"]
                params = ep["params_func"](url)
                log_id = f"{ep['name']}-{url}"
                raw = fetch_api(req_url, params, log_id)
                doc = ep["transform"](raw, params)
                load_docs(client, MONGO_DB, COLLECTION_NAME, doc)
                print(f"[INFO] Completed {ep['name']} for {url}")
    finally:
        client.close()
        print("[INFO] MongoDB connection closed.")

if __name__ == "__main__":
    main()
