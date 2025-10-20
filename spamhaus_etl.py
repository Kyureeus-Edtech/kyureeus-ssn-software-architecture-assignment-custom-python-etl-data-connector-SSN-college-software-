import os
from dotenv import load_dotenv
import requests
from pymongo import MongoClient, UpdateOne
from datetime import datetime, timezone

# Load environment variables from .env
load_dotenv()

DROP_URL = os.getenv("DROP_URL")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def extract(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def transform(raw_text):
    records = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        parts = line.split(";", 1)
        cidr = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
        records.append({
            "cidr": cidr,
            "description": description,
            "last_updated": datetime.now(timezone.utc)
        })
    return records

def load(records):
    client = MongoClient(MONGO_URI)
    coll = client[DB_NAME][COLLECTION_NAME]
    ops = [UpdateOne({"cidr": r["cidr"]}, {"$set": r}, upsert=True) for r in records]
    if ops:
        coll.bulk_write(ops)
        print(f"Upserted {len(ops)} records")
    client.close()

if __name__ == "__main__":
    raw = extract(DROP_URL)
    data = transform(raw)
    load(data)
