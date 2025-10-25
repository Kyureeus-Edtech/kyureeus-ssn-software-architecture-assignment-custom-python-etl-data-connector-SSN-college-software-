import os
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("DB_URI")
WEATHER = os.getenv("WEATHER")

def fetch_data(url):
    """Fetch data from the Weather API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"✅ Fetched Weather data from {url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch Weather data: {e}")
        return None

def transform(data):
    """Transform Weather API response."""
    if not data:
        return {}

    current = data.get("current_weather", {})
    transformed = {
        "endpoint": "weather_data",
        "timestamp": datetime.utcnow(),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "temperature": current.get("temperature"),
        "windspeed": current.get("windspeed"),
        "winddirection": current.get("winddirection"),
        "weathercode": current.get("weathercode"),
        "time": current.get("time"),
        "source": "Open-Meteo API"
    }

    print(f"🧩 Transformed Weather data: {transformed}")
    return transformed

def insert_into_mongo(data):
    """Insert data into MongoDB."""
    if not data:
        print("⚠️ No Weather data to insert.")
        return

    client = MongoClient(MONGODB_URI)
    db = client.get_database()
    collection = db['api_data']

    result = collection.insert_one(data)
    print(f"📦 Inserted Weather document with id: {result.inserted_id}")

def main():
    data = fetch_data(WEATHER)
    clean_data = transform(data)
    insert_into_mongo(clean_data)

if __name__ == "__main__":
    main()
