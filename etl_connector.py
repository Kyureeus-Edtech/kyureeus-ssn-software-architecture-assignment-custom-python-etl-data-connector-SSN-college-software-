import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set ABUSEIPDB_API_KEY in your .env file.")

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["etl_database"]
collection = db["abuseipdb_raw"]

# Function to extract data from AbuseIPDB
def extract_data(ip_address, max_age=90):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": max_age
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data for {ip_address}: {e}")
        return None

# Function to transform data
def transform_data(raw_json):
    if not raw_json or "data" not in raw_json:
        return None
    
    data = raw_json["data"]
    return {
        "ipAddress": data.get("ipAddress"),
        "isWhitelisted": data.get("isWhitelisted"),
        "abuseConfidenceScore": data.get("abuseConfidenceScore"),
        "countryCode": data.get("countryCode"),
        "usageType": data.get("usageType"),
        "isp": data.get("isp"),
        "domain": data.get("domain"),
        "totalReports": data.get("totalReports"),
        "lastReportedAt": data.get("lastReportedAt"),
        "ingestion_time": datetime.utcnow()
    }

# Function to load into MongoDB
def load_data(document):
    if document:
        collection.insert_one(document)
        print(f"[INFO] Inserted data for IP {document['ipAddress']} into MongoDB")

if __name__ == "__main__":
    ips = ["8.8.8.8", "1.1.1.1", "45.33.32.156"]  # Example IPs

    for ip in ips:
        raw = extract_data(ip)
        if not raw or "data" not in raw:
            print(f"[WARNING] No data returned for IP {ip}")
            continue

        transformed = transform_data(raw)
        if not transformed:
            print(f"[WARNING] Transformation failed for IP {ip}")
            continue

        load_data(transformed)
