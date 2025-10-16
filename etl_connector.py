"""
ETL Connector for Blocklist.de
Author: K. Keerthana
Roll No: 3122225001060
Description: 
This script extracts data from multiple blocklist.de APIs, 
transforms them into structured JSON, and loads them into MongoDB.
"""

import os
import requests
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# ------------------ LOAD ENVIRONMENT VARIABLES ------------------
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# ------------------ CONNECT TO MONGODB ------------------
try:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("✅ MongoDB connection successful!")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    exit()

# ------------------ DEFINE API SOURCES ------------------
API_SOURCES = {
    "ssh": "https://api.blocklist.de/api/ssh/",
    "mail": "https://api.blocklist.de/api/mail/",
    "apache": "https://api.blocklist.de/api/apache/",
    "imap": "https://api.blocklist.de/api/imap/",
    "bots": "https://api.blocklist.de/api/bots/"
}

# ------------------ ETL FUNCTIONS ------------------

def extract_data(api_url):
    """Extract raw text data from API"""
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"⚠️ API returned status {response.status_code} for {api_url}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {api_url}: {e}")
        return None

def transform_data(raw_text):
    """Transform plain text IP list into structured list"""
    if not raw_text:
        return []
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    valid_ips = [ip for ip in lines if not ip.startswith("#")]  # skip comments
    return valid_ips

def load_to_mongo(source_name, data_list):
    """Load transformed data into MongoDB with timestamp"""
    if not data_list:
        print(f"⚠️ No data to insert for {source_name}. Skipping.")
        return

    document = {
        "source": source_name,
        "record_count": len(data_list),
        "data": data_list,
        "ingested_at": datetime.datetime.utcnow()
    }
    collection.insert_one(document)
    print(f"✅ Inserted {len(data_list)} records from {source_name} into MongoDB.")

# ------------------ MAIN ETL PROCESS ------------------

if __name__ == "__main__":
    print("\n🚀 Starting ETL Process for Blocklist APIs...\n")

    for name, url in API_SOURCES.items():
        print(f"🔹 Processing {name.upper()} API...")
        raw_data = extract_data(url)
        transformed = transform_data(raw_data)
        load_to_mongo(name, transformed)

    print("\n🎯 ETL Process Completed Successfully!")
