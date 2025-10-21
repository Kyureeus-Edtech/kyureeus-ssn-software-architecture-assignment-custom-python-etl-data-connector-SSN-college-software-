import os
import requests
import logging
import ipaddress
from datetime import datetime
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# ------------------- Setup Logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------- Load Environment Variables -------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DEFAULT_DB_NAME = os.getenv("DB_NAME")
DEFAULT_COLLECTION_NAME = os.getenv("COLLECTION_NAME")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))  # Optional env var

# ------------------- MongoDB Connection -------------------
def get_collection(db_name, collection_name):
    """Connect to MongoDB and return the specified collection."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        coll = db[collection_name]
        client.admin.command('ping')
        logging.info(f"Connected to MongoDB database: {db_name}, collection: {collection_name}")
        return coll
    except errors.ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        raise

# ------------------- ETL Functions -------------------
def extract():
    """Fetch raw data from FireHOL IP List."""
    url = "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset"
    try:
        logging.info(f"Extracting data from {url} ...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        logging.error(f"Extraction failed: {e}")
        return []

def transform(data):
    """Clean, classify, normalize, and deduplicate IP/CIDR entries."""
    logging.info("Transforming data ...")
    cleaned = []
    seen = set()

    for line in data:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if "/" in line:
                # Normalize CIDR
                net = ipaddress.ip_network(line, strict=False)
                normalized = str(net)
                record_type = "cidr"
            else:
                # Normalize single IP
                ip_obj = ipaddress.ip_address(line)
                normalized = str(ip_obj)
                record_type = "ip"

            if normalized not in seen:
                seen.add(normalized)
                cleaned.append({
                    "ip": normalized,
                    "type": record_type,
                    "ingested_at": datetime.utcnow()
                })
        except ValueError:
            logging.warning(f"Skipping invalid entry: {line}")

    logging.info(f"Transformation complete. {len(cleaned)} unique valid records found.")
    return cleaned

def load(records, coll):
    """Insert transformed data into MongoDB with batching."""
    if not records:
        logging.warning("No valid records to insert.")
        return

    logging.info(f"Loading {len(records)} records into MongoDB ...")
    try:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            for rec in batch:
                coll.update_one(
                    {"ip": rec["ip"]},
                    {"$set": rec},
                    upsert=True
                )
        logging.info("Data loaded successfully.")
    except errors.PyMongoError as e:
        logging.error(f"Failed to insert into MongoDB: {e}")

def run_pipeline(db_name=None, collection_name=None):
    """Run full ETL pipeline with optional DB and collection override."""
    start_time = datetime.utcnow()
    logging.info("ETL Pipeline started.")

    db_name = db_name or DEFAULT_DB_NAME
    collection_name = collection_name or DEFAULT_COLLECTION_NAME

    coll = get_collection(db_name, collection_name)

    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data, coll)

    end_time = datetime.utcnow()
    logging.info(f"ETL Pipeline finished. Duration: {end_time - start_time}")

# ------------------- Main -------------------
if __name__ == "__main__":
    run_pipeline()
