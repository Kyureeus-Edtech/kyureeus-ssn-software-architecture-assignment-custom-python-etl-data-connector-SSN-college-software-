#!/usr/bin/env python3
"""
etl_blocklist_no_apikey.py

ETL connector for blocklist.de WITHOUT API keys.
Supports three public query modes (no registration required):

 - ip  : HTTP API IP lookup
         e.g. http://api.blocklist.de/api.php?ip=1.2.3.4&format=json

 - list: Export lists (plain text) hosted under lists.blocklist.de
         e.g. https://lists.blocklist.de/lists/ssh.txt  (service names: ssh, mail, apache, bots, ...)

 - rbl : DNS/RBL check using bl.blocklist.de (reverse-ip.bl.blocklist.de)
         e.g. query TXT/A records for 2.0.0.127.bl.blocklist.de

Usage:
  python etl_blocklist_no_apikey.py --mode ip --items 1.2.3.4 8.8.8.8
  python etl_blocklist_no_apikey.py --mode list --items ssh mail apache
  python etl_blocklist_no_apikey.py --mode rbl --items 1.2.3.4
  python etl_blocklist_no_apikey.py --run-all
  python etl_blocklist_no_apikey.py --mode ip --items 1.2.3.4 --dry-run
"""

import os
import sys
import argparse
import logging
import time
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from dotenv import load_dotenv
from pymongo import MongoClient, errors as pymongo_errors
import dns.resolver  # from dnspython

# load .env (if present)
load_dotenv()

# config (can be overridden in .env)
API_BASE = os.getenv("API_BASE", "http://api.blocklist.de/api.php")
LIST_BASE = os.getenv("LIST_BASE", "https://lists.blocklist.de/lists")
RBL_ZONE = os.getenv("RBL_ZONE", "bl.blocklist.de")  # reverse-ip.<zone>
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "etl_assignment_db")
CONNECTOR_PREFIX = os.getenv("CONNECTOR_PREFIX", "blocklist")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "0.5"))

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("etl_blocklist_no_apikey")

SUPPORTED_MODES = ["ip", "list", "rbl"]

# --- helper: HTTP session with retries ---
def create_session(retries: int = MAX_RETRIES, backoff: float = RETRY_BACKOFF) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=backoff,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# --- EXTRACT ---
def extract_ip(ip: str, start: Optional[int] = None, end: Optional[int] = None) -> Any:
    """Call http://api.blocklist.de/api.php?ip=...&format=json"""
    params = {"ip": ip, "format": "json"}
    if start:
        params["start"] = int(start)
    if end:
        params["end"] = int(end)
    url = API_BASE
    session = create_session()
    logger.info("HTTP IP lookup: %s %s", url, params)
    try:
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        logger.error("Network error: %s", e)
        raise
    if resp.status_code != 200:
        logger.error("Non-200: %s %s", resp.status_code, resp.text[:200])
        raise RuntimeError(f"API returned {resp.status_code}")
    try:
        return resp.json()
    except ValueError:
        # fallback: return raw text
        return {"_raw_text": resp.text}

def extract_list(service: str) -> Any:
    """Download the plain-text export list for a service from lists.blocklist.de"""
    url = f"{LIST_BASE}/{service}.txt"
    session = create_session()
    logger.info("Downloading list: %s", url)
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        logger.error("Network error: %s", e)
        raise
    if resp.status_code != 200:
        logger.error("Non-200 when fetching list: %s %s", resp.status_code, resp.text[:200])
        raise RuntimeError(f"List fetch failed {resp.status_code}")
    text = resp.text.strip()
    # lists are newline-separated IPs; ignore comments/empty lines
    ips = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    logger.info("Fetched %d IPs from %s", len(ips), service)
    return {"service": service, "count": len(ips), "ips": ips, "_raw_text_head": text[:1024]}

def ip_to_rbl_name(ip: str) -> str:
    """Convert dotted IP to reversed-dot rbl query name, e.g. 1.2.3.4 -> 4.3.2.1.bl.blocklist.de"""
    parts = ip.strip().split(".")
    if len(parts) != 4:
        raise ValueError("Only IPv4 supported for RBL in this script")
    rev = ".".join(reversed(parts))
    return f"{rev}.{RBL_ZONE}"

