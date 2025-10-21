import os
import time
import logging
import pymongo
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "abusech_db")
THREATFOX_KEY = os.getenv("THREATFOX_AUTH_KEY")
URLHAUS_KEY = os.getenv("URLHAUS_AUTH_KEY")

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

logging.basicConfig(level=logging.INFO)

def load_to_mongo(collection_name, docs):
    if not docs:
        logging.info(f"No docs to insert for {collection_name}")
        return
    coll = db[collection_name]
    # add ingestion timestamp to each doc
    for d in docs:
        d["_ingested_at"] = datetime.utcnow()
    coll.insert_many(docs)
    logging.info(f"Inserted {len(docs)} docs into {collection_name}")

### Connector 1: ThreatFox – get IOCs
def extract_threatfox(days=1):
    url = "https://threatfox-api.abuse.ch/api/v1/"
    headers = {"Auth-Key": THREATFOX_KEY}
    data = {"query": "get_iocs", "days": days}
    resp = requests.post(url, json=data, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])

def transform_threatfox(records):
    transformed = []
    for rec in records:
        # your transform logic: pick relevant fields
        transformed.append({
            "ioc": rec.get("ioc"),
            "ioc_type": rec.get("ioc_type"),
            "threat_type": rec.get("threat_type"),
            "malware": rec.get("malware"),
            "first_seen": rec.get("first_seen"),
            "last_seen": rec.get("last_seen"),
            "reporter": rec.get("reporter")
        })
    return transformed

def run_threatfox():
    logging.info("Running ThreatFox connector")
    raw = extract_threatfox(days=3)
    clean = transform_threatfox(raw)
    load_to_mongo("threatfox_raw", clean)



### Connector 2 Alternative: FeodoTracker – IP blocklist
def extract_feodotracker():
    url = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    lines = resp.text.splitlines()
    records = []

    for line in lines:
        # skip comments and empty lines
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 2:
            continue
        ip, first_seen = parts[0], parts[1]
        records.append({"ip": ip, "first_seen": first_seen, "source": "FeodoTracker"})

    return records

def transform_feodotracker(records):
    # already in dict format
    return records

def run_feodotracker():
    logging.info("Running FeodoTracker connector")
    raw = extract_feodotracker()
    logging.info(f"FeodoTracker raw response count: {len(raw)}")
    load_to_mongo("feodotracker_raw", raw)



### Connector 3: URLhaus – get URL IOC data
def extract_urlhaus(limit=100):
    url = "https://urlhaus-api.abuse.ch/v1/urls/recent/"
    headers = {"Auth-Key": URLHAUS_KEY}  # include your key here
    params = {"limit": limit}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("urls", [])

def transform_urlhaus(records):
    transformed = []
    for rec in records:
        transformed.append({
            "url": rec.get("url"),
            "host": rec.get("host"),
            "threat": rec.get("threat"),
            "tags": rec.get("tags"),
            "firstseen": rec.get("dateadded"),
            "reporter": rec.get("reporter"),
            "source": "URLhaus"
        })
    return transformed

def run_urlhaus():
    logging.info("Running URLhaus connector")
    raw = extract_urlhaus(limit=100)
    clean = transform_urlhaus(raw)
    load_to_mongo("urlhaus_raw", clean)


def main():
    try:
        run_threatfox()
        time.sleep(2)
        print()
        run_feodotracker()
        time.sleep(2)
        print()
        run_urlhaus()
    except Exception as e:
        logging.exception("ETL run failed")

if __name__ == "__main__":
    main()
