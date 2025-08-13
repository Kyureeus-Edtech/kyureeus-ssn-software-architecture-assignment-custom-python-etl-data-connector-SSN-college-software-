#!/usr/bin/env python3
"""
GreyNoise RIOT ETL Connector

Extracts data from the GreyNoise RIOT API endpoint and loads it into MongoDB.

Pipeline: Extract → Transform → Load
- Extract: GET https://api.greynoise.io/v2/riot (requires API key)
- Transform: Pass-through since RIOT returns structured JSON
- Load: Insert into MongoDB with ingestion timestamps

Env vars (put these in a local .env):
  GREYNOISE_API_KEY=your_api_key_here
  MONGO_URI=mongodb://localhost:27017
  MONGO_DB=threat_intel
  COLLECTION_NAME=greynoise_riot_raw

Usage:
  python etl_connector.py
"""

import os
import datetime as dt
import logging
import sys
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# ----------------------------- Logging -------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("greynoise_riot_etl")

# ----------------------------- Config --------------------------------------
BASE_URL = "https://api.greynoise.io/v3/community/8.8.8.8"

# ----------------------------- ETL Functions -------------------------------

def extract(api_key: str):
    headers = {
        "Accept": "application/json",
        "key": api_key
    }
    logger.info("Extracting GreyNoise RIOT data...")
    try:
        resp = requests.get(BASE_URL, headers=headers, timeout=20)
    except requests.exceptions.RequestException as e:
        logger.error("HTTP request failed: %s", e)
        sys.exit(1)

    if resp.status_code != 200:
        logger.error("API request failed with status %s: %s", resp.status_code, resp.text)
        sys.exit(1)

    try:
        return resp.json(), {
            "status_code": resp.status_code,
            "fetched_at": dt.datetime.utcnow()
        }
    except requests.exceptions.JSONDecodeError:
        logger.error("Response was not valid JSON:\n%s", resp.text)
        sys.exit(1)

def transform(data: dict):
    # For RIOT, no transformation needed
    return data

def load_mongo(doc: dict, db_name: str, coll_name: str, mongo_uri: str):
    client = MongoClient(mongo_uri)
    try:
        coll = client[db_name][coll_name]
        doc_copy = dict(doc)
        doc_copy["etl"] = {
            "source": "greynoise_riot",
            "ingested_at": dt.datetime.utcnow(),
            "version": 1
        }
        coll.insert_one(doc_copy)
        logger.info("Inserted 1 document into MongoDB collection '%s'", coll_name)
    except PyMongoError as e:
        logger.error("MongoDB error: %s", e)
        raise
    finally:
        client.close()

# ----------------------------- Main ----------------------------------------

def main():
    load_dotenv()
    api_key = os.getenv("GREYNOISE_API_KEY")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db = os.getenv("MONGO_DB", "threat_intel")
    coll = os.getenv("COLLECTION_NAME", "greynoise_riot_raw")

    if not api_key:
        logger.error("Missing GREYNOISE_API_KEY in environment or .env file")
        sys.exit(1)

    data, meta = extract(api_key)
    parsed = transform(data)
    parsed["http"] = meta
    load_mongo(parsed, db, coll, mongo_uri)
    logger.info("ETL complete")

if __name__ == "__main__":
    main()
