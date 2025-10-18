import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint

# Load MongoDB config from .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "kyureeus_ssn")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "dshield_top_attackers_raw")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# 1. Count total documents
count = collection.count_documents({})
print(f"Total documents in {MONGO_DB}.{MONGO_COLLECTION}: {count}")

if count == 0:
    print("⚠️ No data found. Did you run etl_connector.py?")
else:
    # 2. Show first 5 docs
    print("\nSample documents:")
    for doc in collection.find().limit(5):
        pprint(doc)

    # 3. Show unique country codes
    countries = collection.distinct("country")
    print(f"\nUnique countries in this dataset: {countries}")

    # 4. Check latest ingestion timestamp
    latest_doc = collection.find_one(sort=[("ingested_at", -1)])
    print(f"\nLatest ingestion timestamp: {latest_doc.get('ingested_at') if latest_doc else 'N/A'}")
