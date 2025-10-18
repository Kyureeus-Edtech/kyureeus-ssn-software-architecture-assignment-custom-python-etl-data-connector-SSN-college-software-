"""
Multi-Source Threat Intelligence ETL Pipeline

This script extracts data from multiple cybersecurity APIs (CISA and Blocklist.de),
handles different data formats (JSON, XML, and Text), transforms the data into a
standardized format, and loads it into a MongoDB database using an upsert strategy.
"""

import os
import logging
import json
import xmltodict
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne
from pymongo.errors import PyMongoError, ConnectionFailure

# --- 1. Setup and Global Configuration ---

# Configure logging to show timestamp, level, and message
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from a .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cybersecurity_data") # Default DB name if not set

# --- 2. Endpoint Configuration ---
ENDPOINTS_TO_PROCESS = [
    # --- CISA Endpoints ---
    {
        "name": "CISA KEV Catalog",
        "url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        "format": "json",
        "collection": "cisa_kev_catalog_raw",
        "data_key_path": ["vulnerabilities"], # Path to the list of records in the JSON
        "id_key": "cveID"                     # Unique key for upserting
    },
    {
        "name": "CISA Alerts",
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "format": "xml",
        "collection": "cisa_alerts_raw",
        "data_key_path": ["rss", "channel", "item"], # Path to the list of records in the XML
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
    {
        "name": "CISA News & Events",
        "url": "https://www.cisa.gov/news.xml",
        "format": "xml",
        "collection": "cisa_news_raw",
        "data_key_path": ["rss", "channel", "item"],
        "id_key": "guid"
    },

    # --- Blocklist.de Endpoints ---
    {
        "name": "Blocklist.de All IPs",
        "url": "https://api.blocklist.de/lists/all.txt",
        "format": "text",
        "collection": "blocklist_de_all_raw",
        "data_key_path": [],  # Not applicable, text format is a flat list
        "id_key": "ip_address" # We will create this key during transformation
    },
    {
        "name": "Blocklist.de SSH Attacks",
        "url": "https://api.blocklist.de/lists/ssh.txt",
        "format": "text",
        "collection": "blocklist_de_ssh_raw",
        "data_key_path": [],
        "id_key": "ip_address"
    },
    {
        "name": "Blocklist.de Bot IPs",
        "url": "https://api.blocklist.de/lists/bots.txt",
        "format": "text",
        "collection": "blocklist_de_bots_raw",
        "data_key_path": [],
        "id_key": "ip_address"
    }
]


# --- 3. ETL Core Functions ---

def extract_data(api_url: str) -> Optional[str]:
    """
    (E)xtracts raw data text from a specified API endpoint.
    Returns: The full text content from the API, or None if an error occurs.
    """
    logging.info(f"Extracting data from: {api_url}")
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
    A helper function to safely navigate a nested dictionary using a list of keys
    (e.g., ['rss', 'channel', 'item']).
    """
    if not path: # Handles cases like FreeGeoIP where the whole object is the record
        if isinstance(data, dict):
            return [data] # Wrap the single object in a list
        logging.warning("Empty data path, but root data is not a dictionary.")
        return []

    try:
        temp_data = data
        for key in path:
            temp_data = temp_data[key]
        
        # Handle cases where an XML feed has only one item (it's a dict, not a list)
        if isinstance(temp_data, list):
            return temp_data
        elif isinstance(temp_data, dict):
            return [temp_data] # Wrap the single item in a list
        return []
    except (KeyError, TypeError, IndexError) as e:
        logging.warning(f"Could not find a valid list/dict at path {path}: {e}")
        return []

def transform_data(parsed_data: Union[Dict, List[str]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    (T)ransforms parsed data (from JSON, XML, or Text) into a standardized
    list of dictionaries for MongoDB insertion.
    
    - Adds a consistent 'ingestion_timestamp' to each record.
    - Converts text-based IP lists into a structured dictionary.
    """
    records_list = []
    ingestion_time = datetime.utcnow()
    data_format = config.get("format")

    try:
        if data_format in ("json", "xml"):
            # parsed_data is a Dict. We need to find the list of records inside it.
            records_list = get_nested_data(parsed_data, config.get("data_key_path", []))
            logging.info(f"Transforming {len(records_list)} {data_format} records...")
            for record in records_list:
                if isinstance(record, dict):
                    record['ingestion_timestamp'] = ingestion_time
        
        elif data_format == "text":
            # parsed_data is a List[str]. We need to convert it to a List[Dict].
            logging.info(f"Transforming {len(parsed_data)} text-based records...")
            for item in parsed_data:
                ip_str = item.strip()
                if ip_str:  # Ensure it's not an empty line
                    records_list.append({
                        "ip_address": ip_str,
                        "ingestion_timestamp": ingestion_time
                    })
        
        else:
            logging.warning(f"Unknown format in transform_data: {data_format}")
            return []

        logging.info(f"Transformation complete. {len(records_list)} records prepared.")
        return records_list

    except Exception as e:
        logging.error(f"Error during transformation: {e}")
        return []


def load_data(records: List[Dict[str, Any]], collection_name: str, unique_id_key: str):
    """
    (L)oads transformed data into a specified MongoDB collection using an efficient
    'upsert' strategy (update if exists, insert if new).
    """
    if not records:
        logging.warning(f"No records to load into '{collection_name}'.")
        return

    logging.info(f"Connecting to MongoDB to load data into '{collection_name}'...")
    try:
        # Use a context manager for safe and automatic connection handling
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]
            
            # Prepare a list of 'ReplaceOne' operations for bulk writing
            operations = []
            for record in records:
                unique_id = record.get(unique_id_key)
                if isinstance(record, dict) and unique_id:
                    operations.append(
                        ReplaceOne(
                            {unique_id_key: unique_id},  # Filter: Find doc with this ID
                            record,                      # New data to replace/insert
                            upsert=True                  # The 'upsert' flag
                        )
                    )
                else:
                    logging.warning(f"Skipping record in '{collection_name}' (missing '{unique_id_key}' or not a dict).")

            if not operations:
                logging.warning(f"No valid records with unique IDs to load into '{collection_name}'.")
                return

            # Execute the bulk operation
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
        logging.error(f"An unexpected error occurred during data load: {e}")

