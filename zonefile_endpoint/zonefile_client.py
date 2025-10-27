from __future__ import annotations
import os
import sys
import time
import json
import logging
import argparse
import hashlib
import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# ensure project root on sys.path so sibling packages are importable when run in-folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# import auth helpers (try package then fallback)
try:
    from authentication_endpoint.authreq import AuthClient, request_with_auth, _get_mongo_collection
except Exception:
    try:
        from authreq import AuthClient, request_with_auth, _get_mongo_collection
    except Exception as e:
        raise RuntimeError("Could not import AuthClient/request_with_auth from authreq.py: %s" % e)

# logging config
DEBUG_ENV = os.getenv("CZDS_DEBUG", "").lower() in ("1", "true", "yes")
logging.basicConfig(level=logging.DEBUG if DEBUG_ENV else logging.INFO, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# config from env
CZDS_API_BASE = os.getenv("CZDS_API_BASE", "https://czds-api.icann.org").rstrip("/")
CZDS_ZONEFILES_URL = os.getenv("CZDS_ZONEFILES_URL", f"{CZDS_API_BASE}/czds/downloads").rstrip("/")
LIST_TIMEOUT = int(os.getenv("CZDS_ZONE_TIMEOUT_SECONDS", "30"))
MAX_RETRIES = int(os.getenv("CZDS_ZONE_RETRIES", "3"))

# mongo collections
ZONE_RAW = os.getenv("MONGO_ZONEFILES_RAW", "czds_zonefiles_raw")
ZONE_LATEST = os.getenv("MONGO_ZONEFILES_LATEST", "czds_zonefiles_latest")
ZONE_HISTORY = os.getenv("MONGO_ZONEFILES_HISTORY", "czds_zonefiles_history")

def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def _backoff(attempt: int, base: float = 0.5, factor: float = 2.0, cap: float = 10.0) -> float:
    delay = min(base * (factor ** (attempt - 1)), cap)
    try:
        rand = os.urandom(1)[0] / 255.0
    except Exception:
        rand = 0.5
    jitter = 0.5 + rand / 2.0
    return delay * jitter

def _get_db_from_col(col):
    if col is None:
        return None
    try:
        return col.database
    except Exception:
        return None

# -------------------------
# Mongo logging helpers
# -------------------------
def _log_zone_raw(payload: Dict[str, Any]) -> None:
    col = _get_mongo_collection()
    if col is None:
        if DEBUG_ENV:
            logger.debug("Mongo not configured: skipping raw zone log")
        return
    db = _get_db_from_col(col)
    if db is None:
        return
    try:
        db[ZONE_RAW].insert_one({"ingested_at": now_utc(), **payload})
    except Exception as e:
        logger.warning("Failed to write czds_zonefiles_raw: %s", e)

def _upsert_zone_latest(normalized: Dict[str, Any]) -> None:
    col = _get_mongo_collection()
    if col is None:
        return
    db = _get_db_from_col(col)
    if db is None:
        return
    try:
        q = {"tld": normalized["tld"]}
        update = {"$set": {**normalized, "last_checked": now_utc()}}
        db[ZONE_LATEST].update_one(q, update, upsert=True)
    except Exception as e:
        logger.warning("Failed to upsert czds_zonefiles_latest: %s", e)

def _append_zone_history(event: Dict[str, Any]) -> None:
    col = _get_mongo_collection()
    if col is None:
        return
    db = _get_db_from_col(col)
    if db is None:
        return
    try:
        db[ZONE_HISTORY].insert_one({"ingested_at": now_utc(), **event})
    except Exception as e:
        logger.warning("Failed to write czds_zonefiles_history: %s", e)

# -------------------------
# Core client
# -------------------------
class ZonefileClient:
    def __init__(self, auth_client: Optional[AuthClient] = None):
        self.auth = auth_client or AuthClient()
        self.base = CZDS_ZONEFILES_URL

    def list_zonefiles(self) -> List[Dict[str, Any]]:
        """
        GET the list of available zone files. Returns parsed JSON list.
        """
        url = self.base
        attempt = 0
        last_exc = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                if DEBUG_ENV:
                    logger.debug("GET %s", url)
                resp = request_with_auth(self.auth, "GET", url, timeout=LIST_TIMEOUT)
                try:
                    resp.raise_for_status()
                except Exception:
                    logger.warning("list_zonefiles received non-2xx: %s", resp.status_code)
                text = resp.text or ""
                if not text.strip():
                    return []
                data = resp.json()
                items = data.get("downloads") if isinstance(data, dict) and "downloads" in data else data
                if items is None:
                    items = []
                # log each entry raw + upsert normalized
                for raw in items:
                    try:
                        _log_zone_raw({"raw": raw, "source": "czds_zonefiles_raw"})
                        norm = _normalize_zone_meta(raw)
                        if norm.get("tld"):
                            _upsert_zone_latest(norm)
                    except Exception:
                        logger.debug("Failed to process one zone meta", exc_info=True)
                return items
            except Exception as ex:
                last_exc = ex
                delay = _backoff(attempt)
                logger.warning("list_zonefiles attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)
        raise RuntimeError(f"list_zonefiles failed after {MAX_RETRIES} attempts: {last_exc}")

    def download_zonefile(self, tld: str, dest_dir: str, chunk_size: int = 64 * 1024) -> Path:
        """
        Downloads the compressed zone file for `tld` as a .txt.gz into dest_dir.
        Returns Path to saved file.
        """
        os.makedirs(dest_dir, exist_ok=True)
        filename = f"{tld}.txt.gz"
        path = Path(dest_dir) / filename
        url = f"{self.base}/{tld}"
        attempt = 0
        last_exc = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                if DEBUG_ENV:
                    logger.debug("Downloading %s -> %s", url, path)
                resp = request_with_auth(self.auth, "GET", url, timeout=LIST_TIMEOUT, stream=True)
                try:
                    resp.raise_for_status()
                except Exception:
                    logger.warning("download_zonefile non-2xx: %s", resp.status_code)
                # stream write
                with open(path, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if chunk:
                            fh.write(chunk)
                # compute checksum and size
                file_size = path.stat().st_size
                checksum = _compute_sha256(path)
                meta = {
                    "tld": tld,
                    "file_path": str(path.resolve()),
                    "file_size": file_size,
                    "sha256": checksum,
                    "http_status": resp.status_code,
                    "source": "czds_zonefiles"
                }
                # log into mongo
                try:
                    _log_zone_raw({"download_meta": meta})
                except Exception:
                    logger.debug("Failed to log download raw")
                try:
                    _upsert_zone_latest({"tld": tld, "last_downloaded": now_utc(), "file_path": str(path.resolve()), "sha256": checksum, "file_size": file_size})
                except Exception:
                    logger.debug("Failed to upsert latest zone file")
                try:
                    _append_zone_history({"tld": tld, "event": "downloaded", "payload": meta, "status": "success"})
                except Exception:
                    logger.debug("Failed to append zone history")
                return path
            except Exception as ex:
                last_exc = ex
                delay = _backoff(attempt)
                logger.warning("download_zonefile attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)
        raise RuntimeError(f"download_zonefile failed after {MAX_RETRIES} attempts: {last_exc}")

    def get_zonefile_metadata(self, tld: str) -> Dict[str, Any]:
        """Optional: GET metadata for a single zonefile resource (if API supports)."""
        url = f"{self.base}/{tld}/meta"
        resp = request_with_auth(self.auth, "GET", url, timeout=LIST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        _log_zone_raw({"meta": data})
        return data

# -------------------------
# Helpers
# -------------------------
def _normalize_zone_meta(raw: Dict[str, Any]) -> Dict[str, Any]:
    # Expected keys vary; attempt to normalize
    return {
        "tld": raw.get("tld") or raw.get("zone") or raw.get("name"),
        "size": raw.get("size") or raw.get("fileSize"),
        "last_modified": raw.get("lastModified") or raw.get("updatedAt"),
        "raw": raw,
        "source": "czds_zonefiles"
    }

def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_checksum(path: str, expected_hex: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute SHA256 for path and optionally compare to expected_hex.
    Returns dict with sha256 and match boolean (if expected provided).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    sha = _compute_sha256(p)
    res = {"path": str(p.resolve()), "sha256": sha}
    if expected_hex:
        res["match"] = (sha.lower() == expected_hex.lower())
    return res

# -------------------------
# CLI
# -------------------------
def _cli_args():
    p = argparse.ArgumentParser(description="CZDS Zonefile client (list/download/verify)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub_list = sub.add_parser("list", help="List available zone files")
    sub_list.add_argument("--limit", type=int, default=200)

    sub_download = sub.add_parser("download", help="Download a zone file for a TLD")
    sub_download.add_argument("tld", type=str, help="TLD to download (e.g., com)")
    sub_download.add_argument("--dest", type=str, default="./downloads", help="Destination directory")

    sub_verify = sub.add_parser("verify", help="Verify a downloaded file checksum")
    sub_verify.add_argument("path", type=str, help="Local file path")
    sub_verify.add_argument("--sha256", type=str, default=None, help="Expected sha256 hex")

    return p.parse_args()

def _print_json(obj):
    print(json.dumps(obj, default=str, indent=2))

if __name__ == "__main__":
    args = _cli_args()
    client = ZonefileClient()
    if args.cmd == "list":
        items = client.list_zonefiles()
        _print_json(items)
    elif args.cmd == "download":
        p = client.download_zonefile(args.tld, args.dest)
        print("Saved to:", p)
    elif args.cmd == "verify":
        out = verify_checksum(args.path, expected_hex=args.sha256)
        _print_json(out)
