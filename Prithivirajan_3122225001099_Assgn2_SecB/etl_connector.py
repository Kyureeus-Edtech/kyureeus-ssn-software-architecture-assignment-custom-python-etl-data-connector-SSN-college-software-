# import os, io, requests, pandas as pd
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# # Mongo setup
# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# MONGO_DB = os.getenv("MONGO_DB", "etl_db")
# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB]

# # ---------------- URLhaus ----------------
# def extract_urlhaus():
#     url = os.getenv("URLHAUS_URL")
#     resp = requests.get(url)
#     resp.raise_for_status()
#     return resp.text

# def transform_urlhaus(csv_text):
#     df = pd.read_csv(io.StringIO(csv_text), on_bad_lines="skip")
#     df["ingested_at"] = datetime.utcnow()
#     return df.to_dict(orient="records")

# def load_urlhaus(records):
#     if records:
#         db["urlhaus_raw"].insert_many(records)
#         print(f"Inserted {len(records)} into urlhaus_raw")

# # ---------------- SonarQube ----------------
# def extract_sonarqube(endpoint):
#     base_url, token = os.getenv("SONARQUBE_URL"), os.getenv("SONARQUBE_TOKEN")
#     resp = requests.get(f"{base_url}{endpoint}", auth=(token, ""))
#     resp.raise_for_status()
#     return resp.json()

# def transform_sonarqube(data):
#     if "components" in data:
#         for item in data["components"]:
#             item["ingested_at"] = datetime.utcnow()
#         return data["components"]
#     elif "issues" in data:
#         for issue in data["issues"]:
#             issue["ingested_at"] = datetime.utcnow()
#         return data["issues"]
#     return []

# def load_sonarqube(collection, records):
#     if records:
#         db[collection].insert_many(records)
#         print(f"Inserted {len(records)} into {collection}")

# # ---------------- Main ----------------
# if __name__ == "__main__":
#     try:
#         raw_csv = extract_urlhaus()
#         load_urlhaus(transform_urlhaus(raw_csv))
#     except Exception as e:
#         print("URLhaus pipeline failed:", e)

#     SONARQUBE_ENDPOINTS = {
#         "sonarqube_projects_raw": "/api/projects/search",
#         "sonarqube_issues_raw": "/api/issues/search"
#     }
#     for collection, endpoint in SONARQUBE_ENDPOINTS.items():
#         try:
#             load_sonarqube(collection, transform_sonarqube(extract_sonarqube(endpoint)))
#         except Exception as e:
#             print(f"Pipeline failed for {collection}:", e)


#!/usr/bin/env python3
"""
SonarQube ETL connector
- Fetches multiple SonarQube endpoints (paginated)
- Transforms (adds ingested_at, source)
- Loads into MongoDB (one collection per endpoint)
"""

import os
import time
import math
import logging
import requests
from datetime import datetime, timezone
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment
load_dotenv()

# Config from .env (set defaults where sensible)
SONARQUBE_URL = os.getenv("SONARQUBE_URL", "").rstrip("/")  # e.g. http://localhost:9000
SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "etl_db")
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "500"))               # SonarQube default page size may vary
REQUEST_SLEEP = float(os.getenv("REQUEST_SLEEP", "0.3"))     # seconds between API calls
MEASURES_CHUNK = int(os.getenv("MEASURES_CHUNK", "50"))      # chunk metricKeys count per request to /measures/component
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))           # requests timeout

if not SONARQUBE_URL or not SONARQUBE_TOKEN:
    raise SystemExit("ERROR: SONARQUBE_URL and SONARQUBE_TOKEN must be set in your .env")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# HTTP session for reuse + headers with Bearer token
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {SONARQUBE_TOKEN}",
    "Accept": "application/json"
})

# Mongo client
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# ------------------ helper functions ------------------

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def safe_request(url: str, params: dict = None) -> dict:
    """
    Send GET request, handle basic retry on connection errors,
    rate-limit (Retry-After) support.
    Returns JSON decoded dict.
    """
    params = params or {}
    tries = 0
    while tries < 4:
        try:
            resp = session.get(url, params=params, timeout=TIMEOUT)
            if resp.status_code == 429:  # rate limited
                wait = int(resp.headers.get("Retry-After", "5"))
                logging.warning("Rate limited; sleeping %s seconds", wait)
                time.sleep(wait)
                tries += 1
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as ex:
            tries += 1
            logging.warning("Request error (%s). Retrying %s/3 after backoff...", ex, tries)
            time.sleep(2 ** tries)
    raise RuntimeError(f"Failed to GET {url} after retries")

