import os
import datetime
from pymongo import MongoClient

# -------------------------------
# 1️⃣ LOAD ENVIRONMENT VARIABLES (for MongoDB only)
# -------------------------------
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "circl_pdns_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "circl_pdns_raw")

# -------------------------------
# 2️⃣ CONNECT TO MONGODB
# -------------------------------
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# -------------------------------
# 3️⃣ MOCK CIRCL ENDPOINT DATA
# -------------------------------
mock_data = {
    "passive_dns": [
        {"domain": "example.com", "ip": "1.2.3.4", "rrtype": "A"},
        {"domain": "test.com", "ip": "5.6.7.8", "rrtype": "A"}
    ],
    "search_ip": [
        {"ip": "8.8.8.8", "domain": "google.com", "rrtype": "A"}
    ],
    "timeline": [
        {"domain": "example.com", "event": "created", "date": "2025-10-01"}
    ]
}

# -------------------------------
# 4️⃣ TRANSFORM FUNCTION
# -------------------------------
def transform_data(raw_data):
    transformed = []
    for endpoint, data in raw_data.items():
        transformed.append({
            "endpoint": endpoint,
            "fetched_at": datetime.datetime.utcnow(),
            "data": data
        })
    return transformed

# -------------------------------
# 5️⃣ LOAD FUNCTION
# -------------------------------
def load_to_mongodb(data):
    if data:
        collection.insert_many(data)
        print("✅ Mock data successfully inserted into MongoDB!")
    else:
        print("⚠️ No data to insert.")

# -------------------------------
# 6️⃣ MAIN EXECUTION
# -------------------------------
def run_etl():
    print("🚀 Starting Mock CIRCL Passive DNS ETL Pipeline...")
    transformed = transform_data(mock_data)
    load_to_mongodb(transformed)
    print("🎯 ETL process complete.")

if __name__ == "__main__":
    run_etl()
