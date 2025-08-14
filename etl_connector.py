"""
ETL Connector for AlienVault OTX IPv4 General endpoint.
Extracts indicator data for one or more IPs, transforms it, and loads into MongoDB.
""" 
import os
import argparse
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, errors
load_dotenv()

OTX_API_KEY = os.getenv("OTX_API_KEY")
OTX_BASE = os.getenv("OTX_BASE")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
COLL_NAME = os.getenv("COLLECTION_NAME")
LOG = logging.getLogger("etl_otx_ip")
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
LOG.addHandler(handler)

def fetch_ip_general(ip: str) -> dict:
    """Fetch general threat data for a given IPv4 from OTX API."""
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    url = f"{OTX_BASE}/IPv4/{ip}/general"
    LOG.info(f"Fetching OTX general data for IP: {ip}")

    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as e:
        LOG.error(f"Network error for {ip}: {e}")
        return None

    try:
        data = resp.json()
    except ValueError:
        LOG.error(f"Non-JSON response for {ip}: {resp.text[:200]}")
        return None

    if resp.status_code != 200:
        LOG.error(f"API error {resp.status_code} for {ip}: {data}")
        return None

    return data


def transform(raw: dict, ip: str) -> dict:
    """Transform raw OTX API response into MongoDB-friendly document."""
    if not isinstance(raw, dict):
        LOG.error(f"Unexpected response type for {ip}: {type(raw)}")
        return None

    pulse_info = raw.get("pulse_info") or {}
    reputation = raw.get("reputation") or {}

    return {
        "ip": ip,
        "raw": raw, 
        "ingested_at": datetime.utcnow(),
        "pulse_count": pulse_info.get("count", 0),
        "is_malicious": reputation.get("malicious", False),
    }


def get_collection():
    """Get MongoDB collection with index."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    coll = client[MONGO_DB][COLL_NAME]
    coll.create_index([("ip", 1), ("ingested_at", 1)])
    return coll


def insert_documents(collection, docs):
    """Insert documents into MongoDB."""
    if not docs:
        LOG.warning("No valid documents to insert.")
        return 0
    try:
        result = collection.insert_many(docs, ordered=False)
        LOG.info(f"Inserted {len(result.inserted_ids)} documents.")
        return len(result.inserted_ids)
    except errors.BulkWriteError as bwe:
        inserted = bwe.details.get("nInserted", 0)
        LOG.warning(f"Bulk write error; inserted {inserted}. Details: {bwe.details}")
        return inserted
    except errors.PyMongoError as e:
        LOG.error(f"MongoDB error: {e}")
        return 0

def run_etl(ips):
    if not OTX_API_KEY:
        raise EnvironmentError("OTX_API_KEY not found in environment or .env file")

    coll = get_collection()
    docs = []

    for ip in ips:
        raw = fetch_ip_general(ip)
        if not raw:
            LOG.warning(f"Skipping {ip} due to fetch error.")
            continue

        doc = transform(raw, ip)
        if not doc:
            LOG.warning(f"Skipping {ip} due to transform error.")
            continue

        docs.append(doc)

    inserted_count = insert_documents(coll, docs)
    LOG.info(f"ETL finished. Total inserted: {inserted_count}")

def main():
    parser = argparse.ArgumentParser(description="OTX IPv4 General ETL Connector")
    parser.add_argument("--ips", required=True, help="Comma-separated IPv4 list")
    args = parser.parse_args()

    ips = [ip.strip() for ip in args.ips.split(",") if ip.strip()]
    if not ips:
        LOG.error("No valid IPs provided.")
        return

    run_etl(ips)

if __name__ == "__main__":
    main()
    