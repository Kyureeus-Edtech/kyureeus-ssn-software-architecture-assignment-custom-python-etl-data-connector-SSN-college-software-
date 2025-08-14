import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client["etl_database"]
collection = db["abuseipdb_raw"]

# API details
BASE_URL = "https://api.abuseipdb.com/api/v2/check"
IP_TO_CHECK = "8.8.8.8"  # Example IP
MAX_AGE_DAYS = 90

def extract():
    """Extract data from AbuseIPDB API."""
    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": IP_TO_CHECK,
        "maxAgeInDays": MAX_AGE_DAYS
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def transform(data):
    """Transform JSON for MongoDB compatibility."""
    if data and "data" in data:
        record = data["data"]
        record["ingested_at"] = datetime.utcnow()
        return record
    return None

def load(record):
    """Load transformed data into MongoDB."""
    if record:
        collection.insert_one(record)
        print("✅ Data inserted into MongoDB")
    else:
        print("⚠️ No data to insert")

def run_etl():
    print("🚀 Starting ETL Pipeline...")
    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)
    print("🏁 ETL Pipeline Completed.")

if __name__ == "__main__":
    run_etl()
