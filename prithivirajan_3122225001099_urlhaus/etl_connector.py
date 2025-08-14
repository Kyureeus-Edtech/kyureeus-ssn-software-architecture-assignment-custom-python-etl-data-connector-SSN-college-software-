# import os
# import requests
# import pandas as pd
# from pymongo import MongoClient
# from datetime import datetime
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# API_URL = os.getenv("API_URL")
# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# def extract_data():
#     """Download CSV from URLhaus API"""
#     print("[*] Extracting data from API...")
#     response = requests.get(API_URL)
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch data: {response.status_code}")
    
#     return response.content

# def transform_data(csv_content):
#     """Transform CSV content into DataFrame"""
#     print("[*] Transforming data...")
#     df = pd.read_csv(pd.compat.StringIO(csv_content.decode('utf-8')), comment='#')
    
#     # Add timestamp for ingestion
#     df['ingestion_time'] = datetime.utcnow()
    
#     return df

# def load_data(df):
#     """Load data into MongoDB"""
#     print("[*] Loading data into MongoDB...")
#     client = MongoClient(MONGO_URI)
#     db = client[DB_NAME]
#     collection = db[COLLECTION_NAME]
    
#     # Convert DataFrame to dictionary
#     records = df.to_dict(orient='records')
#     if records:
#         collection.insert_many(records)
#         print(f"[+] Inserted {len(records)} records into MongoDB.")
#     else:
#         print("[!] No records to insert.")

# def main():
#     try:
#         csv_content = extract_data()
#         df = transform_data(csv_content)
#         load_data(df)
#         print("[✓] ETL process completed successfully.")
#     except Exception as e:
#         print(f"[✗] Error: {e}")

# if __name__ == "__main__":
#     main()

import requests
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import io

# ------------------------
# 1. Load environment variables
# ------------------------
load_dotenv()

API_URL = os.getenv("API_URL")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# ------------------------
# 2. Check MongoDB connection
# ------------------------
client = MongoClient(MONGO_URI)
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)

# ------------------------
# 3. Extract data from API
# ------------------------
print(f"📡 Fetching data from {API_URL} ...")
response = requests.get(API_URL)

if response.status_code != 200:
    print(f"❌ Failed to fetch data. Status code: {response.status_code}")
    exit(1)

print("📂 Data downloaded successfully.")

# ------------------------
# 4. Transform data
# ------------------------
print("🔄 Transforming data...")
try:
    # Read CSV directly from API response text
    df = pd.read_csv(io.StringIO(response.text), comment="#")
except Exception as e:
    print("❌ Failed to read CSV:", e)
    exit(1)

# Add ingestion timestamp
df["ingested_at"] = datetime.utcnow()

# Convert DataFrame to list of dicts for MongoDB
data_records = df.to_dict(orient="records")
print(f"📊 Prepared {len(data_records)} records for insertion.")

# ------------------------
# 5. Load data into MongoDB
# ------------------------
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

if data_records:
    collection.delete_many({})  # Clears the collection before new insert

    result = collection.insert_many(data_records)
    print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB collection '{COLLECTION_NAME}'.")
else:
    print("⚠️ No data to insert.")

print("🎉 ETL process completed successfully!")

