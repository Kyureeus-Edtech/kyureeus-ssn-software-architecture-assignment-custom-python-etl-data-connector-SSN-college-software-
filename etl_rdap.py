import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

import requests
import pymongo
from dotenv import load_dotenv

load_dotenv()

RDAP_API_BASE = os.getenv("RDAP_BASE_URL", "https://rdap.org/")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "etl_db")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "rdap_data")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def fetch_rdap_data(domains: List[str] = None, ips: List[str] = None, asns: List[int] = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    if domains:
        for domain in domains:
            url = f"{RDAP_API_BASE.rstrip('/')}/domain/{domain}"
            try:
                logger.info(f"Fetching RDAP domain data for: {domain}")
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    results.append({"type": "domain", "key": domain, "data": resp.json()})
                else:
                    logger.warning(f"Failed to fetch domain {domain}: HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.error(f"Error fetching domain {domain}: {e}")

    if ips:
        for ip in ips:
            url = f"{RDAP_API_BASE.rstrip('/')}/ip/{ip}"
            try:
                logger.info(f"Fetching RDAP IP data for: {ip}")
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    results.append({"type": "ip", "key": ip, "data": resp.json()})
                else:
                    logger.warning(f"Failed to fetch IP {ip}: HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.error(f"Error fetching IP {ip}: {e}")

    if asns:
        for asn in asns:
            url = f"{RDAP_API_BASE.rstrip('/')}/autnum/{asn}"
            try:
                logger.info(f"Fetching RDAP ASN data for: {asn}")
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    results.append({"type": "autnum", "key": asn, "data": resp.json()})
                else:
                    logger.warning(f"Failed to fetch ASN {asn}: HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.error(f"Error fetching ASN {asn}: {e}")

    return results

def sanitize_mongo_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k.replace(".", "_").replace("$", "_"): sanitize_mongo_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_mongo_keys(i) for i in obj]
    else:
        return obj

def transform_data(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logger.info("Transforming RDAP data for MongoDB insertion...")
    transformed = []
    for record in raw_records:
        transformed.append({
            "object_type": record["type"],
            "object_key": record["key"],
            "rdap_data": sanitize_mongo_keys(record["data"]),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
    return transformed

def load_to_mongo(docs: List[Dict[str, Any]]):
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI environment variable not set.")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    if docs:
        result = collection.insert_many(docs)
        logger.info(f"Inserted {len(result.inserted_ids)} RDAP records into {DB_NAME}.{COLLECTION_NAME}")
    else:
        logger.warning("No documents to insert into MongoDB.")

def run_etl():
    domains = ["example.com", "openai.com"]
    ips = ["8.8.8.8", "2001:4860:4860::8888"]
    asns = [15169]

    try:
        raw_data = fetch_rdap_data(domains=domains, ips=ips, asns=asns)
        transformed_docs = transform_data(raw_data)
        load_to_mongo(transformed_docs)
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception(f"ETL process failed: {e}")

if __name__ == "__main__":
    run_etl()
