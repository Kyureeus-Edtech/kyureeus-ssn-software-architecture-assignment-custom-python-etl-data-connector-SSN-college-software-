import os
import requests
import pymongo
from datetime import datetime

from config.wayback import waybackConfig
from config.mongo import mongoConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection_availability = db[mongoConfig["COLLECTION_AVAILABILITY"]]

def extract_availability(url, timestamp=None, closest="either", status_code=None, tag=None):
    params = {
        "url": url,
        "closest": closest
    }
    if timestamp:
        params["timestamp"] = timestamp
    if status_code:
        params["status_code"] = status_code
    if tag:
        params["tag"] = tag
    response = requests.get(waybackConfig["BASE_URL"] + "/wayback/v1/available", params=params)
    response.raise_for_status()
    data = response.json()
    return data

def transform_availability(record, url, tag=None):
    now = datetime.utcnow().isoformat() + 'Z'
    snapshot = record.get("archived_snapshots", {}).get("closest", {}) or {}
    doc = {
        "url": url,
        "queried_at": now,
        "timestamp_requested": record.get("timestamp"),
        "tag": tag,
        "snapshot_status": snapshot.get("status"),
        "snapshot_url": snapshot.get("url"),
        "snapshot_timestamp": snapshot.get("timestamp")
    }
    return doc

def load_availability(doc):
    if doc:
        collection_availability.insert_one(doc)
        print(f"Inserted availability doc for url {doc['url']}")
    else:
        print("No record to insert.")

def main_availability(url_list, timestamp=None):
    for url in url_list:
        try:
            raw = extract_availability(url, timestamp=timestamp)
            doc = transform_availability(raw, url)
            load_availability(doc)
        except Exception as e:
            print(f"Availability ETL failed for {url}: {e}")

if __name__ == "__main__":
    urls = ["https://example.com", "https://someotherdomain.com"]
    main_availability(urls, timestamp="20250101")
