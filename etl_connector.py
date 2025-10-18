#!/usr/bin/env python3
"""
etl_connector.py
RDAP ETL connector (multi-endpoint)

Usage examples:
  python etl_connector.py --resource domain --query example.com
  python etl_connector.py --resource ip --query 8.8.8.8
  python etl_connector.py --resource asn --query 15169
  python etl_connector.py --resource nameserver --query a.iana-servers.net
  python etl_connector.py --resource entity --query EXAMPLE-REG

This script:
 - loads config from .env
 - calls rdap (default rdap.org redirector) or registry endpoint
 - does basic retries & backoff for 429/5xx
 - transforms and upserts into MongoDB collection `rdap_<resource>_raw`
"""

import os
import sys
import time
import json
import argparse
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# Load .env (make sure .env is in .gitignore)
load_dotenv()

# Config, can be set in .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "rdap_db")
RDAP_BASE = os.getenv("RDAP_BASE", "https://rdap.org")  # rdap.org acts as a redirector/bootstrap

# HTTP client settings
USER_AGENT = os.getenv("USER_AGENT", "rdap-etl/1.0 (+https://example.edu)")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", "3"))
BACKOFF_FACTOR = float(os.getenv("HTTP_BACKOFF_FACTOR", "1.0"))


def build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        backoff_factor=BACKOFF_FACTOR,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/rdap+json, application/json"})
    return s


def resource_path(resource: str, query: str) -> str:
    """
    Map resource type to RDAP path. RDAP paths usually:
      /domain/{fqdn}
      /ip/{ip_address}
      /autnum/{asn}  OR /autnum/{ASNNUM} sometimes /asn endpoint may be used
      /nameserver/{ns}
      /entity/{handle}

    Use standard names; user can override RDAP_BASE if desired.
    """
    resource = resource.lower()
    if resource in ("domain", "domains"):
        return f"/domain/{query}"
    if resource in ("ip", "address", "ipaddress"):
        return f"/ip/{query}"
    if resource in ("asn", "as", "autnum", "autonomous-system", "autnum"):
        # RDAP uses autnum in RFCs but registries may support /autnum or /autnum/{number}
        # Many servers also accept /autnum/{asn} or /asn/{asn}. We'll try autnum.
        cleaned = str(query).lstrip("AS").lstrip("as")
        return f"/autnum/{cleaned}"
    if resource in ("nameserver", "nameservers", "ns"):
        return f"/nameserver/{query}"
    if resource in ("entity", "entities"):
        return f"/entity/{query}"
    # fallback: use resource as path segment
    return f"/{resource}/{query}"


def stable_doc_id(resource: str, query: str) -> str:
    """
    Create a stable document id (sha256) so repeated ingestion for same query
    will upsert the same document if desired.
    """
    key = f"{resource}:{query}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


def transform_for_mongo(raw_json: Any, resource: str, query: str, source_url: str) -> Dict[str, Any]:
    """
    Attach metadata and ensure the top-level is a dict for MongoDB insertion.
    """
    print("[TRANSFORM] Transforming data for MongoDB storage...")
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": stable_doc_id(resource, query),
        "resource": resource,
        "query": query,
        "source_url": source_url,
        "ingestion_timestamp": now,
        "raw": raw_json,
    }
    print("[TRANSFORM] Transformation complete.")
    return doc


