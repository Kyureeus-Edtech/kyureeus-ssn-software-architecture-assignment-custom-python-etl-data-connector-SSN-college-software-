# etl_connector.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
SOURCE_COLLECTION = os.getenv("SOURCE_COLLECTION")
TARGET_COLLECTION = os.getenv("TARGET_COLLECTION")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
source_collection = db[SOURCE_COLLECTION]
target_collection = db[TARGET_COLLECTION]

def extract():
    """Extract data from the source MongoDB collection."""
    return list(source_collection.find())

def transform(data):
    """Transform the data before loading."""
    for doc in data:
        doc['processed_at'] = datetime.utcnow()
        doc.pop('_id', None)  # Remove _id to avoid duplicate key errors
    return data

def load(data):
    """Load transformed data into the target MongoDB collection."""
    if data:
        target_collection.insert_many(data)
        print(f"Inserted {len(data)} documents into {DB_NAME}.{TARGET_COLLECTION}")
    else:
        print("No data to load.")

if __name__ == "__main__":
    try:
        raw_data = extract()
        processed_data = transform(raw_data)
        load(processed_data)
    except Exception as e:
        print(f"ETL pipeline failed: {e}")