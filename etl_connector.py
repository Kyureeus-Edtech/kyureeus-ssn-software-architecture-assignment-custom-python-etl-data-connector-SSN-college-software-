import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

DB_NAME = "Cloudflare"
COLLECTION_NAME = "Request_Trace_Raw"

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/request-tracer/trace"


# EXTRACT
def extract_data(url_to_trace, method="GET", protocol="HTTP/1.1", headers=None, cookies=None):
    """Send a trace request to Cloudflare API and return the JSON response"""
    try:
        payload = {
            "method": method,
            "url": url_to_trace,
            "protocol": protocol,
            "headers": headers or {},
            "cookies": cookies or {}
        }

        resp = requests.post(
            BASE_URL,
            headers={
                "X-Auth-Email": CLOUDFLARE_EMAIL,
                "X-Auth-Key": CLOUDFLARE_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=20
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error extracting Cloudflare trace data: {e}")
        return None


# TRANSFORM
def transform_data(data):
    """Simplify and structure Cloudflare trace data for MongoDB"""
    if not data or not isinstance(data, dict):
        return None

    # Extract key fields if available
    result = data.get("result", {})
    summary = {
        "trace_id": result.get("trace_id"),
        "method": result.get("method"),
        "url": result.get("url"),
        "protocol": result.get("protocol"),
        "colo": result.get("colo"),
        "ray_id": result.get("ray_id"),
        "status": "success" if data.get("success") else "failed",
        "errors": data.get("errors"),
        "messages": data.get("messages"),
        "ingested_at": datetime.utcnow()
    }
    return summary


# LOAD
def load_data(data):
    """Insert transformed data into MongoDB"""
    if data:
        collection.insert_one(data)
        print(f"✅ Trace data inserted for URL: {data.get('url')} at {data.get('ingested_at')}")
    else:
        print("⚠️ No data to insert.")


# RUN ETL
def run_etl(url_to_trace):
    try:
        raw = extract_data(url_to_trace)
        transformed = transform_data(raw)
        load_data(transformed)
    except Exception as e:
        print(f"ETL process failed: {e}")


# MAIN
if __name__ == "__main__":
    target_url = "https://www.cloudflare.com/"
    run_etl(target_url)
