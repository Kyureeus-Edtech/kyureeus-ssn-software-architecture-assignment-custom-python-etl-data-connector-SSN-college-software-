import os
import time
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
from requests.exceptions import HTTPError, RequestException

# -------------------
# Load environment variables
# -------------------
load_dotenv()

API_KEY = os.getenv("OTX_API_KEY")  # OTX API Key from .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

if not API_KEY:
    raise ValueError(
        "OTX_API_KEY not found in environment variables. Please check your .env file."
    )

# -------------------
# MongoDB Setup
# -------------------
client = pymongo.MongoClient(MONGO_URI)
db = client["etl_assignment"]
collection = db["otx_pulses_raw"]

# Create index to avoid duplicate pulses based on unique pulse_id
collection.create_index("pulse_id", unique=True)

# -------------------
# API Setup
# -------------------
BASE_URL = "https://otx.alienvault.com/api/v1"
HEADERS = {"X-OTX-API-KEY": API_KEY}


# -------------------
# Extract Function
# -------------------
def extract(page=1):
    url = f"{BASE_URL}/pulses/subscribed?page={page}&limit=50"
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 5))
                print(f"[Rate Limit] Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise
        except RequestException as req_err:
            print(f"[Error] Request failed: {req_err}. Retrying...")
            time.sleep(3)
    raise RuntimeError(
        f"Failed to retrieve data from API after 3 attempts (page {page})."
    )


# -------------------
# Transform Function
# -------------------
def transform(data):
    transformed = []
    for pulse in data.get("results", []):
        transformed.append(
            {
                "pulse_id": pulse.get("id"),
                "name": pulse.get("name"),
                "description": pulse.get("description"),
                "created": pulse.get("created"),
                "modified": pulse.get("modified"),
                "indicator_count": pulse.get("indicator_count"),
                "subscriber_count": pulse.get("subscriber_count"),
                "tags": pulse.get("tags"),
                "tlp": pulse.get("tlp"),
                "public": pulse.get("public"),
                "adversary": pulse.get("adversary"),
                "industries": pulse.get("industries"),
                "targeted_countries": pulse.get("targeted_countries"),
                "references": pulse.get("references"),
                "ingested_at": datetime.utcnow(),
            }
        )
    return transformed


# -------------------
# Load Function
# -------------------
def load(records):
    inserted_count = 0
    for record in records:
        try:
            collection.insert_one(record)
            inserted_count += 1
        except pymongo.errors.DuplicateKeyError:
            continue
    print(
        f"[DB] API sent {len(records)} records, inserted {inserted_count}, skipped {len(records) - inserted_count}"
    )


# -------------------
# Main ETL Runner
# -------------------
def run_etl():
    print("[ETL] Starting AlienVault OTX ETL job (FULL LOAD)...")
    page = 1
    total_inserted = 0
    total_received = 0

    while True:
        try:
            print(f"[ETL] Processing page {page}...")
            raw_data = extract(page=page)
            records_received = len(raw_data.get("results", []))
            print(f"[ETL] Received {records_received} pulses from API")
            total_received += records_received

            if not records_received:
                break

            transformed_data = transform(raw_data)
            before_count = collection.count_documents({})
            load(transformed_data)
            after_count = collection.count_documents({})
            inserted = after_count - before_count
            total_inserted += max(inserted, 0)

            if not raw_data.get("next"):
                break

            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"[ETL Error] {e}")
            break

    print(
        f"[ETL] Completed. Total API records received: {total_received}, total new inserted: {total_inserted}"
    )


# -------------------
# Run Script
# -------------------
if __name__ == "__main__":
    run_etl()
