import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from config.mongo import mongoConfig
from config.blocklist import blocklistConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection_latest = db[mongoConfig["COLLECTION_LATEST"]]

def extract_latest(diff_time=None, service=None):
    params = {}
    if diff_time is not None:
        params["time"] = diff_time
    if service is not None:
        params["service"] = service
    url = blocklistConfig["GETLAST_URL"]
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json() if response.headers.get('Content-Type','').startswith('application/json') else response.text
    return data

def transform_latest(raw_data, service=None):
    now = datetime.utcnow().isoformat() + "Z"
    doc = {
        "queried_at": now,
        "service": service,
        "raw": raw_data
    }
    # If raw_data is list of IPs, you might want to store differently
    if isinstance(raw_data, list):
        doc["ips"] = raw_data
    return doc

def load_latest(doc):
    if doc:
        collection_latest.insert_one(doc)
        print("Inserted latest-IPs document.")
    else:
        print("No document to insert.")

def main_latest(diff_time=None, service=None):
    try:
        raw = extract_latest(diff_time=diff_time, service=service)
        doc = transform_latest(raw, service=service)
        load_latest(doc)
    except Exception as e:
        print(f"Latest-IPs ETL failed: {e}")

if _name_ == "_main_":
    # Example: last 3600 seconds, service "ssh"
    main_latest(diff_time=3600, service="ssh")