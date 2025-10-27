import os, sys
import time
import json
import threading
import logging
import datetime
from typing import Optional
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

# load .env if present
load_dotenv()

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ----------------------------
# Environment / Configuration
# ----------------------------
def get_env(key, default=None, required=False):
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val

AUTH_URL = get_env("CZDS_AUTH_URL", required=True)
USERNAME = get_env("CZDS_USERNAME", required=True)
PASSWORD = get_env("CZDS_PASSWORD", required=True)
AUTH_TIMEOUT = int(get_env("CZDS_AUTH_TIMEOUT_SECONDS", 15))
AUTH_RETRIES = int(get_env("CZDS_AUTH_RETRIES", 3))
TOKEN_CACHE_PATH = get_env("CZDS_TOKEN_CACHE_PATH", None)  # optional

# Mongo (optional; if unset, logging is skipped)
MONGO_URI = get_env("MONGO_URI", None)
MONGO_DB = get_env("MONGO_DB", None)
MONGO_COLLECTION = get_env("MONGO_AUTH_COLLECTION", "czds_auth")  # collection name

# lazy Mongo client / collection cache
__mongo_client = None
__mongo_col = None

def _get_mongo_collection():
    """
    Returns a cached MongoDB collection handle or None if env not configured
    or if connection fails.
    """
    global __mongo_client, __mongo_col
    if (MONGO_URI is None) or (MONGO_DB is None):
        return None
    if __mongo_col is not None:
        return __mongo_col
    try:
        from pymongo import MongoClient
        __mongo_client = MongoClient(MONGO_URI)
        __mongo_col = __mongo_client[MONGO_DB][MONGO_COLLECTION]
        return __mongo_col
    except Exception as e:
        logger.warning("MongoDB not available (%s). Auth events will not be logged.", e)
        return None

def _log_auth_event(data: dict):
    """
    Inserts an auth audit event into MongoDB (if configured).
    Always appends a UTC timestamp; never logs raw tokens or passwords.
    """
    col = _get_mongo_collection()
    # Explicit None check avoids Collection truth-testing
    if col is None:
        return
    try:
        record = {
            "ingested_at": datetime.datetime.now(datetime.timezone.utc),
            **data
        }
        col.insert_one(record)
    except Exception as e:
        logger.warning("Failed to write auth audit event to MongoDB: %s", e)

# ----------------------------
# Backoff helper
# ----------------------------
def backoff(attempt, base=0.5, factor=2.0, max_delay=10.0):
    delay = min(base * (factor ** (attempt - 1)), max_delay)
    rand_byte = os.urandom(1)[0]
    jitter = 0.5 + (rand_byte / 255.0) / 2.0
    return delay * jitter

# ----------------------------
# Auth
# ----------------------------
class AuthError(Exception):
    pass

