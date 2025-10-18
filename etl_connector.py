from dotenv import load_dotenv
import os
import requests
from pymongo import MongoClient
import datetime

load_dotenv()

OTX_API_KEY = os.getenv("OTX_API_KEY", "").strip()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "otx_database")
LIMIT = int(os.getenv("LIMIT", 5))
MODIFIED_SINCE = os.getenv("MODIFIED_SINCE")
HEADERS = {"X-OTX-API-KEY": OTX_API_KEY}

mongo_client = MongoClient(MONGO_URI)
database = mongo_client[DB_NAME]

BASE = "https://otx.alienvault.com/api/v1"

def make_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_subscribed_pulses(page=1, limit=LIMIT):
    return make_request(f"{BASE}/pulses/subscribed", {"limit": limit, "page": page})

def fetch_pulse_details(pulse_id):
    return make_request(f"{BASE}/pulses/{pulse_id}")

def fetch_indicators_by_pulse(pulse_id, page=1, limit=LIMIT):
    return make_request(f"{BASE}/pulses/{pulse_id}/indicators", {"limit": limit, "page": page})

def fetch_indicator_details(indicator_type, indicator_value):
    return make_request(f"{BASE}/indicator/{indicator_type}/{indicator_value}")

def transform_pulses(api_response):
    transformed = []
    for pulse in api_response.get("results", []):
        record = {
            "id": pulse.get("id"),
            "name": pulse.get("name"),
            "author_name": pulse.get("author_name"),
            "description": pulse.get("description"),
            "created": pulse.get("created"),
            "modified": pulse.get("modified"),
            "tags": pulse.get("tags", []),
            "references": pulse.get("references", []),
            "targeted_countries": pulse.get("targeted_countries", []),
            "indicators": [
                {
                    "indicator": i.get("indicator"),
                    "type": i.get("type"),
                    "title": i.get("title"),
                    "description": i.get("description")
                } for i in pulse.get("indicators", [])
            ],
            "ingestion_timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        transformed.append(record)
    return transformed

def load_to_mongodb(collection_name, records):
    if not records:
        return
    collection = database[collection_name]
    for record in records:
        try:
            collection.update_one({"id": record.get("id")}, {"$set": record}, upsert=True)
        except Exception as e:
            print(f"Error inserting/updating record {record.get('id')}: {e}")

def main():
    print(f"\nStarting Extended OTX ETL — {datetime.datetime.now(datetime.timezone.utc)}")

    subs = fetch_subscribed_pulses()
    load_to_mongodb("subscribed_pulses", transform_pulses(subs))

    pulse_detail = fetch_pulse_details("6842f45696f96557e5f757b1")
    if pulse_detail:
        load_to_mongodb("subscribed_pulses", transform_pulses({"results": [pulse_detail]}))

    indicators = fetch_indicators_by_pulse("6842f45696f96557e5f757b1")
    if indicators and "results" in indicators:
        load_to_mongodb("pulse_indicators", indicators["results"])

    indicator_detail = fetch_indicator_details("IPv4", "62.234.24.38")
    if indicator_detail:
        load_to_mongodb("indicator_details", [indicator_detail])

    print("\nETL Pipeline completed successfully!")

if __name__ == "__main__":
    main()
