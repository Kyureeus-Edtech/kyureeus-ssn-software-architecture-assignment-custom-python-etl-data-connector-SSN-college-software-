import requests
import json
import pymongo
import os
from dotenv import load_dotenv

# ------------------ Load config from .env ------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mitre_attack")

# MITRE JSON endpoints for all 3 domains
MITRE_ENDPOINTS = {
    "enterprise-attack": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
    "mobile-attack": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/mobile-attack/mobile-attack.json",
    "ics-attack": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/ics-attack/ics-attack.json"
}

# ------------------ MongoDB Connection ------------------
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

print("\n[CONFIG] MongoDB connected.")
print(f"[CONFIG] Database: {DB_NAME}")
print("=" * 60)


# ------------------ Function Definitions ------------------
def extract_data(url):
    """Extract raw data from a given MITRE ATT&CK endpoint."""
    print(f"\n=== EXTRACT PHASE for {url} ===")
    print(f"Downloading MITRE ATT&CK data from: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"[ERROR] Failed to fetch data from {url}. Status Code: {response.status_code}")

    data = response.json()
    print(f"[INFO] Downloaded {len(data['objects'])} STIX objects successfully.")
    return data


def transform_record(record):
    """Transform a STIX attack-pattern record into a simpler MongoDB structure."""
    return {
        "id": record.get("id"),
        "name": record.get("name"),
        "description": record.get("description"),
        "created": record.get("created"),
        "modified": record.get("modified"),
        "kill_chain_phases": [phase.get("phase_name") for phase in record.get("kill_chain_phases", [])],
        "external_references": [
            {
                "source_name": ref.get("source_name"),
                "url": ref.get("url"),
                "description": ref.get("description")
            }
            for ref in record.get("external_references", [])
        ]
    }


def transform_data(data):
    """Filter and transform all 'attack-pattern' objects."""
    print("\n=== TRANSFORM PHASE ===")
    transformed = [transform_record(obj) for obj in data['objects'] if obj['type'] == 'attack-pattern']
    print(f"[INFO] Transformed {len(transformed)} 'attack-pattern' records.")
    return transformed


def load_data(collection_name, transformed_data):
    """Load transformed data into MongoDB."""
    print(f"\n=== LOAD PHASE for Collection: {collection_name} ===")
    collection = db[collection_name]
    if transformed_data:
        collection.delete_many({})  # clear old data
        collection.insert_many(transformed_data)
        print(f"[SUCCESS] Inserted {len(transformed_data)} records into collection '{collection_name}'.")
    else:
        print(f"[WARNING] No transformed data available for '{collection_name}'.")


# ------------------ Main ETL Flow ------------------
print("\n🚀 Starting multi-endpoint MITRE ATT&CK ETL Pipeline...\n")

for domain, url in MITRE_ENDPOINTS.items():
    print("=" * 60)
    print(f"\n📂 Processing Domain: {domain.upper()}")
    print("=" * 60)

    # 1️⃣ Extract
    data = extract_data(url)

    # Show a raw sample
    sample_raw = next((obj for obj in data['objects'] if obj['type'] == 'attack-pattern'), None)
    if sample_raw:
        print("\n[BEFORE TRANSFORMATION] Sample Record:")
        print(json.dumps(sample_raw, indent=2)[:500] + "\n...")

    # 2️⃣ Transform
    transformed_data = transform_data(data)

    # Show a transformed sample
    if transformed_data:
        print("\n[AFTER TRANSFORMATION] Sample Record:")
        print(json.dumps(transformed_data[0], indent=2))

    # 3️⃣ Load
    load_data(domain.replace("-", "_"), transformed_data)

print("\n✅ ETL Pipeline for all MITRE endpoints completed successfully!")
print("=" * 60)
