import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CISA_URL = os.getenv("CISA_URL")

def extract():
    print("[*] Extracting data from CISA KEV API...")
    resp = requests.get(CISA_URL)
    resp.raise_for_status()
    return resp.json()

def transform(data):
    print("[*] Transforming data...")
    transformed = []
    for v in data.get("vulnerabilities", []):
        try:
            transformed.append({
                "cve_id": v.get("cveID"),
                "vendor_project": v.get("vendorProject"),
                "product": v.get("product"),
                "description": v.get("description"),
                "date_added": datetime.fromisoformat(v.get("dateAdded")),
                "due_date": datetime.fromisoformat(v.get("dueDate")),
                "notes": v.get("notes"),
                "required_action": v.get("requiredAction")
            })
        except Exception as e:
            print(f"[!] Error parsing {v.get('cveID')}: {e}")
    return transformed

def load(data):
    print("[*] Loading into MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    for item in data:
        collection.update_one(
            {"cve_id": item["cve_id"]},
            {"$set": item},
            upsert=True
        )
    print(f"[✓] Loaded {len(data)} records into MongoDB.")

if __name__ == "__main__":
    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)
    print("[✓] ETL process complete.")
