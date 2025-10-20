import os
import sys
import time
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("SSL_LABS_BASE_URL", "https://api.ssllabs.com/api/v3")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "ssllabs_db")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "ssl_analysis")

# Initialize MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# API helper
def get_api(endpoint, params=None):
    """Generic GET function with retry logic."""
    for i in range(3):
        try:
            response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=20)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None


# 1️⃣ Get API Info
def get_api_info():
    print("Fetching API info...")
    info = get_api("info")
    if info:
        print(f"SSL Labs API version: {info.get('engineVersion', 'N/A')}")
    return info


# 2️⃣ Analyze Domain
def analyze_domain(domain):
    print(f"\nAnalyzing domain: {domain}")
    params = {"host": domain, "publish": "off", "fromCache": "on", "all": "done"}
    analysis = get_api("analyze", params=params)
    if not analysis:
        return None

    # Wait until analysis is ready (status READY)
    status = analysis.get("status")
    while status and status not in ["READY", "ERROR"]:
        print(f"Status: {status}... waiting 10s")
        time.sleep(10)
        analysis = get_api("analyze", params=params)
        if not analysis:
            break
        status = analysis.get("status")

    return analysis


# 3️⃣ Get Endpoint Data
def get_endpoint_data(host, ipAddress):
    print(f"Fetching endpoint data for {host} - {ipAddress}")
    params = {"host": host, "s": ipAddress}
    return get_api("getEndpointData", params=params)


# Transform data
def transform_data(domain, raw_analysis):
    if not raw_analysis:
        return None

    endpoints = raw_analysis.get("endpoints", [])
    transformed = []
    for ep in endpoints:
        endpoint_info = get_endpoint_data(domain, ep.get("ipAddress"))
        transformed.append({
            "domain": domain,
            "ipAddress": ep.get("ipAddress"),
            "grade": ep.get("grade"),
            "statusMessage": ep.get("statusMessage"),
            "serverName": endpoint_info.get("serverName") if endpoint_info else None,
            "details": endpoint_info.get("details", {}) if endpoint_info else {},
            "timestamp": datetime.utcnow()
        })
    return transformed


# Load data to MongoDB
def load_to_mongo(transformed_data):
    if not transformed_data:
        print("No data to insert.")
        return
    try:
        collection.insert_many(transformed_data)
        print(f"Inserted {len(transformed_data)} records into MongoDB.")
    except Exception as e:
        print(f"MongoDB insert failed: {e}")


# Main ETL
def main(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    get_api_info()

    for domain in domains:
        raw_analysis = analyze_domain(domain)
        transformed = transform_data(domain, raw_analysis)
        load_to_mongo(transformed)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python etl_connector.py <path_to_domains_file>")
        sys.exit(1)

    main(sys.argv[1])