def iter_paginated(endpoint: str, params: dict, items_keys: List[str]) -> List[Dict[str, Any]]:
    """
    Generic paginator for SonarQube endpoints that use 'paging' or return list directly.
    items_keys: candidate keys in response where list might be (e.g. ['components','projects','issues'])
    Returns accumulated list of items.
    """
    url = f"{SONARQUBE_URL}{endpoint}"
    page = 1
    page_size = PAGE_SIZE
    all_items = []

    while True:
        params_page = params.copy()
        # Sonar uses 'p' and 'ps' historically, but many endpoints also accept 'page'/'pageSize'.
        # We'll try 'p' & 'ps' first.
        params_page.update({"p": page, "ps": page_size})
        logging.debug("Requesting %s params=%s", url, params_page)
        js = safe_request(url, params=params_page)

        # find items array
        items = None
        for key in items_keys:
            if key in js and isinstance(js[key], list):
                items = js[key]
                break

        # If response itself is a list (unlikely raw), handle that:
        if items is None and isinstance(js, list):
            items = js

        # If still None, maybe this endpoint returns single-object (no pagination)
        if items is None:
            # return single object as one-element list
            logging.debug("No items list found; returning object")
            return [js] if js else []

        # annotate and append
        if items:
            for it in items:
                it["_ingested_at"] = now_utc_iso()
            all_items.extend(items)

        # paging logic
        paging = js.get("paging") if isinstance(js, dict) else None
        if paging and isinstance(paging, dict):
            total = paging.get("total", len(all_items))
            # Sonar's page indexing may be 1-based; we used page variable accordingly
            if page * page_size >= total:
                break
            page += 1
        else:
            # no paging info, break to avoid infinite loop
            break

        time.sleep(REQUEST_SLEEP)

    return all_items

def insert_many_safe(collection_name: str, records: List[dict]):
    if not records:
        logging.info("No records to insert into %s", collection_name)
        return
    col = db[collection_name]
    try:
        # Insert documents (raw dumps). Do not deduplicate here; keep raw ingestion for audit.
        col.insert_many(records, ordered=False)
        logging.info("Inserted %d records into %s", len(records), collection_name)
    except errors.BulkWriteError as bwe:
        logging.warning("BulkWriteError while inserting into %s: %s", collection_name, bwe.details)
    except Exception as ex:
        logging.error("Error inserting into %s: %s", collection_name, ex)

# ------------------ SonarQube-specific pipelines ------------------

def fetch_and_store_projects():
    """
    Fetch projects (components / projects endpoint) and store into sonarqube_projects_raw
    """
    candidates = ["/api/projects/search", "/api/components/search"]  # depending on SonarQube version
    items_keys = ["components", "projects", "components"]  # possible keys
    for endpoint in candidates:
        try:
            logging.info("Fetching projects from endpoint: %s", endpoint)
            records = iter_paginated(endpoint, params={}, items_keys=items_keys)
            # tag source
            for r in records:
                r["_source_endpoint"] = endpoint
            insert_many_safe("sonarqube_projects_raw", records)
            return
        except Exception as e:
            logging.debug("Endpoint %s failed: %s", endpoint, e)
    logging.error("Failed to fetch projects from any known endpoint")

def fetch_and_store_issues():
    """
    Fetch issues via /api/issues/search (supports paging)
    """
    endpoint = "/api/issues/search"
    items_keys = ["issues"]
    logging.info("Fetching issues from %s", endpoint)
    records = iter_paginated(endpoint, params={}, items_keys=items_keys)
    for r in records:
        r["_source_endpoint"] = endpoint
    insert_many_safe("sonarqube_issues_raw", records)

def fetch_and_store_users():
    """
    Fetch user list via /api/users/search (if available)
    """
    endpoint = "/api/users/search"
    items_keys = ["users"]
    logging.info("Fetching users from %s", endpoint)
    records = iter_paginated(endpoint, params={}, items_keys=items_keys)
    for r in records:
        r["_source_endpoint"] = endpoint
    insert_many_safe("sonarqube_users_raw", records)

def fetch_and_store_metrics():
    """
    Fetch metric definitions via /api/metrics/search
    """
    endpoint = "/api/metrics/search"
    items_keys = ["metrics"]
    logging.info("Fetching metrics from %s", endpoint)
    records = iter_paginated(endpoint, params={}, items_keys=items_keys)
    for r in records:
        r["_source_endpoint"] = endpoint
    insert_many_safe("sonarqube_metrics_raw", records)
    return records

