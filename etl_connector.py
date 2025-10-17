#!/usr/bin/env python3
"""
RDAP ETL Connector
- Calls RDAP endpoints: /domain/{name}, /ip/{address}, /autnum/{asn}
- Transforms and stores results in MongoDB collections:
    rdap_domain_raw, rdap_ip_raw, rdap_autnum_raw
- Uses environment variables for configuration and secrets (.env)
"""

import os
import time
import json
import logging
import argparse
from datetime import datetime
from typing import Any, Dict, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# Load environment variables from .env if present
load_dotenv()

# === Configuration from ENV ===
RDAP_BASE = os.getenv("RDAP_BASE", "https://rdap.org")  # default RDAP public resolver
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "rdap_data")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "1.0"))
USER_AGENT = os.getenv("USER_AGENT", "rdap-etl/1.0 (+https://example.org)")

# Basic logging config
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("rdap_etl")


# === HTTP session with retries ===
def create_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": USER_AGENT})
    return s


session = create_session()


# === MongoDB helper ===
def get_mongo_client() -> MongoClient:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info("Connected to MongoDB")
        return client
    except errors.PyMongoError as e:
        logger.exception("Failed to connect to MongoDB: %s", e)
        raise


# === Utilities: safe request handling and transformation ===
def safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    tries = 0
    while True:
        tries += 1
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            logger.warning("Request error (try %d): %s", tries, e)
            if tries >= MAX_RETRIES:
                raise
            time.sleep(BACKOFF_FACTOR * (2 ** (tries - 1)))
            continue

        status = resp.status_code
        if status == 429:
            ra = resp.headers.get("Retry-After")
            wait = int(ra) if ra and ra.isdigit() else BACKOFF_FACTOR * (2 ** (tries - 1))
            logger.warning("Rate limited (429). Retry after %s seconds", wait)
            time.sleep(wait)
            if tries >= MAX_RETRIES:
                raise RuntimeError("Too many 429 responses")
            continue

        if 500 <= status < 600:
            logger.warning("Server error %d on %s", status, url)
            if tries >= MAX_RETRIES:
                resp.raise_for_status()
            time.sleep(BACKOFF_FACTOR * (2 ** (tries - 1)))
            continue

        try:
            payload = resp.json()
        except ValueError:
            logger.error("Non-JSON response from %s", url)
            raise RuntimeError(f"Non-JSON response from {url} (status {status})")

        return {
            "status_code": status,
            "headers": dict(resp.headers),
            "payload": payload,
            "url": resp.url,
        }


def normalized_summary(rdap_obj: Dict[str, Any]) -> Dict[str, Any]:
    summary = {}
    ocn = rdap_obj.get("objectClassName")
    summary["objectClassName"] = ocn

    for k in ("handle", "ldhName", "name", "startAddress", "endAddress", "startAutnum", "autnum", "country"):
        if k in rdap_obj:
            summary[k] = rdap_obj.get(k)

    if "status" in rdap_obj:
        summary["status"] = rdap_obj.get("status")

    if "entities" in rdap_obj and isinstance(rdap_obj["entities"], list):
        entities = []
        for e in rdap_obj["entities"]:
            ent = {"handle": e.get("handle"), "objectClassName": e.get("objectClassName")}
            if "vcardArray" in e:
                try:
                    v = e["vcardArray"]
                    for item in v[1]:
                        if item and isinstance(item, list) and item[0] == "fn":
                            ent["fn"] = item[3]
                            break
                except Exception:
                    pass
            if "roles" in e:
                ent["roles"] = e.get("roles")
            entities.append({k: v for k, v in ent.items() if v is not None})
        summary["entities"] = entities

    return summary


def make_document(rdap_resp: Dict[str, Any]) -> Dict[str, Any]:
    payload = rdap_resp["payload"]
    doc = {
        "ingested_at": datetime.utcnow(),
        "source_url": rdap_resp.get("url"),
        "http_status": rdap_resp.get("status_code"),
        "headers": rdap_resp.get("headers"),
        "raw": payload,
        "normalized": normalized_summary(payload),
    }
    return doc


