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

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cybersecurity_data")


def extract_data(api_url: str) -> Optional[str]:
    """Extracts raw data text from a specified API endpoint."""
    logging.info(f"Starting data extraction from: {api_url}")
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
        logging.info(f"Successfully extracted raw data from {api_url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to extract data from {api_url}: {e}")
        return None


def get_nested_data(data: Dict, path: List[str]) -> List[Dict]:
    """Safely navigate a nested dictionary using a list of keys."""
    if not path:
        if isinstance(data, dict):
            return [data]
        return []
    try:
        temp_data = data
        for key in path:
            temp_data = temp_data[key]
        if isinstance(temp_data, list):
            return temp_data
        elif isinstance(temp_data, dict):
            return [temp_data]
        return []
    except (KeyError, TypeError, IndexError) as e:
        logging.warning(f"Could not find valid path {path}: {e}")
        return []


def transform_tor_exit_nodes(raw_text: str) -> List[Dict[str, Any]]:
    """
    Transform raw Tor Exit Node text data into a structured list of dictionaries.
    Each line corresponds to one Tor exit IP.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    records = []
    ingestion_time = datetime.utcnow()

    for ip in lines:
        records.append({
            "exit_node_ip": ip,
            "source": "tor_exit_list",
            "ingestion_timestamp": ingestion_time
        })

    logging.info(f"Transformed {len(records)} Tor exit nodes.")
    return records


def load_data(records: List[Dict[str, Any]], collection_name: str, unique_id_key: str):
    """Load transformed data into MongoDB with upsert."""
    if not records:
        logging.warning(f"No records to load into '{collection_name}'.")
        return

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]

            operations = [
                ReplaceOne({unique_id_key: record[unique_id_key]}, record, upsert=True)
                for record in records if unique_id_key in record
            ]

            if not operations:
                logging.warning(f"No valid records to upsert into '{collection_name}'.")
                return

            result = collection.bulk_write(operations)
            logging.info(
                f"MongoDB write complete — Inserted: {result.inserted_count}, "
                f"Updated: {result.modified_count}, Upserted: {result.upserted_count}"
            )
    except (ConnectionFailure, PyMongoError) as e:
        logging.error(f"Error loading data to MongoDB: {e}")


def run_etl_pipeline(config: Dict[str, Any]):
    """Runs the ETL process for a single endpoint."""
    logging.info(f"--- Starting ETL for {config['name']} ---")

    raw_text = extract_data(config["url"])
    if not raw_text:
        logging.error(f"Stopping ETL for {config['collection']} due to extraction failure.")
        return

    if config["format"] == "tor_exit_list":
        records = transform_tor_exit_nodes(raw_text)
    elif config["format"] == "json":
        parsed_data = json.loads(raw_text)
        records = get_nested_data(parsed_data, config["data_key_path"])
    elif config["format"] == "xml":
        parsed_data = xmltodict.parse(raw_text)
        records = get_nested_data(parsed_data, config["data_key_path"])
    else:
        logging.error(f"Unsupported format '{config['format']}' for {config['name']}")
        return

    load_data(records, config["collection"], config["id_key"])
    logging.info(f"--- Finished ETL for {config['name']} ---")


if _name_ == "_main_":
    logging.info("====== Starting Master ETL Process ======")

    endpoints_to_process = [
        {
            "name": "Tor Exit Node List",
            "url": "https://check.torproject.org/torbulkexitlist",
            "format": "tor_exit_list",
            "collection": "tor_exit_nodes_raw",
            "id_key": "exit_node_ip",
            "data_key_path": []  # Not used here
        }
    ]

    for endpoint in endpoints_to_process:
        run_etl_pipeline(endpoint)

    logging.info("======= Master ETL Process Finished =======")