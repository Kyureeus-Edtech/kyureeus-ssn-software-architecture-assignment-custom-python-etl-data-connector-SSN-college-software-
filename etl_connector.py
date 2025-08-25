#!/usr/bin/env python3
"""
DShield Top Attackers ETL Connector

- Extracts the ASCII/TXT feed from DShield (ipsascii.html)
- Transforms into MongoDB-friendly documents
- Loads into a MongoDB collection with ingestion timestamps

Run:
  python etl_connector.py --dry-run        # test parsing only (no DB writes)
  python etl_connector.py                  # normal run (writes to MongoDB)
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import os
import re
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

try:
    from pymongo import MongoClient, UpdateOne
    from pymongo.errors import PyMongoError
except Exception:
    MongoClient = None  # type: ignore


# ---------------------------
# Utilities
# ---------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _with_timeout(func, timeout_s: int):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout_s
        return func(method, url, **kwargs)
    return wrapped

def get_session(timeout_s: int = 20) -> requests.Session:
    sess = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.7,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset({"HEAD", "GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    sess.headers.update({"User-Agent": "ETL-DShield-Connector/1.0 (+github.com/your-org)"})
    # ensure all requests have a timeout
    sess.request = _with_timeout(sess.request, timeout_s)  # type: ignore[assignment]
    return sess

def stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


# ---------------------------
# Extraction
# ---------------------------

def fetch_dshield_text(url: str, session: requests.Session) -> Tuple[str, Dict[str, str]]:
    """Fetch source text and capture helpful HTTP metadata for auditing."""
    meta: Dict[str, str] = {}

    try:
        h = session.head(url, allow_redirects=True)
        if h.ok:
            if "ETag" in h.headers:
                meta["etag"] = h.headers["ETag"]
            if "Last-Modified" in h.headers:
                meta["last-modified"] = h.headers["Last-Modified"]
            if "Content-Length" in h.headers:
                meta["content_length"] = h.headers["Content-Length"]
    except requests.RequestException:
        pass  # continue; not fatal

    resp = session.get(url)
    if not resp.ok:
        raise RuntimeError(f"Failed to fetch feed: HTTP {resp.status_code}")
    meta["content_type"] = resp.headers.get("Content-Type", "")
    return resp.text, meta


# ---------------------------
# Transformation
# ---------------------------

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def normalize_field(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"(^_+|_+$)", "", s)
    return s or "field"

def parse_lines_ascii_table(text: str) -> List[Dict]:
    """
    Parse the DShield ASCII/TXT as a whitespace-delimited table.

    - Skips lines starting with '#'
    - Uses header row if present (alphabetic tokens)
    - Otherwise assigns generic columns: col1..colN
    - Extracts first IPv4 occurrence as 'ip' (validated)
    - Keeps '_source_row' for lineage/audit
    """
    docs: List[Dict] = []
    lines = text.splitlines()

    raw_rows = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not raw_rows:
        return docs

    header_tokens = None
    first_tokens = re.split(r"\s+|\t+", raw_rows[0])
    if any(re.search(r"[A-Za-z]", tok) for tok in first_tokens):
        header_tokens = [normalize_field(tok) for tok in first_tokens]
        data_rows = raw_rows[1:]
    else:
        data_rows = raw_rows

    for row in data_rows:
        tokens = re.split(r"\s+|\t+", row.strip())
        if not tokens:
            continue

        if header_tokens and len(tokens) == len(header_tokens):
            record = {header_tokens[i]: tokens[i] for i in range(len(tokens))}
        else:
            record = {f"col{i+1}": tokens[i] for i in range(len(tokens))}

        # try to locate an IP
        ip = None
        for k, v in list(record.items()):
            if k.lower() in {"ip", "source", "source_ip", "attacker", "src"} and IPV4_RE.fullmatch(str(v) or ""):
                ip = v
                break
        if not ip:
            m = IPV4_RE.search(row)
            if m:
                ip = m.group(0)

        if ip:
            try:
                ipaddress.IPv4Address(ip)
                record["ip"] = ip
            except Exception:
                pass

        record["_source_row"] = row
        docs.append(record)

    return docs

def transform_for_mongo(docs: List[Dict], source_url: str, meta: Dict[str, str]) -> List[Dict]:
    ts = utc_now_iso()
    out_docs: List[Dict] = []
    for d in docs:
        out = dict(d)
        out["_ingested_at"] = ts
        out["_source"] = "dshield_top_attackers"
        out["_source_url"] = source_url
        if meta:
            out["_http_meta"] = meta
        raw = d.get("_source_row", "")
        out["_row_hash"] = stable_hash(f"{source_url}\n{raw}")
        out_docs.append(out)
    return out_docs


# ---------------------------
# Load
# ---------------------------

def load_to_mongo(
    docs: List[Dict],
    mongo_uri: str,
    db_name: str,
    collection_name: str,
    create_unique_index: bool = True,
) -> Tuple[int, int]:
    """
    Upserts by _row_hash to be idempotent.
    Returns (upserted_count, matched_existing_count).
    """
    if MongoClient is None:
        raise RuntimeError("pymongo not installed. Check requirements.txt and your environment.")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection_name]

    if create_unique_index:
        col.create_index("_row_hash", unique=True, background=True)

    if not docs:
        return (0, 0)

    ops = [
        UpdateOne({"_row_hash": d["_row_hash"]}, {"$setOnInsert": d}, upsert=True)
        for d in docs
    ]

    try:
        res = col.bulk_write(ops, ordered=False)
    except PyMongoError as e:
        raise RuntimeError(f"Mongo bulk_write failed: {e}")

    upserts = getattr(res, "upserted_count", 0) or 0
    matched_existing = len(ops) - upserts
    return (upserts, matched_existing)


# ---------------------------
# CLI
# ---------------------------

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="ETL: DShield Top Attackers (TXT feed)")
    parser.add_argument("--dry-run", action="store_true", help="Parse/transform only; do not write to MongoDB")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of rows ingested (0 = no limit)")
    args = parser.parse_args()

    source_url = os.getenv("DSHIELD_URL", "https://www.dshield.org/ipsascii.html").strip()
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    db_name = os.getenv("MONGODB_DB", "dshield_etl").strip()
    collection = os.getenv("MONGODB_COLLECTION", "dshield_top_attackers_raw").strip()

    if not args.dry_run and not mongo_uri:
        print("ERROR: MONGODB_URI is required (or run with --dry-run). Set it in .env.", file=sys.stderr)
        sys.exit(2)

    session = get_session()

    # Extract
    try:
        text, meta = fetch_dshield_text(source_url, session)
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Extraction returned empty payload. Aborting.", file=sys.stderr)
        sys.exit(1)

    # Transform
    parsed = parse_lines_ascii_table(text)
    if args.limit and args.limit > 0:
        parsed = parsed[: args.limit]
    if not parsed:
        print("No rows parsed from feed. Check source format.", file=sys.stderr)
        sys.exit(1)

    transformed = transform_for_mongo(parsed, source_url, meta)

    print(f"[INFO] Extracted {len(parsed)} rows from {source_url}")
    if args.dry_run:
        preview = transformed[:3]
        print("[DRY-RUN] Preview of transformed docs:")
        for i, doc in enumerate(preview, 1):
            slim = {k: doc[k] for k in ["ip", "_ingested_at", "_row_hash", "_source_row"] if k in doc}
            print(f"  {i}. {slim}")
        print("[DRY-RUN] Skipping MongoDB write.")
        return

    # Load
    try:
        upserts, matched = load_to_mongo(transformed, mongo_uri, db_name, collection)
    except Exception as e:
        print(f"Load failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[SUCCESS] Upserted: {upserts}, Already present: {matched}, Collection: {db_name}.{collection}")


if __name__ == "__main__":
    main()
