import os
import time
import requests
from datetime import datetime
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "etl_db")
THREATFOX_AUTH_KEY = os.getenv("THREATFOX_AUTH_KEY")
DAYS = int(os.getenv("DAYS", 7))  # Default 7 days
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "threatfox_raw")
API_URL = os.getenv("API_URL")

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Extract
def extract_data():
    print("[INFO] Extracting data from ThreatFox API...")
    retries = 0
    headers = {"Auth-Key": THREATFOX_AUTH_KEY}
    payload = {"query": "get_iocs", "days": DAYS}

    while retries < MAX_RETRIES:
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", RETRY_DELAY))
                print(f"[WARNING] Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
                continue

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict) or "data" not in data:
                print("[ERROR] API response structure invalid.")
                return None

            return data

        except requests.exceptions.Timeout:
            print(f"[ERROR] Request timed out. Retrying in {RETRY_DELAY} seconds...")
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Connection error. Retrying in {RETRY_DELAY} seconds...")
        except Exception as e:
            print(f"[ERROR] Failed to fetch data: {e}")
            break

        retries += 1
        time.sleep(RETRY_DELAY)

    print("[ERROR] Max retries reached. Extraction failed.")
    return None

# Transform
def transform_data(raw_data):
    print("[INFO] Transforming data for MongoDB...")
    transformed = []
    if not raw_data or "data" not in raw_data or not raw_data["data"]:
        print("[WARNING] No valid entries found in API response.")
        return transformed

    for entry in raw_data["data"]:
        if not isinstance(entry, dict):
            continue
        if "id" not in entry:
            continue
        entry["ingested_at"] = datetime.utcnow()
        transformed.append(entry)

    print(f"[INFO] Transformed {len(transformed)} records.")
    return transformed

# Load
def load_to_mongo(data):
    if not data:
        print("[WARNING] No data to insert into MongoDB.")
        return

    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        collection.create_index("id", unique=True)

        inserted_count = 0
        for doc in data:
            try:
                collection.insert_one(doc)
                inserted_count += 1
            except errors.DuplicateKeyError:
                continue

        print(f"[INFO] Inserted {inserted_count} new documents into '{COLLECTION_NAME}'.")
    except Exception as e:
        print(f"[ERROR] Failed to insert data into MongoDB: {e}")

# Main ETL Flow
if __name__ == "__main__":
    raw_data = extract_data()
    transformed_data = transform_data(raw_data)
    load_to_mongo(transformed_data)