# === Specific RDAP endpoint fetchers ===
def fetch_domain(domain_name: str) -> Dict[str, Any]:
    return safe_get(f"{RDAP_BASE.rstrip('/')}/domain/{domain_name}")


def fetch_ip(ip_addr: str) -> Dict[str, Any]:
    return safe_get(f"{RDAP_BASE.rstrip('/')}/ip/{ip_addr}")


def fetch_autnum(asn: str) -> Dict[str, Any]:
    asn_clean = asn.upper().replace("AS", "")
    return safe_get(f"{RDAP_BASE.rstrip('/')}/autnum/{asn_clean}")


# === ETL operations ===
class RDAPConnector:
    def __init__(self, mongo_client: MongoClient, db_name: str = MONGO_DB):
        self.client = mongo_client
        self.db = self.client[db_name]

    def ensure_indexes(self):
        try:
            self.db["rdap_domain_raw"].create_index("source_url", unique=True, sparse=True)
            self.db["rdap_ip_raw"].create_index("source_url", unique=True, sparse=True)
            self.db["rdap_autnum_raw"].create_index("source_url", unique=True, sparse=True)
        except Exception as e:
            logger.warning("Index creation issue: %s", e)

    def upsert_doc(self, collection_name: str, doc: Dict[str, Any]):
        coll = self.db[collection_name]
        source = doc.get("source_url")
        try:
            if source:
                result = coll.update_one(
                    {"source_url": source},
                    {"$set": doc, "$setOnInsert": {"first_ingested_at": doc["ingested_at"]}},
                    upsert=True,
                )
                logger.info(
                    "Upsert into %s matched=%s modified=%s upserted_id=%s",
                    collection_name,
                    result.matched_count,
                    result.modified_count,
                    result.upserted_id,
                )
            else:
                res = coll.insert_one(doc)
                logger.info("Inserted doc into %s id=%s", collection_name, res.inserted_id)
        except errors.PyMongoError as e:
            logger.exception("MongoDB write error for %s: %s", collection_name, e)
            raise


# === Load targets ===
def load_config_targets() -> Dict[str, List[str]]:
    """Always try loading config.json from same folder as script."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(
            "Loaded %d domains, %d IPs, %d ASNs from config.json",
            len(data.get("domains", [])),
            len(data.get("ips", [])),
            len(data.get("autnums", [])),
        )
        return data
    except Exception as e:
        logger.warning("Could not load config.json (%s); using demo defaults.", e)
        return {
            "domains": ["iana.org", "example.com"],
            "ips": ["8.8.8.8"],
            "autnums": ["AS15169"],
        }


# === Main orchestration ===
def main():
    parser = argparse.ArgumentParser(description="RDAP ETL Connector")
    parser.add_argument("--dry-run", action="store_true", help="Perform fetches but do not write to MongoDB")
    args = parser.parse_args()

    targets = load_config_targets()

    client = get_mongo_client()
    connector = RDAPConnector(client)
    connector.ensure_indexes()

    for d in targets["domains"]:
        try:
            resp = fetch_domain(d)
            if args.dry_run:
                logger.info("Dry-run domain %s => %s", d, resp.get("status_code"))
                continue
            connector.upsert_doc("rdap_domain_raw", make_document(resp))
        except Exception as e:
            logger.exception("Failed processing domain %s: %s", d, e)

    for ip in targets["ips"]:
        try:
            resp = fetch_ip(ip)
            if args.dry_run:
                logger.info("Dry-run ip %s => %s", ip, resp.get("status_code"))
                continue
            connector.upsert_doc("rdap_ip_raw", make_document(resp))
        except Exception as e:
            logger.exception("Failed processing ip %s: %s", ip, e)

    for a in targets["autnums"]:
        try:
            resp = fetch_autnum(a)
            if args.dry_run:
                logger.info("Dry-run autnum %s => %s", a, resp.get("status_code"))
                continue
            connector.upsert_doc("rdap_autnum_raw", make_document(resp))
        except Exception as e:
            logger.exception("Failed processing autnum %s: %s", a, e)

    logger.info("Finished processing targets.")


if __name__ == "__main__":
    main()
