import os
import requests
import pymongo
from datetime import datetime

from config.wayback import waybackConfig
from config.mongo import mongoConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection_cdx = db[mongoConfig["COLLECTION_CDX"]]

def extract_cdx(url, start_ts=None, end_ts=None, filters=None, fields=None, collapse=None, output="json"):
    params = {
        "url": url,
        "output": output
    }
    if start_ts:
        params["from"] = start_ts
    if end_ts:
        params["to"] = end_ts
    if filters:
        # filters expected as list of strings like "statuscode:200"
        params["filter"] = filters
    if fields:
        params["fl"] = fields
    if collapse:
        params["collapse"] = collapse
    url_base = waybackConfig["CDX_BASE_URL"] # e.g., "https://web.archive.org/cdx/search/cdx"
    response = requests.get(url_base, params=params)
    response.raise_for_status()
    # assume JSON output
    data = response.json()
    return data

def transform_cdx(records, url):
    transformed = []
    now = datetime.utcnow().isoformat() + 'Z'
    # assuming records is a list of dicts or arrays
    for rec in records:
        # if rec is array of values, map to fields accordingly
        doc = {
            "url": url,
            "queried_at": now,
            "timestamp": rec.get("timestamp") or rec[0],
            "original": rec.get("original") or rec[1],
            "statuscode": rec.get("statuscode") or rec[2] if len(rec)>2 else None
        }
        transformed.append(doc)
    return transformed

def load_cdx(docs):
    if docs:
        collection_cdx.insert_many(docs)
        print(f"Inserted {len(docs)} CDX snapshot docs for URL.")
    else:
        print("No CDX docs to insert.")

def main_cdx(url_list, start_ts=None, end_ts=None):
    for url in url_list:
        try:
            raw = extract_cdx(url, start_ts=start_ts, end_ts=end_ts, filters=["statuscode:200"], fields="timestamp,original,statuscode", collapse="digest")
            docs = transform_cdx(raw, url)
            load_cdx(docs)
        except Exception as e:
            print(f"CDX ETL failed for {url}: {e}")

if __name__ == "__main__":
    urls = ["https://example.com"]
    main_cdx(urls, start_ts="20000101", end_ts="20250101")
