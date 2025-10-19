import os
import requests
import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GREYNOISE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
HEADERS = {"Accept": "application/json", "key": API_KEY}

client = MongoClient(MONGO_URI)
db = client["greynoise_db"]

BASE_URL_V3 = "https://api.greynoise.io/v3"
BASE_URL_V1 = "https://api.greynoise.io/v1"

def safe_api_get(url, params=None):
    """Helper for API GET requests with error handling."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if resp.status_code == 429:
            print(f"[Rate Limit] Too many requests to {url}")
            return None, "Rate limit exceeded"
        elif resp.status_code >= 400:
            print(f"[Error] HTTP {resp.status_code} for {url}: {resp.text}")
            return None, f"HTTP {resp.status_code}"
        data = resp.json()
        if not data:
            print(f"[Warning] Empty response from {url}")
            return None, "Empty response"
        return data, None
    except requests.exceptions.RequestException as e:
        print(f"[Exception] Connection error for {url}: {e}")
        return None, str(e)


def extract_ip_lookup(ip_address, quick=False):
    url = f"{BASE_URL_V3}/ip/{ip_address}"
    params = {"quick": str(quick).lower()}
    data, error = safe_api_get(url, params)
    print(f"\nRaw IP Lookup Data for {ip_address}:\n{data if data else error}")
    return data


def extract_cve_info(cve_id):
    url = f"{BASE_URL_V1}/cve/{cve_id}"
    data, error = safe_api_get(url)
    print(f"\nRaw CVE Data for {cve_id}:\n{data if data else error}")
    return data


def extract_community_info(ip_address):
    url = f"{BASE_URL_V3}/community/{ip_address}"
    data, error = safe_api_get(url)
    print(f"\nRaw Community Data for {ip_address}:\n{data if data else error}")
    return data


def transform(data, endpoint_name):
    if not data:
        print(f"[Transform] No data to transform from {endpoint_name}")
        return None
    transformed = {
        "source": endpoint_name,
        "data": data,
        "ingested_at": datetime.datetime.utcnow()
    }
    print(f"\nTransformed Data for {endpoint_name}:\n{transformed}")
    return transformed


def load_to_mongo(data, collection_name):
    if not data:
        print(f"[Load] No data to load into {collection_name}")
        return 0
    try:
        collection = db[collection_name]
        result = collection.insert_one(data)
        print(f"[Load] Inserted document ID: {result.inserted_id} into {collection_name}")
        return 1
    except PyMongoError as e:
        print(f"[Load Error] MongoDB insertion error for {collection_name}: {e}")
        return 0


def run_etl():
    print("Starting GreyNoise ETL process...\n")

    ip_address = "8.8.8.8"
    cve_id = "CVE-2024-12345"

    ip_data = extract_ip_lookup(ip_address)
    cve_data = extract_cve_info(cve_id)
    community_data = extract_community_info(ip_address)

    transformed_ip = transform(ip_data, "ip_lookup")
    transformed_cve = transform(cve_data, "cve_lookup")
    transformed_community = transform(community_data, "community_lookup")

    total_loaded = 0
    total_loaded += load_to_mongo(transformed_ip, "greynoise_ip_lookup_raw")
    total_loaded += load_to_mongo(transformed_cve, "greynoise_cve_lookup_raw")
    total_loaded += load_to_mongo(transformed_community, "greynoise_community_lookup_raw")

    print(f"\nTotal documents loaded into MongoDB: {total_loaded}")
    print("\nETL process completed!\n")


if __name__ == "__main__":
    run_etl()
