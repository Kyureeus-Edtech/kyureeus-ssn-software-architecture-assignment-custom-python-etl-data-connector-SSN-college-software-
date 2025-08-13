import os
import sys
import re
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
from dotenv import load_dotenv


# -----------------------------
# Logging
# -----------------------------
def log(msg: str):
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] {msg}")


# -----------------------------
# HTTP client with retries
# -----------------------------
def build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": "SSN-ETL-Connector/1.0"})
    return s


# -----------------------------
# Provider Strategy Interface
# -----------------------------
class Provider:
    name: str

    def __init__(self, session: requests.Session):
        self.session = session

    def extract(self) -> Iterable[Dict]:
        """Yield raw records (dicts). Should handle pagination / errors."""
        raise NotImplementedError

    def transform(self, raw: Dict) -> Dict:
        """Return Mongo-ready document (must include `source_id`)."""
        raise NotImplementedError

    @property
    def unique_key(self) -> str:
        return "source_id"


# -----------------------------
# PROVIDER #1: CISA KEV (JSON, no auth)
# -----------------------------
class CisaKevProvider(Provider):
    name = "cisa_kev"

    def __init__(self, session: requests.Session):
        super().__init__(session)
        self.url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    def extract(self) -> Iterable[Dict]:
        log(f"[extract] GET {self.url}")
        r = self.session.get(self.url, timeout=60)
        if r.status_code != 200:
            log(f"Non-200: {r.status_code} {r.text[:200]}")
            return
        data = r.json() or {}
        for item in data.get("vulnerabilities", []):
            yield item

    def transform(self, raw: Dict) -> Dict:
        source_id = raw.get("cveID") or raw.get("vulnerabilityName")
        return {
            "source_id": source_id,
            "cve_id": raw.get("cveID"),
            "vuln_name": raw.get("vulnerabilityName"),
            "vendor": raw.get("vendorProject"),
            "product": raw.get("product"),
            "date_added": raw.get("dateAdded"),
            "short_description": raw.get("shortDescription"),
            "required_action": raw.get("requiredAction"),
            "due_date": raw.get("dueDate"),
            "notes": raw.get("notes"),
            "ingested_at": datetime.now(timezone.utc),
            "_raw": raw,
        }


# -----------------------------
# PROVIDER #2: Spamhaus DROP (TXT, no auth)
# -----------------------------
ASN_REGEX = re.compile(r"\bAS(\d+)\b", re.IGNORECASE)

class SpamhausDropProvider(Provider):
    name = "spamhaus_drop"

    def __init__(self, session: requests.Session):
        super().__init__(session)
        self.url = "https://www.spamhaus.org/drop/drop.txt"

    def extract(self) -> Iterable[Dict]:
        log(f"[extract] GET {self.url}")
        r = self.session.get(self.url, timeout=60)
        if r.status_code != 200:
            log(f"Non-200: {r.status_code} {r.text[:200]}")
            return
        for line in r.text.splitlines():
            line = line.strip()
            if not line or line.startswith(";"):  # comment or blank
                continue
            if ";" in line:
                prefix, comment = [p.strip() for p in line.split(";", 1)]
            else:
                prefix, comment = line, None
            yield {"prefix": prefix, "comment": comment}

    def transform(self, raw: Dict) -> Dict:
        prefix = raw.get("prefix")
        comment = raw.get("comment") or ""
        asn_match = ASN_REGEX.search(comment) if comment else None
        asn = f"AS{asn_match.group(1)}" if asn_match else None
        return {
            "source_id": prefix,  # unique per CIDR
            "prefix": prefix,
            "asn": asn,
            "comment": comment,
            "list": "DROP",
            "provider": "Spamhaus",
            "ingested_at": datetime.now(timezone.utc),
            "_raw": raw,
        }


