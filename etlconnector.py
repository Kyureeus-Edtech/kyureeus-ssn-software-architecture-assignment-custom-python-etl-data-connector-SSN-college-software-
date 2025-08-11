import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


def extract_apod_data(api_key, count=5):
    """Extracts a specified number of random entries from the NASA APOD API."""
    print(f"Extracting {count} records from NASA APOD...")
    api_url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&count={count}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Checks for HTTP errors
        print("Extraction successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Extraction failed: {e}")
        return None


def transform_data(data):
    """Transforms data for loading."""
    if not data:
        return []
    
    print("Transforming data...")
    transformed_records = []
    for record in data:
        transformed_record = {
            'title': record.get('title'),
            'date': record.get('date'),
            'description': record.get('explanation'),
            'url': record.get('url'),
            'media_type': record.get('media_type'),
            'copyright': record.get('copyright', 'Public Domain'),
            'ingestion_timestamp': datetime.now(timezone.utc)
        }
        transformed_records.append(record)
    
    print("Transformation successful!")
    return transformed_records


def load_data(data):
    """Loads transformed data into MongoDB."""
    if not data:
        print("No data to load.")
        return

    print("Loading data into MongoDB...")
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not found in environment variables.")
        return

    try:
        client = MongoClient(mongo_uri)
        db = client.data_pipelines
        collection = db.nasa_apod_raw 
        
        result = collection.insert_many(data)
        print(f"Successfully loaded {len(result.inserted_ids)} records.")
    except Exception as e:
        print(f"Load failed: {e}")
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    nasa_api_key = os.getenv("NASA_API_KEY")
    if not nasa_api_key:
        print("Fatal Error: NASA_API_KEY is not set in your .env file.")
    else:
        extracted_data = extract_apod_data(nasa_api_key, count=25)
        if extracted_data:
            transformed_data = transform_data(extracted_data)
            load_data(transformed_data)