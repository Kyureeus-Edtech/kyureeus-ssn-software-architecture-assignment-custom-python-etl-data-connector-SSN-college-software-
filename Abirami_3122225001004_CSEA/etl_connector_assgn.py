import hashlib
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables from .env
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

# Correct GreyNoise API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.greynoise.io/v3/community")
API_KEY = os.getenv("API_KEY")

# IPs to look up
TARGET_IPS = os.getenv("TARGET_IPS", "8.8.8.8,1.1.1.1").split(",")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sanitize_for_mongo(doc: Dict[str, Any]) -> Dict[str, Any]:
    def _sanitize_key(k: str) -> str:
        k = k.replace(".", "_")
        if k.startswith("$"):
            k = "_" + k[1:]
        return k

    def _sanitize(value: Any) -> Any:
        if isinstance(value, dict):
            return {_sanitize_key(k): _sanitize(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_sanitize(v) for v in value]
        else:
            return value

    return _sanitize(doc)


class ExtractError(Exception):
    pass


class BaseConnector:
    name: str = "base"

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()

    def auth_headers(self) -> Dict[str, str]:
        headers = {}
        if API_KEY:
            headers["key"] = API_KEY  # Correct GreyNoise auth header
        return headers

    def extract(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return sanitize_for_mongo(record)

    def with_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        doc["_metadata"] = {
            "ingested_at": utc_now_iso(),
            "source": self.name,
        }
        doc["hash_key"] = stable_hash(doc)
        return doc

    def load(self, coll: Collection, docs: Iterable[Dict[str, Any]]) -> None:
        ops = []
        for d in docs:
            key = d.get("hash_key") or stable_hash(d)
            ops.append(UpdateOne({"hash_key": key}, {"$set": d}, upsert=True))
        if ops:
            result = coll.bulk_write(ops, ordered=False)
            print(f"[LOAD] upserted={result.upserted_count}, modified={result.modified_count}, matched={result.matched_count}")
        else:
            print("[LOAD] nothing to write.")


class GreyNoiseConnector(BaseConnector):
    name = "GreyNoise_IP_Lookup"

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type(ExtractError),
    )
    def _get_ip_info(self, ip: str) -> Dict[str, Any]:
        try:
            url = f"{API_BASE_URL}/{ip.strip()}"
            resp = self.session.get(url, headers=self.auth_headers(), timeout=20)
        except requests.RequestException as e:
            raise ExtractError(f"Network error: {e}") from e

        if resp.status_code == 429:
            reset_after = int(resp.headers.get("Retry-After", "2"))
            print(f"[RATE LIMIT] Sleeping {reset_after}s...")
            time.sleep(reset_after)
            raise ExtractError("Rate limited")

        if not resp.ok:
            raise ExtractError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            return resp.json()
        except ValueError as e:
            raise ExtractError("Invalid JSON response") from e

    def extract(self) -> Iterable[Dict[str, Any]]:
        for ip in TARGET_IPS:
            data = self._get_ip_info(ip)
            yield {
                "ip": data.get("ip"),
                "noise": data.get("noise"),
                "riot": data.get("riot"),
                "classification": data.get("classification"),
                "name": data.get("name"),
                "last_seen": data.get("last_seen"),
                "actor": data.get("actor"),
                "metadata": data.get("metadata", {}),
                "tags": data.get("tags", []),
                "raw_response": data,  # store full JSON for reference
            }


def get_mongo_collection() -> Collection:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    return db[MONGODB_COLLECTION]


def run() -> None:
    coll = get_mongo_collection()
    connector = GreyNoiseConnector()
    raw_docs = connector.extract()
    docs = (connector.with_metadata(connector.transform(r)) for r in raw_docs)
    connector.load(coll, docs)


if __name__ == "__main__":
    run()
