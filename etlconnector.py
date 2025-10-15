import os
import json
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Base settings
# You can override OSV_BASE_URL in .env; the endpoints below use the user's specified host + paths.
OSV_BASE = os.getenv("OSV_BASE_URL", "https://api.osv.dev").rstrip("/")
TIMEOUT = 30

ENDPOINTS = {
    "vuln_by_id": {
        "url": f"{OSV_BASE}/v1/vulns/OSV-2020-111",
        "method": "GET"
    },
    "import_findings": {
        "url": f"{OSV_BASE}/v1experimental/importfindings/almalinux-alba",
        "method": "GET"
    },
    "determine_version": {
        "url": f"{OSV_BASE}/v1experimental/determineversion",
        "method": "POST"
    },
    "query": {
        "url": f"{OSV_BASE}/v1/query",
        "method": "POST"
    },
    "querybatch": {
        "url": f"{OSV_BASE}/v1/querybatch",
        "method": "POST"
    }
}

def _mongo_client():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI not set in environment")
    return MongoClient(mongo_uri)

def store_in_mongo(collection_name, payload):
    """Store fetched payload in MongoDB with timestamp."""
    try:
        client = _mongo_client()
        db = client.osv_etl
        db[collection_name].insert_one({
            "data": payload,
            "ingested_at": datetime.now(timezone.utc)
        })
        print(f"[OK] Stored document in collection: {collection_name}")
    except Exception as e:
        print(f"[ERR] Failed to store in MongoDB: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def fetch_get(url):
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[ERR] GET {url} -> {e}")
        return None

def fetch_post(url, payload):
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        # some endpoints may return plain text; try json safely
        try:
            return resp.json()
        except ValueError:
            return {"text": resp.text}
    except Exception as e:
        print(f"[ERR] POST {url} -> {e}")
        return None

def load_env_payload(key, default):
    """Load JSON payload from environment variable or return default."""
    raw = os.getenv(key)
    if not raw or raw.strip() == "":
        return default
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"[WARN] Failed to parse {key} as JSON: {e}. Using default.")
        return default

# ---------------------- ETL flows ----------------------

def etl_vuln_by_id():
    cfg = ENDPOINTS["vuln_by_id"]
    data = fetch_get(cfg["url"])
    if data:
        store_in_mongo("osv_gets", {"endpoint": cfg["url"], "response": data})
    return data

def etl_import_findings():
    cfg = ENDPOINTS["import_findings"]
    data = fetch_get(cfg["url"])
    if data:
        store_in_mongo("osv_gets", {"endpoint": cfg["url"], "response": data})
    return data

def etl_determine_version():
    cfg = ENDPOINTS["determine_version"]
    default_payload = load_env_payload("DETERMINE_VERSION_PAYLOAD", {"package": "pkg:rpm/almalinux/alba@1.0.0"})
    data = fetch_post(cfg["url"], default_payload)
    if data:
        store_in_mongo("osv_posts", {"endpoint": cfg["url"], "payload": default_payload, "response": data})
    return data

def etl_query():
    cfg = ENDPOINTS["query"]
    default_payload = load_env_payload("QUERY_PAYLOAD", {"query": "openssl", "limit": 5})
    data = fetch_post(cfg["url"], default_payload)
    if data:
        store_in_mongo("osv_posts", {"endpoint": cfg["url"], "payload": default_payload, "response": data})
    return data

def etl_querybatch():
    cfg = ENDPOINTS["querybatch"]
    default_payload = load_env_payload("QUERYBATCH_PAYLOAD", [{"query":"openssl"}])
    data = fetch_post(cfg["url"], default_payload)
    if data:
        store_in_mongo("osv_posts", {"endpoint": cfg["url"], "payload": default_payload, "response": data})
    return data

if __name__ == "__main__":
    print("Starting OSV ETL connector...")
    try:
        etl_vuln_by_id()
        etl_import_findings()
        etl_determine_version()
        etl_query()
        etl_querybatch()
        print("ETL run completed.")
    except Exception as e:
        print(f"[FATAL] ETL run failed: {e}")
