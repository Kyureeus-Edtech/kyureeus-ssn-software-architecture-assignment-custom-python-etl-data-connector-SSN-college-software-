import os
import time
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ssn_sw_arch")
CONNECTOR_NAME = os.getenv("CONNECTOR_NAME", "freegeoip_connector")
FREEGEOIP_BASE = os.getenv("FREEGEOIP_BASE", "https://freegeoip.app")
RPS = float(os.getenv("RPS", "5"))
SLEEP_BETWEEN = 1.0 / max(RPS, 1.0)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[f"{CONNECTOR_NAME}_raw"]

# Default list of IPs
IPS = ["8.8.8.8", "1.1.1.1", "example.com"]

def fetch_data(ip, fmt):
    """Fetch data from FreeGeoIP API in specified format"""
    url = f"{FREEGEOIP_BASE}/{fmt}/{ip}"
    try:
        response = requests.get(url)
        time.sleep(SLEEP_BETWEEN)
        if response.status_code == 200:
            return response.text
        else:
            print(f"⚠️  Failed for {ip} in {fmt} format: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def parse_csv(csv_text):
    reader = csv.reader(csv_text.strip().splitlines())
    rows = list(reader)
    if len(rows) >= 2:
        header, values = rows[0], rows[1]
        return dict(zip(header, values))
    return {}

def parse_xml(xml_text):
    try:
        root = ET.fromstring(xml_text)
        return {child.tag: child.text for child in root}
    except Exception:
        return {"raw_xml": xml_text}

def transform_data(fmt, data_text):
    if fmt == "json":
        return json.loads(data_text)
    elif fmt == "csv":
        return parse_csv(data_text)
    elif fmt == "xml":
        return parse_xml(data_text)
    else:
        return {"raw": data_text}

def etl_process():
    for ip in IPS:
        print(f"\n🔹 Processing IP: {ip}")
        for fmt in ["json", "csv", "xml"]:
            raw_data = fetch_data(ip, fmt)
            if raw_data:
                transformed = transform_data(fmt, raw_data)
                document = {
                    "ip": ip,
                    "format": fmt,
                    "data": transformed,
                    "timestamp": datetime.utcnow()
                }
                collection.insert_one(document)
                print(f"✅ Inserted {fmt.upper()} data for {ip}")

if __name__ == "__main__":
    etl_process()
