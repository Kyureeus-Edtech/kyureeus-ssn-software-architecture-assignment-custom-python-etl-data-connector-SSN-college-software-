import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["abuseipdb_raw"]

def extract_data(ip="8.8.8.8"):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Accept": "application/json", "Key": API_KEY}
    params = {"ipAddress": ip, "maxAgeInDays": "90"}
    r = requests.get(url, headers=headers, params=params)
    return r.json() if r.status_code == 200 else None

def transform_data(data):
    if not data:
        return None
    record = data.get("data", {})
    record["ingested_at"] = datetime.utcnow()
    return record

def load_data(record):
    if record:
        collection.insert_one(record)
        print("Data inserted successfully.")

def main():
    raw = extract_data("8.8.8.8")  # Example IP
    transformed = transform_data(raw)
    load_data(transformed)

if __name__ == "__main__":
    main()
