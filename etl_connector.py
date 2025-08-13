import os
import csv
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
PHISHTANK_URL = os.getenv("PHISHTANK_URL")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    client.server_info()  # Force connection check
    db = client["etl_db"]
    collection = db["phishtank_raw"]
    collection.create_index("phish_id", unique=True)
    print("Connected to MongoDB.")
except ServerSelectionTimeoutError:
    print("Could not connect to MongoDB. Check your network/VPN and MONGO_URI.")
    exit(1)

def transform(row):
    """Clean and transform CSV row safely."""
    try:
        phish_id = row.get("phish_id", "").strip()
        url = row.get("url", "").strip()
        if not phish_id or not url:
            return None  # Skip invalid rows

        # Convert submission_time to datetime if available
        submission_time = None
        if row.get("submission_time"):
            try:
                submission_time = datetime.fromisoformat(row["submission_time"])
            except ValueError:
                submission_time = None  # Invalid format

        verified = row.get("verified", "").lower() in ["yes", "y", "true"]

        return {
            "phish_id": phish_id,
            "url": url,
            "submission_time": submission_time,
            "verified": verified,
            "ingested_at": datetime.utcnow()
        }
    except Exception as e:
        print(f"Error transforming row {row}: {e}")
        return None

def extract_and_load(limit=None, batch_size=1000):
    """Download CSV, transform rows, and bulk load to MongoDB."""
    print("Downloading CSV from PhishTank...")

    # Retry logic for network errors
    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(PHISHTANK_URL, stream=True, timeout=30)
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Failed to fetch data after multiple attempts.")
                return

    reader = csv.DictReader(resp.iter_lines(decode_unicode=True))
    operations = []
    count_inserted = 0
    count_skipped = 0
    count_invalid = 0
    processed = 0

    for row in reader:
        if limit and processed >= limit:
            break

        doc = transform(row)
        if not doc:
            count_invalid += 1
            processed += 1
            continue

        operations.append(UpdateOne(
            {"phish_id": doc["phish_id"]},
            {"$set": doc},
            upsert=True
        ))

        if len(operations) >= batch_size:
            try:
                result = collection.bulk_write(operations, ordered=False)
                count_inserted += result.upserted_count
                count_skipped += result.matched_count
            except BulkWriteError as bwe:
                print(f"Bulk write error: {bwe.details}")
            operations = []

        processed += 1

    # Write remaining operations
    if operations:
        try:
            result = collection.bulk_write(operations, ordered=False)
            count_inserted += result.upserted_count
            count_skipped += result.matched_count
        except BulkWriteError as bwe:
            print(f"Bulk write error: {bwe.details}")

    print(f"Pipeline complete: {count_inserted} inserted, {count_skipped} updated, {count_invalid} invalid skipped. Processed {processed} rows.")

if __name__ == "__main__":
    # Example: limit to 500 rows for testing
    extract_and_load(limit=500, batch_size=500)
