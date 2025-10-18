import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from config.mongo import mongoConfig
from config.blocklist import blocklistConfig

client = pymongo.MongoClient(mongoConfig["URI"])
db = client[mongoConfig["DB"]]
collection_ip = db[mongoConfig["COLLECTION_IP"]]

def extract_ip(ip_address, start_ts=None, end_ts=None, output_format="json"):
    params = {"ip": ip_address}
    if start_ts is not None:
        params["start"] = start_ts
    if end_ts is not None:
        params["end"] = end_ts
    params["format"] = output_format
    url = blocklistConfig["BASE_URL"] + "/api.php"
    response = requests.get(url, params=params)
    response.raise_for_status()
    if output_format == "json":
        data = response.json()
    else:
        data = response.text
    return data

def transform_ip(raw_data, ip_address):
    now = datetime.utcnow().isoformat() + "Z"
    # raw_data may have keys like 'attacks', 'reports', etc (depending on format)
    # We’ll assume JSON and keys 'attacks' & 'reports'
    doc = {
        "ip": ip_address,
        "queried_at": now,
        "attacks": raw_data.get("attacks"),
        "reports": raw_data.get("reports"),
        "raw": raw_data
    }
    return doc

def load_ip(doc):
    if doc:
        collection_ip.insert_one(doc)
        print(f"Inserted IP query doc for {doc['ip']}")
    else:
        print("No document to insert.")

def main_ip(ip_list, start_ts=None, end_ts=None):
    for ip in ip_list:
        try:
            raw = extract_ip(ip, start_ts=start_ts, end_ts=end_ts, output_format="json")
            doc = transform_ip(raw, ip)
            load_ip(doc)
        except Exception as e:
            print(f"IP query ETL failed for {ip}: {e}")

if _name_ == "_main_":
    ips = ["78.46.91.239", "1.2.3.4"]
    main_ip(ips, start_ts=1)