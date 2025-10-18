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
collection_server = db[mongoConfig["COLLECTION_SERVER"]]

def extract_server(server_id=None, email=None, apikey=None, start_ts=None, end_ts=None, output_format="json"):
    params = {}
    if server_id is not None:
        params["server"] = server_id
    if email is not None:
        params["email"] = email
    if apikey is not None:
        params["apikey"] = apikey
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

def transform_server(raw_data, server_id=None, email=None):
    now = datetime.utcnow().isoformat() + "Z"
    doc = {
        "queried_at": now,
        "server_id": server_id,
        "email": email,
        "raw": raw_data
    }
    if isinstance(raw_data, dict):
        doc["attacks"] = raw_data.get("attacks")
        doc["reports"] = raw_data.get("reports")
    return doc

def load_server(doc):
    if doc:
        collection_server.insert_one(doc)
        print("Inserted server/user query document.")
    else:
        print("No document to insert.")

def main_server(server_id=None, email=None, apikey=None, start_ts=None, end_ts=None):
    try:
        raw = extract_server(server_id=server_id, email=email, apikey=apikey,
                             start_ts=start_ts, end_ts=end_ts, output_format="json")
        doc = transform_server(raw, server_id=server_id, email=email)
        load_server(doc)
    except Exception as e:
        print(f"Server/user query ETL failed: {e}")

if _name_ == "_main_":
    # Example: server with id=25
    main_server(server_id=25, apikey=os.getenv("BLOCKLIST_APIKEY"), start_ts=1270087500)
    # Or user via email
    main_server(email="you@example.com", apikey=os.getenv("BLOCKLIST_APIKEY"), start_ts=1)