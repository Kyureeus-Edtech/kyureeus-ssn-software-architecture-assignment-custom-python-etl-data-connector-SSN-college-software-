import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser

load_dotenv()
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

if not SHODAN_API_KEY:
    raise ValueError("SHODAN_API_KEY not found in .env file")

client = MongoClient("mongodb://localhost:27017/")
db = client["etl_database"]
collection = db["shodan_host_raw"]


def extract_shodan_data(ip_address):
    """Fetch host data from Shodan API."""
    url = f"https://api.shodan.io/shodan/host/{ip_address}?key={SHODAN_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data for {ip_address}: {e}")
        return None


def transform_data(data):
    """Flatten, clean, and standardize Shodan API response for MongoDB."""
    if not data:
        return None

    transformed = {
        "ip": data.get("ip_str"),
        "asn": data.get("asn"),
        "org": data.get("org"),
        "isp": data.get("isp"),
        "country": data.get("country_name"),
        "country_code": data.get("country_code"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "last_update": parser.parse(data["last_update"]) if data.get("last_update") else None,
        "domains": data.get("domains", []),
        "hostnames": data.get("hostnames", []),
        "ports": data.get("ports", []),

        # Extract simplified service info from 'data' array
        "services": [
            {
                "port": s.get("port"),
                "transport": s.get("transport"),
                "org": s.get("org"),
                "asn": s.get("asn"),
                "domains": s.get("domains", []),
                "timestamp": parser.parse(s["timestamp"]) if s.get("timestamp") else None
            }
            for s in data.get("data", [])
        ],

        # ETL metadata
        "_etl_source": "shodan",
        "_etl_ingested_at": datetime.utcnow(),
        "_etl_version": "1.0"
    }

    return transformed


def load_to_mongodb(data):
    """Insert transformed data into MongoDB."""
    if data:
        collection.insert_one(data)
        print(f"[INFO] Inserted document for IP: {data.get('ip')}")


if __name__ == "__main__":
    # Example: Single IP lookup
    test_ip = "8.8.8.8"
    raw_data = extract_shodan_data(test_ip)
    transformed_data = transform_data(raw_data)
    load_to_mongodb(transformed_data)
