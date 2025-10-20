import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()
username = os.getenv("CZDS_USERNAME")
password = os.getenv("CZDS_PASSWORD")
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["software_architecture"]
collection = db["czds_icann_raw"]

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "MichealCZDSConnector/1.0 (SSN Assignment)"
}

# 1️⃣ Authenticate and get token
auth_url = "https://account-api.icann.org/api/authenticate"
auth_payload = {"username": username, "password": password}

try:
    auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
    auth_response.raise_for_status()
    token = auth_response.json().get("accessToken")
    print("✅ Token obtained successfully.")
except Exception as e:
    print("❌ Authentication failed:", e)
    token = None

if token:
    # Add token header for authorized requests
    headers["Authorization"] = f"Bearer {token}"

    # 2️⃣ Get authorized zone download links
    try:
        links_url = "https://czds-api.icann.org/czds/downloads/links"
        links_response = requests.get(links_url, headers=headers)
        links_response.raise_for_status()
        zone_links = links_response.json() if links_response.text else []
        print(f"✅ Retrieved {len(zone_links)} zone links.")
    except Exception as e:
        print("❌ Error fetching zone links:", e)
        zone_links = []

    # 3️⃣ For each zone link, check file status using HEAD
    metadata_list = []
    for link in zone_links[:3]:  # limit to 3 zones for example
        try:
            meta_response = requests.head(link, headers=headers)
            if meta_response.status_code == 200:
                metadata = {
                    "zone_url": link,
                    "content_length": meta_response.headers.get("Content-Length"),
                    "last_modified": meta_response.headers.get("Last-Modified"),
                    "timestamp": datetime.utcnow()
                }
                metadata_list.append(metadata)
                print(f"✅ Metadata fetched for {link.split('/')[-1]}")
            else:
                print(f"⚠️ Skipped {link} - Status:", meta_response.status_code)
        except Exception as e:
            print(f"❌ Error checking {link}:", e)

    # 🧠 Transform: Flatten and enrich with ingestion timestamp
    transformed = {
        "retrieved_at": datetime.utcnow(),
        "total_zones": len(metadata_list),
        "zones_metadata": metadata_list
    }

    # 💾 Load into MongoDB
    if metadata_list:
        collection.insert_one(transformed)
        print("✅ Data successfully inserted into MongoDB.")
    else:
        print("⚠️ No valid data to insert.")
