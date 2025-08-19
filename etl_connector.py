import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
BASE_URL = os.getenv("BASE_URL")
ENDPOINT = os.getenv("ENDPOINT")


def extract_data():
    """Fetch TXT data from DShield Top Attackers endpoint."""
    url = BASE_URL + ENDPOINT
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")
    return response.text

def transform_data(raw_txt):
    """Transform the raw TXT data into structured JSON."""
    lines = raw_txt.strip().split("\n")
    structured_data = []
    
    # First line is header, skip it
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ip, reports, targets = parts[0], parts[1], parts[2]
        structured_data.append({
            "ip": ip,
            "reports": int(reports),
            "targets": int(targets),
            "ingested_at": datetime.datetime.utcnow()
        })
    return structured_data

def load_to_mongodb(data):
    """Insert structured data into MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client["security_data"]
    collection = db["dshield_top_attackers_raw"]
    if data:
        collection.insert_many(data)
        print(f"Inserted {len(data)} records into MongoDB.")
    else:
        print("No data to insert.")

def run_etl():
    """Run the full ETL pipeline."""
    print("Starting ETL for DShield Top Attackers...")
    raw_txt = extract_data()
    data = transform_data(raw_txt)
    load_to_mongodb(data)
    print("ETL process completed.")

if __name__ == "__main__":
    run_etl()