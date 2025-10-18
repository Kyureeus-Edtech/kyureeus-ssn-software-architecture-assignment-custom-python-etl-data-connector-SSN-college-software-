#!/usr/bin/env python3
"""
circl_pdns_etl.py
ETL script to query CIRCL Passive DNS via PyPDNS, transform records, and load into MongoDB.

Source: Hardcoded list of queries (domains/IPs) inside the script.
"""

import os
import time
import sys
from datetime import datetime
from itertools import islice

# Safe imports with user-friendly errors
try:
    from dotenv import load_dotenv
except Exception:
    print("Missing dependency: python-dotenv. Install with: pip install python-dotenv")
    sys.exit(1)

try:
    import pypdns
except Exception:
    print("Missing dependency: pypdns. Install with: pip install pypdns")
    sys.exit(1)

try:
    from pymongo import MongoClient, errors as pymongo_errors
except Exception:
    print("Missing dependency: pymongo. Install with: pip install pymongo")
    sys.exit(1)

try:
    from dateutil import parser as date_parser
except Exception:
    print("Missing dependency: python-dateutil. Install with: pip install python-dateutil")
    sys.exit(1)


# ----------------------------
# Configuration (env)
# ----------------------------
load_dotenv()  # loads variables from .env into environment

CIRCL_USER = os.getenv("CIRCL_PDNS_USER")
CIRCL_PASS = os.getenv("CIRCL_PDNS_PASS")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "etl_database")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.0"))  # seconds between paginated calls if needed
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "1.5"))  # multiplier for backoff

if not CIRCL_USER or not CIRCL_PASS:
    print("[ERROR] CIRCL credentials not found in environment. Create a .env file with CIRCL_PDNS_USER and CIRCL_PDNS_PASS.")
    sys.exit(1)

# ----------------------------
# MongoDB Setup
# ----------------------------
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["circl_pdns_raw"]

# Create a simple index to speed up lookups and prevent large duplicates
try:
    collection.create_index([("rrname", 1), ("rrtype", 1), ("rdata", 1)])
except Exception:
    pass


# ----------------------------
# Utilities
# ----------------------------
def chunked(iterator, size):
    """Yield successive chunks from iterator of length `size`."""
    it = iter(iterator)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def _parse_time_safe(t):
    """Parse time strings (ISO) or epoch-like values into datetime, else None."""
    if t is None:
        return None
    try:
        if isinstance(t, (int, float)):
            return datetime.utcfromtimestamp(int(t))
        if isinstance(t, str):
            # dateutil can parse most ISO formats
            return date_parser.parse(t)
    except Exception:
        return None
    return None


def transform_record(pypdns_record):
    """
    Transform a PyPDNS record object into a dict suitable for MongoDB.
    PyPDNS objects typically expose `.record` (a dict) or are dicts themselves.
    """
    rec = getattr(pypdns_record, "record", None) or pypdns_record
    # defensive: if rec is not dict-like, turn to dict
    if not isinstance(rec, dict):
        try:
            rec = dict(rec)
        except Exception:
            rec = {"raw": str(rec)}

    transformed = {
        "rrname": rec.get("rrname"),
        "rrtype": rec.get("rrtype"),
        "rdata": rec.get("rdata"),
        "time_first": _parse_time_safe(rec.get("time_first")),
        "time_last": _parse_time_safe(rec.get("time_last")),
        "count": rec.get("count"),
        "origin": rec.get("origin"),
        "source": rec.get("source") if rec.get("source") else rec.get("origin"),
        "_raw": rec,
        "_etl_ingested_at": datetime.utcnow(),
        "_etl_source": "circl_pdns"
    }
    return transformed


