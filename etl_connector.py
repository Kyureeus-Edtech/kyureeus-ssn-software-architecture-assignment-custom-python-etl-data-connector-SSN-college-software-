import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# --- CONFIGURATION ---
# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# The CISA KEV Catalog URL
CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DB_NAME = "ssn_assignment_db"
COLLECTION_NAME = "cisa_kev_raw"

# --- EXTRACT ---
def extract_data(url):
    """
    Extracts data from a given URL.
    Returns JSON data if successful, otherwise None.
    """
    print("Beginning data extraction...")
    try:
        response = requests.get(url, timeout=30)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        print("Extraction successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during data extraction: {e}")
        return None

# --- TRANSFORM ---
def transform_data(raw_data):
    """
    Transforms raw data by enriching it with timestamps, converting data types,
    deriving new fields, and standardizing values.
    """
    if not raw_data or "vulnerabilities" not in raw_data:
        print("No vulnerabilities found in the raw data.")
        return []

    print("Beginning data transformation with enrichment...")
    transformed_records = []
    ingestion_time = datetime.utcnow()

    for vuln in raw_data["vulnerabilities"]:
        # T1: Add ingestion timestamp for auditing
        vuln["ingestionTimestamp"] = ingestion_time

        # T2: Convert date strings to proper datetime objects for querying
        try:
            date_added = datetime.strptime(vuln["dateAdded"], "%Y-%m-%d")
            due_date = datetime.strptime(vuln["dueDate"], "%Y-%m-%d")
            vuln["dateAdded"] = date_added
            vuln["dueDate"] = due_date

            # T3: Derive a new field 'daysToPatch' from the converted dates
            remediation_period = due_date - date_added
            vuln["daysToPatch"] = remediation_period.days
        
        except (ValueError, TypeError) as e:
            # Handle cases where dates might be missing or in an unexpected format
            print(f"Warning: Could not process dates for {vuln.get('cveID', 'N/A')}. Error: {e}")
            vuln["daysToPatch"] = None  # Set to null if calculation fails

        # T4: Standardize ransomware text field to a clean boolean
        if vuln.get("knownRansomwareCampaignUse", "").lower() == "known":
            vuln["isRansomwareAssociated"] = True
        else:
            vuln["isRansomwareAssociated"] = False
        
        transformed_records.append(vuln)
    
    print(f"Transformation successful. {len(transformed_records)} records processed and enriched.")
    return transformed_records

# --- LOAD ---
def load_data(records):
    """
    Loads a list of records into a MongoDB collection.
    """
    if not records:
        print("No records to load.")
        return

    print("Beginning data loading into MongoDB...")
    try:
        # Establish connection to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Clear the collection before inserting new data to avoid duplicates
        collection.delete_many({})
        print(f"Cleared old data from '{COLLECTION_NAME}'.")

        # Insert the new, transformed records
        result = collection.insert_many(records)
        print(f"Loading successful. Inserted {len(result.inserted_ids)} records into '{COLLECTION_NAME}'.")

    except Exception as e:
        print(f"An error occurred during data loading: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- CISA KEV ETL PROCESS STARTED ---")
    
    # 1. Extract
    raw_json_data = extract_data(CISA_URL)
    
    if raw_json_data:
        # 2. Transform (with all new steps)
        transformed_vulnerabilities = transform_data(raw_json_data)
        
        # 3. Load
        load_data(transformed_vulnerabilities)

    print("--- CISA KEV ETL PROCESS FINISHED ---")