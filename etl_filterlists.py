import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get configuration from .env
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
API_BASE_URL = os.getenv("API_BASE_URL")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# List of endpoints and their corresponding collection names
endpoints = {
    "lists": "lists_collection",
    "licenses": "licenses_collection",
    "maintainers": "maintainers_collection",
    "software": "software_collection",
    "syntaxes": "syntaxes_collection",
    "tags": "tags_collection"
}

def fetch_and_store(endpoint, collection_name):
    """
    Fetch data from API and store it into MongoDB collection
    """
    url = f"{API_BASE_URL}/{endpoint}"
    print(f"Fetching data from {url} ...")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print(f"Warning: Expected a list but got {type(data)} for {endpoint}")
            return

        # Clear old data before inserting new
        db[collection_name].delete_many({})
        db[collection_name].insert_many(data)

        print(f" Inserted {len(data)} records into '{collection_name}' collection.")
    except requests.exceptions.RequestException as e:
        print(f" Error fetching {endpoint}: {e}")
    except Exception as e:
        print(f" Database error for {endpoint}: {e}")

def main():
    print("🚀 Starting ETL process for FilterLists API...\n")

    for endpoint, collection_name in endpoints.items():
        fetch_and_store(endpoint, collection_name)

    print("\n ETL process completed successfully!")

if __name__ == "__main__":
    main()
