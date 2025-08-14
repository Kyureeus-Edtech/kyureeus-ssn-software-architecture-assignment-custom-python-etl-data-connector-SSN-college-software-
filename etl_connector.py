import os
import requests
import pymongo
from datetime import datetime

from config.malshare import malshareConfig
from config.mongo import mongoConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection = db[mongoConfig["COLLECTION"]]

def extract():
    params = {
        'api_key': malshareConfig["API_KEY"],
        'action': 'getlist'
    }
    response = requests.get(malshareConfig["BASE_URL"], params=params)
    response.raise_for_status()
    data = response.json()
    return data

def transform(records):
    transformed = []
    now = datetime.utcnow().isoformat() + 'Z'
    for rec in records:
        doc = {
            'md5': rec.get('md5'),
            'sha1': rec.get('sha1'),
            'sha256': rec.get('sha256'),
            'ingested_at': now
        }
        transformed.append(doc)
    return transformed

def load(docs):
    if docs:
        collection.insert_many(docs)
        print(f"Inserted {len(docs)} documents into MongoDB.")
    else:
        print("No documents to insert.")

def main():
    try:
        raw_data = extract()
        docs = transform(raw_data)
        load(docs)
    except Exception as e:
        print(f"ETL process failed: {e}")

if __name__ == "__main__":
    main()
