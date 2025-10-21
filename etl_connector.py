"""
ICANN CZDS ETL Data Connector
Author: <Your Name> (<Your Roll Number>)
Description:
    Logs into ICANN's CZDS API, retrieves an access token,
    extracts data from 3 endpoints, transforms it, and loads into MongoDB.
"""

import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

ICANN_EMAIL = os.getenv("ICANN_EMAIL")
ICANN_PASSWORD = os.getenv("ICANN_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")

ACCOUNT_API_URL = "https://account-api.icann.org/api/authenticate"
CZDS_BASE_URL = "https://czds-api.icann.org"

# -------------------------
# MongoDB Connection
# -------------------------
client = pymongo.MongoClient(MONGO_URI)
db = client["czds_db"]
print("✅ Connected to MongoDB successfully.")

# -------------------------
# Step 1: Authenticate to get access token
# -------------------------
def get_access_token():
    """Authenticate to ICANN Account API and return an access token."""
    payload = {
        "username": ICANN_EMAIL,
        "password": ICANN_PASSWORD
    }
    try:
        response = requests.post(ACCOUNT_API_URL, json=payload)
        response.raise_for_status()
        token = response.json().get("accessToken")
        if token:
            print("🔑 Access token obtained successfully.")
            return token
        else:
            print("❌ Failed to get access token. Check credentials or permissions.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication failed: {e}")
        return None

# -------------------------
# Step 2: Fetch Data from CZDS Endpoint
# -------------------------
def fetch_data(endpoint: str, token: str):
    """Fetch JSON or binary data from CZDS endpoint using token."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{CZDS_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        print(f"\n🔍 Status {response.status_code} for {endpoint}")
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        # Try JSON first
        try:
            return response.json()
        except ValueError:
            # Not JSON, save as file
            filename = endpoint.replace("/", "_") + ".bin"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"📦 Saved raw data to {filename}")
            return [{"file_saved": filename, "endpoint": endpoint, "status": "saved"}]

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from {endpoint}: {e}")
        return []


# -------------------------
# Step 3: Transform Data
# -------------------------
def transform_data(data):
    """Add timestamps and clean structure."""
    transformed = []
    for item in data:
        item["ingested_at"] = datetime.utcnow().isoformat()
        transformed.append(item)
    return transformed

# -------------------------
# Step 4: Load to MongoDB
# -------------------------
def load_to_mongo(data, collection_name):
    """Insert transformed data into MongoDB."""
    if not data:
        print(f"⚠️ No data to insert for {collection_name}.")
        return
    collection = db[collection_name]
    collection.insert_many(data)
    print(f"✅ Inserted {len(data)} records into {collection_name}.")

# -------------------------
# Step 5: Run ETL
# -------------------------
def run_czds_etl():
    token = get_access_token()
    if not token:
        print("❌ Cannot continue without access token.")
        return

    endpoints = {
        "czds/downloads": "czds_downloads_raw",
        "czds/requests": "czds_requests_raw",
        "czds/zonefile/org": "czds_zonefile_raw"
    }

    for endpoint, collection in endpoints.items():
        print(f"\n🚀 Running ETL for: {endpoint}")
        raw_data = fetch_data(endpoint, token)
        transformed_data = transform_data(raw_data)
        load_to_mongo(transformed_data, collection)

    print("\n🎯 ETL process completed for all endpoints!")

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    run_czds_etl()
