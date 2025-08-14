import os
import logging
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure

# ---------------- LOGGING CONFIG ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("nvd_fetch.log"),
        logging.StreamHandler()
    ]
)

# ---------------- LOAD ENV ----------------
load_dotenv()
MONGO_URL = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = "nvd_raw"

# ---------------- API CONFIG ----------------
BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
START_INDEX = 0
RESULTS_PER_PAGE = 2000
PARAMS = {
    "startIndex": START_INDEX,
    "resultsPerPage": RESULTS_PER_PAGE,
}

def fetch_cve_data():
    """Fetch CVE data from NVD API."""
    try:
        logging.info(f"Fetching CVE data from {BASE_URL}...")
        response = requests.get(BASE_URL, params=PARAMS, timeout=60)
        response.raise_for_status()
        logging.info(f"Successfully fetched data. Status Code: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from NVD API: {e}")
        return None

def save_to_mongo(data):
    """Save fetched data to MongoDB."""
    if not MONGO_URL or not MONGO_DB:
        logging.error("MONGO_URI or MONGO_DB_NAME is not set in .env")
        return

    try:
        logging.info("Connecting to MongoDB...")
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection test
        db = client[MONGO_DB]
        collection = db[COLLECTION_NAME]

        logging.info(f"Clearing existing data in '{COLLECTION_NAME}'...")
        collection.delete_many({})

        if isinstance(data, dict):
            collection.insert_one(data)
        elif isinstance(data, list):
            collection.insert_many(data)
        else:
            logging.error("Data format not supported for MongoDB insertion.")
            return

        logging.info(f"Data successfully inserted into '{COLLECTION_NAME}' collection.")

    except (ConnectionFailure, PyMongoError) as e:
        logging.error(f"MongoDB error: {e}")

def main():
    data = fetch_cve_data()
    if data:
        save_to_mongo(data)
    else:
        logging.error("No data fetched. Skipping MongoDB save.")

if __name__ == "__main__":
    main()
