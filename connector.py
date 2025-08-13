import requests
import time
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

SHODAN_BASE_URL = "https://api.shodan.io/shodan/host"
TARGET_IPS = ["8.8.8.8"]
RATE_LIMIT_DELAY = 1.1

def fetch_shodan_data(ip):
    url = f"{SHODAN_BASE_URL}/{ip}?key={SHODAN_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] {ip} -> {response.status_code} {response.text}")
        return None

def transform_data(raw_json):
    if not raw_json:
        return None
    return {
        "ip": raw_json.get("ip_str"),
        "org": raw_json.get("org"),
        "os": raw_json.get("os"),
        "isp": raw_json.get("isp"),
        "hostnames": raw_json.get("hostnames", []),
        "ports": raw_json.get("ports", []),
        "last_update": raw_json.get("last_update"),
        "country": raw_json.get("country_name"),
        "timestamp": datetime.utcnow()
    }

def load_to_mongodb(data_list):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    for doc in data_list:
        collection.update_one(
            {"ip": doc["ip"]},
            {"$set": doc},
            upsert=True
        )

    print(f"[LOAD] Inserted/Updated {len(data_list)} documents.")
    client.close()

def run_etl():
    all_transformed = []
    
    for ip in TARGET_IPS:
        raw = fetch_shodan_data(ip)
        transformed = transform_data(raw)
        if transformed:
            all_transformed.append(transformed)
        time.sleep(RATE_LIMIT_DELAY)
    
    if all_transformed:
        load_to_mongodb(all_transformed)

if __name__ == "__main__":
    run_etl()
