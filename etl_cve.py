# etl_cve.py
"""
ETL Script for NVD CVE API
Author: Mugilkrishna D U
Purpose: Extract CVE JSON from NVD API, transform it, and load into MongoDB
Collections: Separate collection per API endpoint
"""

import os
import requests
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ---------- STEP 0: LOAD ENVIRONMENT VARIABLES ----------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
CVE_DB = os.getenv("CVE_DB")
CONNECTOR_NAME = os.getenv("CONNECTOR_NAME")

# ---------- STEP 1: EXTRACT ----------
def extract_json(url):
    """
    Fetch JSON data from a given URL.
    Handles network errors and prints informative logs.
    """
    try:
        print(f"[INFO] Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch JSON: {e}")
        return None

# ---------- STEP 2: TRANSFORM ----------
def transform_json(json_data, key='vulnerabilities'):
    """
    Transform JSON into a list of dicts suitable for MongoDB.
    Adds an ingestion timestamp.
    """
    try:
        if not json_data or key not in json_data:
            print(f"[ERROR] Key '{key}' not found in JSON response.")
            return []
        records = json_data[key]
        for rec in records:
            rec['ingested_at'] = datetime.now(timezone.utc)
        print(f"[INFO] Transformed {len(records)} records for MongoDB")
        return records
    except Exception as e:
        print(f"[ERROR] Failed to transform JSON: {e}")
        return []

# ---------- STEP 3: LOAD ----------
def load_to_mongo(records, collection_name):
    """
    Load records into MongoDB using upsert to avoid duplicates.
    Uses cveId as unique identifier.
    """
    if not records:
        print("[WARNING] No records to load.")
        return
    try:
        client = MongoClient(MONGO_URI)
        db = client[CVE_DB]
        collection = db[collection_name]
        operations = []

        for rec in records:
            cve_id = rec.get('cve', {}).get('id')
            if not cve_id:
                continue
            operations.append(
                UpdateOne({'cve.cveId': cve_id}, {'$set': rec}, upsert=True)
            )

        if operations:
            result = collection.bulk_write(operations)
            print(f"[INFO] Inserted: {result.upserted_count}, Modified: {result.modified_count}")
        else:
            print("[INFO] No valid CVE IDs found to upsert.")
    except Exception as e:
        print(f"[ERROR] Failed to load into MongoDB: {e}")

# ---------- MAIN FUNCTION ----------
def main():
    """
    Main ETL execution
    Iterates through multiple CVE API endpoints and loads each into separate collections.
    """
    cve_endpoints = {
        "cve_by_id": "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2019-1010218",
        "cve_critical_cvssv3": "https://services.nvd.nist.gov/rest/json/cves/2.0?cvssV3Severity=CRITICAL",
        "cve_cvssv2_avn_ach_cia": "https://services.nvd.nist.gov/rest/json/cves/2.0?cvssV2Metrics=AV:N/AC:H/Au:N/C:C/I:C/A:C"
    }

    for name, url in cve_endpoints.items():
        print(f"\n[INFO] Processing endpoint: {name}")
        json_data = extract_json(url)
        records = transform_json(json_data)
        load_to_mongo(records, collection_name=f"{CONNECTOR_NAME}_{name}")

if __name__ == "__main__":
    main()
