import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("MALSHARE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")


client = MongoClient(MONGO_URI)
db = client['malshare_db']
collection = db['malshare_raw']

def extract():
    url = f"https://malshare.com/api.php?api_key={API_KEY}&action=getlist"
    response = requests.get(url)
    response.raise_for_status()
    try:
        data = response.json() 
    except ValueError:
        data = [{"hash": line.strip()} for line in response.text.splitlines() if line.strip()]
    return data


def transform(data):
    transformed = []
    for item in data:
        transformed.append({
            "hash": item.get("sha256") or item.get("hash"),
            "source": item.get("source", "malshare"),
            "fetched_at": datetime.utcnow()
        })
    return transformed


def load(data):
    if data:
        collection.insert_many(data)
        print(f"{len(data)} records inserted into MongoDB.")
    else:
        print("No data to insert.")


if __name__ == "__main__":
    try:
        raw_data = extract()
        clean_data = transform(raw_data)
        load(clean_data)
    except Exception as e:
        print(f"ETL process failed: {e}")
