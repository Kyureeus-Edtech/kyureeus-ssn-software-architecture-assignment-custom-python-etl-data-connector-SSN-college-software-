import os
import requests
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# -------------------------------------------------
# STEP 1: Load environment variables
# -------------------------------------------------
load_dotenv()
BASE_URL = os.getenv("RIPESTAT_BASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# -------------------------------------------------
# STEP 2: MongoDB connection setup
# -------------------------------------------------
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["ripe_connector_raw"]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    exit()

# -------------------------------------------------
# STEP 3: Extract Function
# -------------------------------------------------
def extract_data(endpoint, params=None):
    """Fetch data from a given RIPEstat endpoint."""
    try:
        url = f"{BASE_URL}/{endpoint}/data.json"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        print(f"[EXTRACT] Successfully fetched data from {endpoint}.")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] Failed to fetch {endpoint}: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"[ERROR] Connection issue while fetching {endpoint}: {err}")
        return None

# -------------------------------------------------
# STEP 4: Transform Function
# -------------------------------------------------
def transform_data(raw_data, endpoint_name):
    """Clean and standardize the API response for MongoDB storage."""
    if raw_data is None:
        print(f"[TRANSFORM] Skipping {endpoint_name} — no data extracted.")
        return None

    transformed = {
        "endpoint": endpoint_name,
        "timestamp": datetime.datetime.now(datetime.UTC),
        "data_call_name": raw_data.get("data_call_name", "unknown"),
        "data": raw_data.get("data", {}),
        "metadata": raw_data.get("metadata", {}),
    }

    print(f"[TRANSFORM] Data transformed for {endpoint_name}.")
    return transformed

# -------------------------------------------------
# STEP 5: Load Function
# -------------------------------------------------
def load_data(transformed_data):
    """Insert transformed data into MongoDB."""
    if transformed_data:
        try:
            result = collection.insert_one(transformed_data)
            print(f"[LOAD] Inserted document ID: {result.inserted_id}")
        except Exception as e:
            print(f"[ERROR] Failed to insert data into MongoDB: {e}")
    else:
        print("[LOAD] No data to insert.")

# -------------------------------------------------
# STEP 6: Run ETL for 3 RIPEstat endpoints
# -------------------------------------------------
def run_etl():
    print("🚀 Starting RIPEstat ETL pipeline (3-endpoint version)...")

    endpoints = [
        "as-overview",              # Overview of AS details
        "as-routing-consistency",   # Routing consistency info
        "asn-neighbours"            # ASN neighbour details
    ]

    params_list = [
        {"resource": "AS3333"},       # Example ASN (RIPE NCC)
        {"resource": "AS3333"},
        {"resource": "AS3333"}
    ]

    for i, endpoint in enumerate(endpoints):
        print(f"\n[EXTRACT] Fetching data from {endpoint} endpoint...")
        raw_data = extract_data(endpoint, params_list[i])
        transformed_data = transform_data(raw_data, endpoint)
        load_data(transformed_data)

    print("\n✅ ETL pipeline completed successfully!")

# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
if __name__ == "__main__":
    run_etl()
