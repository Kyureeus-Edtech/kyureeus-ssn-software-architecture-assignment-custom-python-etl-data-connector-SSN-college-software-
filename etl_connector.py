import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import json  # 👈 for pretty-printing

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("RIPESTAT_BASE_URL")
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["ripe_database"]
collection = db["ripestat_raw"]

def extract(endpoint, params):
    """Extract JSON data from the RIPEstat API"""
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/data.json", params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {endpoint}: {e}")
        return None

def transform(data):
    """Transform data for MongoDB compatibility"""
    if not data or "data" not in data:
        return None
    clean_data = {
        "timestamp": datetime.utcnow(),
        "result": data["data"],
        "status": data.get("status", "unknown")
    }
    return clean_data

def load(data):
    """Load transformed data into MongoDB"""
    if data:
        collection.insert_one(data)
        print("✅ Data inserted successfully")
    else:
        print("⚠️ No data to insert")

def run_pipeline():
    """Main ETL orchestration"""
    endpoints = [
        ("network-info", {"resource": "8.8.8.0/24"}),
        ("as-overview", {"resource": "AS15169"}),
        ("routing-status", {"resource": "AS3333"})   # smaller and faster
    ]

    for endpoint, params in endpoints:
        print(f"\n--- Processing {endpoint} ---")
        raw_data = extract(endpoint, params)
        transformed_data = transform(raw_data)

        # 👇 Print data preview before insertion
        if transformed_data:
            print("📄 Preview of transformed data:")
            print(json.dumps(transformed_data["result"], indent=2)[:1000])  # limit to 1000 chars
        else:
            print("⚠️ No data to display (empty or invalid response).")

        load(transformed_data)

if __name__ == "__main__":
    run_pipeline()
