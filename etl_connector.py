import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

API_KEY = os.getenv("CIRCL_API_KEY")
BASE_URL = "https://www.circl.lu/pdns"

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "ssn_etl"
COLLECTION_NAME = "circl_passive_dns_raw"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def fetch_data(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            for record in data:
                record["ingested_at"] = datetime.utcnow()
            return data
        else:
            return []
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

def fetch_domain_data(domain):
    return fetch_data(f"{BASE_URL}/query/{domain}")

def fetch_ip_data(ip):
    return fetch_data(f"{BASE_URL}/get/{ip}")

def fetch_hash_data(hash_value):
    return fetch_data(f"{BASE_URL}/get/{hash_value}")

def load_to_mongodb(records):
    if records:
        collection.insert_many(records)
        print(f"{len(records)} records inserted into MongoDB.")
    else:
        print("No records to insert.")

if __name__ == "__main__":
    domains = ["example.com", "test.com"]
    ips = ["8.8.8.8", "1.1.1.1"]
    hashes = ["abcd1234ef", "1234abcd56"]

    all_records = []

    for domain in domains:
        all_records.extend(fetch_domain_data(domain))

    for ip in ips:
        all_records.extend(fetch_ip_data(ip))

    for h in hashes:
        all_records.extend(fetch_hash_data(h))

    load_to_mongodb(all_records)
