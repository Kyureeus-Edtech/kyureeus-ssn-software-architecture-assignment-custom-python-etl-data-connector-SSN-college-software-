
import os
import requests
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION")
API_URL = "https://stats.cybergreen.net/api/v1/count"

#Extract data from API
def extract_data_in_pages():
    page = 1
    while True:
        print(f"Fetching page {page} from API...")
        response = requests.get(API_URL, params={"page": page})
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No more data from API.")
            break

        df = pd.DataFrame(results)
        yield df
        page += 1

#Transforming data
def transform_data(df):
    print("Transforming data chunk...")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['risk'] = pd.to_numeric(df['risk'], errors='coerce').astype("Int64")
    df['asn'] = pd.to_numeric(df['asn'], errors='coerce').astype("Int64")
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    df['count_amplified'] = pd.to_numeric(df['count_amplified'], errors='coerce').round(2)
    df['ingested_at'] = datetime.utcnow()
    return df

#Loding data to MongoDB
def load_data_chunk(collection, df):
    records = df.to_dict(orient="records")
    if records:
        collection.insert_many(records)
        print(f"Inserted {len(records)} records.")

def main():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        for df_chunk in extract_data_in_pages():
            transformed_df = transform_data(df_chunk)
            load_data_chunk(collection, transformed_df)
        print("ETL completed successfully.")
    except Exception as e:
        import traceback
        print("ETL failed:")
        traceback.print_exc()

if __name__ == "__main__":
    main()


