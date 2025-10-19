import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASEURL = os.getenv("BASEURL", "http://localhost:9000")
API_ENDPOINT_RULES = os.getenv("API_ENDPOINT_RULES", "/api/rules/search")
RULES_URL = f"{BASEURL}{API_ENDPOINT_RULES}"
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB")
MONGO_COLLECTION = os.getenv("COLLECTION_NAME_RULES")
USERNAME = os.getenv("SONARQUBE_USERNAME")
PASSWORD = os.getenv("SONARQUBE_PASSWORD")

LIMIT = 50  # maximum number of rules to fetch

def fetch_rules(url, limit=50):
    headers = {"Accept": "application/json"}
    params = {
        "ps": limit,  # page size
        "p": 1       # page number
    }
    print(f"Fetching up to {limit} rules from {url} ...")
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD), params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("rules", [])

def insert_rules_to_mongo(rules):
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][MONGO_COLLECTION]

    existing_count = col.count_documents({})
    if existing_count > 0:
        print(f"Cleaning up existing {existing_count} rules from MongoDB...")
        col.delete_many({})

    if rules:
        result = col.insert_many(rules)
        print(f"Inserted {len(result.inserted_ids)} rules into MongoDB.")
    else:
        print("No rules to insert.")

if __name__ == "__main__":
    try:
        rules_data = fetch_rules(RULES_URL, LIMIT)
        insert_rules_to_mongo(rules_data)
    except Exception as e:
        print(f"Error: {e}")
