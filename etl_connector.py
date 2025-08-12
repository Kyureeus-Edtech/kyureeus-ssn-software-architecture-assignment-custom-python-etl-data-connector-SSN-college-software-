import os
import requests
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# Load env variables
load_dotenv()
OTX_API_KEY = os.getenv("OTX_API_KEY")
BASE_URL = os.getenv("OTX_BASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")


try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  
    db = client[MONGO_DB]
    collection = db["pulses_raw"]
    print("[INFO] Connected to MongoDB Atlas.")
except errors.ServerSelectionTimeoutError as e:
    print("[ERROR] Could not connect to MongoDB Atlas:", e)
    exit(1)

def fetch_data(url):
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    retries = 3
    while retries > 0:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                print(f"[WARN] Rate limit hit. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            retries -= 1
            print(f"[ERROR] Request failed: {e}. Retries left: {retries}")
            time.sleep(5)
    print("[ERROR] Max retries reached. Exiting fetch.")
    return None

def transform_data(data):
    transformed = []
    for item in data.get("results", []):
        transformed.append({
            "pulse_id": item["id"],
            "name": item["name"],
            "description": item.get("description", ""),
            "created": item["created"],
            "modified": item["modified"],
            "ingested_at": datetime.now(timezone.utc)  
        })
    return transformed

def load_to_mongo(records):
    if not records:
        print("[WARN] No records to insert.")
        return 0
    try:
        for record in records:
            collection.update_one(
                {"pulse_id": record["pulse_id"]},
                {"$set": record},
                upsert=True
            )
        return len(records)
    except errors.PyMongoError as e:
        print("[ERROR] MongoDB insert failed:", e)
        return 0

def run_etl(max_pages=None):
    url = f"{BASE_URL}/api/v1/pulses/subscribed"
    page_count = 0

    while url:
        page_count += 1
        print(f"[INFO] Fetching page {page_count}...")

        data = fetch_data(url)
        if not data:
            print("[ERROR] No data fetched. Stopping ETL.")
            break

        records = transform_data(data)
        inserted_count = load_to_mongo(records)
        print(f"[INFO] Inserted/Updated {inserted_count} records into MongoDB.")

        if max_pages and page_count >= max_pages:
            print(f"[INFO] Reached max page limit ({max_pages}). Stopping...")
            break

        url = data.get("next") 
        time.sleep(6)  

if __name__ == "__main__":
    run_etl(max_pages=3)  
    print("[INFO] ETL completed.")
