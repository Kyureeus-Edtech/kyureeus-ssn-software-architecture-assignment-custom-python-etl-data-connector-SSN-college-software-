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

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")  # Optional — NVD allows API key for higher rate limits

RESULTS_PER_PAGE = int(os.getenv("RESULTS_PER_PAGE", "10"))
START_INDEX = int(os.getenv("START_INDEX", "0"))

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
            headers["apiKey"] = API_KEY
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

class NvdCveConnector(BaseConnector):
    name = "nvd_cve_2_0"

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type(ExtractError),
    )
    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = self.session.get(API_BASE_URL, headers=self.auth_headers(), params=params, timeout=20)
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
        params = {
            "resultsPerPage": RESULTS_PER_PAGE,
            "startIndex": START_INDEX
        }
        payload = self._get(params)
        if "vulnerabilities" not in payload:
            raise ExtractError("No vulnerabilities field in response")

        for item in payload["vulnerabilities"]:
            cve_data = item.get("cve", {})
            yield {
                "id": cve_data.get("id"),
                "sourceIdentifier": cve_data.get("sourceIdentifier"),
                "published": cve_data.get("published"),
                "lastModified": cve_data.get("lastModified"),
                "descriptions": cve_data.get("descriptions", []),
                "metrics": cve_data.get("metrics", {}),
                "weaknesses": cve_data.get("weaknesses", []),
                "configurations": cve_data.get("configurations", []),
                "references": cve_data.get("references", []),
            }

def get_mongo_collection() -> Collection:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    return db[MONGODB_COLLECTION]

def run() -> None:
    coll = get_mongo_collection()
    connector = NvdCveConnector()
    raw_docs = connector.extract()
    docs = (connector.with_metadata(connector.transform(r)) for r in raw_docs)
    connector.load(coll, docs)

if __name__ == "__main__":
    run()