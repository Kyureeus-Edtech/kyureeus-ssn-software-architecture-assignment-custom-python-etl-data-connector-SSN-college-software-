import os
import requests
import logging
import json
import xmltodict
from pymongo import MongoClient, ReplaceOne
from pymongo.errors import PyMongoError, ConnectionFailure
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Configuration ---
# Configure logging to show timestamp, level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file for security
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cybersecurity_data") 


# --- ETL Core Functions ---

def extract_data(api_url: str) -> Optional[str]:
    """
    Extracts raw data text from a specified API endpoint with error handling.
    Returns: The full text content from the API as a string, or None if an error occurs.
    """
    logging.info(f"Starting data extraction from: {api_url}")
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        logging.info(f"Successfully extracted raw data from {api_url}")
        return response.text
    except requests.exceptions.HTTPError as e:
        logging.error(f"[HTTP Error] Failed to extract data from {api_url}: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"[Connection Error] Failed to extract data from {api_url}: {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"[Timeout Error] Failed to extract data from {api_url}: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[Request Error] Failed to extract data from {api_url}: {e}")
    return None

def get_nested_data(data: Dict, path: List[str]) -> List[Dict]:
    """
    Helper function to safely navigate a nested dictionary using a list of keys.
    Handles cases where the final data is a list or a single dictionary.
    """
    # If the path is empty, it means the root object is the data we want.
    if not path:
        if isinstance(data, dict):
            return [data] # Wrap the single object in a list
        logging.warning("Empty data path provided, but root data is not a dictionary.")
        return []

    try:
        temp_data = data
        for key in path:
            temp_data = temp_data[key]
        
        # If the result is a list, return it directly.
        if isinstance(temp_data, list):
            return temp_data
        # If it's a single item (common in RSS feeds with one entry), wrap it in a list.
        elif isinstance(temp_data, dict):
            return [temp_data]
        return []
    except (KeyError, TypeError, IndexError) as e:
        logging.warning(f"Could not find a valid list/dict at path {path}: {e}")
        return []

def transform_data(parsed_data: Dict, data_key_path: List[str]) -> List[Dict[str, Any]]:
    """
    Transforms parsed data (from JSON or XML).
    - Extracts the relevant list of records using the data_key_path.
    - Adds a consistent ingestion timestamp to each record.
    """
    if not parsed_data:
        logging.warning("No parsed data available to transform.")
        return []

    records_list = get_nested_data(parsed_data, data_key_path)

    if not records_list:
        logging.warning(f"No records found at path: {data_key_path}")
        return []

    logging.info(f"Transforming {len(records_list)} records...")
    ingestion_time = datetime.utcnow()
    
    for record in records_list:
        if isinstance(record, dict):
            record['ingestion_timestamp'] = ingestion_time
    
    logging.info("Transformation complete.")
    return records_list

def load_data(records: List[Dict[str, Any]], collection_name: str, unique_id_key: str):
    """
    Loads transformed data into a specified MongoDB collection using an efficient
    'upsert' strategy (update if exists, insert if new).
    """
    if not records:
        logging.warning(f"No records to load into '{collection_name}'.")
        return

    logging.info(f"Connecting to MongoDB to load data into '{collection_name}'...")
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]
            
            operations = []
            for record in records:
                unique_id = record.get(unique_id_key)
                if isinstance(record, dict) and unique_id:
                    operations.append(
                        ReplaceOne(
                            {unique_id_key: unique_id}, # Filter condition
                            record,                     # New data
                            upsert=True                 # The magic 'upsert' flag
                        )
                    )
                else:
                    logging.warning(f"Skipping record in '{collection_name}' (missing '{unique_id_key}' or not a dict).")

            if not operations:
                logging.warning(f"No valid records with unique IDs to load into '{collection_name}'.")
                return

            logging.info(f"Performing bulk upsert of {len(operations)} records into '{collection_name}'...")
            result = collection.bulk_write(operations)
            logging.info(
                f"MongoDB write to '{collection_name}' complete. "
                f"Inserted: {result.inserted_count}, "
                f"Updated: {result.modified_count}, "
                f"Upserted: {result.upserted_count}"
            )

    except ConnectionFailure as e:
        logging.error(f"MongoDB connection failed: {e}")
    except PyMongoError as e:
        logging.error(f"Error loading data to MongoDB collection '{collection_name}': {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during data load to '{collection_name}': {e}")

# --- ETL Pipeline Controller ---

def run_etl_pipeline(config: Dict[str, Any]):
    """
    Runs the full E-T-L process for a single configured endpoint.
    Handles data parsing based on the specified format.
    """
    collection_name = config["collection"]
    logging.info(f"--- Starting ETL for {config['name']} ({collection_name}) ---")
    
    # 1. Extract raw text data
    raw_text = extract_data(config["url"])
    if not raw_text:
        logging.error(f"Stopping ETL for {collection_name} due to extraction failure.")
        return

    # 2. Parse the text into a dictionary based on its format
    parsed_data = None
    try:
        if config["format"] == "json":
            parsed_data = json.loads(raw_text)
        elif config["format"] == "xml":
            parsed_data = xmltodict.parse(raw_text)
        else:
            logging.error(f"Unknown data format '{config['format']}' for {collection_name}")
            return
    except Exception as e:
        logging.error(f"Failed to parse data for {collection_name}: {e}")
        return

    # 3. Transform the data to add timestamps and ensure structure
    records_to_load = transform_data(parsed_data, config["data_key_path"])

    # 4. Load the final records into the database
    load_data(records_to_load, collection_name, config["id_key"])
    
    logging.info(f"--- Finished ETL for {config['name']} ---")

# --- Main Execution Block ---

if __name__ == "__main__":
    logging.info("====== Starting Master ETL Process ======")
    
    # --- List of all endpoints to process here ---
    endpoints_to_process = [
        # --- CISA Endpoints ---
        {
            "name": "CISA KEV Catalog",
            "url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            "format": "json",
            "collection": "cisa_kev_catalog_raw",
            "data_key_path": ["vulnerabilities"],
            "id_key": "cveID"               
        },
        {
            "name": "CISA Alerts",
            "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
            "format": "xml",
            "collection": "cisa_alerts_raw",
            "data_key_path": ["rss", "channel", "item"],
            "id_key": "guid" 
        },
        {
            "name": "CISA ICS Advisories",
            "url": "https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml",
            "format": "xml",
            "collection": "cisa_ics_advisories_raw",
            "data_key_path": ["rss", "channel", "item"],
            "id_key": "guid"
        },

        # --- FreeGeoIP Endpoints ---
        {
            "name": "GeoIP for Google DNS",
            "url": "https://freegeoip.app/json/8.8.8.8",
            "format": "json",
            "collection": "geoip_lookups_raw_endpoint_1",
            "data_key_path": [],  
            "id_key": "ip"
        },
        {
            "name": "GeoIP for Cloudflare DNS",
            "url": "https://freegeoip.app/json/1.1.1.1",
            "format": "json",
            "collection": "geoip_lookups_raw_endpoint_2",
            "data_key_path": [],
            "id_key": "ip"
        },
        {
            "name": "GeoIP for Self",
            "url": "https://freegeoip.app/json/",
            "format": "json",
            "collection": "geoip_lookups_raw_endpoint_3",
            "data_key_path": [],
            "id_key": "ip"
        }
    ]

    # Loop through and process each configured endpoint
    for endpoint_config in endpoints_to_process:
        run_etl_pipeline(endpoint_config)

    logging.info("======= Master ETL Process Finished =======")
