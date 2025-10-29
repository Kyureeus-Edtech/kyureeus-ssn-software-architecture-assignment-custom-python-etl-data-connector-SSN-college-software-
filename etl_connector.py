
import os
import requests
import pymongo
from datetime import datetime

# Configuration settings
settings = {
    "API_TOKEN": os.getenv('MALSHARE_API_KEY'),
    "API_ENDPOINT": "https://malshare.com/api.php",
    "MONGO_CONN": os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
    "DATABASE": "my_db",
    "COLLECTION": "my_collection"
}

# Database connection
mongo_client = pymongo.MongoClient(settings["MONGO_CONN"])
mongo_db = mongo_client[settings["DATABASE"]]
mongo_collection = mongo_db[settings["COLLECTION"]]

def fetch_data():
    query = {
        'api_key': settings["API_TOKEN"],
        'action': 'getlist'
    }
    resp = requests.get(settings["API_ENDPOINT"], params=query)
    resp.raise_for_status()
    return resp.json()

def process_data(items):
    processed = []
    timestamp = datetime.utcnow().isoformat() + 'Z'
    for item in items:
        entry = {
            'md5': item.get('md5'),
            'sha1': item.get('sha1'),
            'sha256': item.get('sha256'),
            'created_at': timestamp
        }
        processed.append(entry)
    return processed

def store_data(entries):
    if entries:
        mongo_collection.insert_many(entries)
        print(f"Successfully added {len(entries)} records to MongoDB.")
    else:
        print("No records to add.")

def run_etl():
    try:
        data = fetch_data()
        docs = process_data(data)
        store_data(docs)
    except Exception as error:
        print(f"ETL operation failed: {error}")

if __name__ == "__main__":
    run_etl()
