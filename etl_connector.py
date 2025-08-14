# etl_connector.py
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests
from pymongo import MongoClient

# -------------------- LOAD ENV --------------------
load_dotenv()

API_BASE_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/"
EMAIL = os.getenv("HIBP_EMAIL")
API_KEY = os.getenv("HIBP_API_KEY")  # HIBP uses a header key
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "kyureeus_assignments")
CONNECTOR_NAME = os.getenv("CONNECTOR_NAME", "hibp_connector")

# -------------------- EXTRACT --------------------
def extract(email: str):
    headers = {
        "hibp-api-key": API_KEY,
        "User-Agent": "Kyureeus-ETL/1.0",
    }
    url = f"{API_BASE_URL}{email}"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 404:
        # No breach found
        return []
    resp.raise_for_status()
    return resp.json()

# -------------------- TRANSFORM --------------------
def sanitize_for_mongo(doc):
    """Replace MongoDB illegal keys"""
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            nk = k.replace(".", "_")
            if nk.startswith("$"):
                nk = "_" + nk[1:]
            new_doc[nk] = sanitize_for_mongo(v) if isinstance(v, (dict, list)) else v
        return new_doc
    elif isinstance(doc, list):
        return [sanitize_for_mongo(i) for i in doc]
    return doc

def transform(records):
    now_ts = datetime.now(timezone.utc)
    for rec in records:
        clean = sanitize_for_mongo(rec)
        clean["_ingestion_ts"] = now_ts
        clean["_source"] = {"connector": CONNECTOR_NAME}
        yield clean

# -------------------- LOAD --------------------
def load_to_mongo(docs):
    client = MongoClient(MONGODB_URI)
    coll = client[MONGODB_DB][f"{CONNECTOR_NAME}_raw"]
    if docs:
        coll.insert_many(list(docs))
        print(f"Inserted {len(docs)} documents into {CONNECTOR_NAME}_raw")
    else:
        print("No documents to insert.")

# -------------------- RUN --------------------
def main():
    if not EMAIL or not API_KEY:
        raise SystemExit("Please set HIBP_EMAIL and HIBP_API_KEY in your .env file")

    raw_data = extract(EMAIL)
    transformed_data = list(transform(raw_data))
    load_to_mongo(transformed_data)

if __name__ == "__main__":
    main()
