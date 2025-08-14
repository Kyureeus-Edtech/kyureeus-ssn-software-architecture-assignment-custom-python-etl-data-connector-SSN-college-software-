import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import time


load_dotenv()

def log(msg):
    """Simple timestamped logger."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# -------------------- EXTRACT -------------------- #
def extract_threatfox_iocs(api_key=None, limit=50):
    """
    Extracts IOCs from ThreatFox API.
    Falls back to public feed if API key is not provided.
    """
    log(f"Starting extraction... (limit={limit})")
    start_time = time.time()

    if api_key:
        api_url = "https://threatfox-api.abuse.ch/api/v1/"
        headers = {
            "Content-Type": "application/json",
            "Auth-Key": api_key
        }
        payload = {
            "query": "get_iocs",
            "limit": limit,
            "days": 1,
            "auth_key": api_key
        }
    else:
        log("⚠ No API key provided — using public feed (last 1 day).")
        api_url = "https://threatfox.abuse.ch/export/json/recent/"
        headers = {}
        payload = None

    try:
        if api_key:
            response = requests.post(api_url, headers=headers, json=payload)
        else:
            response = requests.get(api_url, headers=headers)

        response.raise_for_status()
        data = response.json()
        elapsed = time.time() - start_time
        log(f"Extraction successful! Retrieved {len(data.get('data', [])) if isinstance(data, dict) else len(data)} records in {elapsed:.2f}s.")
        return data
    except Exception as e:
        log(f"❌ Extraction failed: {e}")
        return None

# -------------------- TRANSFORM -------------------- #
def transform_data(data):
    """
    Transforms raw ThreatFox data into MongoDB-friendly format.
    Converts dates to datetime objects and ensures tags are lists.
    """
    if not data:
        log("⚠ No data to transform.")
        return []

    records = data["data"] if isinstance(data, dict) and "data" in data else data
    log(f"Transforming {len(records)} records...")
    start_time = time.time()

    transformed_records = []
    for record in records:
        try:
            transformed_record = {
                'ioc': record.get('ioc'),
                'threat_type': record.get('threat_type'),
                'malware': record.get('malware'),
                'confidence_level': int(record.get('confidence_level', 0)),
                'first_seen': parse_datetime(record.get('first_seen')),
                'last_seen': parse_datetime(record.get('last_seen')),
                'reference': record.get('reference'),
                'tags': record.get('tags') if isinstance(record.get('tags'), list) else [],
                'ingestion_timestamp': datetime.now(timezone.utc)
            }
            transformed_records.append(transformed_record)
        except Exception as e:
            log(f"⚠ Skipping record due to transformation error: {e}")

    elapsed = time.time() - start_time
    log(f"Transformation completed: {len(transformed_records)} records transformed in {elapsed:.2f}s.")
    return transformed_records

def parse_datetime(date_str):
    """Parse date string into datetime object (UTC)."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None

# -------------------- LOAD -------------------- #
def load_data(data):
    """
    Loads data into MongoDB with duplicate prevention based on IOC value.
    """
    if not data:
        log("⚠ No data to load.")
        return 0

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        log("❌ MONGO_URI not found in environment variables.")
        return 0

    log("Connecting to MongoDB...")
    start_time = time.time()

    inserted_count = 0
    try:
        client = MongoClient(mongo_uri)
        db = client.data_pipelines
        collection = db.threatfox_iocs

        for record in data:
            if not collection.find_one({"ioc": record["ioc"]}):
                collection.insert_one(record)
                inserted_count += 1

        elapsed = time.time() - start_time
        log(f"Load completed: {inserted_count} new records inserted in {elapsed:.2f}s.")
        return inserted_count
    except Exception as e:
        log(f"❌ Load failed: {e}")
        return 0
    finally:
        if 'client' in locals():
            client.close()

# -------------------- MAIN ETL -------------------- #
if __name__ == "__main__":
    threatfox_api_key = os.getenv("THREATFOX_API_KEY")
    extracted_data = extract_threatfox_iocs(threatfox_api_key, limit=50)

    transformed_data = transform_data(extracted_data)

    loaded_count = load_data(transformed_data)

    log("===== ETL SUMMARY =====")
    log(f"Extracted: {len(extracted_data.get('data', [])) if extracted_data else 0}")
    log(f"Transformed: {len(transformed_data)}")
    log(f"Loaded: {loaded_count}")
    log("=======================")
