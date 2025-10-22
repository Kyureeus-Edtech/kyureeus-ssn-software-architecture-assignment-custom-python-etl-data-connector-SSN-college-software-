#!/usr/bin/env python3
"""
RIPEstat ETL Connector
Author: Prathiyangira Devi V C
College: Sri Sivasubramaniya Nadar College of Engineering
Description: ETL pipeline to fetch network intelligence data from the RIPEstat Data API
"""

import os
import sys
import logging
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RIPEstat API base URL
BASE_URL = "https://stat.ripe.net/data"

# Your unique identifier for RIPEstat usage
SOURCE_APP = "custom_ripestat_etl"

# Resources to fetch
RESOURCES = ["AS3333", "193.0.10.0/23", "NL", "ripe.net"]
# Endpoint to fetch
ENDPOINT = "whois"  # you can change to other endpoints like 'asn-routing', 'geoloc', etc.


def load_environment():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")
    if not mongo_uri or not mongo_db:
        logger.error("Missing required environment variables (MONGO_URI, MONGO_DB)")
        sys.exit(1)
    return mongo_uri, mongo_db


def connect_to_mongodb(mongo_uri, mongo_db):
    try:
        logger.info("Connecting to MongoDB...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[mongo_db]
        collection = db["ripestat_data"]
        logger.info("Successfully connected to MongoDB")
        return client, db, collection
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        sys.exit(1)


def fetch_data_from_ripestat(resource, endpoint=ENDPOINT):
    """Fetch data from RIPEstat Data API via HTTP request"""
    url = f"{BASE_URL}/{endpoint}/data.json"
    params = {
        "resource": resource,
        "sourceapp": SOURCE_APP,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            logger.error(f"RIPEstat API returned error for {resource}: {data.get('messages')}")
            return None
        return data.get("data", {})
    except Exception as e:
        logger.error(f"Failed to fetch {resource}: {e}")
        return None


def transform_data(resource, endpoint, data):
    """Transform raw data into MongoDB document"""
    if not data:
        return {}
    transformed = {
        "resource": resource,
        "endpoint": endpoint,
        "fetched_at": datetime.utcnow(),
        "raw_data": data
    }
    return transformed


def load_to_mongodb(collection, transformed_data):
    if not transformed_data:
        logger.warning("No data to insert into MongoDB")
        return False
    try:
        logger.info(f"Loading data for {transformed_data['resource']} into MongoDB...")
        result = collection.insert_one(transformed_data)
        if result.inserted_id:
            logger.info(f"Successfully inserted document with ID: {result.inserted_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}")
        return False


def print_summary(collection):
    try:
        print("\n" + "=" * 50)
        print("DATA SUMMARY")
        print("=" * 50)
        total_docs = collection.count_documents({})
        print(f"Total documents: {total_docs}")
        latest_doc = collection.find_one({}, sort=[("fetched_at", -1)])
        if latest_doc:
            print(f"Latest ingestion: {latest_doc['fetched_at']}")
        print("=" * 50)
    except Exception as e:
        logger.warning(f"Could not generate summary: {e}")


def main():
    print("RIPEstat ETL Connector Started")
    print("=" * 50)
    start_time = datetime.now()
    try:
        mongo_uri, mongo_db = load_environment()
        client, db, collection = connect_to_mongodb(mongo_uri, mongo_db)

        for resource in RESOURCES:
            raw_data = fetch_data_from_ripestat(resource)
            transformed = transform_data(resource, ENDPOINT, raw_data)
            load_to_mongodb(collection, transformed)

        print_summary(collection)
        duration = datetime.now() - start_time
        logger.info(f"ETL pipeline completed successfully in {duration.total_seconds():.2f} seconds")

    except KeyboardInterrupt:
        logger.warning("ETL pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in ETL pipeline: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")


if __name__ == "__main__":
    main()
