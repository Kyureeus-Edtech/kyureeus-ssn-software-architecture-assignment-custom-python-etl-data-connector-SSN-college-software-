from __future__ import annotations
import os
import sys
import time
import json
import logging
import datetime
import argparse
from typing import Optional, Dict, Any, List

# Ensure project root is on sys.path so sibling packages are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Try to import auth helpers (authreq may be in authentication_endpoint/authreq.py)
try:
    # Preferred package path
    from authentication_endpoint.authreq import AuthClient, request_with_auth, _get_mongo_collection
except Exception as exc:
    # Try fallback direct import (if files were copied flat)
    try:
        from authentication_endpoint.authreq import AuthClient, request_with_auth, _get_mongo_collection
    except Exception as exc2:
        raise RuntimeError(f"Failed to import auth helpers: {exc} / {exc2}")

# Logging
DEBUG_ENV = os.getenv("CZDS_DEBUG", "").lower() in ("1", "true", "yes")
logging.basicConfig(
    level=logging.DEBUG if DEBUG_ENV else logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(__name__)

# ----------------------------
# Configuration (env-driven)
# ----------------------------
CZDS_API_BASE = os.getenv("CZDS_API_BASE", "https://czds-api.icann.org").rstrip("/")
CZDS_REQUESTS_URL = os.getenv("CZDS_REQUESTS_URL", f"{CZDS_API_BASE}/czds/requests").rstrip("/")
LIST_TIMEOUT = int(os.getenv("CZDS_REQ_TIMEOUT_SECONDS", "20"))
MAX_RETRIES = int(os.getenv("CZDS_REQ_RETRIES", "3"))

REQS_RAW = os.getenv("MONGO_REQS_RAW", "czds_requests_raw")
REQS_LATEST = os.getenv("MONGO_REQS_LATEST", "czds_requests_latest")
REQS_HISTORY = os.getenv("MONGO_REQS_HISTORY", "czds_requests_history")

# ----------------------------
# Small utilities
# ----------------------------
def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def _backoff(attempt: int, base: float = 0.5, factor: float = 2.0, cap: float = 10.0) -> float:
    delay = min(base * (factor ** (attempt - 1)), cap)
    rand = os.urandom(1)[0] / 255.0
    jitter = 0.5 + rand / 2.0
    return delay * jitter

def _get_db_from_col(col):
    if col is None:
        return None
    try:
        return col.database
    except Exception:
        return None

# ----------------------------
# Mongo helpers (safe no-op when not configured)
# ----------------------------
def _log_request_raw(payload: Dict[str, Any]) -> None:
    """
    Inserts raw payload / raw response debug info into the raw collection.
    Safe no-op if no Mongo configured.
    """
    col = _get_mongo_collection()
    if col is None:
        if DEBUG_ENV:
            logger.debug("Mongo not configured, skipping raw log.")
        return
    db = _get_db_from_col(col)
    if db is None:
        if DEBUG_ENV:
            logger.debug("Mongo collection has no .database, skipping raw log.")
        return
    try:
        db[REQS_RAW].insert_one({"ingested_at": now_utc(), **payload})
    except Exception as e:
        logger.warning("Failed to write czds_requests_raw: %s", e)

def _upsert_latest(normalized: Dict[str, Any]) -> None:
    col = _get_mongo_collection()
    if col is None:
        return
    db = _get_db_from_col(col)
    if db is None:
        return
    try:
        q = {"request_id": normalized["request_id"]}
        update = {"$set": {**normalized, "last_checked": now_utc()}}
        db[REQS_LATEST].update_one(q, update, upsert=True)
    except Exception as e:
        logger.warning("Failed to upsert czds_requests_latest: %s", e)

def _append_history(event: Dict[str, Any]) -> None:
    col = _get_mongo_collection()
    if col is None:
        return
    db = _get_db_from_col(col)
    if db is None:
        return
    try:
        db[REQS_HISTORY].insert_one({"ingested_at": now_utc(), **event})
    except Exception as e:
        logger.warning("Failed to write czds_requests_history: %s", e)

# ----------------------------
# Normalization helpers
# ----------------------------
def _parse_dt(value) -> Optional[datetime.datetime]:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            pass
    try:
        return datetime.datetime.fromtimestamp(float(value), datetime.timezone.utc)
    except Exception:
        return None

def _normalize_request(raw: Dict[str, Any]) -> Dict[str, Any]:
    request_id = raw.get("id") or raw.get("requestId") or raw.get("request_id")
    tld = raw.get("tld") or raw.get("zone") or raw.get("zoneName")
    status = raw.get("status") or raw.get("state")
    requested_at = _parse_dt(raw.get("requestedAt") or raw.get("requested_at") or raw.get("requestDate"))
    approved_at = _parse_dt(raw.get("approvedAt") or raw.get("approved_at") or raw.get("approvalDate"))
    expiry_date = _parse_dt(raw.get("expiryDate") or raw.get("expiresAt") or raw.get("expiry"))
    return {
        "request_id": request_id,
        "tld": tld,
        "status": status,
        "requested_at": requested_at,
        "approved_at": approved_at,
        "expiry_date": expiry_date,
        "raw": raw,
        "source": "czds_requests"
    }

# ----------------------------
# RequestsClient implementation
# ----------------------------
class RequestsClient:
    def __init__(self, auth_client: Optional[AuthClient] = None):
        self.auth = auth_client or AuthClient()
        self.requests_url = os.getenv("CZDS_REQUESTS_URL", f"{CZDS_API_BASE}/czds/requests").rstrip("/")

    def list_requests(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        url = self.requests_url
        params = {"limit": limit, "offset": offset}
        attempt = 0
        last_exc = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                if DEBUG_ENV:
                    logger.debug("list_requests calling %s params=%s", url, params)
                resp = request_with_auth(self.auth, "GET", url, params=params, timeout=LIST_TIMEOUT)
                # handle non-2xx
                try:
                    resp.raise_for_status()
                except Exception:
                    logger.warning("list_requests received non-2xx: %s", resp.status_code)
                # tolerate empty body
                text = resp.text or ""
                if not text.strip():
                    # no body; return empty list (or treat as empty)
                    if DEBUG_ENV:
                        logger.debug("list_requests returned empty body")
                    return []
                data = None
                try:
                    data = resp.json()
                except Exception as je:
                    logger.warning("list_requests response not JSON: %s", je)
                    # log raw
                    try:
                        _log_request_raw({"response_status": resp.status_code, "response_text_preview": text[:2000], "source": "czds_requests_raw"})
                    except Exception:
                        pass
                    return []
                items = data.get("requests") if isinstance(data, dict) and "requests" in data else data
                if items is None:
                    items = []
                # process items
                for raw in items:
                    try:
                        _log_request_raw({"raw": raw, "source": "czds_requests_raw"})
                        norm = _normalize_request(raw)
                        if norm.get("request_id"):
                            _upsert_latest(norm)
                    except Exception:
                        logger.debug("Failed to process item", exc_info=True)
                return items
            except Exception as ex:
                last_exc = ex
                delay = _backoff(attempt)
                logger.warning("list_requests attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)
        raise RuntimeError(f"list_requests failed after {MAX_RETRIES} attempts: {last_exc}")

    def get_request(self, request_id: str) -> Dict[str, Any]:
        url = f"{self.requests_url}/{request_id}"
        attempt = 0
        last_exc = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                if DEBUG_ENV:
                    logger.debug("get_request calling %s", url)
                resp = request_with_auth(self.auth, "GET", url, timeout=LIST_TIMEOUT)
                resp.raise_for_status()
                text = resp.text or ""
                if not text.strip():
                    # empty body but 2xx: return structured
                    return {"status_code": resp.status_code, "message": "empty body", "source": "czds_requests_raw"}
                try:
                    data = resp.json()
                except Exception:
                    logger.warning("get_request response not JSON")
                    _log_request_raw({"response_status": resp.status_code, "response_text_preview": text[:2000], "source": "czds_requests_raw"})
                    raise
                _log_request_raw({"raw": data, "source": "czds_requests_raw"})
                norm = _normalize_request(data)
                if norm.get("request_id"):
                    _upsert_latest(norm)
                return data
            except Exception as ex:
                last_exc = ex
                delay = _backoff(attempt)
                logger.warning("get_request attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)
        raise RuntimeError(f"get_request failed after {MAX_RETRIES} attempts: {last_exc}")

    def create_request(self, tld: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new request for a TLD and handle empty/non-JSON responses robustly.
        This version ensures we call _log_request_raw() exactly once for the successful
        or fallback result (so tests that monkeypatch _log_request_raw see one write).
        """
        url = self.requests_url
        body = {"tld": tld}
        if comment:
            body["comment"] = comment

        attempt = 0
        last_exc = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                if DEBUG_ENV:
                    logger.debug("create_request POST %s body=%s", url, body)
                resp = request_with_auth(self.auth, "POST", url, json=body, timeout=LIST_TIMEOUT)
                status = resp.status_code
                text = resp.text or ""
                headers = {k.lower(): v for k, v in resp.headers.items()}

                # NOTE: do not call _log_request_raw() here (attempt) to avoid double-logging.
                # Instead, we'll call _log_request_raw exactly once below with final data/fallback.

                # If body exists, prefer JSON parse
                if text.strip():
                    try:
                        data = resp.json()
                    except Exception:
                        logger.warning("create_request: non-JSON body returned (status %s). Returning fallback.", status)
                        fallback = {"status_code": status, "raw_text": text, "response_headers": headers, "source": "czds_requests_raw"}
                        # Log the fallback once
                        try:
                            _log_request_raw(fallback)
                        except Exception:
                            logger.debug("Failed to write fallback to raw collection", exc_info=True)
                        try:
                            _append_history({"request_id": None, "event": "created_non_json", "payload": {"status": status, "preview": text[:200]}, "status": None, "source": "czds_requests"})
                        except Exception:
                            logger.debug("Failed to append history for non-json response", exc_info=True)
                        return fallback

                    # JSON parsed successfully: log parsed JSON once and return
                    try:
                        _log_request_raw({"raw": data, "source": "czds_requests_raw"})
                    except Exception:
                        logger.debug("Failed to write parsed JSON to raw collection", exc_info=True)
                    norm = _normalize_request(data)
                    if norm.get("request_id"):
                        _upsert_latest(norm)
                        _append_history({"request_id": norm["request_id"], "event": "created", "payload": data, "status": norm.get("status"), "source": "czds_requests"})
                    return data

                # Empty body: 2xx treat specially
                if 200 <= status < 300:
                    # 1) Follow Location header if present
                    location = headers.get("location")
                    if location:
                        logger.info("create_request: following Location header: %s", location)
                        try:
                            follow_url = location if location.startswith("http") else (self.requests_url.rstrip("/") + location)
                            follow_resp = request_with_auth(self.auth, "GET", follow_url, timeout=LIST_TIMEOUT)
                            follow_resp.raise_for_status()
                            follow_text = follow_resp.text or ""
                            try:
                                follow_data = follow_resp.json()
                            except Exception:
                                fallback = {"status_code": follow_resp.status_code, "raw_text": follow_text, "source": "czds_requests_raw"}
                                try:
                                    _log_request_raw(fallback)
                                except Exception:
                                    logger.debug("Failed to write follow fallback", exc_info=True)
                                return fallback
                            try:
                                _log_request_raw({"raw": follow_data, "source": "czds_requests_raw"})
                            except Exception:
                                logger.debug("Failed to write followed JSON to raw collection", exc_info=True)
                            norm = _normalize_request(follow_data)
                            if norm.get("request_id"):
                                _upsert_latest(norm)
                                _append_history({"request_id": norm["request_id"], "event": "created_followed", "payload": follow_data, "status": norm.get("status"), "source": "czds_requests"})
                            return follow_data
                        except Exception as e:
                            logger.debug("Following Location failed: %s", e)

                    # 2) Check common header IDs for direct GET
                    for hdr in ("x-request-id", "x-requestid", "x-resource-id"):
                        if hdr in headers:
                            rid = headers[hdr]
                            logger.info("create_request: found header %s -> %s; attempting get_request", hdr, rid)
                            try:
                                data = self.get_request(rid)
                                return data
                            except Exception:
                                logger.debug("get_request by header id failed for %s", rid)

                    # 3) Fallback: search recent list for a matching TLD created recently
                    try:
                        recent = self.list_requests(limit=200, offset=0)
                        now = datetime.datetime.now(datetime.timezone.utc)
                        for item in recent:
                            norm = _normalize_request(item)
                            if norm.get("tld") and norm.get("tld").lower() == tld.lower():
                                requested_at = norm.get("requested_at")
                                if requested_at is None:
                                    # log & return
                                    try:
                                        _log_request_raw({"raw": item, "source": "czds_requests_raw"})
                                    except Exception:
                                        logger.debug("Failed to write inferred raw item", exc_info=True)
                                    _upsert_latest(norm)
                                    _append_history({"request_id": norm.get("request_id"), "event": "created_inferred", "payload": item, "status": norm.get("status"), "source": "czds_requests"})
                                    return item
                                delta = now - requested_at if isinstance(requested_at, datetime.datetime) else None
                                if delta is not None and delta.total_seconds() < 300:
                                    try:
                                        _log_request_raw({"raw": item, "source": "czds_requests_raw"})
                                    except Exception:
                                        logger.debug("Failed to write inferred recent raw item", exc_info=True)
                                    _upsert_latest(norm)
                                    _append_history({"request_id": norm.get("request_id"), "event": "created_inferred_recent", "payload": item, "status": norm.get("status"), "source": "czds_requests"})
                                    return item
                    except Exception:
                        logger.debug("Fallback list-based inference failed", exc_info=True)

                    # 4) Nothing found: return structured success-without-body and log it once
                    fallback = {"status_code": status, "message": "empty body (no JSON)", "source": "czds_requests_raw"}
                    try:
                        _log_request_raw(fallback)
                    except Exception:
                        logger.debug("Failed to write empty-body fallback", exc_info=True)
                    return fallback

                # non-2xx and empty body -> error & retry
                raise ValueError(f"Non-JSON empty response with status {status}")

            except Exception as ex:
                last_exc = ex
                delay = _backoff(attempt)
                logger.warning("create_request attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)

        # exhausted retries
        raise RuntimeError(f"create_request failed after {MAX_RETRIES} attempts: {last_exc}")

# ----------------------------
# CLI for quick manual testing
# ----------------------------
# --- add this helper after RequestsClient class ---

def _find_recent_created(client: RequestsClient, tld: str, lookback_seconds: int = 300):
    """
    Search recent list_requests() for an item with matching tld created within lookback_seconds.
    Returns the matching item or None.
    """
    try:
        recent = client.list_requests(limit=200, offset=0)
    except Exception:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    for item in recent:
        norm = _normalize_request(item)
        if not norm.get("tld"):
            continue
        if norm["tld"].lower() != tld.lower():
            continue
        req_at = norm.get("requested_at")
        if req_at is None:
            # no timestamp: treat as candidate
            return item
        delta = now - req_at
        if delta.total_seconds() <= lookback_seconds:
            return item
    return None

# Update CLI parser to include wait options
def _cli_args():
    p = argparse.ArgumentParser(description="CZDS Requests client (list/create/get)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub_list = sub.add_parser("list", help="List requests")
    sub_list.add_argument("--limit", type=int, default=100)
    sub_list.add_argument("--offset", type=int, default=0)

    sub_create = sub.add_parser("create", help="Create a request for a TLD")
    sub_create.add_argument("tld", type=str, help="TLD name (e.g., com)")
    sub_create.add_argument("--comment", type=str, default=None)
    sub_create.add_argument("--wait", action="store_true", help="Poll list_requests() until the created request appears")
    sub_create.add_argument("--wait-seconds", type=int, default=120, help="Total seconds to wait when --wait is used")
    sub_create.add_argument("--poll-interval", type=int, default=5, help="Seconds between polls")

    sub_get = sub.add_parser("get", help="Get a single request by id")
    sub_get.add_argument("request_id", type=str, help="Request ID")

    return p.parse_args()

def _print_json(obj):
    print(json.dumps(obj, default=str, indent=2))

if __name__ == "__main__":
    args = _cli_args()
    client = RequestsClient()
    if args.cmd == "list":
        items = client.list_requests(limit=args.limit, offset=args.offset)
        _print_json(items)
    elif args.cmd == "create":
        res = client.create_request(args.tld, comment=args.comment)
        _print_json(res)
        # If user asked to wait, poll until we find a matching request
        if getattr(args, "wait", False):
            import time
            deadline = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=args.wait_seconds)
            found = None
            while datetime.datetime.now(datetime.timezone.utc) < deadline:
                found = _find_recent_created(client, args.tld, lookback_seconds=args.wait_seconds + 60)
                if found:
                    print("\nCreated request discovered via list_requests():")
                    _print_json(found)
                    break
                time.sleep(args.poll_interval)
            if not found:
                print(f"\nTimed out after {args.wait_seconds} seconds waiting for created request to appear.")
    elif args.cmd == "get":
        res = client.get_request(args.request_id)
        _print_json(res)