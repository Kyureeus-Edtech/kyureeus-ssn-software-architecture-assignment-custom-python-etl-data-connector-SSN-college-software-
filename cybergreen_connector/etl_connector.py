import os
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from datetime import datetime

# Load environment variables from .env
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

def extract_metrics(metric_name="open_resolvers", date="2023-01-01"):
    """
    Extracts data from the CyberGreen Metrics API.
    """
    try:
        url = f"{BASE_URL}/metrics"
        params = {
            "name": metric_name,
            "date": date
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raises an error for bad status codes
        data = response.json()
        if not data:
            raise ValueError("No data returned from API")
        return data
    except Exception as e:
        print("Error during data extraction:", e)
        raise

def transform_data(data):
    """
    Adds ingestion timestamp for audit purposes.
    """
    transformed = data.copy()
    transformed["ingested_at"] = datetime.utcnow()
    return transformed

def load_to_mongo(data):
    """
    Loads transformed data into MongoDB.
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)
        print("Data inserted successfully.")
    except Exception as e:
        print("Error loading data to MongoDB:", e)
        raise

if __name__ == "__main__":
    try:
        raw_data = extract_metrics()  # default params; can pass args here
        transformed_data = transform_data(raw_data)
        load_to_mongo(transformed_data)
    except Exception as e:
        print("Error in ETL process:", e)
