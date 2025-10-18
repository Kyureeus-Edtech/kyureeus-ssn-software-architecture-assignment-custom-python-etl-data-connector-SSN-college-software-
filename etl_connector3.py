import os
import requests
import pymongo
from datetime import datetime

from config.wayback import waybackConfig
from config.mongo import mongoConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection_save = db[mongoConfig["COLLECTION_SAVE"]]

def extract_save(url, user_agent=None, tags=None):
    headers = {}
    if user_agent:
        headers["User-Agent"] = user_agent
    params = {"url": url}
    if tags:
        params["tags"] = tags  # optional extra metadata
    response = requests.post(waybackConfig["SAVE_BASE_URL"] + "/save/", params=params, headers=headers)
    response.raise_for_status()
    # The response may redirect or contain JSON/headers with info.
    # For simplicity we capture response headers and final url
    archive_url = response.url
    return {"url": url, "archive_url": archive_url, "status_code": response.status_code}

def transform_save(record):
    now = datetime.utcnow().isoformat() + 'Z'
    doc = {
        "url": record["url"],
        "archive_url": record["archive_url"],
        "response_status": record["status_code"],
        "saved_at": now
    }
    return doc

def load_save(doc):
    if doc:
        collection_save.insert_one(doc)
        print(f"Inserted save doc for url {doc['url']}")
    else:
        print("No doc to insert.")

def main_save(url_list, user_agent=None):
    for url in url_list:
        try:
            raw = extract_save(url, user_agent=user_agent)
            doc = transform_save(raw)
            load_save(doc)
        except Exception as e:
            print(f"Save ETL failed for {url}: {e}")

if __name__ == "__main__":
    urls = ["https://example.com"]
    main_save(urls, user_agent="MyApp/1.0")
