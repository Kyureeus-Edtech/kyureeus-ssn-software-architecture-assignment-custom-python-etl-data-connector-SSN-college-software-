import os
import time
import requests
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "ssn_etl")
COLLECTION = "tor_exit_nodes_raw"
API_URL = "https://onionoo.torproject.org/summary?flag=exit"

def fetch_exit_relays():
    """Extract step: Fetch Tor exit relays."""
    print(" Fetching data from Tor Onionoo API...")
    resp = requests.get(API_URL, timeout=20)
    resp.raise_for_status()
    return resp.json()

def transform_relays(data):
    """Transform step: Clean and format data."""
    relays = data.get("relays", [])
    fetched_at = datetime.now(timezone.utc)
    docs = []
    for r in relays:
        name = r.get("n")
        fingerprint = r.get("f")
        ips = r.get("a", [])
        running = r.get("r", False)
        for ip in ips:
            docs.append({
                "ip": ip,
                "name": name,
                "fingerprint": fingerprint,
                "running": running,
                "fetched_at": fetched_at,
                "ingestion_ts": fetched_at
            })
    print(f" Transformed {len(docs)} records.")
    return docs

def load_to_mongo(docs):
    """Load step: Insert or update records in MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[COLLECTION]

    ops = [
        UpdateOne(
            {"ip": d["ip"]},
            {"$set": d},
            upsert=True
        ) for d in docs
    ]
    result = coll.bulk_write(ops)
    print(f" Upserted: {result.upserted_count}, Modified: {result.modified_count}")

def main():
    print(" Starting ETL process...")
    for attempt in range(3):
        try:
            data = fetch_exit_relays()
            docs = transform_relays(data)
            load_to_mongo(docs)
            print(" ETL process completed successfully.")
            return
        except requests.RequestException as e:
            print(f" Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    print(" ETL process failed after 3 attempts.")

if __name__ == "__main__":
    main()
