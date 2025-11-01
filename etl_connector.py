import os
import time
import json
import datetime as dt
from typing import Dict, Iterable, List, Optional

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

def now_iso():
    return dt.datetime.now(dt.UTC).isoformat()

def load_env_vars():
    load_dotenv()
    cfg = {
        "GN_API_KEY": os.getenv("GN_API_KEY", "").strip(),
        "GN_BASE_URL": os.getenv("GN_BASE_URL", "https://api.greynoise.io").rstrip("/"),
        "TARGET_IPS": os.getenv("TARGET_IPS", ""),
        "INPUT_IPS_FILE": os.getenv("INPUT_IPS_FILE", ""),
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "greynoise"),
        "CONNECTOR_NAME": os.getenv("CONNECTOR_NAME", "greynoise_riot"),
        "MONGO_COLLECTION_SUFFIX": os.getenv("MONGO_COLLECTION_SUFFIX", "_raw"),
        "REQUEST_TIMEOUT_SECONDS": float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10")),
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "5")),
        "INITIAL_BACKOFF_SECONDS": float(os.getenv("INITIAL_BACKOFF_SECONDS", "1.0"))
    }
    return cfg

class GreyNoiseIPConnector:
    def _init_(self, cfg: Dict):
        self.cfg = cfg
        self.session = requests.Session()
        self.headers = {"Accept": "application/json"}
        if cfg["GN_API_KEY"]:
            self.headers["key"] = cfg["GN_API_KEY"]

        self.client = MongoClient(cfg["MONGO_URI"])
        self.db = self.client[cfg["MONGO_DB"]]
        self.collection_name = f"{cfg['CONNECTOR_NAME']}{cfg['MONGO_COLLECTION_SUFFIX']}"
        self.col = self.db[self.collection_name]

        self.col.create_index([("ip", ASCENDING), ("fetched_at", ASCENDING)], unique=True)
        self.col.create_index([("ingested_at", ASCENDING)])
        self.col.create_index([("connector", ASCENDING)])

    def _url_for_ip(self, ip: str) -> str:
        return f"{self.cfg['GN_BASE_URL']}/v3/ip/{ip}"

    def extract(self, ip: str) -> Dict:
        url = self._url_for_ip(ip)
        backoff = self.cfg["INITIAL_BACKOFF_SECONDS"]
        for attempt in range(1, self.cfg["MAX_RETRIES"] + 1):
            try:
                resp = self.session.get(url, headers=self.headers, timeout=self.cfg["REQUEST_TIMEOUT_SECONDS"])
                if resp.status_code == 429:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                if attempt == self.cfg["MAX_RETRIES"]:
                    raise
                time.sleep(backoff)
                backoff *= 2
        raise RuntimeError("Failed to fetch after retries")

    def transform(self, ip: str, raw: Dict) -> Dict:
        doc = {
            "connector": "greynoise",
            "ip": raw.get("ip", ip),
            "business_service": raw.get("business_service_intelligence"),
            "internet_scanner_summary": {
                "seen": None,
                "classification": None,
                "first_seen": None,
                "last_seen": None,
                "found": None,
                "actor": None,
                "bot": None,
                "vpn": None,
                "tags": None,
                "metadata": None
            },
            "request_metadata": raw.get("request_metadata"),
            "raw": raw,
            "fetched_at": now_iso(),
            "ingested_at": now_iso(),
            "_source": {
                "endpoint": self._url_for_ip(ip)
            }
        }

        isc = raw.get("internet_scanner_intelligence") or {}
        doc["internet_scanner_summary"]["seen"] = isc.get("seen")
        doc["internet_scanner_summary"]["classification"] = isc.get("classification")
        doc["internet_scanner_summary"]["first_seen"] = isc.get("first_seen")
        doc["internet_scanner_summary"]["last_seen"] = isc.get("last_seen")
        doc["internet_scanner_summary"]["found"] = isc.get("found")
        doc["internet_scanner_summary"]["actor"] = isc.get("actor")
        doc["internet_scanner_summary"]["bot"] = isc.get("bot")
        doc["internet_scanner_summary"]["vpn"] = isc.get("vpn")
        doc["internet_scanner_summary"]["tags"] = isc.get("tags")
        doc["internet_scanner_summary"]["metadata"] = isc.get("metadata")
        return doc

    def load(self, doc: Dict) -> None:
        try:
            self.col.insert_one(doc)
        except DuplicateKeyError:
            pass

    def run_batch(self, ips: Iterable[str], dry_run: bool = False) -> List[Dict]:
        summary = []
        for ip in ips:
            ip = ip.strip()
            if not ip:
                continue
            try:
                raw = self.extract(ip)
            except Exception as e:
                summary.append({"ip": ip, "status": "error", "error": str(e)})
                continue

            doc = self.transform(ip, raw)
            if dry_run:
                print(json.dumps(doc, indent=2))
                summary.append({"ip": ip, "status": "dry-run"})
            else:
                self.load(doc)
                summary.append({"ip": ip, "status": "inserted"})
        return summary

def parse_ips(env_ips: str, ips_file: str) -> List[str]:
    ips = []
    if env_ips:
        ips.extend([x.strip() for x in env_ips.split(",") if x.strip()])
    if ips_file and os.path.isfile(ips_file):
        with open(ips_file, "r", encoding="utf-8") as f:
            for line in f:
                v = line.strip()
                if v and not v.startswith("#"):
                    ips.append(v)
    seen = set(); out = []
    for ip in ips:
        if ip not in seen:
            seen.add(ip); out.append(ip)
    return out

if __name__ == "_main_":
    import argparse
    load_dotenv()
    cfg = load_env_vars()
    parser = argparse.ArgumentParser(description="GreyNoise IP ETL -> MongoDB")
    parser.add_argument("--dry-run", action="store_true", help="print docs rather than inserting")
    parser.add_argument("--ips", nargs="*", help="override ips")
    args = parser.parse_args()
    if args.ips:
        ips = args.ips
    else:
        ips = parse_ips(cfg["TARGET_IPS"], cfg["INPUT_IPS_FILE"])
        if not ips:
            raise SystemExit("No IPs provided: set TARGET_IPS or INPUT_IPS_FILE")
    connector = GreyNoiseIPConnector(cfg)
    results = connector.run_batch(ips, dry_run=args.dry_run)
    print(json.dumps(results, indent=2))