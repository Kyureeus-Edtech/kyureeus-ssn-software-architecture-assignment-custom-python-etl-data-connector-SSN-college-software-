#!/usr/bin/env python3
"""
ETL: Have I Been Pwned (HIBP) API v3  -> MongoDB
Author: <Your Name> (<Roll No.>)
Course: SSN CSE — Software Architecture (Kyureeus EdTech)
"""

import os
import time
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from requests import Response
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from pydantic import BaseModel, Field, ValidationError
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# =========================
# Config & Environment
# =========================
load_dotenv()

HIBP_API_BASE = os.getenv("HIBP_API_BASE", "https://haveibeenpwned.com/api/v3")
HIBP_API_KEY = os.getenv("HIBP_API_KEY")  # required for v3 (except Pwned Passwords)
HIBP_USER_AGENT = os.getenv("HIBP_USER_AGENT", "SSN-Software-Architecture-ETL/1.0 (student)")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "ssn_software_architecture")
# Optional account-specific endpoints (only queried if set)
TEST_ACCOUNT_EMAIL = os.getenv("TEST_ACCOUNT_EMAIL")  # e.g., "test@example.com"

# Respect HIBP’s rate-limit guidance. Historically ~1.5 secs between calls.
HIBP_MIN_DELAY_SEC = float(os.getenv("HIBP_MIN_DELAY_SEC", "1.6"))

# =========================
# Mongo Setup
# =========================
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

COL_BREACHES = db["hibp_breaches_raw"]
COL_BREACH_DETAILS = db["hibp_breach_details_raw"]
COL_DATACLASSES = db["hibp_dataclasses_raw"]
COL_PASTES = db["hibp_pastes_raw"]
COL_BREACHED_ACCOUNTS = db["hibp_breached_accounts_raw"]
COL_METADATA = db["hibp_etl_runs"]

# Helpful: indexes (idempotent)
COL_BREACHES.create_index("Name", unique=True)
COL_BREACH_DETAILS.create_index("Name", unique=True)
COL_DATACLASSES.create_index("DataClass", unique=True)
COL_PASTES.create_index(["Id", "Source"], unique=True)
COL_BREACHED_ACCOUNTS.create_index(["Name", "Account"], unique=True)


# =========================
# Models (Pydantic)
# =========================
class BreachSummary(BaseModel):
    Name: str
    Title: Optional[str] = None
    Domain: Optional[str] = None
    BreachDate: Optional[str] = None
    AddedDate: Optional[str] = None
    ModifiedDate: Optional[str] = None
    PwnCount: Optional[int] = None
    Description: Optional[str] = None
    DataClasses: Optional[List[str]] = None
    IsVerified: Optional[bool] = None
    IsFabricated: Optional[bool] = None
    IsSensitive: Optional[bool] = None
    IsRetired: Optional[bool] = None
    IsSpamList: Optional[bool] = None
    LogoPath: Optional[str] = None
    _source_url: Optional[str] = None
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataClassItem(BaseModel):
    DataClass: str
    _source_url: Optional[str] = None
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PasteItem(BaseModel):
    Id: str
    Source: Optional[str] = None
    Title: Optional[str] = None
    Date: Optional[str] = None
    EmailCount: Optional[int] = None
    _source_url: Optional[str] = None
    Account: Optional[str] = None
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BreachedAccountItem(BaseModel):
    Name: str
    Title: Optional[str] = None
    Domain: Optional[str] = None
    BreachDate: Optional[str] = None
    AddedDate: Optional[str] = None
    PwnCount: Optional[int] = None
    DataClasses: Optional[List[str]] = None
    IsVerified: Optional[bool] = None
    IsSensitive: Optional[bool] = None
    Account: Optional[str] = None
    _source_url: Optional[str] = None
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# HTTP helpers
# =========================
class HIBPError(Exception):
    pass


