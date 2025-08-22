#!/usr/bin/env python3
"""
CISA KEV - ETL connector (Extract → Transform → Load)
- Extracts JSON feed from CISA
- Transforms to a compact schema (plus keeps raw)
- Loads/upserts into MongoDB

Run: python etl_connector.py
"""
import os
import sys
import time
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

FEED_URL = os.getenv(
    "CISA_KEV_URL",
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
)

# ---------- Helpers ----------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_http_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": os.getenv("HTTP_USER_AGENT", "SSN-KEV-ETL/1.0 (+student)"),
        # Optionally include If-None-Match/If-Modified-Since via .env
        **({"If-None-Match": os.getenv("HTTP_IF_NONE_MATCH")} if os.getenv("HTTP_IF_NONE_MATCH") else {}),
        **({"If-Modified-Since": os.getenv("HTTP_IF_MODIFIED_SINCE")} if os.getenv("HTTP_IF_MODIFIED_SINCE") else {}),
    })
    return session


# ---------- Extract ----------

def extract(session: requests.Session) -> Tuple[Dict[str, Any], Dict[str, str]]:
    resp = session.get(FEED_URL, timeout=(5, 30))
    meta = {
        "status_code": str(resp.status_code),
        "etag": resp.headers.get("ETag", ""),
        "last_modified": resp.headers.get("Last-Modified", ""),
        "fetched_at": utc_now_iso(),
    }
    if resp.status_code == 304:
        # Not modified – upstream supports conditional GET
        return {"vulnerabilities": []}, meta
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict) or "vulnerabilities" not in data:
        raise RuntimeError("Unexpected JSON shape – 'vulnerabilities' key missing")

    vulns = data.get("vulnerabilities") or []
    if not isinstance(vulns, list):
        raise RuntimeError("'vulnerabilities' is not a list")

    return {"vulnerabilities": vulns}, meta


# ---------- Transform ----------

# Keep flexible: only map if fields exist; do not break on schema drift
FIELD_MAP = {
    "cveID": "cve_id",
    "vendorProject": "vendor",
    "product": "product",
    "vulnerabilityName": "title",
    "shortDescription": "description",
    "dateAdded": "date_added",
    "dueDate": "due_date",
    "requiredAction": "required_action",
    "knownRansomwareCampaignUse": "ransomware_use",
    "notes": "notes",
}


def transform(vulns: List[Dict[str, Any]], source_meta: Dict[str, str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ingested_at = utc_now_iso()
    raw_docs: List[Dict[str, Any]] = []
    shaped_docs: List[Dict[str, Any]] = []

    for v in vulns:
        if not isinstance(v, dict):
            continue
        # Raw document with audit metadata
        raw = {
            **v,
            "_source": {
                "feed": "cisa_kev",
                "url": FEED_URL,
                "etag": source_meta.get("etag", ""),
                "last_modified": source_meta.get("last_modified", ""),
                "fetched_at": source_meta.get("fetched_at", ""),
            },
            "ingested_at": ingested_at,
        }
        raw_docs.append(raw)

        # Shaped document (query‑friendly)
        shaped: Dict[str, Any] = {
            "_id": v.get("cveID") or hashlib.sha1(json.dumps(v, sort_keys=True).encode()).hexdigest(),
            "cve_id": v.get("cveID"),
            "title": v.get("vulnerabilityName"),
            "vendor": v.get("vendorProject"),
            "product": v.get("product"),
            "description": v.get("shortDescription"),
            "date_added": v.get("dateAdded"),
            "due_date": v.get("dueDate"),
            "required_action": v.get("requiredAction"),
            "ransomware_use": v.get("knownRansomwareCampaignUse"),
            "notes": v.get("notes"),
            "_audit": {
                "ingested_at": ingested_at,
                "source_etag": source_meta.get("etag", ""),
                "source_last_modified": source_meta.get("last_modified", ""),
            },
        }
        shaped_docs.append(shaped)

    return raw_docs, shaped_docs


# ---------- Load ----------

def get_mongo() -> MongoClient:
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI not set. Put it in .env")
    return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)


def load_to_mongo(raw_docs: List[Dict[str, Any]], shaped_docs: List[Dict[str, Any]]) -> None:
    client = get_mongo()
    try:
        db_name = os.getenv("MONGODB_DB", "ssn_assignment")
        col_raw_name = os.getenv("MONGODB_COLLECTION_RAW", "cisa_kev_raw")
        col_shaped_name = os.getenv("MONGODB_COLLECTION_SHAPED", "cisa_kev")

        db = client[db_name]
        col_raw = db[col_raw_name]
        col_shaped = db[col_shaped_name]

        # Insert raw as-is (unordered for speed)
        if raw_docs:
            col_raw.insert_many(raw_docs, ordered=False)

        # Upsert shaped by _id (cveID)
        if shaped_docs:
            ops = []
            for d in shaped_docs:
                ops.append(
                    UpdateOne({"_id": d["_id"]}, {"$set": d}, upsert=True)
                )
            if ops:
                col_shaped.bulk_write(ops, ordered=False)

        # Basic index suggestions (idempotent)
        col_shaped.create_index("cve_id")
        col_shaped.create_index("vendor")
        col_shaped.create_index("product")
        col_shaped.create_index("date_added")

    finally:
        client.close()


# ---------- Main ----------

def main() -> int:
    load_dotenv()
    session = build_http_session()

    try:
        payload, meta = extract(session)
        vulns = payload.get("vulnerabilities", [])
        if not vulns:
            print("No new vulnerabilities (304 or empty list). Nothing to do.")
            return 0
        raw_docs, shaped_docs = transform(vulns, meta)
        load_to_mongo(raw_docs, shaped_docs)
        print(f"Ingested {len(vulns)} vulnerabilities → MongoDB ✔")
        return 0

    except (requests.RequestException, RuntimeError, PyMongoError) as e:
        print(f"ETL failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())