def fetch_and_store_rules():
    """
    Fetch rules via /api/rules/search
    """
    endpoint = "/api/rules/search"
    items_keys = ["rules"]
    logging.info("Fetching rules from %s", endpoint)
    records = iter_paginated(endpoint, params={}, items_keys=items_keys)
    for r in records:
        r["_source_endpoint"] = endpoint
    insert_many_safe("sonarqube_rules_raw", records)

def fetch_and_store_measures_for_projects(metric_keys: List[str], project_keys: List[str]):
    """
    For each project key, fetch measures via /api/measures/component?component=<key>&metricKeys=...
    Because metricKeys length may be long, chunk them using MEASURES_CHUNK
    We store results into sonarqube_measures_raw with one document per call
    """
    endpoint = "/api/measures/component"
    logging.info("Fetching measures for %d projects with %d metrics", len(project_keys), len(metric_keys))
    for proj in project_keys:
        # chunk metric keys
        for i in range(0, len(metric_keys), MEASURES_CHUNK):
            chunk = metric_keys[i:i + MEASURES_CHUNK]
            params = {"component": proj, "metricKeys": ",".join(chunk)}
            url = f"{SONARQUBE_URL}{endpoint}"
            try:
                js = safe_request(url, params=params)
                # annotate
                doc = {
                    "_ingested_at": now_utc_iso(),
                    "_source_endpoint": endpoint,
                    "project": proj,
                    "requested_metrics": chunk,
                    "response": js
                }
                insert_many_safe("sonarqube_measures_raw", [doc])
            except Exception as e:
                logging.warning("Failed to fetch measures for project %s: %s", proj, e)
            time.sleep(REQUEST_SLEEP)

def get_project_keys_from_db_or_api():
    """
    Try to read project keys from DB (if already present). Otherwise fetch from API.
    """
    col = db["sonarqube_projects_raw"]
    docs = list(col.find({}, {"key": 1}))  # Sonar project key might be under 'key' or 'component.key'
    keys = []
    for d in docs:
        if not d:
            continue
        if "key" in d:
            keys.append(d["key"])
        elif "k" in d:
            keys.append(d["k"])
        else:
            # nested component key
            comp = d.get("component") or d.get("project")
            if isinstance(comp, dict) and "key" in comp:
                keys.append(comp["key"])
    keys = [k for k in keys if k]
    if keys:
        logging.info("Found %d project keys from DB", len(keys))
        return keys

    # else call API
    logging.info("No project keys in DB, fetching from API")
    fetch_and_store_projects()
    docs = list(col.find({}, {"key": 1}))
    keys = []
    for d in docs:
        if "key" in d:
            keys.append(d["key"])
        else:
            comp = d.get("component") or d.get("project")
            if isinstance(comp, dict) and "key" in comp:
                keys.append(comp["key"])
    logging.info("Fetched %d project keys", len(keys))
    return keys

# ------------------ Orchestration ------------------

def run_all_sonarqube_pipelines():
    logging.info("Starting SonarQube ETL pipelines")
    # projects
    fetch_and_store_projects()

    # users, rules, metrics, issues - independent
    try:
        fetch_and_store_metrics()  # metrics first so measures can use metric keys
    except Exception as e:
        logging.warning("metrics pipeline failed: %s", e)

    try:
        fetch_and_store_rules()
    except Exception as e:
        logging.warning("rules pipeline failed: %s", e)

    try:
        fetch_and_store_users()
    except Exception as e:
        logging.warning("users pipeline failed: %s", e)

    try:
        fetch_and_store_issues()
    except Exception as e:
        logging.warning("issues pipeline failed: %s", e)

    # measures: need project keys and metric keys
    metric_docs = list(db["sonarqube_metrics_raw"].find({}))
    metric_keys = []
    for md in metric_docs:
        # in Sonar metrics, key is 'key'
        if isinstance(md, dict) and "key" in md:
            metric_keys.append(md["key"])
    logging.info("Total metric keys to request: %d", len(metric_keys))

    project_keys = get_project_keys_from_db_or_api()
    if project_keys and metric_keys:
        fetch_and_store_measures_for_projects(metric_keys, project_keys)
    else:
        logging.warning("Skipping measures: missing project_keys or metric_keys")

    logging.info("SonarQube ETL pipelines finished")

if __name__ == "__main__":
    run_all_sonarqube_pipelines()
