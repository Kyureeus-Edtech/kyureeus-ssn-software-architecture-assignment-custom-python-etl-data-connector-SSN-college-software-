import os
import sys
import time
import requests
import pymongo
from dotenv import load_dotenv
import ipaddress

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GREYNOISE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

if not API_KEY:
    print("Error: GREYNOISE_API_KEY not found in .env file")
    sys.exit(1)

BASE_URL = "https://api.greynoise.io/v3/ip"
MAX_RETRIES = 3
RETRY_DELAY = 2 

# Validate IP Address
def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

# Extract (with retries)
def fetch_ip_data(ip):
    url = f"{BASE_URL}/{ip}"
    headers = {
        "key": API_KEY,
        "Accept": "application/json"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Error fetching {ip}: 404 - IP not found")
                return None
            else:
                print(f"Error fetching {ip}: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Timeout for {ip} (Attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"Skipping {ip} after {MAX_RETRIES} failed attempts")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {ip}: {e}")
            return None

# Transform
def transform_data(raw_data):
    if not raw_data:
        return None
    return {
        "ip": raw_data.get("ip"),
        "category": raw_data.get("business_service_intelligence", {}).get("category"),
        "name": raw_data.get("business_service_intelligence", {}).get("name"),
        "description": raw_data.get("business_service_intelligence", {}).get("description"),
        "trust_level": raw_data.get("business_service_intelligence", {}).get("trust_level"),
        "last_updated": raw_data.get("business_service_intelligence", {}).get("last_updated"),
    }

# Load
def load_to_mongo(data):
    if not data:
        return
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["greynoise_db"]
        collection = db["ip_data"]
        collection.insert_one(data)
        print(f"Inserted into MongoDB: {data['ip']}")
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")

# Process Single IP
def process_ip(ip_address):
    if not validate_ip(ip_address):
        print(f"Invalid IP address: {ip_address}")
        return
    raw_data = fetch_ip_data(ip_address)
    transformed_data = transform_data(raw_data)
    load_to_mongo(transformed_data)

# Main ETL for File
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python etl_connector.py <path_to_txt_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, "r") as f:
        ip_list = [line.strip() for line in f if line.strip()]

    print(f"Found {len(ip_list)} IPs in file.")
    for ip in ip_list:
        process_ip(ip)
