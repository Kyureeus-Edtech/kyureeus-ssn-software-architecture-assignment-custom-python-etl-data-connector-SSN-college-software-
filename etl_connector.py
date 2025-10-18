#!/usr/bin/env python3
"""
ETL Connector: MITRE ATT&CK TAXII API -> MongoDB
Author: A. Nandhine (CSE-B, Roll 76)
"""

import os
import time
import json
import logging
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from taxii2client.v21 import Server
from requests.exceptions import RequestException

# -------------------- Load Environment Variables --------------------
load_dotenv()

TAXII_API_ROOT = os.getenv("TAXII_API_ROOT", "https://cti-taxii.mitre.org/staxapi/")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mitre_attack_etl")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "4"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "2.0"))

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# -------------------- MongoDB Setup --------------------
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DATABASE_NAME]
    logger.info(f"Connected to MongoDB: {DATABASE_NAME}")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    raise

# -------------------- ETL Functions --------------------
def get_collections():
    """Connect to TAXII server and return collections"""
    try:
        logger.info(f"Connecting to TAXII server at {TAXII_API_ROOT}")
        server = Server(TAXII_API_ROOT)
        api_root = server.api_roots[0]
        return api_root.collections
    except RequestException as e:
        logger.error(f"TAXII server connection failed: {e}")
        return None

def fetch_collection_objects(collection):
    """Fetch objects from a TAXII collection with retry"""
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            stix_bundle = collection.get_objects()
            if isinstance(stix_bundle, dict):
                return stix_bundle.get("objects", [])
            return list(stix_bundle)
        except Exception as e:
            attempts += 1
            wait = RETRY_BACKOFF * (2 ** (attempts - 1))
            logger.warning(f"Attempt {attempts} failed for collection {collection.title}: {e}. Retrying in {wait}s")
            time.sleep(wait)
    logger.error(f"Failed to fetch objects from collection {collection.title} after {MAX_RETRIES} attempts")
    return []

def transform_objects(objects, collection_id):
    """Transform STIX objects for MongoDB"""
    transformed = []
    for obj in objects:
        doc = {
            "collection_id": collection_id,
            "ingested_at": datetime.utcnow(),
            "stix_id": obj.get("id"),
            "stix_type": obj.get("type"),
            "raw": obj
        }
        transformed.append(doc)
    return transformed

def load_to_mongo(collection_name, docs):
    """Load documents into MongoDB"""
    if docs:
        coll = db[collection_name]
        coll.insert_many(docs)
        logger.info(f"Inserted {len(docs)} documents into collection: {collection_name}")
    else:
        logger.info(f"No documents to insert into collection: {collection_name}")

def run_etl_with_local_fallback():
    """Main ETL process with fallback to local sample JSON"""
    collections = get_collections()
    total_inserted = 0

    if collections is None:
        # Fallback to local sample
        logger.info("Using local sample STIX data as fallback.")
        sample_file = os.path.join(os.path.dirname(__file__), "sample_stix.json")
        if not os.path.exists(sample_file):
            logger.error(f"Sample file not found: {sample_file}")
            return
        with open(sample_file, "r", encoding="utf-8") as f:
            stix_data = json.load(f)
        docs = transform_objects(stix_data.get("objects", []), "local_sample")
        load_to_mongo("mitre_attack_local_sample_raw", docs)
        total_inserted += len(docs)
    else:
        # Normal TAXII processing
        for coll in collections:
            logger.info(f"Processing collection: {coll.title} (ID: {coll.id})")
            objects = fetch_collection_objects(coll)
            docs = transform_objects(objects, coll.id)
            collection_name = f"mitre_attack_{coll.id}_raw"
            load_to_mongo(collection_name, docs)
            total_inserted += len(docs)

    logger.info(f"ETL completed successfully. Total documents inserted: {total_inserted}")

# -------------------- Run ETL --------------------
if __name__ == "__main__":
    run_etl_with_local_fallback()