# ----------------------------
# Extract: PyPDNS with retries/backoff
# ----------------------------
def extract_pdns(q, rrtype=None, limit=None):
    """
    Generator: yields PyPDNS records for query q.
    - q: domain, hostname, or IP
    - rrtype: optional RR type (A, CNAME, MX, etc.)
    - limit: optional maximum number of records to yield
    """
    # instantiate client once
    client = pypdns.PyPDNS(basic_auth=(CIRCL_USER, CIRCL_PASS))

    kwargs = {}
    if rrtype:
        kwargs["filter_rrtype"] = rrtype

    count = 0
    retries = 0

    while True:
        try:
            for rec in client.iter_query(q=q, **kwargs):
                yield rec
                count += 1
                if limit and count >= limit:
                    return
                if REQUEST_DELAY:
                    time.sleep(REQUEST_DELAY)
            # finished normally
            return
        except Exception as exc:
            retries += 1
            if retries > MAX_RETRIES:
                print(f"[ERROR] extract_pdns: maximum retries exceeded for q={q}. Last error: {exc}")
                return
            sleep_for = (RETRY_BACKOFF ** retries)
            print(f"[WARN] extract_pdns: error on attempt {retries} for q={q}: {exc}. Backing off {sleep_for:.1f}s")
            time.sleep(sleep_for)
            # then retry


# ----------------------------
# Load: batch insert with basic handling
# ----------------------------
def load_batch_to_mongo(docs):
    """Insert a batch of documents into MongoDB with basic error handling."""
    if not docs:
        return 0
    try:
        res = collection.insert_many(docs, ordered=False)
        n = len(res.inserted_ids)
        print(f"[INFO] Inserted {n} documents.")
        return n
    except pymongo_errors.BulkWriteError as bwe:
        # partial insert; get number inserted if available
        details = bwe.details or {}
        n = details.get("nInserted") or details.get("nInserted", 0)
        print(f"[WARN] BulkWriteError: inserted {n}, details: {details}")
        return n if n else 0
    except Exception as e:
        print(f"[ERROR] MongoDB insert failed: {e}")
        return 0


# ----------------------------
# Main ETL runner
# ----------------------------
def run_etl(query, rrtype=None, limit=None, purge_old=False):
    """
    Run ETL for a single query and return a dict with counts.
    """
    print(f"[INFO] ETL start: query={query}, rrtype={rrtype}, limit={limit}")

    if purge_old:
        try:
            res = collection.delete_many({"_raw.rrname": query})
            print(f"[INFO] Purged {res.deleted_count} old records for rrname={query}")
        except Exception as e:
            print(f"[WARN] purge_old failed: {e}")

    gen = extract_pdns(q=query, rrtype=rrtype, limit=limit)
    batch = []
    processed = 0
    inserted_total = 0

    for rec in gen:
        doc = transform_record(rec)
        doc["_query"] = query
        doc["_query_rrtype"] = rrtype
        batch.append(doc)
        processed += 1

        if len(batch) >= BATCH_SIZE:
            inserted = load_batch_to_mongo(batch)
            inserted_total += inserted
            batch = []

    # flush remaining
    if batch:
        inserted = load_batch_to_mongo(batch)
        inserted_total += inserted

    print(f"[INFO] ETL complete for {query}. Processed: {processed}, Inserted: {inserted_total}")
    return {"processed": processed, "inserted": inserted_total}


# ----------------------------
# Hardcoded queries (Source: 2)
# Edit this list to include domains/IPs you want to fetch.
# ----------------------------
if __name__ == "__main__":
    hardcoded_queries = [
        {"q": "example.com", "rrtype": "A", "limit": 500},
        {"q": "ietf.org", "rrtype": None, "limit": 200},
        # add more: {"q": "another-domain.tld", "rrtype": "CNAME", "limit": 100}
    ]

    summary = []
    for job in hardcoded_queries:
        res = run_etl(query=job["q"], rrtype=job.get("rrtype"), limit=job.get("limit"), purge_old=False)
        summary.append({"query": job["q"], **res})

    print("\nSUMMARY:")
    for s in summary:
        print(s)