def hibp_headers() -> Dict[str, str]:
    if not HIBP_API_KEY:
        # Many v3 endpoints require an API key.
        # We still return headers (some endpoints may not strictly require).
        pass
    return {
        "hibp-api-key": HIBP_API_KEY or "",
        "user-agent": HIBP_USER_AGENT,
        "accept": "application/json",
    }


@retry(
    retry=retry_if_exception_type(HIBPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
    reraise=True,
)
def get_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """GET wrapper with backoff. Raises HIBPError on non-2xx/empty."""
    url = f"{HIBP_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    resp: Response = requests.get(url, headers=hibp_headers(), params=params, timeout=30)
    # Handle common statuses
    if resp.status_code == 200:
        try:
            data = resp.json()
        except ValueError:
            raise HIBPError(f"Invalid JSON at {url}")
        return data, url
    elif resp.status_code == 404:
        # Not found is a valid outcome for some endpoints (e.g., no pastes)
        return None, url
    elif resp.status_code in (401, 403):
        raise HIBPError(f"Auth error {resp.status_code}: Check HIBP_API_KEY and permissions for {url}")
    elif resp.status_code == 429:
        # Rate limited — let tenacity backoff; also sleep a little extra
        time.sleep(2.0)
        raise HIBPError("Rate limited (429). Retrying with backoff.")
    else:
        raise HIBPError(f"Unexpected {resp.status_code} from {url}: {resp.text[:200]}")


def polite_delay():
    """Ensure spacing between calls to respect HIBP rate limits."""
    time.sleep(HIBP_MIN_DELAY_SEC)


# =========================
# Extract
# =========================
def extract_breaches() -> List[Dict[str, Any]]:
    data, url = get_json("/breaches")
    polite_delay()
    items = data or []
    for x in items:
        x["_source_url"] = url
    return items


def extract_breach_detail(name: str) -> Optional[Dict[str, Any]]:
    data, url = get_json(f"/breach/{name}")
    polite_delay()
    if data is None:
        return None
    data["_source_url"] = url
    return data


def extract_dataclasses() -> List[Dict[str, Any]]:
    data, url = get_json("/dataclasses")
    polite_delay()
    # HIBP returns a plain list of strings; convert to objects
    items = [{"DataClass": s, "_source_url": url} for s in (data or [])]
    return items


def extract_pastes_for_account(account: str) -> List[Dict[str, Any]]:
    # Requires API key, may return 404 when no pastes found
    data, url = get_json(f"/pasteaccount/{account}")
    polite_delay()
    if not data:
        return []
    for x in data:
        x["_source_url"] = url
        x["Account"] = account
    return data


def extract_breaches_for_account(account: str) -> List[Dict[str, Any]]:
    # Requires API key; returns list of breaches for account (if any)
    data, url = get_json(f"/breachedaccount/{account}")
    polite_delay()
    if not data:
        return []
    for x in data:
        x["_source_url"] = url
        x["Account"] = account
    return data


# =========================
# Transform
# =========================
def to_breach_summary(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = BreachSummary(**doc)
        return model.model_dump()
    except ValidationError:
        # keep original with timestamp if validation fails
        doc.setdefault("ingestion_timestamp", datetime.now(timezone.utc))
        return doc


def to_breach_detail(doc: Dict[str, Any]) -> Dict[str, Any]:
    # Detail has same shape as summary in v3; keep as-is with validation
    return to_breach_summary(doc)


def to_dataclass_item(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = DataClassItem(**doc)
        return model.model_dump()
    except ValidationError:
        doc.setdefault("ingestion_timestamp", datetime.now(timezone.utc))
        return doc


def to_paste_item(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = PasteItem(**doc)
        return model.model_dump()
    except ValidationError:
        doc.setdefault("ingestion_timestamp", datetime.now(timezone.utc))
        return doc


def to_breached_account_item(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = BreachedAccountItem(**doc)
        return model.model_dump()
    except ValidationError:
        doc.setdefault("ingestion_timestamp", datetime.now(timezone.utc))
        return doc


# =========================
# Load
# =========================
def upsert_breaches(items: List[Dict[str, Any]]):
    ops = []
    for it in items:
        doc = to_breach_summary(it)
        ops.append(
            UpdateOne({"Name": doc.get("Name")}, {"$set": doc}, upsert=True)
        )
    if ops:
        COL_BREACHES.bulk_write(ops, ordered=False)


def upsert_breach_detail(item: Dict[str, Any]):
    if not item:
        return
    doc = to_breach_detail(item)
    COL_BREACH_DETAILS.update_one({"Name": doc.get("Name")}, {"$set": doc}, upsert=True)


def upsert_dataclasses(items: List[Dict[str, Any]]):
    ops = []
    for it in items:
        doc = to_dataclass_item(it)
        ops.append(
            UpdateOne({"DataClass": doc.get("DataClass")}, {"$set": doc}, upsert=True)
        )
    if ops:
        COL_DATACLASSES.bulk_write(ops, ordered=False)


def upsert_pastes(items: List[Dict[str, Any]]):
    ops = []
    for it in items:
        doc = to_paste_item(it)
        key = {"Id": doc.get("Id"), "Source": doc.get("Source")}
        ops.append(UpdateOne(key, {"$set": doc}, upsert=True))
    if ops:
        COL_PASTES.bulk_write(ops, ordered=False)


def upsert_breached_accounts(items: List[Dict[str, Any]]):
    ops = []
    for it in items:
        doc = to_breached_account_item(it)
        key = {"Name": doc.get("Name"), "Account": doc.get("Account")}
        ops.append(UpdateOne(key, {"$set": doc}, upsert=True))
    if ops:
        COL_BREACHED_ACCOUNTS.bulk_write(ops, ordered=False)


# =========================
# Orchestration
# =========================
def run_etl(selected_breach_names: Optional[List[str]] = None):
    start = datetime.now(timezone.utc)

    # 1) Breaches (list)
    breaches = extract_breaches()
    upsert_breaches(breaches)

    # 2) Breach details (for either provided names or top-N from list)
    names = selected_breach_names or [b["Name"] for b in breaches[:10]]  # cap to avoid long runs
    for name in names:
        try:
            detail = extract_breach_detail(name)
            if detail:
                upsert_breach_detail(detail)
        except HIBPError as e:
            print(f"[WARN] Detail for {name} failed: {e}")

    # 3) Data classes
    dataclasses = extract_dataclasses()
    upsert_dataclasses(dataclasses)

    # Optional: account-specific endpoints if TEST_ACCOUNT_EMAIL is set
    if TEST_ACCOUNT_EMAIL:
        try:
            pastes = extract_pastes_for_account(TEST_ACCOUNT_EMAIL)
            upsert_pastes(pastes)
        except HIBPError as e:
            print(f"[WARN] Pastes for {TEST_ACCOUNT_EMAIL} failed: {e}")

        try:
            acc_breaches = extract_breaches_for_account(TEST_ACCOUNT_EMAIL)
            upsert_breached_accounts(acc_breaches)
        except HIBPError as e:
            print(f"[WARN] BreachedAccount for {TEST_ACCOUNT_EMAIL} failed: {e}")

    end = datetime.now(timezone.utc)
    COL_METADATA.insert_one(
        {
            "etl_name": "hibp_v3",
            "started_at": start,
            "finished_at": end,
            "breaches_upserted": len(breaches),
            "dataclasses_upserted": len(dataclasses),
            "selected_breach_names": names,
            "account_used": bool(TEST_ACCOUNT_EMAIL),
        }
    )
    print("ETL completed.")


if __name__ == "__main__":
    # Optional: allow names via env (comma-separated)
    names_env = os.getenv("BREACH_NAMES")
    names = [n.strip() for n in names_env.split(",")] if names_env else None
    run_etl(selected_breach_names=names)
