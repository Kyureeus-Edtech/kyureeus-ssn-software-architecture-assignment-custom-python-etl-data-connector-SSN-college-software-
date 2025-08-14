import requests
import json
import pymongo
import os
from dotenv import load_dotenv

# ------------------ Load config from .env ------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mitre_attack")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "techniques")
MITRE_JSON_URL = os.getenv(
    "MITRE_JSON_URL",
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"
)

# ------------------ MongoDB Connection ------------------
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("\n[CONFIG] MongoDB connected.")
print(f"[CONFIG] Database: {DB_NAME}, Collection: {COLLECTION_NAME}")

# ------------------ Extract ------------------
print("\n=== EXTRACT PHASE ===")
print(f"Downloading MITRE ATT&CK data from {MITRE_JSON_URL} ...")
response = requests.get(MITRE_JSON_URL)

if response.status_code != 200:
    raise Exception(f"Failed to fetch data. Status Code: {response.status_code}")

data = response.json()
print(f"Downloaded {len(data['objects'])} STIX objects.")

# Show sample raw data
sample_raw = next((obj for obj in data['objects'] if obj['type'] == 'attack-pattern'), None)
print("\n[BEFORE TRANSFORMATION] Sample record:")
print(json.dumps(sample_raw, indent=2)[:500] + "\n...")

# ------------------ Transform ------------------
print("\n=== TRANSFORM PHASE ===")

def transform_record(record):
    """Convert STIX attack-pattern to a cleaner MongoDB-friendly structure."""
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

transformed_data = [
    transform_record(obj) for obj in data['objects'] if obj['type'] == 'attack-pattern'
]

# Show transformed sample
print("\n[AFTER TRANSFORMATION] Sample record:")
print(json.dumps(transformed_data[0], indent=2))

# ------------------ Load ------------------
print("\n=== LOAD PHASE ===")
if transformed_data:
    collection.delete_many({})  # Clear old data
    collection.insert_many(transformed_data)
    print(f"Inserted {len(transformed_data)} transformed records into MongoDB.")
else:
    print("No transformed data to insert.")

print("\n✅ ETL Pipeline completed successfully!")
