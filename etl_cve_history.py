# etl_cve_history.py
"""
ETL Script for NVD CVE Change History API
Author: Mugilkrishna D U
Purpose: Extract CVE history JSON from NVD API, transform it, and load into MongoDB
Collections: Separate collection per API endpoint
Upsert logic: Uses 'cve.id' if present, otherwise timestamp + action as unique _id
"""

import os
import requests
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ---------- STEP 0: LOAD ENVIRONMENT VARIABLES ----------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")                  # MongoDB connection string
CVE_HISTORY_DB = os.getenv("CVE_HISTORY_DB")        # Database for CVE history
CONNECTOR_NAME = os.getenv("CONNECTOR_NAME")        # Prefix for collection names

# ---------- STEP 1: EXTRACT ----------
def extract_json(url):
    """Fetch JSON data from a given URL."""
    try:
        print(f"[INFO] Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch JSON: {e}")
        return None

# ---------- STEP 2: TRANSFORM ----------
def transform_json(json_data, key='cveChanges'):
    """
    Transform JSON into a list of dicts suitable for MongoDB.
    Extracts the 'change' field from each cveChanges element.
    Adds an ingestion timestamp.
    """
    if not json_data or key not in json_data:
        print(f"[ERROR] Key '{key}' not found in JSON response.")
        return []

    records = []
    for rec in json_data[key]:
        change_record = rec.get('change')  # drill down to actual change record
        if change_record:
            change_record['ingested_at'] = datetime.now(timezone.utc)
            records.append(change_record)

    print(f"[INFO] Transformed {len(records)} records for MongoDB")
    return records

# ---------- STEP 3: LOAD ----------
def load_to_mongo(records, collection_name):
    """
    Load CVE History records into MongoDB using bulk upsert.
    Upsert key:
        - 'cve.id' if present
        - else fallback: timestamp + action
    """
    if not records:
        print("[WARNING] No records to load.")
        return

    try:
        client = MongoClient(MONGO_URI)
        db = client[CVE_HISTORY_DB]
        collection = db[collection_name]
        operations = []

        for rec in records:
            # Determine unique identifier for upsert
            if 'cve' in rec and 'id' in rec['cve']:
                unique_id = rec['cve']['id']
            else:
                unique_id = rec.get('timestamp', '') + "_" + rec.get('action', 'NA')

            operations.append(
                UpdateOne(
                    {'_id': unique_id},  # unique key in MongoDB
                    {'$set': rec},
                    upsert=True
                )
            )

        if operations:
            result = collection.bulk_write(operations)
            print(f"[INFO] Inserted/Upserted: {result.upserted_count}, Modified: {result.modified_count}")
        else:
            print("[INFO] No valid records found to upsert.")
    except Exception as e:
        print(f"[ERROR] Failed to load into MongoDB: {e}")

# ---------- MAIN FUNCTION ----------
def main():
    """
    Main ETL execution.
    Iterates through multiple CVE History API endpoints
    and loads each into separate collections.
    """
    history_endpoints = {
        "history_date_range": "https://services.nvd.nist.gov/rest/json/cvehistory/2.0/?changeStartDate=2021-08-04T13:00:00.000%2B01:00&changeEndDate=2021-10-22T13:36:00.000%2B01:00",
        "history_by_cveid": "https://services.nvd.nist.gov/rest/json/cvehistory/2.0?cveId=CVE-2025-0001",
        "history_paged_results": "https://services.nvd.nist.gov/rest/json/cvehistory/2.0/?resultsPerPage=20&startIndex=0"
    }

    for name, url in history_endpoints.items():
        print(f"\n[INFO] Processing endpoint: {name}")
        json_data = extract_json(url)
        records = transform_json(json_data, key='cveChanges')  # drill down 'change'
        load_to_mongo(records, collection_name=f"{CONNECTOR_NAME}_{name}")

if __name__ == "__main__":
    main()
