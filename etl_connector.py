#!/usr/bin/env python3
"""
Kyureeus EdTech – Software Architecture Assignment
Custom Python ETL Data Connector for AbuseIPDB → MongoDB

Extract:   Calls AbuseIPDB /check for a list of IPs (IPv4/IPv6)
Transform: Normalizes JSON for MongoDB (adds audit metadata)
Load:      Upserts into a single collection (e.g., abuseipdb_raw)

Features
- Secure .env loading (no secrets in code)
- Robust error handling (timeouts, HTTP errors, rate limits 429, empty/invalid)
- Exponential backoff with Retry-After support
- Input from CLI (--ip or --file) and dry-run mode
- Connectivity checks to MongoDB and index creation
- Ingestion timestamps + source metadata for audits
"""

import argparse
import datetime as dt
import ipaddress
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, Optional, Tuple

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, errors as mongo_errors
from pymongo.collection import Collection



def load_config() -> Dict[str, Any]:
    load_dotenv()  # loads from .env

    cfg = {
        "ABUSEIPDB_API_KEY": os.getenv("ABUSEIPDB_API_KEY"),
        "ABUSEIPDB_BASE_URL": os.getenv("ABUSEIPDB_BASE_URL", "https://api.abuseipdb.com/api/v2"),
        "ABUSEIPDB_MAX_AGE_DAYS": int(os.getenv("ABUSEIPDB_MAX_AGE_DAYS", "90")),
        "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        "MONGODB_DB": os.getenv("MONGODB_DB", "kyureeus_assignments"),
        "MONGODB_COLLECTION": os.getenv("MONGODB_COLLECTION", "abuseipdb_raw"),
        "REQUEST_TIMEOUT_SECONDS": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")),
        "RETRY_MAX_ATTEMPTS": int(os.getenv("RETRY_MAX_ATTEMPTS", "5")),
        "RETRY_BASE_SLEEP_SECONDS": float(os.getenv("RETRY_BASE_SLEEP_SECONDS", "1.5")),
    }
    missing = [k for k in ["ABUSEIPDB_API_KEY"] if not cfg.get(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    return cfg



def utcnow_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()

def validate_ip(candidate: str) -> bool:
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False

def iter_ips(cli_ip: Optional[str], file_path: Optional[str]) -> Iterable[str]:
    if cli_ip:
        yield cli_ip.strip()
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line


class AbuseIPDBClient:
    def __init__(self, api_key: str, base_url: str, timeout_s: int, retry_attempts: int, base_sleep_s: float):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.retry_attempts = retry_attempts
        self.base_sleep_s = base_sleep_s
        self.session = requests.Session()
        self.session.headers.update({
            "Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Kyureeus-AbuseIPDB-ETL/1.0"
        })

    def _sleep_backoff(self, attempt: int, retry_after_header: Optional[str]) -> None:
        if retry_after_header:
            try:
                sleep_s = float(retry_after_header)
                time.sleep(sleep_s)
                return
            except Exception:
                pass
        # exponential backoff: base_sleep_s * 2^(attempt-1) with jitter
        sleep_s = self.base_sleep_s * (2 ** max(0, attempt - 1))
        time.sleep(sleep_s)

    def check_ip(self, ip: str, max_age_days: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Calls /check?ipAddress=<ip>&maxAgeInDays=<days>
        Returns: (json_payload_or_none, error_message_or_none)
        """
        url = f"{self.base_url}/check"
        params = {"ipAddress": ip, "maxAgeInDays": max_age_days}
        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout_s)
            except requests.RequestException as e:
                if attempt >= self.retry_attempts:
                    return None, f"Network error after {attempt} attempts: {e}"
                self._sleep_backoff(attempt, None)
                continue

            # Handle rate limit 429
            if resp.status_code == 429:
                if attempt >= self.retry_attempts:
                    return None, f"Rate limited (429) after {attempt} attempts."
                self._sleep_backoff(attempt, resp.headers.get("Retry-After"))
                continue

            # Other non-200 HTTP
            if not resp.ok:
                # 4xx/5xx—do not retry on 4xx except 429, but we already handled 429
                if 400 <= resp.status_code < 500 or attempt >= self.retry_attempts:
                    return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
                self._sleep_backoff(attempt, None)
                continue

            # Parse JSON
            try:
                data = resp.json()
            except json.JSONDecodeError:
                return None, "Invalid JSON response"
            if not data:
                return None, "Empty JSON response"

            return data, None

        return None, "Unexpected error in retry loop"


def transform_record(raw: Dict[str, Any], ip: str) -> Dict[str, Any]:
    """
    Normalize payload for MongoDB:
    - Embed raw payload
    - Add audit fields
    """
    now = utcnow_iso()
    doc = {
        "_source": "abuseipdb",
        "_extracted_at": now,
        "_connector_version": "1.0",
        "_input_ip": ip,
        "raw": raw,                    # keep the full unmodified payload for traceability
    }

    # Convenience fields if present in AbuseIPDB schema (robust to missing keys)
    data = raw.get("data", {}) if isinstance(raw, dict) else {}
    doc.update({
        "ipAddress": data.get("ipAddress"),
        "isPublic": data.get("isPublic"),
        "ipVersion": data.get("ipVersion"),
        "isWhitelisted": data.get("isWhitelisted"),
        "abuseConfidenceScore": data.get("abuseConfidenceScore"),
        "countryCode": data.get("countryCode"),
        "usageType": data.get("usageType"),
        "domain": data.get("domain"),
        "hostnames": data.get("hostnames"),
        "totalReports": data.get("totalReports"),
        "numDistinctUsers": data.get("numDistinctUsers"),
        "lastReportedAt": data.get("lastReportedAt"),
    })
    return doc



def get_collection(uri: str, db_name: str, coll_name: str) -> Collection:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Force a ping to validate connectivity early
        client.admin.command("ping")
    except mongo_errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB connectivity failed: {e}")

    db = client[db_name]
    coll = db[coll_name]
    # Ensure helpful indexes: dedupe by ip + lastReportedAt (or fallback input ip)
    try:
        coll.create_index(
            [("ipAddress", 1), ("lastReportedAt", 1)],
            name="ip_lastReport_idx",
            background=True
        )
        coll.create_index(
            [("_extracted_at", -1)],
            name="extracted_at_desc_idx",
            background=True
        )
    except mongo_errors.PyMongoError as e:
        print(f"[WARN] Failed to create indexes: {e}", file=sys.stderr)

    return coll

def load_document(coll: Collection, doc: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Upsert strategy:
    If 'ipAddress' & 'lastReportedAt' exist, use them as identity; else fallback to ('_input_ip', '_extracted_at') to avoid loss.
    """
    try:
        key = {}
        if doc.get("ipAddress") and doc.get("lastReportedAt"):
            key = {"ipAddress": doc["ipAddress"], "lastReportedAt": doc["lastReportedAt"]}
        else:
            key = {"_input_ip": doc.get("_input_ip"), "_extracted_at": doc.get("_extracted_at")}

        res = coll.update_one(key, {"$set": doc}, upsert=True)
        return True, None
    except mongo_errors.PyMongoError as e:
        return False, str(e)


def run_etl(args: argparse.Namespace) -> int:
    cfg = load_config()
    coll = get_collection(cfg["MONGODB_URI"], cfg["MONGODB_DB"], cfg["MONGODB_COLLECTION"])

    client = AbuseIPDBClient(
        api_key=cfg["ABUSEIPDB_API_KEY"],
        base_url=cfg["ABUSEIPDB_BASE_URL"],
        timeout_s=cfg["REQUEST_TIMEOUT_SECONDS"],
        retry_attempts=cfg["RETRY_MAX_ATTEMPTS"],
        base_sleep_s=cfg["RETRY_BASE_SLEEP_SECONDS"],
    )

    # Iterate IPs
    ip_count = 0
    success = 0
    failures = 0

    for ip in iter_ips(args.ip, args.file):
        ip_count += 1

        # Validate input
        if not validate_ip(ip):
            print(f"[SKIP] Invalid IP format: {ip}", file=sys.stderr)
            failures += 1
            continue

        # Extract
        payload, err = client.check_ip(ip, max_age_days=cfg["ABUSEIPDB_MAX_AGE_DAYS"])
        if err:
            print(f"[ERR] Extract failed for {ip}: {err}", file=sys.stderr)
            failures += 1
            continue

        # Transform
        doc = transform_record(payload, ip)

        # Optional: print in dry-run
        if args.dry_run:
            print(json.dumps(doc, indent=2))
            success += 1
            continue

        # Load
        ok, load_err = load_document(coll, doc)
        if not ok:
            print(f"[ERR] Load failed for {ip}: {load_err}", file=sys.stderr)
            failures += 1
            continue

        print(f"[OK] Upserted {ip}")
        success += 1

    print(f"\nSummary: processed={ip_count}, success={success}, failures={failures}")
    return 0 if failures == 0 else 2

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="AbuseIPDB → MongoDB ETL connector (Extract, Transform, Load)"
    )
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--ip", help="Single IP address (IPv4/IPv6) to check")
    grp.add_argument("--file", help="Path to file containing IPs (one per line)")

    p.add_argument("--dry-run", action="store_true", help="Do not write to MongoDB; print transformed docs")
    return p.parse_args()

if __name__ == "__main__":
    try:
        args = parse_args()
        sys.exit(run_etl(args))
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        sys.exit(1)