class AuthClient:
    """
    Thread-safe token manager with optional MongoDB audit logging.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None
        # optionally load cached token from disk
        if TOKEN_CACHE_PATH:
            try:
                self._load_cache()
            except Exception as e:
                logger.debug("No usable token cache: %s", e)

    def _load_cache(self):
        with open(TOKEN_CACHE_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        token = data.get("token")
        expires_at = data.get("expires_at")
        if token and expires_at and expires_at > time.time() + 10:
            self._token = token
            self._expires_at = expires_at

    def _save_cache(self):
        if not TOKEN_CACHE_PATH:
            return
        with open(TOKEN_CACHE_PATH + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"token": self._token, "expires_at": self._expires_at}, fh)
        os.replace(TOKEN_CACHE_PATH + ".tmp", TOKEN_CACHE_PATH)

    def _authenticate(self):
        payload = {"username": USERNAME, "password": PASSWORD}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        last_exc = None
        for attempt in range(1, AUTH_RETRIES + 1):
            try:
                r = requests.post(AUTH_URL, json=payload, headers=headers, timeout=AUTH_TIMEOUT)
                if r.status_code in (401, 403):
                    # credential rejection: don't retry further
                    _log_auth_event({
                        "username": USERNAME,
                        "status": "failure",
                        "http_status": r.status_code,
                        "reason": "credentials_rejected",
                        "source": "czds_auth"
                    })
                    raise AuthError(f"Credentials rejected (status {r.status_code})")
                r.raise_for_status()
                # parse response defensively
                try:
                    data = r.json()
                except ValueError:
                    _log_auth_event({
                        "username": USERNAME,
                        "status": "failure",
                        "http_status": r.status_code,
                        "reason": "invalid_json",
                        "source": "czds_auth"
                    })
                    raise AuthError(f"Auth response not valid JSON: {r.text[:200]}")
                token = data.get("accessToken") or data.get("token") or data.get("access_token")
                expires_in = data.get("expiresIn") or data.get("expires") or data.get("expires_in")
                if not token:
                    _log_auth_event({
                        "username": USERNAME,
                        "status": "failure",
                        "http_status": r.status_code,
                        "reason": "missing_token_field",
                        "raw_keys": list(data.keys()),
                        "source": "czds_auth"
                    })
                    raise AuthError(f"Auth response missing token field: {data}")
                # compute expiry (timezone-aware)
                exp = time.time() + (int(expires_in) if expires_in else 3600)
                # set token
                self._token = token
                self._expires_at = exp
                # cache persist
                try:
                    self._save_cache()
                except Exception as e:
                    logger.debug("Could not persist token cache: %s", e)
                logger.info("Authenticated successfully; token valid until %s", time.ctime(exp))
                # audit success (never store raw token)
                _log_auth_event({
                    "username": USERNAME,
                    "status": "success",
                    "http_status": r.status_code,
                    "token_length": len(self._token),
                    "expires_at": datetime.datetime.fromtimestamp(self._expires_at, datetime.timezone.utc),
                    "source": "czds_auth"
                })
                return
            except AuthError:
                # handled / audited above
                raise
            except Exception as ex:
                # Catch transient errors (including those raised by the responses test lib).
                # AuthError is handled above and should not be caught here.
                last_exc = ex
                delay = backoff(attempt)
                logger.warning("Auth attempt %d failed: %s — retrying in %.2f sec", attempt, ex, delay)
                time.sleep(delay)

        # if we reach here, auth failed after retries
        _log_auth_event({
            "username": USERNAME,
            "status": "failure",
            "http_status": getattr(last_exc, "response", None).status_code if getattr(last_exc, "response", None) else None,
            "reason": "retries_exhausted",
            "source": "czds_auth"
        })
        raise AuthError(f"Authentication failed after retries: {last_exc}")

    def get_token(self, safety_margin_seconds: int = 30) -> str:
        """
        Return a valid token. If missing or expiring soon, authenticate.
        Thread-safe.
        """
        with self._lock:
            now = time.time()
            if self._token and self._expires_at and (now + safety_margin_seconds) < self._expires_at:
                return self._token
            self._authenticate()
            if not self._token:
                raise AuthError("Authentication succeeded but no token available")
            return self._token

    def invalidate_token(self):
        with self._lock:
            self._token = None
            self._expires_at = None
            if TOKEN_CACHE_PATH and os.path.exists(TOKEN_CACHE_PATH):
                try:
                    os.remove(TOKEN_CACHE_PATH)
                except Exception:
                    logger.debug("Failed to remove token cache file")
            _log_auth_event({
                "username": USERNAME,
                "status": "token_invalidated",
                "source": "czds_auth"
            })

# ----------------------------
# Authenticated request wrapper
# ----------------------------
def request_with_auth(auth_client: AuthClient, method: str, url: str, max_retries_on_401: int = 1, **kwargs):
    """
    Performs the HTTP request with token, retries once on 401 after refreshing token.
    """
    attempt = 0
    while True:
        attempt += 1
        token = auth_client.get_token()
        headers = kwargs.pop("headers", {})
        headers = {**headers, "Authorization": f"Bearer {token}"}
        try:
            resp = requests.request(method, url, headers=headers, **kwargs)
        except RequestException as e:
            logger.exception("Network error on request: %s", e)
            raise
        if resp.status_code == 401 and max_retries_on_401 >= 1:
            logger.info("Got 401; invalidating token and retrying auth (attempt %d)", attempt)
            auth_client.invalidate_token()
            max_retries_on_401 -= 1
            continue
        try:
            resp.raise_for_status()
        except RequestException as e:
            logger.warning("Request failed: %s", e)
            raise
        return resp

# ----------------------------
# Runnable main block
# ----------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting CZDS authentication test...")
    try:
        client = AuthClient()
        token = client.get_token()
        print("\nAuthentication successful!")
        # show only a preview of token for safety
        print("Token preview:", token[:10] + "..." if token else "(none)")
        print("Token expires at:", datetime.datetime.fromtimestamp(client._expires_at, datetime.timezone.utc))
    except AuthError as e:
        print("\nAuthentication failed:", e)
    except Exception as e:
        print("\nUnexpected error:", e)