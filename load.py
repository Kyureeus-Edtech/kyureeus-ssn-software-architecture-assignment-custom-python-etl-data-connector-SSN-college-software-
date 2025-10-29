from pymongo import MongoClient
import logging
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

def load(endpoint, records):
    try:
        coll = db[endpoint]
        coll.delete_many({})
        if records:
            coll.insert_many(records)
            logging.info(f"Inserted {len(records)} records into {endpoint}")
        else:
            logging.warning(f"No records to insert for {endpoint}")
    except Exception as e:
        logging.error(f"Load failed for {endpoint}: {e}")

def load_list_details(records, fetch_detail):
    try:
        coll = db["lists_details"]
        coll.delete_many({})
        for item in records:
            if "id" not in item:
                logging.warning("Record without id skipped")
                continue
            detail = fetch_detail(item["id"])
            if detail:
                coll.insert_one(detail)
            else:
                logging.error(f"Failed to fetch detail for list {item['id']}")
        logging.info(f"Inserted detailed records for {len(records)} lists")
    except Exception as e:
        logging.error(f"Load failed for list details: {e}")