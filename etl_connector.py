import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import time

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
COUNTRY_RESOURCE_URL = os.getenv("RIPESTAT_COUNTRY_RESOURCE_URL")
ANNOUNCED_PREFIXES_URL = os.getenv("RIPESTAT_ANNOUNCED_PREFIXES_URL")
ATLAS_PROBES_URL = os.getenv("RIPESTAT_ATLAS_PROBES_URL")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

collections = {
    "country_resources": db["country_resources"],
    "announced_prefixes": db["announced_prefixes"],
    "atlas_probes": db["atlas_probes"]
}

countries = ["IN", "GB", "DE"]
asns = ["AS3333", "AS3356", "AS15169"]

def fetch_with_retries(url, params, retries=3, timeout=30):
    for i in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if i < retries - 1:
                time.sleep(2 ** i)
            else:
                return None

def extract_country_resources(country):
    return fetch_with_retries(COUNTRY_RESOURCE_URL, {"resource": country})

def extract_announced_prefixes(asn):
    return fetch_with_retries(ANNOUNCED_PREFIXES_URL, {"resource": asn})

def extract_atlas_probes(country):
    return fetch_with_retries(ATLAS_PROBES_URL, {"resource": country})

def transform_country_resources(data, country):
    if not data or "data" not in data:
        return []
    resources = data["data"].get("resources", [])
    transformed = [{"country": country, "prefixes": resources}]
    return transformed

def transform_announced_prefixes(data, asn):
    if not data or "data" not in data:
        return []
    prefixes = [p["prefix"] for p in data["data"].get("prefixes", [])]
    transformed = [{"asn": asn, "prefixes": prefixes}]
    return transformed

def transform_atlas_probes(data, country):
    if not data or "data" not in data:
        return []
    probes = data["data"].get("probes", [])
    transformed = [{"country": country, "probes": probes}]
    return transformed

def load(collection_name, records, upsert_key):
    if records:
        coll = collections[collection_name]
        for record in records:
            coll.update_one(
                {upsert_key: record[upsert_key]},
                {"$set": record},
                upsert=True
            )

def main():
    for country in countries:
        data = extract_country_resources(country)
        records = transform_country_resources(data, country)
        load("country_resources", records, "country")

    for asn in asns:
        data = extract_announced_prefixes(asn)
        records = transform_announced_prefixes(data, asn)
        load("announced_prefixes", records, "asn")

    for country in countries:
        data = extract_atlas_probes(country)
        records = transform_atlas_probes(data, country)
        load("atlas_probes", records, "country")

if __name__ == "__main__":
    main()
