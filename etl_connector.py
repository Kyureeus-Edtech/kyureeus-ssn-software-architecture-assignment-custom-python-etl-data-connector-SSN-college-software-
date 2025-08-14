import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from the .env file
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
# Use a specific collection name for this connector
COLLECTION_NAME = "cisa_kev_catalog_raw"

# API Configuration for CISA KEV Catalog
API_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

# --- ETL Pipeline ---

def extract_data():
    """
    Extracts data from the CISA KEV JSON feed.
    Returns: The full JSON content from the API or None if an error occurs.
    """
    logging.info("Starting data extraction from CISA KEV feed...")
    try:
        response = requests.get(API_URL, timeout=15) # Increased timeout for a potentially larger file
        response.raise_for_status() # Check for HTTP errors
        logging.info("Successfully extracted data from API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during extraction: {e}")
        return None

def transform_data(data):
    """
    Transforms the raw CISA data.
    - Extracts the list of vulnerabilities from the main JSON object.
    - Adds an ingestion timestamp to each vulnerability record.
    """
    if not data or 'vulnerabilities' not in data:
        logging.warning("No data or 'vulnerabilities' key found to transform.")
        return []

    # The actual list of vulnerabilities is inside the 'vulnerabilities' key
    vulnerabilities = data.get('vulnerabilities', [])
    
    logging.info(f"Transforming {len(vulnerabilities)} vulnerability records...")
    transformed_records = []
    for record in vulnerabilities:
        # Add the ingestion timestamp as required by the assignment
        record['ingestion_timestamp'] = datetime.utcnow()
        transformed_records.append(record)

    logging.info("Transformation complete.")
    return transformed_records

def load_data(data):
    """
    Loads the transformed data into a MongoDB collection.
    """
    if not data:
        logging.warning("No data to load.")
        return

    logging.info(f"Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        logging.info(f"Deleting old data from '{COLLECTION_NAME}' to ensure freshness.")
        collection.delete_many({}) # Clear old data before inserting new data

        logging.info(f"Loading {len(data)} records into '{DB_NAME}.{COLLECTION_NAME}'...")
        result = collection.insert_many(data)
        logging.info(f"Successfully loaded {len(result.inserted_ids)} records into MongoDB.")
    except Exception as e:
        logging.error(f"Error loading data to MongoDB: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            logging.info("MongoDB connection closed.")

# --- Main Execution Block ---

if __name__ == "__main__":
    logging.info("====== Starting CISA KEV ETL Process ======")
    
    # 1. Extract
    raw_data = extract_data()

    if raw_data:
        # 2. Transform
        transformed_data = transform_data(raw_data)

        # 3. Load
        load_data(transformed_data)

    logging.info("======= ETL Process Finished =======")