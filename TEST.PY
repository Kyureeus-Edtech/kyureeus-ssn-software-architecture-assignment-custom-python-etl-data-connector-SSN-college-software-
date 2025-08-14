import requests
from pymongo import MongoClient
from pprint import pprint  # For pretty printing JSON
import os
from datetime import datetime

def transform(raw_data):
    transformed = []
    for item in raw_data:
        # Example transformation:
        # - Keep only id, title, and body fields
        # - Rename 'id' to 'post_id'
        # - Convert title to uppercase
        # - Add ingestion timestamp

        transformed_item = {
            "post_id": item.get("id"),
            "title": item.get("title", "").upper(),
            "content": item.get("body", ""),
            "ingested_at": datetime.utcnow()
        }

        # Example: Filter out posts where title is empty
        if transformed_item["title"]:
            transformed.append(transformed_item)

    print(f"Transformed {len(transformed)} records")
    return transformed

# MongoDB connection URI
MONGODB_URI = "mongodb://localhost:27017/vi"

# Example public API (you can replace with your own)
API_URL = "https://jsonplaceholder.typicode.com/posts"

def fetch_api_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()  # API data in JSON format (list of dicts)
        return data
    else:
        print(f"Failed to fetch data: Status code {response.status_code}")
        return []

def insert_into_mongo(data):
    client = MongoClient(MONGODB_URI)
    db = client.get_database()
    collection = db['VIGS']  # Collection name

    if not data:
        print("No data to insert")
        return

    # Insert data into MongoDB
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents into MongoDB")

def main():
    data = fetch_api_data()

    print("Fetched JSON data:")
    clean_data=transform(data);
    insert_into_mongo(clean_data)

if __name__ == "__main__":
    main()
