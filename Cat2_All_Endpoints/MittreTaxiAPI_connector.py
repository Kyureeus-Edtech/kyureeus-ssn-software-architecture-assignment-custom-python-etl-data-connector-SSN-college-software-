import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

BASE_URL = "https://attack-taxii.mitre.org/api/v21"


def fetch_data(endpoint):
    # Fetch data from API with proper headers.
    headers = {"Accept": "application/taxii+json;version=2.1"}
    try:
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def store_in_mongo(collection_name, data):
    # Store data in MongoDB.
    if not data:
        return
    try:
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        db = client.mitre_attack

        db[collection_name].insert_one({
            "data": data,
            "ingested_at": datetime.now(timezone.utc)
        })
        print(f"Stored {collection_name}")
    except Exception as e:
        print(f"MongoDB insert failed: {e}")
    finally:
        if 'client' in locals():
            client.close()

# ---------------------- ETL Steps ----------------------

def etl_collections():
    # Step 1: Fetch collections and store.
    url = f"{BASE_URL}/collections"
    data = fetch_data(url)
    if not data:
        return []

    collections = data.get("collections", [])
    store_in_mongo("collections", collections)
    return [col["id"] for col in collections[:3]]

def etl_manifest(collection_ids):
    # Step 2: Fetch manifest for each collection and store (limit 3).
    for cid in collection_ids:
        url = f"{BASE_URL}/collections/{cid}/manifest"
        data = fetch_data(url)
        if not data:
            continue

        objects = data.get("objects", [])[:3]  # limit 3 objects
        store_in_mongo("manifest", {"collection_id": cid, "objects": objects})

def etl_objects(collection_ids):
    # Step 3: Fetch objects for each collection and store (limit 5 + x_mitre_contents limit 5).
    object_ids = {}
    for cid in collection_ids:
        url = f"{BASE_URL}/collections/{cid}/objects"
        data = fetch_data(url)
        if not data:
            continue

        objects = data.get("objects", [])[:3]  # limit 3 objects
        for obj in objects:
            if "x_mitre_contents" in obj:
                obj["x_mitre_contents"] = obj["x_mitre_contents"][:3]  # limit to 3

        store_in_mongo("objects", {"collection_id": cid, "objects": objects})
        object_ids[cid] = [obj["id"] for obj in objects]

    return object_ids

def etl_versions(collection_ids, object_map):
    # Step 4: Fetch versions for each object and store.
    for cid in collection_ids:
        for obj_id in object_map.get(cid, []):
            url = f"{BASE_URL}/collections/{cid}/objects/{obj_id}/versions"
            data = fetch_data(url)
            if not data:
                continue
            store_in_mongo("versions", {"collection_id": cid, "object_id": obj_id, "versions": data})



if __name__ == "__main__":
    collection_ids = etl_collections()
    etl_manifest(collection_ids)
    object_map = etl_objects(collection_ids)
    etl_versions(collection_ids, object_map)
