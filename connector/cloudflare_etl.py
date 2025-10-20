
#AUTHOR: HARINISHREE - Roll No: 3122225001035

#!/usr/bin/env python3
import os
import datetime as dt
import logging
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# -----------------------------------
# Logging setup
# -----------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("cloudflare_etl")

BASE_URL = "https://www.cloudflare.com"

# -----------------------------------
# Define endpoints (All working public ones)
# -----------------------------------
ENDPOINTS = {
    # Cloudflare Trace Diagnostic Info
    "trace_info": {
        "path": "/cdn-cgi/trace",
        "method": "GET",
        "params": None
    },

    # Cloudflare IP (Shows your public IP in JSON)
    "ip_info": {
        "path": "https://www.cloudflare.com/cdn-cgi/trace",  # same endpoint reused for IP extraction
        "method": "GET",
        "params": None
    },

    #  HTTPBin - IP and user-agent info (public testing API)
    "httpbin_info": {
        "path": "https://httpbin.org/get",
        "method": "GET",
        "params": None
    },

    # Public DNS-over-HTTPS from Cloudflare (works without auth)
    "dns_resolve_example": {
        "path": "https://cloudflare-dns.com/dns-query",
        "method": "GET",
        "params": {"name": "example.com", "type": "A"},
    }
}


# Extract

def extract(module: str, ep_def: dict):
    headers = {
        "Accept": "application/dns-json" if "dns-query" in ep_def["path"] else "application/json"
    }
    url = ep_def["path"] if ep_def["path"].startswith("http") else BASE_URL + ep_def["path"]
    params = ep_def.get("params")
    method = ep_def.get("method", "GET")

    logger.info("Calling %s -> %s", module, url)
    try:
        resp = requests.request(method, url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("HTTP error on %s: %s", module, e)
        return None, None

    # Handle text (trace endpoint) or JSON
    try:
        if "trace" in url:
            data = {}
            for line in resp.text.strip().split("\n"):
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k] = v
        else:
            data = resp.json()
    except ValueError:
        logger.error("Invalid JSON on %s: %s", module, resp.text)
        return None, None

    meta = {
        "module": module,
        "path": url,
        "status_code": resp.status_code,
        "fetched_at": dt.datetime.utcnow(),
        "params": params
    }
    return data, meta


# Transform

def transform(data: dict):
    if not data:
        return {}
    transformed = {k: v for k, v in data.items()}
    transformed["processed_at"] = dt.datetime.utcnow().isoformat()
    return transformed


# Load (MongoDB)

def load_mongo(doc: dict, meta: dict, db_name: str, coll_name: str, mongo_uri: str):
    client = MongoClient(mongo_uri)
    try:
        coll = client[db_name][coll_name]
        rec = {
            "data": doc,
            "meta": meta,
            "etl": {
                "source": "cloudflare_multi_etl",
                "ingested_at": dt.datetime.utcnow(),
                "version": 1
            }
        }
        coll.insert_one(rec)
        logger.info("Inserted module %s record", meta.get("module"))
    except PyMongoError as e:
        logger.error("MongoDB error: %s", e)
    finally:
        client.close()


# Main ETL Workflow
def main():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db = os.getenv("MONGO_DB", "network_data")
    coll = os.getenv("COLLECTION_NAME", "cloudflare_etl")

    for module, ep_def in ENDPOINTS.items():
        data, meta = extract(module, ep_def)
        if data is None:
            continue
        transformed = transform(data)
        load_mongo(transformed, meta, db, coll, mongo_uri)

    logger.info("All modules processed successfully.")



if __name__ == "__main__":
    main()
