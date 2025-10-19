# etl_connector.py

import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient

# --- Configuration ---
BASE_URL = "https://attack-taxii.mitre.org/api/v21"
ENTERPRISE_COLLECTION_ID = "x-mitre-collection--1f5f1533-f617-4ca8-9ab4-6a02367fa019"
HEADERS = {"Accept": "application/taxii+json;version=2.1"}

# --- Database and Data Handling Functions ---

def connect_to_mongodb(mongo_uri):
    """Establishes a connection to MongoDB."""
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ismaster')
        print("✅ MongoDB connection successful.")
        return client.get_database("software_architecture_assignment")
    except Exception as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        return None

def load_to_mongodb(db, data, collection_name):
    """
    Loads transformed data into a specified MongoDB collection.
    It intelligently uses the record's '_id' field if present, otherwise it uses the 'id' field.
    """
    if not data:
        print(f"⚠️ No data to load for '{collection_name}'.")
        return
    
    collection = db[collection_name]
    print(f"➡️ Loading {len(data)} records into '{collection_name}'...")
    
    for record in data:
        # Determine the unique key for the MongoDB document.
        # The sophisticated transform creates '_id', the generic ones leave the original 'id'.
        mongo_id = record.get('_id') or record.get('id')
        
        if not mongo_id:
            print(f"⚠️ Skipping record due to missing 'id' or '_id' field: {record}")
            continue
        
        collection.update_one({'_id': mongo_id}, {'$set': record}, upsert=True)
        
    print(f"✅ Load complete for '{collection_name}'.")

# --- Transformation Functions ---

def transform_generic(data_list):
    """A simple transform that just adds an ingestion timestamp."""
    for record in data_list:
        record['ingestion_timestamp'] = datetime.now(timezone.utc)
    return data_list

def transform_attack_pattern(attack_patterns):
    """
    A sophisticated transform for attack-pattern objects.
    It selects key fields, enriches the data, and standardizes the format.
    """
    transformed_list = []
    for pattern in attack_patterns:
        attack_id_ref = next((ref for ref in pattern.get("external_references", []) if ref.get("source_name") == "mitre-attack"), {})
        
        transformed_pattern = {
            "_id": pattern.get("id"),
            "name": pattern.get("name"),
            "description": pattern.get("description"),
            "attack_id": attack_id_ref.get("external_id"),
            "attack_url": attack_id_ref.get("url"),
            "platforms": pattern.get("x_mitre_platforms", []),
            "tactics": [phase.get("phase_name") for phase in pattern.get("kill_chain_phases", [])],
            "created": datetime.fromisoformat(pattern.get("created")),
            "modified": datetime.fromisoformat(pattern.get("modified")),
            "ingestion_timestamp": datetime.now(timezone.utc)
        }
        transformed_list.append(transformed_pattern)
        
    return transformed_list

# --- ETL Functions for Each Endpoint ---

def etl_for_all_collections(db):
    """ETL for Endpoint 1: Fetches metadata for all available collections."""
    print("\n--- Running ETL for Endpoint 1: /collections ---")
    endpoint_url = f"{BASE_URL}/collections/"
    
    print(f"➡️ Extracting data from {endpoint_url}")
    response = requests.get(endpoint_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    collections = response.json().get("collections", [])
    
    transformed_data = transform_generic(collections)
    
    load_to_mongodb(db, transformed_data, "mitre_collections_metadata")

def etl_for_attack_patterns(db):
    """ETL for Endpoint 2: Fetches 'attack-pattern' objects from the Enterprise collection."""
    print("\n--- Running ETL for Endpoint 2: /objects (Attack Patterns) ---")
    endpoint_url = f"{BASE_URL}/collections/{ENTERPRISE_COLLECTION_ID}/objects/"
    params = {"match[type]": "attack-pattern"}

    print(f"➡️ Extracting data from {endpoint_url}")
    response = requests.get(endpoint_url, headers=HEADERS, params=params, timeout=60)
    response.raise_for_status()
    objects = response.json().get("objects", [])
    
    print(f"➡️ Transforming {len(objects)} attack patterns...")
    transformed_data = transform_attack_pattern(objects)
    
    load_to_mongodb(db, transformed_data, "mitre_attack_patterns")

def etl_for_collection_manifest(db):
    """ETL for Endpoint 3: Fetches the manifest of all objects in the Enterprise collection."""
    print("\n--- Running ETL for Endpoint 3: /collections/{id}/manifest ---")
    endpoint_url = f"{BASE_URL}/collections/{ENTERPRISE_COLLECTION_ID}/manifest/"

    print(f"➡️ Extracting data from {endpoint_url}")
    response = requests.get(endpoint_url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    manifest_objects = response.json().get("objects", [])
    
    transformed_data = transform_generic(manifest_objects)

    load_to_mongodb(db, transformed_data, "mitre_collection_manifest")

def main():
    """Main function to run the ETL pipelines."""
    print("🚀 Starting ETL pipelines using 'requests' library...")
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        print("❌ MONGO_URI not found in .env file. Exiting.")
        return

    db = connect_to_mongodb(mongo_uri)
    
    if db is not None:
        try:
            etl_for_all_collections(db)
            etl_for_attack_patterns(db)
            etl_for_collection_manifest(db)
        except requests.exceptions.RequestException as e:
            print(f"\n❌ A network or API error occurred: {e}")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
    
    print("\n🏁 All ETL pipelines finished.")

if __name__ == "__main__":
    main()