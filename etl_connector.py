import os
import requests
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone


load_dotenv()

API_URL = os.getenv("API_URL")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_mongo_collection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logging.info("Connected to MongoDB successfully")
        return collection
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        raise


def extract_data():
    try:
        logging.info(f"Fetching data from API: {API_URL}")
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Extracted {len(data)} records from API")
        return data
    except Exception as e:
        logging.error(f"API extraction failed: {e}")
        raise


def transform_data(data):
    try:
        logging.info("Transforming data...")
        
        vulnerabilities = data.get("vulnerabilities", [])
        transformed = []
        
        for item in vulnerabilities:
            transformed.append({
                "cveID": item.get("cveID"),
                "vendorProject": item.get("vendorProject"),
                "product": item.get("product"),
                "vulnerabilityName": item.get("vulnerabilityName"),
                "dateAdded": item.get("dateAdded"),
                "shortDescription": item.get("shortDescription"),
                "dueDate": item.get("dueDate"),
                "knownRansomwareCampaignUse": item.get("knownRansomwareCampaignUse"),
                "requiredAction": item.get("requiredAction"),
                "notes": item.get("notes"),
                "cwes": item.get("cwes"),
                "ingestion_timestamp": datetime.now(timezone.utc),
            })
        
        logging.info(f"Data transformation complete: {len(transformed)} records ready")
        return transformed
    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        raise



def load_data(collection, data):
    try:
        if not data:
            return
        result = collection.insert_many(data)
        logging.info(f"Inserted {len(result.inserted_ids)} records into MongoDB")
    except Exception as e:
        logging.error(f"Loading to MongoDB failed: {e}")
        raise

def run_etl():
    try:
        collection = get_mongo_collection()
        extracted_data = extract_data()
        transformed_data = transform_data(extracted_data)
        load_data(collection, transformed_data)
        logging.info("ETL job completed successfully")
    except Exception as e:
        logging.error(f"ETL job failed: {e}")

if __name__ == "__main__":
    run_etl()
