import os
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MALSHARE_API_KEY = os.getenv("MALSHARE_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "malshare_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "malshare_raw")

BASE_URL = "https://malshare.com/api.php"
PARAMS = {
    "api_key": MALSHARE_API_KEY,
    "action": "getlist"
}

def extract():
    try:
        response = requests.get(BASE_URL, params=PARAMS, timeout=30)
        response.raise_for_status()
        data = response.text
        if not data.strip():
            raise ValueError("Empty response from the API.")
        return data
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        return None

def transform(raw_txt):
    # Each line is: SHA256<TAB>first_seen<TAB>type<TAB>origin
    records = []
    for line in raw_txt.strip().splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split('\t')
        if len(parts) >= 4:
            sha256, first_seen, filetype, origin = parts[:4]
        elif len(parts) == 3:
            sha256, first_seen, filetype = parts
            origin = ""
        else:
            print(f"[WARN] Skipping malformed line: {line}")
            continue
        record = {
            "sha256": sha256,
            "first_seen": first_seen,
            "filetype": filetype,
            "origin": origin,
            "ingested_at": datetime.utcnow()
        }
        records.append(record)
    return records

def load(records):
    if not records:
        print("[INFO] No records to insert.")
        return
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        result = collection.insert_many(records)
        print(f"[INFO] Inserted {len(result.inserted_ids)} records into MongoDB collection '{MONGODB_COLLECTION}'.")
    except Exception as e:
        print(f"[ERROR] Loading to MongoDB failed: {e}")

def main():
    print("[INFO] Starting MalShare ETL pipeline...")
    raw_txt = extract()
    if not raw_txt:
        print("[INFO] Extraction yielded no data, exiting.")
        return
    records = transform(raw_txt)
    if records:
        load(records)
    print("[INFO] ETL pipeline completed.")

if __name__ == "__main__":
    main()
