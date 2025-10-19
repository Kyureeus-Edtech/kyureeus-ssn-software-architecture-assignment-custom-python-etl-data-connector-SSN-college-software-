import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables
BASEURL = os.getenv("BASEURL", "http://localhost:9000")
API_ENDPOINT = os.getenv("API_ENDPOINT_METRIC", "/api/metrics/search")
METRICS_URL = f"{BASEURL}{API_ENDPOINT}"
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB")
MONGO_COLLECTION = os.getenv("COLLECTION_NAME_METRIC")
USERNAME = os.getenv("SONARQUBE_USERNAME")
PASSWORD = os.getenv("SONARQUBE_PASSWORD")
# EXTRACT JSON
def fetch_json(url, payload=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    print(f"Fetching JSON data from {url} ...")
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD) ,json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# LOAD
def insert_to_mongo(data):
    """
    Insert each metric as a separate document into MongoDB.
    Keeps reference to the parent _id.
    """
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][MONGO_COLLECTION]

    # Clean existing data
    existing_count = col.count_documents({})
    if existing_count > 0:
        print(f"Cleaning up existing {existing_count} records from MongoDB...")
        col.delete_many({})

    records_to_insert = []

    if isinstance(data, dict):
        # Single JSON object with metrics array
        parent_id = data.get("_id")
        for metric in data.get("metrics", []):
            metric_record = metric.copy()
            metric_record["parent_id"] = parent_id
            records_to_insert.append(metric_record)
    elif isinstance(data, list):
        # List of JSON objects
        for item in data:
            parent_id = item.get("_id")
            for metric in item.get("metrics", []):
                metric_record = metric.copy()
                metric_record["parent_id"] = parent_id
                records_to_insert.append(metric_record)
    else:
        print("Invalid data format. Must be dict or list of dicts.")
        return

    if records_to_insert:
        result = col.insert_many(records_to_insert)
        print(f"Inserted {len(result.inserted_ids)} metrics into MongoDB.")
    else:
        print("No metrics to insert.")


# MAIN PIPELINE
if __name__ == "__main__":
    try:
        payload = {}  # Add payload if needed for your POST request
        metrics_data = fetch_json(METRICS_URL, payload)
        insert_to_mongo(metrics_data)
    except Exception as e:
        print(f"Error: {e}")
