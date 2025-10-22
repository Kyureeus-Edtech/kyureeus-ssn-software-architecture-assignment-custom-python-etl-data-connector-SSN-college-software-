import os
import time
import logging
from datetime import datetime
from typing import List, Dict

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# --- Load environment variables ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "1.5"))

if not MONGO_URI or not MONGO_DB:
    raise EnvironmentError("MONGO_URI or MONGO_DB not defined in .env")

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("blocklist_etl")
logger.info(f"Connecting to MongoDB: {MONGO_URI}, Database: {MONGO_DB}")

# --- MongoDB client ---
client = MongoClient(MONGO_URI)
database = client[MONGO_DB]

# --- Blocklist.de feeds ---
FEED_URLS = {
    "ssh": "https://lists.blocklist.de/lists/ssh.txt",
    "mail": "https://lists.blocklist.de/lists/mail.txt",
    "apache": "https://lists.blocklist.de/lists/apache.txt",
    "imap": "https://lists.blocklist.de/lists/imap.txt",
    "ftp": "https://lists.blocklist.de/lists/ftp.txt",
    "bots": "https://lists.blocklist.de/lists/bots.txt",
}

# --- HTTP GET with retries ---
def fetch_url(url: str) -> requests.Response:
    attempt = 0
    session = requests.Session()
    while attempt <= MAX_RETRIES:
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response
            elif 500 <= response.status_code < 600:
                raise requests.RequestException(f"Server error {response.status_code}")
            else:
                response.raise_for_status()
        except requests.RequestException as err:
            attempt += 1
            wait_time = BACKOFF_FACTOR ** attempt
            logger.warning("Attempt %d failed for %s. Retrying in %.1fs. Error: %s", attempt, url, wait_time, err)
            time.sleep(wait_time)
    raise ConnectionError(f"Failed to fetch {url} after {MAX_RETRIES} attempts")

# --- Parse IP list to documents ---
def transform_feed(text: str, service: str) -> List[Dict]:
    documents = []
    timestamp = datetime.utcnow()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ip_address = line.split()[0]
        documents.append({
            "ip": ip_address,
            "service": service,
            "source": "blocklist.de/lists",
            "fetched_at": timestamp
        })
    return documents

# --- Get collection ---
def get_collection():
    return database["blocklist"]  # unified collection for all feeds

# --- Safe insertion ---
def insert_documents(collection, docs: List[Dict]) -> int:
    if not docs:
        logger.info("No records to insert into %s", collection.name)
        return 0
    try:
        result = collection.insert_many(docs, ordered=False)
        logger.info("Inserted %d records into %s", len(result.inserted_ids), collection.name)
        return len(result.inserted_ids)
    except errors.BulkWriteError as bwe:
        inserted_count = bwe.details.get("nInserted", 0)
        logger.warning("Partial insert: %d inserted before error. Details: %s", inserted_count, str(bwe))
        return inserted_count

# --- ETL process ---
def run_etl():
    collection = get_collection()
    total_inserted = 0
    for service, url in FEED_URLS.items():
        logger.info("Fetching feed for '%s' from %s", service, url)
        try:
            response = fetch_url(url)
            docs = transform_feed(response.text, service)
            inserted = insert_documents(collection, docs)
            total_inserted += inserted
            time.sleep(1)  # short delay between requests
        except Exception as e:
            logger.error("Failed to process feed %s: %s", service, e)
    logger.info("ETL completed. Total documents inserted: %d", total_inserted)

# --- Main execution ---
if __name__ == "__main__":
    logger.info("Starting Blocklist.de ETL connector")
    run_etl()
    logger.info("ETL finished successfully")


