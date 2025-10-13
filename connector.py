#!/usr/bin/env python3
import os
import datetime as dt
import logging
import sys
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("greynoise_full_etl")

BASE_URL = "https://api.greynoise.io"

# Define all the “modules” / endpoints to call
ENDPOINTS = {
    "ping": {
        "path": "/v3/ping",
        "method": "GET",
        "params": None
    },
    "community_ip": {
        "path": "/v3/community/{ip}",
        "method": "GET",
        "params": None
    },
    "ip_context": {
        "path": "/v3/ip/{ip}",
        "method": "GET",
        "params": None
    },
    "gnql_query": {
        "path": "/v3/gnql/query",
        "method": "GET",
        "params": { "query": "last_seen:1d" }  # example query; customize
    },
    "gnql_stats": {
        "path": "/v3/gnql/stats",
        "method": "GET",
        "params": { "query": "last_seen:30d" }
    },
    "ip_timeline_daily": {
        "path": "/v3/noise/ips/{ip}/daily-summary",
        "method": "GET",
        "params": None
    },
    "ip_similarity": {
        "path": "/v3/ip/similar/{ip}",
        "method": "GET",
        "params": None
    },
    "tag_metadata": {
        "path": "/v3/tags",
        "method": "GET",
        "params": None
    },
    # Add more if there are other modules your subscription supports
}


def extract(api_key: str, module: str, ep_def: dict, ip: str = None):
    headers = {
        "Accept": "application/json",
        "key": api_key
    }
    path = ep_def["path"]
    if "{ip}" in path:
        if ip is None:
            logger.warning("Module %s requires an IP; skipping", module)
            return None, None
        path = path.replace("{ip}", ip)
    url = BASE_URL + path
    params = ep_def.get("params")
    method = ep_def.get("method", "GET")

    logger.info("Calling %s -> %s", module, url)
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=20)
        else:
            resp = requests.request(method, url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("HTTP error on %s: %s", module, e)
        return None, None

    try:
        data = resp.json()
    except ValueError:
        logger.error("Invalid JSON on %s: %s", module, resp.text)
        return None, None

    meta = {
        "module": module,
        "path": path,
        "status_code": resp.status_code,
        "fetched_at": dt.datetime.utcnow(),
        "params": params
    }
    return data, meta


def transform(data: dict):
    # Could put normalization, filtering, flattening, etc.
    return data


def load_mongo(doc: dict, meta: dict, db_name: str, coll_name: str, mongo_uri: str):
    client = MongoClient(mongo_uri)
    try:
        coll = client[db_name][coll_name]
        rec = {
            "data": doc,
            "meta": meta,
            "etl": {
                "source": "greynoise_full",
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


def main():
    load_dotenv()
    api_key = os.getenv("GREYNOISE_API_KEY")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db = os.getenv("MONGO_DB", "threat_intel")
    coll = os.getenv("COLLECTION_NAME", "greynoise_full")

    if not api_key:
        logger.error("Missing GREYNOISE_API_KEY")
        sys.exit(1)

    # Example: which IP to fetch for modules needing IP
    target_ip = os.getenv("TARGET_IP", "8.8.8.8")

    for module, ep_def in ENDPOINTS.items():
        data, meta = extract(api_key, module, ep_def, ip=target_ip)
        if data is None:
            continue
        transformed = transform(data)
        load_mongo(transformed, meta, db, coll, mongo_uri)

    logger.info("All modules processed.")


if __name__ == "__main__":
    main()
