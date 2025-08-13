import os
import time
import requests
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

# =======================
# Load credentials
# =======================
load_dotenv()
API_KEY = os.getenv("API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

# =======================
# API configuration
# =======================
BASE_URL = "https://www.virustotal.com/api/v3/files/"
HEADERS = {
    "x-apikey": API_KEY
}

# =======================
# Test file hash list
# =======================
# Safe known hashes (EICAR test file and a known SHA-256)
hash_list = [
    "44d88612fea8a8f36de82e1278abb02f",  # MD5 - EICAR test file
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"  # SHA-256 sample
]

# =======================
# Extract Step
# =======================
def extract_data(hash_list):
    """Fetch VirusTotal file reports for each hash in the list."""
    results = []
    for file_hash in hash_list:
        url = BASE_URL + file_hash
        try:
            response = requests.get(url, headers=HEADERS)
            # Handle HTTP errors
            if response.status_code == 429:
                print("[Rate Limit] Hit API rate limit, sleeping for 20 seconds...")
                time.sleep(20)
                continue
            response.raise_for_status()
            data = response.json()
            results.append(data)
            print(f"[Extract] Retrieved data for hash: {file_hash}")
        except requests.exceptions.HTTPError as e:
            print(f"[Extract Error] Failed for hash {file_hash}: {e}")
        except Exception as e:
            print(f"[Extract Error] Unexpected issue for hash {file_hash}: {e}")

        # Pause to respect free API limit (4 req/min)
        time.sleep(15)
    return results

# =======================
# Transform Step
# =======================
def transform_data(raw_data):
    """Add an ingestion timestamp to each record."""
    transformed = []
    ingestion_time = datetime.now(timezone.utc)
    for item in raw_data:
        transformed_item = dict(item)  # make a shallow copy
        transformed_item['ingested_at'] = ingestion_time
        transformed.append(transformed_item)
    return transformed

# =======================
# Load Step
# =======================
def load_data(mongo_collection, data):
    """Insert transformed data into MongoDB."""
    if data:
        mongo_collection.insert_many(data)
        print(f"[Load] Inserted {len(data)} records into MongoDB.")
    else:
        print("[Load] No data to insert.")

# =======================
# Main ETL Flow
# =======================
def main():
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client["etl_base"]
    collection = db["virustotal_raw"]

    try:
        # Extract
        raw_data = extract_data(hash_list)
        print(f"[Main] Total records extracted: {len(raw_data)}")

        # Transform
        transformed = transform_data(raw_data)
        print(f"[Main] Records after transform: {len(transformed)}")

        # Load
        load_data(collection, transformed)
        print("[Main] Data successfully loaded into MongoDB.")

    except requests.exceptions.RequestException as api_err:
        print(f"[Main Error] API Request Failed: {api_err}")
    except Exception as e:
        print(f"[Main Error] Unexpected Error: {e}")

if __name__ == "__main__":
    main()