def safe_get_json(session: requests.Session, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    GET with error handling and exponential backoff for 429 and 5xx.
    Returns parsed JSON or None on fatal error.
    """
    attempt = 0
    max_attempts = max(1, MAX_RETRIES + 1)
    while attempt < max_attempts:
        attempt += 1
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print(f"[ERROR] Network/Request error on attempt {attempt}: {e}", file=sys.stderr)
            # backoff then retry
            sleep_time = BACKOFF_FACTOR * (2 ** (attempt - 1))
            time.sleep(sleep_time)
            continue

        # Rate limiting or server errors
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else BACKOFF_FACTOR * (2 ** (attempt - 1))
            print(f"[WARN] 429 Rate limited. Sleeping {wait}s (attempt {attempt})", file=sys.stderr)
            time.sleep(wait)
            continue
        if 500 <= resp.status_code < 600:
            sleep_time = BACKOFF_FACTOR * (2 ** (attempt - 1))
            print(f"[WARN] Server error {resp.status_code}. Sleeping {sleep_time}s (attempt {attempt})", file=sys.stderr)
            time.sleep(sleep_time)
            continue

        if resp.status_code == 404:
            # Resource not found — return a small informative object rather than None
            print(f"[INFO] 404 Not found for URL {url}", file=sys.stderr)
            return {"rdap_not_found": True, "status_code": 404, "url": url}

        if resp.status_code != 200:
            # other client errors
            print(f"[ERROR] Unexpected status code {resp.status_code} for {url}: {resp.text[:200]}", file=sys.stderr)
            return None

        # success
        try:
            return resp.json()
        except ValueError:
            print(f"[ERROR] Response not JSON for {url}", file=sys.stderr)
            return None

    print(f"[ERROR] Exhausted retries for {url}", file=sys.stderr)
    return None


def upsert_to_mongo(mongo_uri: str, db_name: str, collection_name: str, doc: Dict[str, Any]) -> bool:
    """
    Upsert document to MongoDB (replace on _id).
    """
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        coll = db[collection_name]
        # replace or insert
        result = coll.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        if result.acknowledged:
            print(f"[OK] Upserted doc _id={doc['_id']} into {db_name}.{collection_name}")
            return True
        else:
            print(f"[WARN] Mongo not acknowledged for _id={doc['_id']}", file=sys.stderr)
            return False
    except errors.PyMongoError as e:
        print(f"[ERROR] MongoDB error: {e}", file=sys.stderr)
        return False


def run_etl(resource: str, query: str, rdap_base: str = RDAP_BASE) -> int:
    """
    Perform one ETL run for the given resource & query.
    Returns 0 on success, non-zero on error.
    Displays clear ETL phase statuses and timings.
    """
    print("=" * 70)
    print(f"[ETL START] Resource: {resource.upper()} | Query: {query}")
    print(f"[INFO] Using RDAP base: {rdap_base}")
    print("=" * 70)

    # ----------------- EXTRACT PHASE -----------------
    extract_start = time.time()
    print("[EXTRACT] Initiating data fetch from RDAP endpoint...")
    session = build_session()
    path = resource_path(resource, query)
    url = rdap_base.rstrip("/") + path
    print(f"[EXTRACT] Fetching URL: {url}")

    raw = safe_get_json(session, url)
    extract_time = time.time() - extract_start

    if raw is None:
        print(f"[EXTRACT] Failed to fetch or parse JSON data. (Time: {extract_time:.2f}s)", file=sys.stderr)
        return 2

    print(f"[EXTRACT] Data successfully fetched in {extract_time:.2f}s.")

    # ----------------- TRANSFORM PHASE -----------------
    transform_start = time.time()
    print("[TRANSFORM] Transforming data for MongoDB storage...")
    doc = transform_for_mongo(raw, resource, query, url)
    transform_time = time.time() - transform_start
    print(f"[TRANSFORM] Transformation complete in {transform_time:.2f}s.")

    # ----------------- LOAD PHASE -----------------
    load_start = time.time()
    coll = f"rdap_{resource}_raw"
    print(f"[LOAD] Loading data into MongoDB collection: {MONGO_DB}.{coll}")
    ok = upsert_to_mongo(MONGO_URI, MONGO_DB, coll, doc)
    load_time = time.time() - load_start

    if ok:
        print(f"[LOAD] Data successfully inserted/upserted in {load_time:.2f}s.")
        total_time = extract_time + transform_time + load_time
        print(f"[ETL COMPLETE] Resource '{resource}' for query '{query}' processed successfully "
              f"in {total_time:.2f}s.\n")
        return 0
    else:
        print(f"[LOAD] MongoDB insertion/upsert failed. (Time: {load_time:.2f}s)", file=sys.stderr)
        return 3


def parse_args():
    parser = argparse.ArgumentParser(description="RDAP ETL connector")
    parser.add_argument("--resource", "-r", required=True, help="Resource type: domain/ip/asn/nameserver/entity")
    parser.add_argument("--query", "-q", required=True, help="Resource query (e.g. example.com, 8.8.8.8, 15169)")
    parser.add_argument("--rdap-base", default=RDAP_BASE, help=f"RDAP base URL (default: {RDAP_BASE})")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rc = run_etl(args.resource, args.query, args.rdap_base)
    sys.exit(rc)
