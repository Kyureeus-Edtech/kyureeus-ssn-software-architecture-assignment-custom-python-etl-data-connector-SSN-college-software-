import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


load_dotenv()

CONNECTION_STRING = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ssn_etl_db")
DSHIELD_URL = os.getenv("DSHIELD_URL")
COLLECTION_NAME = "dshield_raw"  


def get_collection():
    try:
        client = MongoClient(CONNECTION_STRING)
        # Trigger connection test
        client.admin.command("ping") 
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB — {e}")
        exit(1)

def extract():
    print(f"Extracting data from {DSHIELD_URL}")
    try:
        res = requests.get(DSHIELD_URL)
        res.raise_for_status()
        data = res.text
        print("Extraction successful!")
        return data
    except requests.RequestException as e:
        print(f"ERROR: Extraction failed — {e}")
        return None

def transform(raw):
    print("Transforming data for MongoDB compatibility")
    if not raw:
        print("WARNING: No raw data received")
        return []

    lines = raw.splitlines()
    records = []
    for line in lines:
        # Skip comments and empty lines
        if not line.strip() or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) >= 5:
            record = {
                "ip": parts[0],
                "attacks": int(parts[1]),
                "targets": int(parts[2]),
                "first_seen": parts[3],
                "last_seen": parts[4],
                "_ingestion_time": datetime.utcnow()
            }
            records.append(record)

    print(f"Transformed {len(records)} records")
    return records


def load(collection, docs):
    if not docs:
        print("INFO: No documents to insert")
        return

    try:
        result = collection.insert_many(docs)
        print(f"Loaded {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"ERROR: Failed to load data — {e}")



if __name__ == "__main__":
    print("Starting DShield ETL Pipeline")

    collection = get_collection()

    raw_data = extract()

    records = transform(raw_data)

    load(collection, records)

    print("ETL completed successfully!")