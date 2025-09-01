import os
import requests
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from io import StringIO

load_dotenv()

def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")
    collection_name = os.getenv("MONGO_COLLECTION")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

def extract_csv(base_url: str, endpoint: str) -> pd.DataFrame:
    url = f"{base_url}{endpoint}"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
    df = pd.read_csv(StringIO(response.text), comment="#")

    return df


def transform_data(df: pd.DataFrame) -> list:
    records = df.to_dict(orient="records")
    for rec in records:
        rec["ingested_at"] = datetime.utcnow()
    return records

def load_to_mongo(records: list):
    collection = get_mongo_collection()
    if records:
        collection.insert_many(records)
        print(f"[INFO] Inserted {len(records)} records into MongoDB")
    else:
        print("[INFO] No records to insert.")


def run_etl():
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    endpoint = os.getenv("ENDPOINT")

    print("[INFO] Starting ETL process...")
    df = extract_csv(base_url, endpoint)
    records = transform_data(df)
    load_to_mongo(records)
    print("[INFO] ETL process completed.")


if __name__ == "__main__":
    run_etl()
