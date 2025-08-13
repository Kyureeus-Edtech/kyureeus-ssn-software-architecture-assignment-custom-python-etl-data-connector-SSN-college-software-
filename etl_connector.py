import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GREYNOISE_API_KEY')
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME =os.getenv('DB_NAME', 'Greynoise')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'IP_DATA')

# MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

BASE_URL = "http://api.greynoise.io/v3/ip"

def extract_data(ip):
    try:
        resp = requests.get(
            f"{BASE_URL}/{ip}?quick=false",
            headers={
                "key": API_KEY,
                "Accept": "application/json"
            },
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error extracting data: {e}")
        return {}

def transform_data(data):

    return {
        "ip": data.get("ip"),
        "classification": data.get("internet_scanner_intelligence", {}).get("classification"),
        "service_name": data.get("business_service_intelligence", {}).get("name"),
        "service_category": data.get("business_service_intelligence", {}).get("category"),
        "asn": data.get("internet_scanner_intelligence", {}).get("metadata", {}).get("asn"),
        "organization": data.get("internet_scanner_intelligence", {}).get("metadata", {}).get("organization"),
        "country": data.get("internet_scanner_intelligence", {}).get("metadata", {}).get("source_country"),
        "city": data.get("internet_scanner_intelligence", {}).get("metadata", {}).get("source_city"),
        "last_seen": data.get("internet_scanner_intelligence", {}).get("last_seen"),
        "ingested_at": datetime.utcnow()
    }


def load_data(data):
    if data:
        collection.insert_one(data)
        print(f"Data inserted for IP: {data.get('ip', 'Unknown')}")

def run_etl(ip):
    try:
        raw = extract_data(ip)
        if raw:
            transformed = transform_data(raw)
            load_data(transformed)
    except Exception as e:
        print(f"ETL process failed: {e}")

if __name__ == "__main__":
    test_ip = "172.69.188.193"
    run_etl(test_ip)
