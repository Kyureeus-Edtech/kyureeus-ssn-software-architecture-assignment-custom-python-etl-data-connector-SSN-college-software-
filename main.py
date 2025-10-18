import os
import logging
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

from pymongo import MongoClient, ReplaceOne
from pymongo.errors import PyMongoError, ConnectionFailure
from dotenv import load_dotenv

from endpoint_cf_trace_1 import ENDPOINT_CONFIG as EP1
from endpoint_cf_trace_2 import ENDPOINT_CONFIG as EP2
from endpoint_cf_trace_3 import ENDPOINT_CONFIG as EP3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cybersecurity_data")

def extract_cf_trace(host: str, timeout: int = 20, retries: int = 2, backoff_sec: int = 3) -> Optional[Dict[str, Any]]:
    """
    GET https://<host>/cdn-cgi/trace
    Parses key=value lines into a dict. Returns None on failure.
    """
    url = f"https://{host}/cdn-cgi/trace"
    attempt = 0
    while attempt <= retries:
        try:
            logging.info(f"[CF TRACE] Fetching: {url} (attempt {attempt+1})")
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            data: Dict[str, Any] = {}
            for line in r.text.strip().splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()
            if "ts" in data:
                try:
                    data["ts"] = int(data["ts"])
                except ValueError:
                    pass
            return data
        except requests.exceptions.RequestException as e:
            logging.warning(f"[CF TRACE] Error fetching {url}: {e}")
            if attempt == retries:
                break
            time.sleep(backoff_sec * (attempt + 1))
            attempt += 1
    logging.error(f"[CF TRACE] Failed after {retries+1} attempts: {url}")
    return None

def get_nested_data(data: Dict, path: List[str]) -> List[Dict]:
    """
    Safely navigates nested dicts/lists.
    For CF Trace we use an empty path [].
    """
    if not path:
        if isinstance(data, dict):
            return [data]
        logging.warning("Empty data path provided, but root data is not a dictionary.")
        return []
    try:
        temp = data
        for key in path:
            temp = temp[key]
        if isinstance(temp, list):
            return temp
        elif isinstance(temp, dict):
            return [temp]
        return []
    except (KeyError, TypeError, IndexError) as e:
        logging.warning(f"Could not find a valid list/dict at path {path}: {e}")
        return []

def transform_data(parsed_data: Dict, data_key_path: List[str], host: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Transforms parsed data:
      - Selects records via data_key_path
      - Adds ingestion_timestamp
      - For CF Trace, adds 'host' and synthetic 'host_ts'
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

    out: List[Dict[str, Any]] = []
    for record in records_list:
        if not isinstance(record, dict):
            continue
        record["ingestion_timestamp"] = ingestion_time

        if host:
            record["host"] = host
            ts_val = record.get("ts")
            if not isinstance(ts_val, int):
                ts_val = int(ingestion_time.timestamp())
                record["ts"] = ts_val
            record["host_ts"] = f"{host}_{ts_val}"

        out.append(record)

    logging.info("Transformation complete.")
    return out

def load_data(records: List[Dict[str, Any]], collection_name: str, unique_id_key: str):
    """
    Bulk upsert into MongoDB using unique_id_key.
    """
    if not records:
        logging.warning(f"No records to load into '{collection_name}'.")
        return

    logging.info(f"Connecting to MongoDB to load data into '{collection_name}'...")
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]

            ops = []
            for rec in records:
                uid = rec.get(unique_id_key)
                if isinstance(rec, dict) and uid:
                    ops.append(ReplaceOne({unique_id_key: uid}, rec, upsert=True))
                else:
                    logging.warning(f"Skipping record (missing '{unique_id_key}' or not a dict).")

            if not ops:
                logging.warning(f"No valid records with '{unique_id_key}' to upsert in '{collection_name}'.")
                return

            logging.info(f"Performing bulk upsert of {len(ops)} records into '{collection_name}'...")
            result = collection.bulk_write(ops)
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
        logging.error(f"Unexpected error during load to '{collection_name}': {e}")

def run_etl_pipeline(config: Dict[str, Any]):
    """
    Runs the E-T-L for a single configured endpoint.
    api_type supported here: 'cf_trace'
    """
    collection_name = config["collection"]
    logging.info(f"--- Starting ETL for {config['name']} ({collection_name}) ---")

    api_type = config.get("api_type", "cf_trace")
    if api_type != "cf_trace":
        logging.error(f"Unsupported api_type '{api_type}' in this script.")
        return

    host = config["host"]
    raw_obj = extract_cf_trace(host)
    if not raw_obj:
        logging.error(f"Stopping ETL for {collection_name} due to extraction failure.")
        return

    parsed_data = raw_obj
    records_to_load = transform_data(parsed_data, config["data_key_path"], host=host)
    load_data(records_to_load, collection_name, config["id_key"])
    logging.info(f"--- Finished ETL for {config['name']} ---")


if __name__ == "__main__":
    logging.info("====== Starting Cloudflare Trace ETL (3 endpoints) ======")

    endpoints_to_process = [EP1, EP2, EP3]
    for endpoint_config in endpoints_to_process:
        run_etl_pipeline(endpoint_config)

    logging.info("======= Cloudflare Trace ETL Finished =======")
