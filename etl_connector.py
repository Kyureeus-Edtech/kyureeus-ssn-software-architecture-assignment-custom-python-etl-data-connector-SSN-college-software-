import os
import time
import requests
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "ssllabs_analyze_raw")

BASE_URL = "https://api.ssllabs.com/api/v3/analyze"
MAX_RETRIES = 3
RETRY_DELAY = 5  # (in seconds)

# Extract data from SSL Labs API with retries
def extract_data(hostname):
    params = {
        "host": hostname,
        "fromCache": "on",
        "all": "done"
    }
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Rate Limit Check
            if isinstance(data, dict) and "errors" in data:
                for err in data["errors"]:
                    if "Rate limit" in err.get("message", ""):
                        print("Rate limit reached, retrying...")
                        time.sleep(RETRY_DELAY)
                        attempt += 1
                        continue

            # Validate basic structure
            if not isinstance(data, dict) or "host" not in data:
                print("Invalid API response structure.")
                return None

            # Empty payload check
            if not data.get("endpoints"):
                print("Empty payload returned by API.")
                return None

            return data

        except requests.RequestException as e:
            print(f"Connectivity error: {e}")
            time.sleep(RETRY_DELAY)
            attempt += 1

    print("Failed to retrieve valid data after retries.")
    return None

# Transform data for MongoDB insertion
def transform_data(data):
    if not data:
        return None
    return {
        "hostname": data.get("host"),
        "status": data.get("status"),
        "endpoints": data.get("endpoints", []),
        "raw": data,
        "ingested_at": datetime.now(timezone.utc)
    }

# Load transformed data into MongoDB with duplicate prevention
def load_to_mongo(document):
    if not document:
        print("No data to load.")
        return

    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Create unique index for hostname + status to avoid duplicate runs
        collection.create_index(
            [("hostname", 1), ("status", 1), ("ingested_at", 1)],
            unique=True
        )

        result = collection.insert_one(document)
        print(f"Data inserted with ID: {result.inserted_id} !")

    except errors.DuplicateKeyError:
        print("Duplicate entry detected. Skipping insertion !")
    except Exception as e:
        print(f" MongoDB insert failed: {e} !")

if __name__ == "__main__":
    hostname = "www.ssllabs.com"  # test domain
    print("Extracting data...")
    raw_data = extract_data(hostname)

    print("Transforming data...")
    transformed = transform_data(raw_data)

    print("Loading into MongoDB...")
    load_to_mongo(transformed)

    print("ETL process completed.")


