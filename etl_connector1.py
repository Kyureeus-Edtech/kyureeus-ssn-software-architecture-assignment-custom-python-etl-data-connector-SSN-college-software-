import os
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("DB_URI")
EXCHANGE = os.getenv("EXCHANGE")

def fetch_data(url):
    """Fetch data from Exchange Rate API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"✅ Fetched Exchange Rate data from {url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch Exchange Rate data: {e}")
        return None

def transform(data):
    """Transform Exchange Rate API response."""
    if not data:
        return {}

    transformed = {
        "endpoint": "exchange_rates",
        "timestamp": datetime.utcnow(),
        "base": data.get("base"),
        "date": data.get("date"),
        "rates": data.get("rates", {}),
        "source": "ExchangeRate API"
    }

    print(f"🧩 Transformed Exchange data: {transformed}")
    return transformed

def insert_into_mongo(data):
    """Insert data into MongoDB."""
    if not data:
        print("⚠️ No Exchange data to insert.")
        return

    client = MongoClient(MONGODB_URI)
    db = client.get_database()
    collection = db['api_data']

    result = collection.insert_one(data)
    print(f"📦 Inserted Exchange document with id: {result.inserted_id}")

def main():
    data = fetch_data(EXCHANGE)
    clean_data = transform(data)
    insert_into_mongo(clean_data)

if __name__ == "__main__":
    main()
