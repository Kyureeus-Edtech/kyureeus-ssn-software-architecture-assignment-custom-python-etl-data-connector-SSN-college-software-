import requests
import csv
from pymongo import MongoClient
from io import StringIO
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables with defaults
BASEURL = os.getenv("BASEURL", "https://urlhaus.abuse.ch")
API_ENDPOINT = os.getenv("API_ENDPOINT", "/downloads/csv_online/")
CSV_URL = f"{BASEURL}{API_ENDPOINT}"
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB")
MONGO_COLLECTION = os.getenv("COLLECTION_NAME")

# EXTRACT
def fetch_csv(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv"
    }
    print(f"Fetching data from {url} ...")
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

# TRANSFORM
def parse_csv(data):
    lines = []
    header_found = False
    
    for line in data.splitlines():
        if not line.strip():
            continue  # skip empty lines
        if line.startswith("#"):
            # The actual column headers line starts with "# id,"
            if line.startswith("# id,"):
                lines.append(line[2:].strip())  # keep header without "# "
                header_found = True
            # skip any other comment line
            continue
        else:
            lines.append(line.strip())
    
    if not header_found:
        raise ValueError("CSV header not found in feed.")
    
    reader = csv.DictReader(StringIO("\n".join(lines)))
    records = list(reader)

    # transform: strip whitespace, convert empty strings to None
    for rec in records:
        for k, v in rec.items():
            rec[k] = v.strip() if v and isinstance(v, str) else None

    print(f"Parsed {len(records)} records. First record:")
    print(records[0] if records else "No data")
    return records



# LOAD
def insert_to_mongo(records):
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][MONGO_COLLECTION]

    existing_count = col.count_documents({})
    if existing_count > 0:
        print(f"Cleaning up existing {existing_count} records from MongoDB...")
        col.delete_many({})

    if records:
        # Could also drop duplicates by URL before inserting
        result = col.insert_many(records)
        print(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
    else:
        print("No records to insert.")

# MAIN PIPELINE
if __name__ == "__main__":
    try:
        raw_csv = fetch_csv(CSV_URL)
        transformed = parse_csv(raw_csv)
        insert_to_mongo(transformed)
    except Exception as e:
        print(f"Error: {e}")
