import os
import requests
import pymongo
from pymongo import UpdateOne
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
MAX_PULSES = int(os.getenv("MAX_PULSES", 50))

if not API_KEY:
    raise ValueError("No API_KEY found in .env file!")

BASE_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"
HEADERS = {
    "X-OTX-API-KEY": API_KEY,
    "User-Agent": "OTX-ETL-Script"
}

def extract_pulses(page):
    """Fetch a single page of pulses from OTX API."""
    response = requests.get(BASE_URL, headers=HEADERS, params={"page": page})
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()
    return data.get("results", []), data.get("next")

def transform_pulses(pulses):
    """Transform raw API data into MongoDB documents."""
    transformed = []
    for p in pulses:
        doc = {
            "_id": p.get("id"),
            "name": p.get("name"),
            "author": p.get("author", {}).get("username") if p.get("author") else None,
            "description": p.get("description"),
            "created": p.get("created"),
            "modified": p.get("modified"),
            "tags": p.get("tags"),
            "indicators": p.get("indicators", [])
        }
        transformed.append(doc)
    return transformed

def load_to_mongo(docs):
    """Insert or update multiple documents into MongoDB."""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    ops = [UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True) for doc in docs]
    if ops:
        result = collection.bulk_write(ops)
        print(f"Upserted: {len(result.upserted_ids)}, Modified: {result.modified_count}")

def run_etl():
    page = 1
    total_fetched = 0
    while total_fetched < MAX_PULSES:
        # Extract phase
        pulses_batch, next_page = extract_pulses(page)

        if not pulses_batch:
            print("No more pulses found.")
            break

        # To trim batch if it goes over limit
        if total_fetched + len(pulses_batch) > MAX_PULSES:
            pulses_batch = pulses_batch[:MAX_PULSES - total_fetched]

        print(f"\nPage {page} — Processing {len(pulses_batch)} pulses...")
        for p in pulses_batch:
            print(f"- {p.get('name')} | ID: {p.get('id')} | Author: {p.get('author', {}).get('username') if p.get('author') else None}")

        # Transform & Load
        transformed_docs = transform_pulses(pulses_batch)
        load_to_mongo(transformed_docs)

        total_fetched += len(pulses_batch)

        if total_fetched >= MAX_PULSES or not next_page:
            print(f"\nReached limit of {MAX_PULSES} pulses — stopping.")
            break

        page += 1

if __name__ == "__main__":
    run_etl()