# -----------------------------
# ETL Orchestrator
# -----------------------------
class ETLPipeline:
    def __init__(self, provider: Provider, mongo_uri: str, db_name: str, connector_name: str, dry_run: bool = False):
        self.provider = provider
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.connector_name = connector_name
        self.collection_name = f"{connector_name}_raw"
        self.dry_run = dry_run

        self.client: Optional[MongoClient] = None
        self.collection = None

    # ----- DB -----
    def _connect_mongo(self):
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=8000)
            self.client.server_info()  # force connection
        except PyMongoError as e:
            log(f"Mongo connection failed: {e}")
            raise

        db = self.client[self.db_name]
        self.collection = db[self.collection_name]
        # idempotency
        self.collection.create_index(self.provider.unique_key, unique=True)
        log(f"Connected to MongoDB → {self.db_name}.{self.collection_name}")

    # ----- Insights helpers -----
    def _print_samples(self, n: int = 3):
        docs = list(self.collection.find({}, {"_raw": 0}).limit(n))
        if not docs:
            log("No documents to sample.")
            return
        log(f"Sample {min(n, len(docs))} document(s):")
        for d in docs:
            print(d)

    def _insights_cisa(self):
        log("Insights (CISA KEV):")
        # Top vendors
        top_vendors = list(
            self.collection.aggregate([
                {"$group": {"_id": "$vendor", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ])
        )
        if top_vendors:
            log("Top 5 vendors by #vulns:")
            for v in top_vendors:
                print(f"  {v['_id'] or 'Unknown'}: {v['count']}")

        # Recent additions (last 30 days)
        try:
            thirty_days_ago = datetime.now(timezone.utc).replace(tzinfo=None)
            recent_count = self.collection.count_documents(
                {"date_added": {"$gte": (datetime.utcnow().date().isoformat())}}
            )
            log(f"Recent additions (today or later by date_added string): {recent_count}")
        except Exception:
            pass

        # Due date stats
        due_within = list(
            self.collection.aggregate([
                {"$match": {"due_date": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$due_date", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 3}
            ])
        )
        if due_within:
            log("Most common due_date values:")
            for d in due_within:
                print(f"  {d['_id']}: {d['count']}")

    def _insights_spamhaus(self):
        log("Insights (Spamhaus DROP):")
        total = self.collection.count_documents({})
        log(f"Total malicious prefixes: {total}")

        # Top ASNs (if parsed)
        top_asn = list(
            self.collection.aggregate([
                {"$match": {"asn": {"$ne": None}}},
                {"$group": {"_id": "$asn", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ])
        )
        if top_asn:
            log("Top ASNs by #blocked prefixes:")
            for a in top_asn:
                print(f"  {a['_id']}: {a['count']}")

        # Example prefixes
        log("Example 5 prefixes:")
        for d in self.collection.find({}, {"prefix": 1, "comment": 1, "_id": 0}).limit(5):
            print(f"  {d.get('prefix')} → {d.get('comment')}")

    # ----- Run -----
    def run(self) -> Tuple[int, int]:
        if not self.dry_run:
            self._connect_mongo()
        else:
            log("DRY RUN: MongoDB writes disabled.")

        to_upsert: List[UpdateOne] = []
        fetched = 0
        written = 0

        # Extract & Transform
        for raw in self.provider.extract():
            fetched += 1
            doc = self.provider.transform(raw)

            # Validation
            if not doc.get(self.provider.unique_key):
                log("Skipping record without unique key.")
                continue

            if not self.dry_run:
                to_upsert.append(
                    UpdateOne(
                        {self.provider.unique_key: doc[self.provider.unique_key]},
                        {"$set": doc},
                        upsert=True,
                    )
                )

            if not self.dry_run and len(to_upsert) >= 500:
                result = self.collection.bulk_write(to_upsert, ordered=False)
                written += (result.upserted_count or 0) + (result.modified_count or 0)
                log(f"Bulk upsert progress: {written}…")
                to_upsert.clear()

        # Flush remaining
        if not self.dry_run and to_upsert:
            result = self.collection.bulk_write(to_upsert, ordered=False)
            written += (result.upserted_count or 0) + (result.modified_count or 0)

        log(f"ETL finished. Fetched={fetched}, Upserted/Updated={written}")

        # Insights
        if not self.dry_run:
            self._print_samples(n=3)
            if self.provider.name == "cisa_kev":
                self._insights_cisa()
            elif self.provider.name == "spamhaus_drop":
                self._insights_spamhaus()

        return fetched, written


# -----------------------------
# Provider Factory
# -----------------------------
def build_provider(session: requests.Session, provider_name: str) -> Provider:
    name = provider_name.lower().strip()
    if name in ("cisa_kev", "cisa-kev", "kev"):
        return CisaKevProvider(session)
    if name in ("spamhaus_drop", "spamhaus-drop", "drop"):
        return SpamhausDropProvider(session)
    raise ValueError(f"Unknown provider: {provider_name}")


# -----------------------------
# Main
# -----------------------------
def main():
    load_dotenv()

    provider_name = os.getenv("PROVIDER")
    connector_name = os.getenv("CONNECTOR_NAME", provider_name)
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "ssn_arch")
    dry_run = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")

    if not provider_name:
        print("ERROR: PROVIDER not set in .env", file=sys.stderr)
        sys.exit(2)

    if not mongo_uri and not dry_run:
        print("ERROR: MONGO_URI missing and not in dry-run", file=sys.stderr)
        sys.exit(2)

    log(f"Starting ETL | provider={provider_name} | db={db_name} | collection={connector_name}_raw | dry_run={dry_run}")

    session = build_session()
    provider = build_provider(session, provider_name)

    pipeline = ETLPipeline(
        provider=provider,
        mongo_uri=mongo_uri or "",
        db_name=db_name,
        connector_name=connector_name,
        dry_run=dry_run,
    )
    pipeline.run()

    log("Done.")


if __name__ == "__main__":
    main()