def extract_rbl(ip: str) -> Any:
    """Query DNS TXT and A records for reversed-ip.<RBL_ZONE> to detect listing"""
    qname = ip_to_rbl_name(ip)
    logger.info("RBL lookup: %s", qname)
    res = {"qname": qname, "listed": False, "answers": [], "_queried_at": datetime.now(timezone.utc).isoformat()}
    resolver = dns.resolver.Resolver()
    resolver.lifetime = REQUEST_TIMEOUT
    try:
        # TXT records (may include description and unix timestamp)
        try:
            txt_answers = resolver.resolve(qname, "TXT")
            for r in txt_answers:
                txt = b"".join(r.strings).decode("utf-8", errors="replace") if hasattr(r, "strings") else str(r)
                res["answers"].append({"type": "TXT", "value": txt})
                res["listed"] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # no TXT
            pass
        # A record may indicate listing with an IP like 127.0.0.<code>
        try:
            a_answers = resolver.resolve(qname, "A")
            for a in a_answers:
                res["answers"].append({"type": "A", "value": a.to_text()})
                res["listed"] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
    except Exception as e:
        logger.warning("RBL DNS query failed: %s", e)
        res["error"] = str(e)
    logger.info("RBL result: listed=%s answers=%d", res.get("listed"), len(res.get("answers", [])))
    return res

# --- TRANSFORM ---
def transform_generic(payload: Any, mode: str, item: str) -> List[Dict[str, Any]]:
    """Normalize payload into a list of documents with ingest metadata."""
    ingested_at = datetime.now(timezone.utc).isoformat()
    docs: List[Dict[str, Any]] = []
    if mode == "ip":
        # payload can be dict or list
        if isinstance(payload, list):
            for rec in payload:
                doc = dict(rec) if isinstance(rec, dict) else {"value": rec}
                doc["_ingested_at"] = ingested_at
                doc["_source_mode"] = mode
                doc["_source_item"] = item
                docs.append(doc)
        elif isinstance(payload, dict):
            doc = dict(payload)
            doc["_ingested_at"] = ingested_at
            doc["_source_mode"] = mode
            doc["_source_item"] = item
            docs.append(doc)
        else:
            docs.append({"_value": payload, "_ingested_at": ingested_at, "_source_mode": mode, "_source_item": item})
    elif mode == "list":
        # we return one doc with aggregated list and also per-ip docs (optional)
        if isinstance(payload, dict) and "ips" in payload:
            # one summary doc
            summary = {"_ingested_at": ingested_at, "_source_mode": mode, "_source_item": payload.get("service"), "service_count": payload.get("count"), "_raw_head": payload.get("_raw_text_head")}
            docs.append(summary)
            # per-ip docs
            for ip in payload.get("ips", [])[:5000]:  # safety cap
                docs.append({"ip": ip, "_ingested_at": ingested_at, "_source_mode": mode, "_source_item": payload.get("service")})
        else:
            docs.append({"_value": payload, "_ingested_at": ingested_at, "_source_mode": mode, "_source_item": item})
    elif mode == "rbl":
        if isinstance(payload, dict):
            doc = dict(payload)
            doc["_ingested_at"] = ingested_at
            doc["_source_mode"] = mode
            doc["_source_item"] = item
            docs.append(doc)
        else:
            docs.append({"_value": payload, "_ingested_at": ingested_at, "_source_mode": mode, "_source_item": item})
    else:
        docs.append({"_value": payload, "_ingested_at": ingested_at, "_source_mode": mode, "_source_item": item})
    logger.info("Transformed into %d documents (mode=%s item=%s)", len(docs), mode, item)
    return docs

# --- LOAD ---
def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except pymongo_errors.PyMongoError as e:
        logger.error("MongoDB connection failed: %s", e)
        raise

