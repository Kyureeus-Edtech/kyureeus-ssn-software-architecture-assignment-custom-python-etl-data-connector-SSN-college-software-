import os
import time
import logging
import pymongo
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGODB_DB", "abusech_db")
THREATFOX_KEY = os.getenv("THREATFOX_AUTH_KEY")
URLHAUS_KEY = os.getenv("URLHAUS_AUTH_KEY")

# MongoDB client setup
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def insert_documents(collection_name, documents):
    """Insert documents into MongoDB with ingestion timestamp"""
    if not documents:
        logging.info(f"No documents to insert into {collection_name}")
        return
    collection = db[collection_name]
    for doc in documents:
        doc["_ingested_at"] = datetime.utcnow()
    collection.insert_many(documents)
    logging.info(f"Inserted {len(documents)} documents into {collection_name}")


# --------------------- Connector 1: ThreatFox ---------------------
def fetch_threatfox(days=1):
    url = "https://threatfox-api.abuse.ch/api/v1/"
    headers = {"Auth-Key": THREATFOX_KEY}
    payload = {"query": "get_iocs", "days": days}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("data", [])


def transform_threatfox(records):
    transformed = []
    for rec in records:
        transformed.append({
            "ioc": rec.get("ioc"),
            "ioc_type": rec.get("ioc_type"),
            "threat_type": rec.get("threat_type"),
            "malware": rec.get("malware"),
            "first_seen": rec.get("first_seen"),
            "last_seen": rec.get("last_seen"),
            "reporter": rec.get("reporter"),
        })
    return transformed


def run_threatfox():
    logging.info("Running ThreatFox ETL")
    raw_data = fetch_threatfox(days=3)
    processed = transform_threatfox(raw_data)
    insert_documents("threatfox_raw", processed)


# --------------------- Connector 2: FeodoTracker ---------------------
def fetch_feodotracker():
    url = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    records = []

    for line in response.text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            ip, first_seen = parts[0], parts[1]
            records.append({"ip": ip, "first_seen": first_seen, "source": "FeodoTracker"})
    return records


def run_feodotracker():
    logging.info("Running FeodoTracker ETL")
    raw_data = fetch_feodotracker()
    logging.info(f"FeodoTracker returned {len(raw_data)} records")
    insert_documents("feodotracker_raw", raw_data)


# --------------------- Connector 3: URLhaus ---------------------
def fetch_urlhaus(limit=100):
    url = "https://urlhaus-api.abuse.ch/v1/urls/recent/"
    headers = {"Auth-Key": URLHAUS_KEY}
    params = {"limit": limit}
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("urls", [])


def transform_urlhaus(records):
    transformed = []
    for rec in records:
        transformed.append({
            "url": rec.get("url"),
            "host": rec.get("host"),
            "threat": rec.get("threat"),
            "tags": rec.get("tags"),
            "first_seen": rec.get("dateadded"),
            "reporter": rec.get("reporter"),
            "source": "URLhaus"
        })
    return transformed


def run_urlhaus():
    logging.info("Running URLhaus ETL")
    raw_data = fetch_urlhaus(limit=100)
    processed = transform_urlhaus(raw_data)
    insert_documents("urlhaus_raw", processed)


# --------------------- Main ETL Runner ---------------------
def main():
    try:
        run_threatfox()
        time.sleep(2)
        run_feodotracker()
        time.sleep(2)
        run_urlhaus()
    except Exception as e:
        logging.exception("ETL execution failed!")


if __name__ == "__main__":
    main()