# --- 4. ETL Orchestrator ---

def run_etl_pipeline(config: Dict[str, Any]):
    """
    Runs the full E-T-L process for a single configured endpoint.
    This function orchestrates the extract, parse, transform, and load steps.
    """
    collection_name = config["collection"]
    data_format = config.get("format", "json") # Default to json
    
    logging.info(f"--- Starting ETL for {config['name']} ({collection_name}) ---")
    
    # 1. EXTRACT raw text data
    raw_text = extract_data(config["url"])
    if not raw_text:
        logging.error(f"Stopping ETL for {collection_name} due to extraction failure.")
        return

    # 2. PARSE the text into a usable structure (Dict or List)
    parsed_data = None
    try:
        if data_format == "json":
            parsed_data = json.loads(raw_text)  # Returns Dict
        elif data_format == "xml":
            parsed_data = xmltodict.parse(raw_text)  # Returns Dict
        elif data_format == "text":
            parsed_data = raw_text.splitlines()  # Returns List[str]
        else:
            logging.error(f"Unknown data format '{data_format}' for {collection_name}")
            return
    except Exception as e:
        logging.error(f"Failed to parse data for {collection_name}: {e}")
        return

    # 3. TRANSFORM the data
    records_to_load = transform_data(parsed_data, config)

    # 4. LOAD the final records into the database
    load_data(records_to_load, collection_name, config["id_key"])
    
    logging.info(f"--- Finished ETL for {config['name']} ---")

# --- 5. Main Execution ---

def main():
    """
    Main function to run the entire ETL process for all configured endpoints.
    """
    logging.info("====== Starting Master ETL Process ======")
    
    for endpoint_config in ENDPOINTS_TO_PROCESS:
        run_etl_pipeline(endpoint_config)

    logging.info("======= Master ETL Process Finished =======")

if __name__ == "__main__":
    main()