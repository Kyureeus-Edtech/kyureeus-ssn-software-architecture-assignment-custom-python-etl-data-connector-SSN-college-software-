import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables
BASEURL = os.getenv("BASEURL", "http://localhost:9000")
API_ENDPOINT_QP = os.getenv("API_ENDPOINT_QUALITY_PROFILES", "/api/qualityprofiles/search")
QP_URL = f"{BASEURL}{API_ENDPOINT_QP}"
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB")
MONGO_COLLECTION_QP = os.getenv("COLLECTION_NAME_QUALITY_PROFILES")
USERNAME = os.getenv("SONARQUBE_USERNAME")
PASSWORD = os.getenv("SONARQUBE_PASSWORD")

# EXTRACT JSON
def fetch_json(url, payload=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    print(f"Fetching JSON data from {url} ...")
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# LOAD into MongoDB
def insert_quality_profiles(data):
    """
    Insert each quality profile as a separate document into MongoDB.
    """
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][MONGO_COLLECTION_QP]

    # Clean existing data
    existing_count = col.count_documents({})
    if existing_count > 0:
        print(f"Cleaning up existing {existing_count} records from MongoDB...")
        col.delete_many({})

    records_to_insert = []

    if isinstance(data, dict):
        # If the API wraps results in a 'profiles' key
        profiles = data.get("profiles", [])
        for profile in profiles:
            records_to_insert.append(profile)
    elif isinstance(data, list):
        records_to_insert = data
    else:
        print("Invalid data format. Must be dict or list of dicts.")
        return

    if records_to_insert:
        result = col.insert_many(records_to_insert)
        print(f"Inserted {len(result.inserted_ids)} quality profiles into MongoDB.")
    else:
        print("No quality profiles to insert.")


# MAIN PIPELINE
if __name__ == "__main__":
    try:
        payload = {}  # Add payload if your GET request requires it
        qp_data = fetch_json(QP_URL, payload)
        insert_quality_profiles(qp_data)
    except Exception as e:
        print(f"Error: {e}")
