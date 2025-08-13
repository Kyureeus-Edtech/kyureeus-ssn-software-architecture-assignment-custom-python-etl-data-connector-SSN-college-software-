import os
import time
import json
import datetime as dt
import logging
from typing import Dict, Iterable, List
import requests
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)
logging.Formatter.converter = time.gmtime 

def now_iso():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()

def load_env_vars():
    load_dotenv()
    cfg = {
        "GN_API_KEY": os.getenv("GN_API_KEY", "").strip(),
        "GN_BASE_URL": os.getenv("GN_BASE_URL", "https://api.greynoise.io").rstrip("/"),
        "TARGET_IPS": os.getenv("TARGET_IPS", ""),
        "INPUT_FILE": os.getenv("INPUT_FILE", ""),
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "greynoise"),
        "CONNECTOR_NAME": os.getenv("CONNECTOR_NAME", "greynoise_riot"),
        "MONGO_SUFFIX": os.getenv("MONGO_SUFFIX", "_raw"),
        "REQ_TIMEOUT": float(os.getenv("REQ_TIMEOUT", "10")),
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "5")),
        "INITIAL_BACKOFFS": float(os.getenv("INITIAL_BACKOFFS", "1.0"))
    }
    return cfg

class GreyNoiseIPConnector:
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.session = requests.Session()
        self.headers = {"Accept": "application/json"}
        if cfg["GN_API_KEY"]:
            self.headers["key"] = cfg["GN_API_KEY"]

        # Mongo setup
        self.client = MongoClient(cfg["MONGO_URI"])
        self.db = self.client[cfg["MONGO_DB"]]
        self.collection_name = f"{cfg['CONNECTOR_NAME']}{cfg['MONGO_SUFFIX']}"
        self.col = self.db[self.collection_name]

        # indexes
        self.col.create_index([("ip", ASCENDING), ("fetched_at", ASCENDING)], unique=True)
        self.col.create_index([("ingested_at", ASCENDING)])
        self.col.create_index([("connector", ASCENDING)])

    def _url_for_ip(self, ip: str) -> str:
        return f"{self.cfg['GN_BASE_URL']}/v3/ip/{ip}"

    def extract(self, ip: str) -> Dict:
        url = self._url_for_ip(ip)
        backoff = self.cfg["INITIAL_BACKOFFS"]
        for attempt in range(1, self.cfg["MAX_RETRIES"] + 1):
            try:
                resp = self.session.get(url, headers=self.headers, timeout=self.cfg["REQ_TIMEOUT"])
                if resp.status_code == 404:
                    logging.warning(f"{ip} not found in GreyNoise.")
                    return {"ip": ip, "_status": "not_found"}
                if resp.status_code == 429:
                    logging.warning("Rate limited — backing off...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                logging.error(f"Error fetching {ip}: {e}")
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
            "internet_scanner_summary": None,
            "request_metadata": raw.get("request_metadata"),
            "raw": raw if "_status" not in raw else None, 
            "fetched_at": now_iso(),
            "ingested_at": now_iso(),
            "_source": {
                "endpoint": self._url_for_ip(ip),
                "base_url": self.cfg["GN_BASE_URL"]
            }
        }

        if "internet_scanner_intelligence" in raw:
            isc = raw["internet_scanner_intelligence"] or {}
            doc["internet_scanner_summary"] = {
                "seen": isc.get("seen"),
                "classification": isc.get("classification"),
                "first_seen": isc.get("first_seen"),
                "last_seen": isc.get("last_seen"),
                "actor": isc.get("actor"),
                "bot": isc.get("bot"),
                "vpn": isc.get("vpn"),
                "tags": isc.get("tags"),
            }

        return doc

    def load(self, doc: Dict) -> None:
        try:
            self.col.insert_one(doc)
            logging.info(f"Inserted the IP {doc['ip']}")
        except DuplicateKeyError:
            logging.info(f"Duplicate ignored for the IP {doc['ip']}")

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

            if raw.get("_status") == "not_found":
                summary.append({"ip": ip, "status": "Not Found"})
                continue

            doc = self.transform(ip, raw)
            if dry_run:
                logging.info(json.dumps(doc, indent=2))
                summary.append({"ip": ip, "status": "Dry-run"})
            else:
                self.load(doc)
                summary.append({"ip": ip, "status": "Inserted"})
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
    seen = set()
    out = []
    for ip in ips:
        if ip not in seen:
            seen.add(ip)
            out.append(ip)
    return out

if __name__ == "__main__":
    import argparse
    cfg = load_env_vars()

    parser = argparse.ArgumentParser(description="GreyNoise IP ETL -> MongoDB")
    parser.add_argument("--dry-run", action="store_true", help="print docs rather than inserting")
    parser.add_argument("--ips", nargs="*", help="override ips")
    args = parser.parse_args()

    if args.ips:
        ips = args.ips
    else:
        ips = parse_ips(cfg["TARGET_IPS"], cfg["INPUT_FILE"])
        if not ips:
            raise SystemExit("No IPs provided: set TARGET_IPS or INPUT_FILE")

    connector = GreyNoiseIPConnector(cfg)
    results = connector.run_batch(ips, dry_run=args.dry_run)
    logging.info(f"Run has been completed: {json.dumps(results, indent=2)}")
