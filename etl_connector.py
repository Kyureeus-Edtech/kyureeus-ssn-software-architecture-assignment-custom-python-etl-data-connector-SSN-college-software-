import requests
import pandas as pd
import io
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv() 
# Config
ABUSE_FEED_URL = os.getenv("ABUSE_FEED_URL")
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# URLhaus CSV expected columns (official docs)
COLUMNS = [
    "id", "date_added", "url", "url_status", "date_modified",
    "threat", "tags", "reporter", "url_info"
]

def fetch_abuse_feed():
    response = requests.get(ABUSE_FEED_URL)
    if response.status_code == 200:
        print("✅ Feed downloaded successfully")
        return response.text
    else:
        print(f"❌ Failed to fetch feed. Status code: {response.status_code}")
        return None

def transform(csv_text):
    if not csv_text:
        return []

    # Skip comment lines
    lines = [line for line in csv_text.splitlines() if not line.startswith("#")]

    # Read CSV with manual column names
    df = pd.read_csv(io.StringIO("\n".join(lines)), names=COLUMNS, header=None)

    print("Columns detected:", df.columns.tolist())  # Debug

    # Drop duplicates & missing URLs
    df = df.drop_duplicates()
    df = df.dropna(subset=["url"])

    # Convert date_added
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

    # Extract domain from URL
    df["domain"] = df["url"].str.extract(r'https?://([^/]+)/?')

    # Ingest timestamp
    df["ingested_at"] = datetime.utcnow()

    # Select relevant fields
    records = df[["url", "domain", "threat", "url_status", "date_added", "ingested_at"]].to_dict(orient="records")

    print(f"✅ Transformed {len(records)} records")
    return records

def insert_into_mongo(records):
    if not records:
        print("⚠️ No records to insert.")
        return

    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    result = collection.insert_many(records)
    print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB")

def main():
    csv_text = fetch_abuse_feed()
    records = transform(csv_text)
    insert_into_mongo(records)

if __name__ == "__main__":
    main()
