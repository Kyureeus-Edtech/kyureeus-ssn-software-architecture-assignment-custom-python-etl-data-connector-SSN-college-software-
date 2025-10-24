@@ -0,0 +1,124 @@
import os
import time
import logging
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGODB_DB", "abusech_db")

if not MONGO_URI:
    raise SystemExit("MONGO_URI not set in .env")

# --------------------------
# MongoDB client setup
# --------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# --------------------------
# Logging
# --------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --------------------------
# Public Feeds
# --------------------------
feeds = {
    "recent_urls": "https://urlhaus.abuse.ch/downloads/csv_recent/",
    "online_urls": "https://urlhaus.abuse.ch/downloads/csv_online/",
    "feodotracker": "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
}

# --------------------------
# Helper Functions
# --------------------------
def fetch_csv(url: str, retries=3) -> pd.DataFrame:
    """Fetch CSV data from URL with retries"""
    for attempt in range(retries):
        try:
            logging.info(f"Fetching data from {url} (Attempt {attempt+1})")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # CSV only
            if "feodotracker" in url:
                # FeodoTracker CSV does not have headers
                df = pd.read_csv(StringIO(response.text), comment="#", names=["ip", "first_seen"], on_bad_lines='skip')
            else:
                df = pd.read_csv(StringIO(response.text), comment="#", on_bad_lines='skip')

            logging.info(f"✅ Fetched {len(df)} records")
            return df

        except Exception as e:
            logging.error(f"Attempt {attempt+1} failed: {e}")
            time.sleep(5)

    logging.warning(f"Failed to fetch data from {url} after {retries} attempts")
    return pd.DataFrame()


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names, remove duplicates"""
    if df.empty:
        return df

    # Clean column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Remove duplicates
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"])
    elif "ip" in df.columns:
        df = df.drop_duplicates(subset=["ip"])
    else:
        df = df.drop_duplicates()

    return df


def load_to_mongo(df: pd.DataFrame, collection_name: str):
    """Insert DataFrame into MongoDB with ingestion timestamp"""
    if df.empty:
        logging.warning(f"No data to load for {collection_name}")
        return

    df["_ingested_at"] = datetime.utcnow()
    records = df.to_dict(orient="records")

    collection = db[collection_name]
    try:
        collection.insert_many(records)
        logging.info(f"💾 Inserted {len(records)} records into {collection_name}")
    except Exception as e:
        logging.error(f"❌ Error inserting into MongoDB: {e}")


# --------------------------
# ETL Runner
# --------------------------
def run_etl():
    for name, url in feeds.items():
        logging.info(f"\n🚀 Running ETL for: {name}")
        df = fetch_csv(url)
        df = transform_data(df)
        load_to_mongo(df, f"{name}_raw")
        time.sleep(2)  # polite pause

    logging.info("\n🎉 ETL process completed successfully!")


# --------------------------
# Main
# --------------------------
if _name_ == "_main_":
    run_etl()