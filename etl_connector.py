import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OTX_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "etl_database")

if not API_KEY:
    raise ValueError("Missing OTX_API_KEY in .env file")
if not MONGO_URI:
    raise ValueError("Missing MONGO_URI in .env file")

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["alienvault_raw"]

BASE_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"
HEADERS = {"X-OTX-API-KEY": API_KEY}

def extract_data(page: int = 1):
    url = f"{BASE_URL}?page={page}"
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    return response.json()

def transform_data(raw_data: dict):
    transformed = []
    pulses = raw_data.get("results", [])
    for pulse in pulses:
        transformed.append({
            "id": pulse.get("id"),
            "name": pulse.get("name"),
            "description": pulse.get("description"),
            "author_name": pulse.get("author_name"),
            "tags": pulse.get("tags", []),
            "created": pulse.get("created"),
            "modified": pulse.get("modified"),
            "indicators": pulse.get("indicators", []),
            "extracted_at": datetime.utcnow()
        })
    return transformed

def load_data(data: list):
    if not data:
        print("No data to insert.")
        return
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")

def run_etl():
    page = 1
    while True:
        print(f"Fetching page {page}...")
        raw_data = extract_data(page)
        transformed = transform_data(raw_data)
        load_data(transformed)
        if not raw_data.get("next"):
            break
        page += 1

if __name__ == "__main__":
    try:
        run_etl()
        print("ETL pipeline completed successfully.")
    except Exception as e:
        print(f"ETL pipeline failed: {e}")