def load_documents(docs: List[Dict[str, Any]], mode: str):
    if not docs:
        logger.info("No docs to load for mode=%s", mode)
        return
    client = get_mongo_client()
    db = client[MONGO_DB]
    coll_name = f"{CONNECTOR_PREFIX}_{mode}_raw"
    coll = db[coll_name]
    try:
        coll.create_index([("_source_mode", 1), ("_source_item", 1)], background=True)
    except Exception:
        pass
    inserted = 0
    upserted = 0
    for doc in docs:
        # upsert by source metadata + ip or qname when possible
        filt = {"_source_mode": mode, "_source_item": doc.get("_source_item")}
        if mode == "ip" and "ip" in doc:
            filt["ip"] = doc["ip"]
        if mode == "rbl" and "qname" in doc:
            filt["qname"] = doc["qname"]
        try:
            res = coll.replace_one(filt, doc, upsert=True)
            if res.matched_count:
                upserted += 1
            else:
                inserted += 1
        except Exception:
            try:
                coll.insert_one(doc)
                inserted += 1
            except Exception as e:
                logger.error("Insert failed: %s", e)
    logger.info("Loaded into %s: inserted=%d upserted=%d", coll_name, inserted, upserted)

# --- Runner wrappers ---
def run_mode(mode: str, items: List[str], start: Optional[int], end: Optional[int], dry_run: bool):
    for item in items:
        try:
            if mode == "ip":
                payload = extract_ip(item, start, end)
            elif mode == "list":
                payload = extract_list(item)
            elif mode == "rbl":
                payload = extract_rbl(item)
            else:
                logger.error("Unsupported mode: %s", mode)
                continue
        except Exception as e:
            logger.error("Extract failed for %s=%s : %s", mode, item, e)
            continue
        docs = transform_generic(payload, mode, item)
        if dry_run:
            logger.info("Dry-run: would load %d docs for %s=%s", len(docs), mode, item)
        else:
            try:
                load_documents(docs, mode)
            except Exception as e:
                logger.error("Load failed: %s", e)

# --- CLI ---
def parse_args():
    parser = argparse.ArgumentParser(description="ETL connector for blocklist.de (no apikey required)")
    parser.add_argument("--mode", choices=SUPPORTED_MODES, help="Mode to run (ip/list/rbl)")
    parser.add_argument("--items", nargs="+", help="Items (IPs, service names, or IPs for RBL)")
    parser.add_argument("--run-all", action="store_true", help="Run ip/list/rbl using defaults or env vars")
    parser.add_argument("--start", type=int, help="Unix start timestamp (optional, only used for ip mode)")
    parser.add_argument("--end", type=int, help="Unix end timestamp (optional, only used for ip mode)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to MongoDB")
    return parser.parse_args()

def main():
    args = parse_args()
    # defaults
    env_ips = [s.strip() for s in os.getenv("BLOCKLIST_IPS","8.8.8.8,1.1.1.1").split(",") if s.strip()]
    env_lists = [s.strip() for s in os.getenv("BLOCKLIST_SERVICES","ssh,mail,apache").split(",") if s.strip()]
    env_rbl_ips = [s.strip() for s in os.getenv("BLOCKLIST_RBL_IPS","8.8.8.8").split(",") if s.strip()]

    # default time window for ip mode = last 24 hours if not provided
    if not args.start and not args.end:
        now = int(time.time())
        start_default = now - 24*3600
        end_default = now
    else:
        start_default = args.start
        end_default = args.end

    if args.run_all:
        logger.info("Running all modes with defaults")
        run_mode("ip", args.items if args.mode == "ip" and args.items else env_ips, start_default, end_default, args.dry_run)
        run_mode("list", env_lists, None, None, args.dry_run)
        run_mode("rbl", env_rbl_ips, None, None, args.dry_run)
        return

    if args.mode:
        items = args.items or []
        if not items:
            if args.mode == "ip":
                items = env_ips
            elif args.mode == "list":
                items = env_lists
            elif args.mode == "rbl":
                items = env_rbl_ips
        if not items:
            logger.error("No items provided for mode=%s (use --items or set env variables)", args.mode)
            sys.exit(2)
        run_mode(args.mode, items, start_default, end_default, args.dry_run)
    else:
        logger.error("No mode specified. Use --mode or --run-all.")
        sys.exit(2)

if __name__ == "__main__":
    main()