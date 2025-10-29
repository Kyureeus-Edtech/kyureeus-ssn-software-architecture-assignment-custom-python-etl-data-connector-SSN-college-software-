from pymongo import MongoClient
from core.utils import log, get_mongo_uri

def load_to_mongodb(data, collection_name):
    if not data:
        log(f"No data to load for {collection_name}")
        return
    
    client = MongoClient(get_mongo_uri())
    db = client["cve_search_db"]
    collection = db[collection_name]
    collection.insert_many(data)
    log(f"Inserted {len(data)} records into {collection_name}")
    client.close()
