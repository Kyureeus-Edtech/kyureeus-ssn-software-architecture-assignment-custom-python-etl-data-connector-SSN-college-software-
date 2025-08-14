import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def extract_threatfox_iocs(api_key, limit=50):
    """Extracts IOCs from ThreatFox API."""
    print(f"Extracting {limit} IOCs from ThreatFox API...")
    api_url = "https://threatfox-api.abuse.ch/api/v1/"

    headers = {
        "Content-Type": "application/json",
        "Auth-Key": api_key
    }

    payload = {
        "query": "get_iocs",
        "limit": limit,
        "days" : 1,
        "auth_key": api_key
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Extraction successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Extraction failed: {e}")
        return None

def transform_data(data):
    """Transforms data for MongoDB insertion."""
    if not data or "data" not in data:
        return []

    print("Transforming data...")
    transformed_records = []
    for record in data["data"]:
        transformed_record = {
            'ioc': record.get('ioc'),
            'threat_type': record.get('threat_type'),
            'malware': record.get('malware'),
            'confidence_level': record.get('confidence_level'),
            'first_seen': record.get('first_seen'),
            'last_seen': record.get('last_seen'),
            'reference': record.get('reference'),
            'tags': record.get('tags', []),
            'ingestion_timestamp': datetime.now(timezone.utc)
        }
        transformed_records.append(transformed_record)

    print("Transformation successful!")
    return transformed_records

def load_data(data):
    """Loads data into MongoDB."""
    if not data:
        print("No data to load.")
        return

    print("Loading data into MongoDB...")
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not found in environment variables.")
        return

    try:
        client = MongoClient(mongo_uri)
        db = client.data_pipelines
        collection = db.threatfox_iocs

        result = collection.insert_many(data)
        print(f"Successfully loaded {len(result.inserted_ids)} records.")
    except Exception as e:
        print(f"Load failed: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    threatfox_api_key = os.getenv("THREATFOX_API_KEY")
    if not threatfox_api_key:
        print("Fatal Error: THREATFOX_API_KEY is not set in your .env file.")
    else:
        extracted_data = extract_threatfox_iocs(threatfox_api_key, limit=50)
        if extracted_data:
            transformed_data = transform_data(extracted_data)
            load_data(transformed_data)