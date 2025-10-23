#!/usr/bin/env python3
"""
malwarebazaar_etl.py

ETL for MalwareBazaar (bazaar.abuse.ch) metadata endpoints -> MongoDB.
"""

import os
import time
import requests
from pymongo import MongoClient, UpdateOne
from typing import Dict, Any, List

MB_API = "https://mb-api.abuse.ch/api/v1/"
MB_AUTH_KEY = os.getenv("MB_AUTH_KEY")  
HEADERS = {"Auth-Key": MB_AUTH_KEY} if MB_AUTH_KEY else {}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MB_DB", "malwarebazaar")
BATCH_SIZE = 100  

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def post_query(payload: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    """Post a form-encoded query to MalwareBazaar API and return json (or empty dict)."""
    try:
        resp = requests.post(MB_API, data=payload, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[ERROR] API request failed for payload={payload}: {e}")
        return {}

def normalize_sample_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single sample dict from MalwareBazaar to a canonical Mongo document.
    The API returns different shapes depending on endpoint; pick common fields safely.
    """
    doc = {
        "sha256_hash": entry.get("sha256_hash") or entry.get("sha256"),
        "sha1_hash": entry.get("sha1_hash") or entry.get("sha1"),
        "md5_hash": entry.get("md5_hash") or entry.get("md5"),
        "filename": entry.get("file_name") or entry.get("filename") or entry.get("file_name"),
        "file_type": entry.get("file_type"),
        "tags": entry.get("tags") or entry.get("tag") or [],
        "first_seen": entry.get("first_seen"),
        "signature": entry.get("signature"),
        "yara_hits": entry.get("yara_hits") if isinstance(entry.get("yara_hits"), list) else None,
        "imphash": entry.get("imphash"),
        "tlsh": entry.get("tlsh"),
        "confidence": entry.get("confidence"),  # sometimes present
        "raw": entry  # keep raw data for future reference
    }
    # Remove None keys
    return {k: v for k, v in doc.items() if v is not None}

def etl_get_recent(limit: int = 100) -> List[Dict[str, Any]]:
    """Extract recent entries using query=get_recent (selector=limit or time)."""
    payload = {"query": "get_recent", "selector": str(limit)}
    out = post_query(payload)
    return out.get("data") or out.get("files") or out.get("return") or out.get("query_results") or out.get("reported_data") or out.get("data", [])

def etl_get_taginfo(tag: str, limit: int = 100) -> List[Dict[str, Any]]:
    payload = {"query": "get_taginfo", "tag": tag, "limit": str(limit)}
    out = post_query(payload)
    # often returns 'data' or 'files'
    return out.get("data") or out.get("files") or []

def etl_get_yarainfo(yara_rule: str, limit: int = 100) -> List[Dict[str, Any]]:
    payload = {"query": "get_yarainfo", "yara_rule": yara_rule, "limit": str(limit)}
    out = post_query(payload)
    return out.get("data") or out.get("files") or []

def etl_get_info(hash_value: str) -> Dict[str, Any]:
    payload = {"query": "get_info", "hash": hash_value}
    out = post_query(payload)
    # get_info returns either a single dict or data list
    if isinstance(out.get("data"), list) and out["data"]:
        return out["data"][0]
    return out.get("data") or out

def etl_get_certificate(serial_number: str) -> List[Dict[str, Any]]:
    payload = {"query": "get_certificate", "serial_number": serial_number}
    out = post_query(payload)
    return out.get("data") or []

def bulk_upsert_samples(collection, docs: List[Dict[str, Any]]):
    """Upsert a list of normalized sample docs into the given collection by sha256_hash."""
    if not docs:
        return 0
    ops = []
    for d in docs:
        if not d.get("sha256_hash"):
            # fallback to md5/sha1 if sha256 missing (rare)
            key = d.get("md5_hash") or d.get("sha1_hash")
            filter_q = {"$or": [{"md5_hash": d.get("md5_hash")}, {"sha1_hash": d.get("sha1_hash")}]}
        else:
            filter_q = {"sha256_hash": d["sha256_hash"]}
        ops.append(UpdateOne(filter_q, {"$set": d}, upsert=True))
    result = collection.bulk_write(ops, ordered=False)
    print(f"[MONGO] upserted={result.upserted_count} modified={result.modified_count}")
    return result.upserted_count + result.modified_count

def run_etl():
    """
    Run ETL for 5 metadata endpoints:
      1) get_recent
      2) get_taginfo (example tag list)
      3) get_yarainfo (example yara names)
      4) get_info (by sample - demonstrates single record query)
      5) get_certificate (certificate metadata)
    """
    samples_col = db["samples"]
    certificates_col = db["certificates"]

    print("[STEP] fetching recent samples...")
    recent = etl_get_recent(limit=100) or []
    norm_recent = [normalize_sample_entry(e) for e in recent]
    bulk_upsert_samples(samples_col, norm_recent)
    time.sleep(1)

    tags_to_fetch = ["TrickBot", "Emotet", "Ransomware"] 
    for tag in tags_to_fetch:
        print(f"[STEP] fetching tag='{tag}'")
        tdata = etl_get_taginfo(tag=tag, limit=100)
        norm = [normalize_sample_entry(e) for e in tdata]
        bulk_upsert_samples(samples_col, norm)
        time.sleep(1)

    yara_rules = ["win_remcos_g0"]  
    for y in yara_rules:
        print(f"[STEP] fetching yara_rule='{y}'")
        ydata = etl_get_yarainfo(yara_rule=y, limit=100)
        norm = [normalize_sample_entry(e) for e in ydata]
        bulk_upsert_samples(samples_col, norm)
        time.sleep(1)

    if norm_recent:
        demo_hash = norm_recent[0].get("sha256_hash") or norm_recent[0].get("md5_hash")
        if demo_hash:
            print(f"[STEP] fetching get_info for hash={demo_hash[:16]}...")
            info = etl_get_info(demo_hash)
            if info:
                doc = normalize_sample_entry(info)
                bulk_upsert_samples(samples_col, [doc])
    time.sleep(1)

    serials = []
    for s in norm_recent:
        raw = s.get("raw", {})
        cert = raw.get("certificate") or raw.get("certificate_serial_number") or raw.get("certificate_serial")
        if cert:
            serials.append(cert)
    if serials:
        serial = serials[0]
        print(f"[STEP] fetching certificate serial={serial}")
        cert_data = etl_get_certificate(serial)
        # store certificate metadata
        for c in cert_data:
            cdoc = c.copy()
            certificates_col.update_one({"serial_number": cdoc.get("serial_number")}, {"$set": cdoc}, upsert=True)
        time.sleep(1)

    print("[DONE] ETL run complete.")

if __name__ == "__main__":
    run_etl()
