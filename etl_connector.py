import os
import requests
import pymongo
import time
from datetime import datetime
from dotenv import load_dotenv

# Load credentials/settings from .env
load_dotenv()
SSL_LABS_EMAIL = os.getenv("SSL_LABS_EMAIL")
BASE_URL = "https://api.ssllabs.com/api/v4/analyze"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ssllabs_etl")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ssllabs_raw")

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

# Target hosts to scan
HOSTS = ["google.com", "bing.com", "yahoo.com", "cricbuzz.com", "youtube.com"]

def get_results(host):
    """
    Initiates an SSL Labs scan and polls until report is READY or ERROR.
    """
    params = {
        "host": host
    }
    headers = {
        "Content-Type": "application/json",
        "email": SSL_LABS_EMAIL
    }

    # Initial request to start scan
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    status = data.get("status")

    if status == "ERROR":
        raise Exception(f"{host} — API Error: {data.get('statusMessage')}")

    # Poll until scan completes
    while status not in ("READY", "ERROR"):
        print(f"Scanning {host}: status={status}")
        time.sleep(30)  # Respect API rate limits
        # Poll again with same headers and minimal params
        poll_params = {"host": host, "all": "done"}
        response = requests.get(BASE_URL, headers=headers, params=poll_params)
        response.raise_for_status()
        data = response.json()
        status = data.get("status")

        if status == "ERROR":
            raise Exception(f"{host} — API Error: {data.get('statusMessage')}")

    # If READY, return final report
    return data

def store_report(report, host):
    """
    Stores the SSL Labs scan report in MongoDB with ingestion timestamp.
    """
    doc = {
        "_id": f"{host}_{datetime.utcnow().isoformat()}",
        "host": host,
        "report": report,
        "ingested_at": datetime.utcnow()
    }
    db[COLLECTION_NAME].insert_one(doc)
    print(f"Stored report for {host}")

if __name__ == "__main__":
    for host in HOSTS:
        try:
            report = get_results(host)
            store_report(report, host)
        except Exception as e:
            print(f"Failed to process {host}: {e}")
