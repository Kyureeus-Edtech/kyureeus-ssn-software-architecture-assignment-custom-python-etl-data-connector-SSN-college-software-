import os
import csv
import json
import logging
import time
import re
from datetime import datetime
import requests
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VT_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "virustotal_raw")

BASE_URL = "https://www.virustotal.com/api/v3/files/"

VALID_HASH_REGEX = re.compile(r"^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$")

logging.basicConfig(
    filename="etl_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.create_index("id", unique=True)
    logging.info("Connected to MongoDB and ensured index on 'id'.")
except errors.ConnectionFailure as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise SystemExit("Cannot continue without DB connection.")

def read_hashes(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return []

    hashes = []
    try:
        if file_path.endswith(".csv"):
            with open(file_path, mode="r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        hashes.append(row[0].strip())
        elif file_path.endswith(".json"):
            with open(file_path, mode="r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    hashes.extend(data)
                elif isinstance(data, dict) and "hashes" in data:
                    hashes.extend(data["hashes"])
        else:
            logging.error("Unsupported file format. Use CSV or JSON.")
            return []
    except json.JSONDecodeError:
        logging.error("Invalid JSON file format.")
        return []
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return []

    valid_hashes = {h for h in hashes if VALID_HASH_REGEX.match(h)}
    invalid_hashes = set(hashes) - valid_hashes
    if invalid_hashes:
        logging.warning(f"Skipped invalid hashes: {invalid_hashes}")
    return list(valid_hashes)

def extract_file_report(file_hash):
    url = f"{BASE_URL}{file_hash}"
    headers = {"x-apikey": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 401:
            logging.error("Invalid API key. Check your VT_API_KEY in .env.")
            raise SystemExit("Cannot continue without valid API key.")

        if response.status_code == 404:
            logging.warning(f"Hash not found: {file_hash}")
            return None
        elif response.status_code == 429:
            logging.warning("Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            return extract_file_report(file_hash)
        elif response.status_code != 200:
            logging.error(f"API Error {response.status_code} for {file_hash}: {response.text}")
            return None

        data = response.json()
        if "error" in data and data["error"].get("code") == "NotFoundError":
            logging.warning(f"VirusTotal returned NotFoundError for {file_hash}")
            return None
        return data
    except requests.Timeout:
        logging.error(f"Timeout when fetching hash {file_hash}")
        return None
    except requests.RequestException as e:
        logging.error(f"Request failed for {file_hash}: {e}")
        return None

def transform_data(raw_data):
    if not raw_data or "data" not in raw_data:
        return None
    return {
        "id": raw_data["data"].get("id"),
        "type": raw_data["data"].get("type"),
        "attributes": raw_data["data"].get("attributes", {}),
        "retrieved_at": datetime.utcnow(),
        "source": "VirusTotal API v3"
    }

def load_to_mongodb(data):
    try:
        result = collection.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        if result.upserted_id:
            logging.info(f"Inserted new: {data['id']}")
        else:
            logging.info(f"Updated existing: {data['id']}")
    except errors.PyMongoError as e:
        logging.error(f"Failed DB write for {data['id']}: {e}")

def main():
    logging.info("ETL Pipeline Started")
    
    file_choice = input("Enter CSV/JSON file path of hashes (or leave empty to enter manually): ").strip()

    if file_choice:
        file_hashes = read_hashes(file_choice)
    else:
        user_hash = input("Enter a single file hash: ").strip()
        file_hashes = [user_hash] if VALID_HASH_REGEX.match(user_hash) else []

    if not file_hashes:
        logging.error("No valid file hashes provided. Exiting.")
        return

    logging.info(f"Processing {len(file_hashes)} hashes.")

    for h in file_hashes:
        logging.info(f"Processing hash: {h}")
        raw = extract_file_report(h)
        transformed = transform_data(raw)
        if transformed:
            load_to_mongodb(transformed)
        else:
            logging.warning(f"No data stored for hash: {h}")

    logging.info("ETL Pipeline Completed")

if __name__ == "__main__":
    main()
