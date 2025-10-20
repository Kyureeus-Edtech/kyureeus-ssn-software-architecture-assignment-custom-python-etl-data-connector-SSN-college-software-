import os
import sys
import time
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# -------------------------------
# Load environment configuration
# -------------------------------
load_dotenv()

SSL_LABS_URL = os.getenv("SSL_LABS_URL", "https://api.ssllabs.com/api/v3")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "ssl_etl_db")
COLLECTION = os.getenv("MONGO_COLLECTION", "analysis_results")

# -------------------------------
# MongoDB Initialization
# -------------------------------
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION]

# -------------------------------
# Generic GET function (with retries)
# -------------------------------
def call_api(endpoint, params=None, retries=3, wait=2):
    for attempt in range(retries):
        try:
            url = f"{SSL_LABS_URL}/{endpoint}"
            resp = requests.get(url, params=params, timeout=25)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"[{endpoint}] HTTP {resp.status_code}: {resp.text[:100]}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/{retries} failed for {endpoint}: {e}")
            time.sleep(wait)
    return None


# 1️⃣ Fetch API Info
def fetch_api_info():
    print("→ Fetching SSL Labs API Information...")
    info = call_api("info")
    if info:
        print(f"API Version: {info.get('engineVersion', 'Unknown')}")
    return info


# 2️⃣ Analyze Domain
def analyze_site(domain):
    print(f"\n→ Initiating SSL analysis for: {domain}")
    params = {"host": domain, "publish": "off", "fromCache": "on", "all": "done"}
    data = call_api("analyze", params=params)
    if not data:
        return None

    # Wait until analysis completes
    while data.get("status") not in ["READY", "ERROR"]:
        print(f"   Status: {data.get('status')} ... waiting 15s")
        time.sleep(15)
        data = call_api("analyze", params=params)
        if not data:
            break

    return data


# 3️⃣ Fetch Endpoint Data
def fetch_endpoint_details(domain, ip):
    print(f"   → Retrieving endpoint data for {domain} - {ip}")
    params = {"host": domain, "s": ip}
    return call_api("getEndpointData", params=params)


# 4️⃣ Fetch Root Certificates (extra endpoint for uniqueness)
def fetch_root_certs():
    print("\n→ Fetching SSL Labs Root Certificates (Raw)...")
    return call_api("getRootCertsRaw")


# -------------------------------
# Transform Data for MongoDB
# -------------------------------
def transform_results(domain, analysis_data):
    if not analysis_data:
        return []

    endpoints = analysis_data.get("endpoints", [])
    transformed = []

    for ep in endpoints:
        ep_details = fetch_endpoint_details(domain, ep.get("ipAddress"))
        transformed.append({
            "domain": domain,
            "ipAddress": ep.get("ipAddress"),
            "grade": ep.get("grade"),
            "status": ep.get("statusMessage"),
            "serverName": ep_details.get("serverName") if ep_details else None,
            "details": ep_details.get("details", {}) if ep_details else {},
            "checkedAt": datetime.utcnow()
        })
    return transformed


# -------------------------------
# Load Data into MongoDB
# -------------------------------
def load_into_mongo(records):
    if not records:
        print("⚠️ No records to insert.")
        return
    try:
        result = collection.insert_many(records)
        print(f"✅ Inserted {len(result.inserted_ids)} documents into MongoDB.")
    except Exception as e:
        print(f"❌ MongoDB Insert Failed: {e}")


# -------------------------------
# Main ETL Execution
# -------------------------------
def main(domains_file):
    if not os.path.exists(domains_file):
        print(f"File not found: {domains_file}")
        sys.exit(1)

    with open(domains_file, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    fetch_api_info()
    fetch_root_certs()  # ← new endpoint for uniqueness

    for domain in domains:
        analysis = analyze_site(domain)
        transformed = transform_results(domain, analysis)
        load_into_mongo(transformed)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ssl_etl.py <path_to_domain_list>")
        sys.exit(1)

    main(sys.argv[1])
