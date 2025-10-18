import os
import requests
import logging
import json
import xmltodict
import time 
from pymongo import MongoClient, ReplaceOne
from pymongo.errors import PyMongoError, ConnectionFailure
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file for security
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cybersecurity_data")
# --- SSL Labs API v4 requires a registered email ---
# --- Add this to your .env file ---
SSLLABS_EMAIL = os.getenv("SSLLABS_EMAIL")


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

def extract_ssllabs_data(host: str, email: str) -> Optional[str]:
    """
    Extracts data from the SSL Labs API, handling the async polling workflow.
    
    1. Starts a new scan.
    2. Polls the 'analyze' endpoint until the status is 'READY' or 'ERROR'.
    
    Returns: The full JSON report as a string, or None if an error occurs.
    """
    API_URL = "https://api.ssllabs.com/api/v4/analyze"
    
    # --- FIX: Email is a query parameter, not a header ---
    # 1. Start the scan
    # 'all': 'done' ensures the full report is returned when READY
    params = {
        "host": host, 
        "startNew": "on", 
        "all": "done", 
        "email": email  # <-- Email added to params
    }
    
    logging.info(f"[SSLLabs] Initiating new scan for: {host}")
    
    try:
        while True:
            # --- FIX: Removed 'headers=headers' ---
            response = requests.get(API_URL, params=params, timeout=30) 
            
            # Handle rate limiting
            if response.status_code == 429:
                logging.warning(f"[SSLLabs] Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue # Retry the same request

            response.raise_for_status()
            data = response.json()
            status = data.get("status")

            if status == "READY":
                logging.info(f"[SSLLabs] Scan for {host} is READY. Returning report.")
                return json.dumps(data) # Return full JSON report as string
            
            elif status == "ERROR":
                logging.error(f"[SSLLabs] Scan for {host} failed with ERROR: {data.get('statusMessage')}")
                return None
            
            elif status in ("IN_PROGRESS", "DNS"):
                # Scan is running, remove 'startNew' for next poll
                params.pop("startNew", None)
                sleep_time = 30
                logging.info(f"[SSLLabs] Scan for {host} is {status}. Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
            
            else:
                logging.error(f"[SSLLabs] Unknown status for {host}: {status}")
                return None

    except requests.exceptions.HTTPError as e:
        logging.error(f"[SSLLabs HTTP Error] Failed to scan {host}: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[SSLLabs Request Error] Failed to scan {host}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"[SSLLabs JSON Error] Failed to parse response for {host}: {e}")
    
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
                            record,                       # New data
                            upsert=True                   # The magic 'upsert' flag
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
    
    raw_text = None
    
    api_type = config.get("api_type", "simple_get") # Default to old method

    if api_type == "ssllabs":
        if not SSLLABS_EMAIL:
            logging.error(f"SSLLABS_EMAIL not set in .env file. Skipping {config['name']}.")
            return
        raw_text = extract_ssllabs_data(config["host"], SSLLABS_EMAIL)
    else:
        # 1. Extract raw text data (original method)
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
    # --- UPDATED: Now contains 6 SSL Labs endpoints ---
    endpoints_to_process = [
        # --- SSL Labs Endpoints ---
        {
            "name": "SSL Labs Scan for google.com",
            "api_type": "ssllabs",  
            "host": "google.com",  
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],   
            "id_key": "host"      
        },
        {
            "name": "SSL Labs Scan for cloudflare.com",
            "api_type": "ssllabs",
            "host": "cloudflare.com",
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],
            "id_key": "host"
        },
        {
            "name": "SSL Labs Scan for cisa.gov",
            "api_type": "ssllabs",
            "host": "cisa.gov",
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],
            "id_key": "host"
        },
        {
            "name": "SSL Labs Scan for github.com",
            "api_type": "ssllabs",
            "host": "github.com",
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],
            "id_key": "host"
        },
        {
            "name": "SSL Labs Scan for amazon.com",
            "api_type": "ssllabs",
            "host": "amazon.com",
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],
            "id_key": "host"
        },
        {
            "name": "SSL Labs Scan for microsoft.com",
            "api_type": "ssllabs",
            "host": "microsoft.com",
            "format": "json",
            "collection": "ssllabs_reports_raw",
            "data_key_path": [],
            "id_key": "host"
        }
    ]

    # Loop through and process each configured endpoint
    for endpoint_config in endpoints_to_process:
        run_etl_pipeline(endpoint_config)

    logging.info("======= Master ETL Process Finished =======")