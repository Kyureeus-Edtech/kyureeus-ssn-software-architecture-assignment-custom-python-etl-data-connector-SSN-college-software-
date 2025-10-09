import os
import json
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://ip-api.com/json/"

def load_queries(file_path="queries.json"):
    """Load list of IPs/domains to query."""
    with open(file_path, "r") as file:
        data = json.load(file)
    return data.get("queries", [])

def connect_to_mongo():
    """Connect to MongoDB."""
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    if not uri or not db_name or not collection_name:
        raise ValueError("MongoDB environment variables missing in .env")

    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]

def fetch_geolocation(query, fields=None, lang=None):
    """Fetch geolocation data for a given IP/domain."""
    params = {}
    if fields:
        params["fields"] = fields
    if lang:
        params["lang"] = lang

    try:
        response = requests.get(BASE_URL + query, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {query}: {e}")
        return None

def store_in_mongo(collection, query, data):
    """Store the API response in MongoDB."""
    if data:
        document = {
            "query": query,
            "data": data,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(document)
        print(f"[SUCCESS] Stored data for {query}")
    else:
        print(f"[SKIPPED] No data to store for {query}")

def main():
    queries = load_queries()
    collection = connect_to_mongo()

    for query in queries:
        print(f"[INFO] Fetching geolocation for {query}...")
        data = fetch_geolocation(query)
        store_in_mongo(collection, query, data)

if __name__ == "__main__":
    main()
