"""
FreeGeoIP ETL Connector
Author: <Your Name>
Roll No: <Your Roll Number>
Course: SSN CSE - Software Architecture (Kyureeus EdTech)
"""

import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

FREEGEOIP_URL = os.getenv("FREEGEOIP_URL", "https://freegeoip.app/json/")
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("⚠️ Missing Mongo URI in .env file!")


client = MongoClient(MONGO_URI)
db = client["etl_connectors"]
collection = db["freegeoip_raw"]

def extract_geoip_data(ip_address=None):
    """
    Extract geolocation data from FreeGeoIP API.
    If IP not given, returns your own public IP details.
    """
    url = f"{FREEGEOIP_URL}{ip_address or ''}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ API Request Failed: {response.status_code} - {response.text}")
        return None

    return response.json()


def transform_data(raw_data):
    """Transform raw FreeGeoIP data for MongoDB storage."""
    if not raw_data:
        return None

    transformed = {
        "ip": raw_data.get("ip"),
        "country_code": raw_data.get("country_code"),
        "country_name": raw_data.get("country_name"),
        "region_code": raw_data.get("region_code"),
        "region_name": raw_data.get("region_name"),
        "city": raw_data.get("city"),
        "zip_code": raw_data.get("zip_code"),
        "latitude": raw_data.get("latitude"),
        "longitude": raw_data.get("longitude"),
        "time_zone": raw_data.get("time_zone"),
        "timestamp": datetime.utcnow()
    }
    return transformed


def load_to_mongodb(data):
    """Load transformed data into MongoDB collection."""
    if not data:
        print("⚠️ No data to load into MongoDB.")
        return
    result = collection.insert_one(data)
    print(f"✅ Data inserted with ID: {result.inserted_id}")


def run_etl(ip_address=None):
    print("🚀 Starting ETL Pipeline for FreeGeoIP API...")
    raw = extract_geoip_data(ip_address)
    transformed = transform_data(raw)
    load_to_mongodb(transformed)
    print("🎯 ETL Process Completed Successfully!\n")

if __name__ == "__main__":
    # You can test with multiple IPs
    for ip in [None, "8.8.8.8", "1.1.1.1"]:
        run_etl(ip)
