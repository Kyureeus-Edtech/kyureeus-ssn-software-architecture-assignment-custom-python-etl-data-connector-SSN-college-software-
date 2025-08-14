import os
import requests
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
API_KEY = os.getenv("THREATFOX_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["threatfox_db"]
collection = db["threatfox_iocs_raw"]

# ThreatFox API endpoint
API_URL = "https://threatfox-api.abuse.ch/api/v1/"

HEADERS = {"Auth-Key": API_KEY}

def fetch_iocs(days=3):
    payload = {"query": "get_iocs", "days": days}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    if j.get("query_status") != "ok":
        print(f"[ERROR] API status: {j.get('query_status')}")
        return []
    return j.get("data", [])

def transform(data):
    transformed = []
    now = datetime.datetime.utcnow()
    for ioc in data:
        ioc["ingested_at"] = now
        transformed.append(ioc)
    return transformed

def load(data):
    if not data:
        print("[WARN] No data to insert")
        return
    result = collection.insert_many(data)
    print(f"[INFO] Inserted {len(result.inserted_ids)} records")

if __name__ == "__main__":
    raw = fetch_iocs(days=7)
    cleaned = transform(raw)
    load(cleaned)
    print("[DONE] ETL complete")
