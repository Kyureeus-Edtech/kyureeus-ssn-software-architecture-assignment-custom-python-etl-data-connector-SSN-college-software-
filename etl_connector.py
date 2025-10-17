#!/usr/bin/env python3
import argparse, time, json, sys, os, logging
from datetime import datetime,timezone
from typing import Dict, Any, List
import requests
from requests.adapters import HTTPAdapter, Retry
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "rdap_etl_db")

ENDPOINTS = {
    "arin": "https://rdap.arin.net/registry/ip/{ip}",
    "ripe": "https://rdap.db.ripe.net/ip/{ip}",
    "apnic": "https://rdap.apnic.net/ip/{ip}"
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def requests_session(retries=3, backoff_factor=0.3, status_forcelist=(500,502,504)):
    s = requests.Session()
    retries_cfg = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    s.mount("https://", HTTPAdapter(max_retries=retries_cfg))
    s.headers.update({"User-Agent": "RDAP-ETL/1.0"})
    return s

def extract_rdap(connector: str, ip: str, session: requests.Session, timeout=10) -> Dict[str, Any]:
    if connector not in ENDPOINTS:
        raise ValueError(f"Unknown connector: {connector}")
    url = ENDPOINTS[connector].format(ip=ip)
    logging.info("Querying %s -> %s", connector, url)
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def transform_rdap(connector: str, ip: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    doc = {
        "connector": connector,
        "queried_ip": ip,
        "fetched_at": datetime.now(timezone.utc),
        "raw": raw,
    }
    entity_names = []
    if isinstance(raw.get("entities"), list):
        for e in raw["entities"]:
            v = e.get("vcardArray") if isinstance(e.get("vcardArray"), list) else None
            if v and len(v) >= 2:
                for item in v[1]:
                    if item and isinstance(item, list) and item[0] == "fn":
                        entity_names.append(item[3])
            elif isinstance(e.get("handle"), str):
                entity_names.append(e.get("handle"))

    network_name = raw.get("name") or raw.get("network") or raw.get("objectClassName")
    start_address = raw.get("startAddress") or raw.get("ipVersion")
    end_address = raw.get("endAddress")
    remarks = raw.get("remarks")
    events = raw.get("events")

    doc["summary"] = {
        "network_name": network_name,
        "start_address": start_address,
        "end_address": end_address,
        "entities": entity_names,
        "remarks_count": len(remarks) if isinstance(remarks, list) else 0,
        "events_count": len(events) if isinstance(events, list) else 0,
    }
    return doc

def load_to_mongo(documents: List[Dict[str, Any]], connector: str):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll_name = f"rdap_{connector}_raw"
    coll = db[coll_name]
    if not documents:
        logging.info("No documents to insert for %s", connector)
        return
    try:
        result = coll.insert_many(documents)
        logging.info("Inserted %d documents into %s.%s", len(result.inserted_ids), MONGO_DB, coll_name)
    except errors.BulkWriteError as e:
        logging.error("Bulk write error: %s", e.details)
        raise

def process_ips_for_connector(connector: str, ips: List[str], sleep_between=0.2):
    session = requests_session()
    docs = []
    for ip in ips:
        try:
            raw = extract_rdap(connector, ip, session)
            doc = transform_rdap(connector, ip, raw)
            docs.append(doc)
        except requests.HTTPError as e:
            logging.warning("HTTP error for %s %s: %s", connector, ip, e)
        except Exception as e:
            logging.exception("Failed processing %s %s: %s", connector, ip, e)
        time.sleep(sleep_between)
    load_to_mongo(docs, connector)

def load_ips_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf8") as fh:
        lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    return lines

def main():
    parser = argparse.ArgumentParser(description="RDAP ETL connector runner")
    parser.add_argument("--connector", choices=list(ENDPOINTS.keys())+["all"], required=True)
    parser.add_argument("--ips", help="comma separated list of IP addresses", default="")
    parser.add_argument("--ips-file", help="path to newline separated file of IPs", default="")
    parser.add_argument("--sleep", type=float, default=0.2, help="sleep between requests (seconds)")
    args = parser.parse_args()

    ips = []
    if args.ips:
        ips = [ip.strip() for ip in args.ips.split(",") if ip.strip()]
    elif args.ips_file:
        ips = load_ips_from_file(args.ips_file)
    else:
        print("Provide --ips or --ips-file")
        sys.exit(1)

    connectors = [args.connector] if args.connector != "all" else list(ENDPOINTS.keys())
    for c in connectors:
        logging.info("Starting connector: %s for %d ips", c, len(ips))
        process_ips_for_connector(c, ips, sleep_between=args.sleep)

if __name__ == "__main__":
    main()
