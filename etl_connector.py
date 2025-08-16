
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ssn_etl_db")
DSHIELD_URL = os.getenv("DSHIELD_URL")

COLLECTION_NAME = "dshield_raw"  # Single collection per connector, per guidelines

if not MONGO_URI or not DSHIELD_URL:
    print("❌ ERROR: Missing MONGO_URI or DSHIELD_URL in .env")
    exit(1)


def get_collection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Trigger connection test
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except ConnectionFailure as e:
        print(f"❌ ERROR: Could not connect to MongoDB — {e}")
        exit(1)


# Extract

def extract():
    print(f"📡 Extracting data from {DSHIELD_URL}")
    try:
        res = requests.get(DSHIELD_URL, timeout=10)
        res.raise_for_status()
        data = res.json()
        print("✅ Extraction successful!")
        return data
    except requests.RequestException as e:
        print(f"❌ ERROR: Extraction failed — {e}")
        return None


# Transform

def transform(raw):
    print("🔄 Transforming data for MongoDB compatibility")
    if not raw:
        print("⚠️ WARNING: No raw data received")
        return []

    # Data may come wrapped; detect and unwrap if needed
    items = raw.get("topips") if isinstance(raw, dict) and "topips" in raw else raw

    if not isinstance(items, list):
        print("❌ ERROR: Expected a list of records; got:", type(items))
        return []

    transformed = []
    for rec in items:
        rec["_ingestion_time"] = datetime.utcnow()
        transformed.append(rec)

    print(f"✅ Transformed {len(transformed)} records")
    return transformed


# Load

def load(collection, docs):
    if not docs:
        print("⚠️ INFO: No documents to insert")
        return

    try:
        result = collection.insert_many(docs)
        print(f"✅ Loaded {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"❌ ERROR: Failed to load data — {e}")



if __name__ == "__main__":
    print("🚀 Starting DShield ETL Pipeline")

    collection = get_collection()

    raw_data = extract()

    records = transform(raw_data)

    load(collection, records)

    print("🎯 ETL completed successfully!")
