# Imports
import os
import io
import pandas as pd
import requests
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

# ----------
# STEP 1: EXTRACT
#   Extract CSV data from API URL
# ----------
def extract_csv(url):
    try:
        print("[INFO] Downloading CSV from:", url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch CSV: {e}")
        return None

# ----------
# STEP 2: TRANSFORM
#   Transform the csv records to a dataframe using Pandas
# ----------
def transform_csv(csv_content):
    try:
        if not csv_content:
            print("[ERROR] No CSV content to transform.")
            return None
        df = pd.read_csv(io.StringIO(csv_content), comment='#')
        df['ingested_at'] = datetime.now(timezone.utc)
        print("[INFO] Successfully transformed CSV data")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[ERROR] Failed to transform CSV: {e}")
        return None

# ----------
# STEP 3: LOAD
#   Load data to MongoDB
# ----------
def load_to_mongo(records, mongo_uri, db_name, collection_name):
    try:
        if not records:
            print("[ERROR] No records to load into MongoDB.")
            return
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        print(f"[INFO] Loading {len(records)} records into MongoDB")
        collection.insert_many(records)
        print("[INFO] Data loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load data into MongoDB: {e}")

# ----------
# MAIN FUNCTION
# ----------
def main():
    load_dotenv()
    csv_url = os.getenv("CSV_API_URL")
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")
    connector_name = os.getenv("CONNECTOR_NAME")

    csv_data = extract_csv(csv_url)
    records = transform_csv(csv_data)
    load_to_mongo(records, mongo_uri, mongo_db, f"{connector_name}_raw")

if __name__ == "__main__":
    main()
