"""PhishTank ETL connector.

This script extracts phishing intelligence data from the PhishTank data feeds,
normalises the payload, and loads the results into MongoDB. Configure the
connector through environment variables (see `.env.example` for the supported
settings).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional

import requests
from pymongo import ASCENDING, MongoClient, UpdateOne, errors
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback when dependency missing
    def load_dotenv(dotenv_path: Optional[str] = None) -> bool:
        """Lightweight .env loader used when python-dotenv is unavailable."""

        logging.warning(
            "python-dotenv is not installed; using a simple fallback loader. "
            "Install dependencies via `pip install -r requirements.txt` for full support."
        )

        candidate = Path(dotenv_path) if dotenv_path else Path(".env")
        if not candidate.exists():
            logging.debug("No .env file found at %s; skipping fallback load", candidate)
            return False

        for line in candidate.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
        return True


DEFAULT_BASE_URL = "https://data.phishtank.com/data"
DEFAULT_ENDPOINTS = ("online-valid.json",)
DEFAULT_USER_AGENT = "SSN-PhishTank-Connector/1.0 (+https://phishtank.org/)"
DEFAULT_OPENPHISH_FEED_URL = "https://openphish.com/feed.txt"
DEFAULT_OPENPHISH_USER_AGENT = "SSN-PhishConnector/1.0 (student)"


@dataclass
class ConnectorConfig:
    """Container for user-provided configuration."""

    app_key: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    endpoints: List[str] = field(default_factory=lambda: list(DEFAULT_ENDPOINTS))
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "phishtank"
    collection_prefix: str = "phishtank_raw"
    batch_size: int = 500
    request_timeout: int = 30  # seconds
    user_agent: str = DEFAULT_USER_AGENT
    checkurl_base_url: str = "https://checkurl.phishtank.com/checkurl/"
    checkurl_format: str = "json"
    checkurl_urls: List[str] = field(default_factory=list)
    openphish_feed_url: str = DEFAULT_OPENPHISH_FEED_URL
    openphish_user_agent: str = DEFAULT_OPENPHISH_USER_AGENT
    openphish_fallback_enabled: bool = True

    @classmethod
    def from_env(cls) -> "ConnectorConfig":
        """Build configuration from environment variables."""

        app_key_env = os.getenv("PHISHTANK_APP_KEY", "").strip()
        app_key: Optional[str] = app_key_env or None
        if not app_key:
            logging.warning(
                "PHISHTANK_APP_KEY not provided; falling back to the public feed path. "
                "Expect tighter rate limits and potential blocking for automated usage."
            )

        base_url = os.getenv("PHISHTANK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        endpoints_raw = os.getenv("PHISHTANK_ENDPOINTS")
        if endpoints_raw:
            endpoints = [
                segment.strip().lstrip("/")
                for segment in endpoints_raw.split(",")
                if segment.strip()
            ]
        else:
            endpoints = list(DEFAULT_ENDPOINTS)

        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        mongodb_database = os.getenv("MONGODB_DATABASE", "phishtank")
        collection_prefix = os.getenv("MONGODB_COLLECTION_PREFIX", "phishtank_raw")

        batch_size = _coerce_positive_int(
            os.getenv("PHISHTANK_BATCH_SIZE"), default=500, name="PHISHTANK_BATCH_SIZE"
        )
        request_timeout = _coerce_positive_int(
            os.getenv("PHISHTANK_REQUEST_TIMEOUT"), default=30, name="PHISHTANK_REQUEST_TIMEOUT"
        )
        user_agent = os.getenv("PHISHTANK_USER_AGENT", DEFAULT_USER_AGENT)

        checkurl_base_url = os.getenv(
            "PHISHTANK_CHECKURL_BASE_URL", "https://checkurl.phishtank.com/checkurl/"
        ).strip()
        if not checkurl_base_url:
            checkurl_base_url = "https://checkurl.phishtank.com/checkurl/"
        if not checkurl_base_url.endswith("/"):
            checkurl_base_url = f"{checkurl_base_url}/"

        checkurl_format = os.getenv("PHISHTANK_CHECKURL_FORMAT", "json").strip().lower()
        if not checkurl_format:
            checkurl_format = "json"

        checkurl_urls: List[str] = []
        urls_env = os.getenv("PHISHTANK_CHECKURL_URLS")
        if urls_env:
            fragments = urls_env.replace("\n", ",").split(",")
            checkurl_urls.extend(fragment.strip() for fragment in fragments if fragment.strip())

        urls_file = os.getenv("PHISHTANK_CHECKURL_URLS_FILE")
        if urls_file:
            file_path = Path(urls_file).expanduser()
            if file_path.exists():
                checkurl_urls.extend(
                    line.strip()
                    for line in file_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                )
            else:
                logging.warning(
                    "PHISHTANK_CHECKURL_URLS_FILE does not exist: %s", file_path
                )

        if checkurl_urls:
            checkurl_urls = list(dict.fromkeys(checkurl_urls))

        openphish_feed_url = (
            os.getenv("OPENPHISH_FEED_URL", DEFAULT_OPENPHISH_FEED_URL).strip()
            or DEFAULT_OPENPHISH_FEED_URL
        )
        openphish_user_agent = os.getenv(
            "OPENPHISH_USER_AGENT", DEFAULT_OPENPHISH_USER_AGENT
        ).strip() or DEFAULT_OPENPHISH_USER_AGENT
        openphish_fallback_enabled = True
        openphish_fallback_env = os.getenv("OPENPHISH_FALLBACK_ENABLED")
        if openphish_fallback_env is not None:
            fallback_value = _to_bool(openphish_fallback_env)
            if fallback_value is not None:
                openphish_fallback_enabled = fallback_value

        return cls(
            app_key=app_key,
            base_url=base_url,
            endpoints=endpoints,
            mongodb_uri=mongodb_uri,
            mongodb_database=mongodb_database,
            collection_prefix=collection_prefix,
            batch_size=batch_size,
            request_timeout=request_timeout,
            user_agent=user_agent,
            checkurl_base_url=checkurl_base_url,
            checkurl_format=checkurl_format,
            checkurl_urls=checkurl_urls,
            openphish_feed_url=openphish_feed_url,
            openphish_user_agent=openphish_user_agent,
            openphish_fallback_enabled=openphish_fallback_enabled,
        )


class PhishTankConnector:
    """ETL pipeline for the PhishTank data feeds."""

    def __init__(self, config: ConnectorConfig, mongo_client: Optional[MongoClient] = None) -> None:
        self.config = config
        self.session = self._build_session()
        self.client = mongo_client or MongoClient(self.config.mongodb_uri, tz_aware=True)
        self.db = self.client[self.config.mongodb_database]
        self._collection_cache: Dict[str, Any] = {}
        self._indexed_collections: set[str] = set()
        self._openphish_fallback_used = False
        self._openphish_executed = False

    def _build_session(self) -> requests.Session:
        """Return a configured HTTP session with retry support."""

        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=("GET", "POST"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": self.config.user_agent})
        return session

    def run(self, dry_run: bool = False, record_limit: Optional[int] = None) -> None:
        """Execute the ETL pipeline for each configured endpoint."""

        for endpoint in self.config.endpoints:
            normalized = endpoint.strip().lower().rstrip("/")
            if normalized == "openphish":
                if self._openphish_executed:
                    logging.info("OpenPhish feed already processed; skipping duplicate request.")
                    continue
                self._run_openphish(dry_run=dry_run, record_limit=record_limit)
                continue

            if normalized == "checkurl":
                self._run_checkurl(dry_run=dry_run, record_limit=record_limit)
                continue

            if not self.config.app_key:
                logging.info(
                    "Skipping PhishTank endpoint %s because PHISHTANK_APP_KEY is missing.",
                    endpoint,
                )
                self._maybe_run_openphish_fallback(dry_run=dry_run, record_limit=record_limit)
                continue

            logging.info("Processing endpoint %s", endpoint)
            processed = 0
            buffer: List[Dict[str, Any]] = []

            try:
                for record in self.extract(endpoint):
                    transformed = self.transform(record, endpoint)
                    if transformed is None:
                        continue

                    buffer.append(transformed)
                    processed += 1

                    if len(buffer) >= self.config.batch_size:
                        self.load(endpoint, buffer, dry_run=dry_run)
                        buffer.clear()

                    if record_limit and processed >= record_limit:
                        logging.info(
                            "Reached record limit (%s) for endpoint %s", record_limit, endpoint
                        )
                        break
            except requests.RequestException as exc:
                logging.error("Extraction failed for %s: %s", endpoint, exc)
                self._maybe_run_openphish_fallback(dry_run=dry_run, record_limit=record_limit)
                continue

            if buffer:
                self.load(endpoint, buffer, dry_run=dry_run)

            logging.info("Completed endpoint %s (%d records processed)", endpoint, processed)

    def _run_checkurl(
        self, dry_run: bool = False, record_limit: Optional[int] = None
    ) -> None:
        """Orchestrate the checkurl endpoint using configured URL queries."""

        endpoint = "checkurl"
        urls = self.config.checkurl_urls or []
        if not urls:
            logging.warning(
                "No URLs provided for checkurl endpoint; configure PHISHTANK_CHECKURL_URLS or "
                "PHISHTANK_CHECKURL_URLS_FILE."
            )
            return

        logging.info("Processing endpoint %s (%d URLs)", endpoint, len(urls))
        processed = 0
        buffer: List[Dict[str, Any]] = []

        for target_url in urls:
            try:
                record = self.extract_checkurl(target_url)
            except requests.RequestException as exc:
                logging.error("Checkurl request failed for %s: %s", target_url, exc)
                continue

            transformed = self.transform_checkurl(record, endpoint)
            if transformed is None:
                continue

            buffer.append(transformed)
            processed += 1

            if len(buffer) >= self.config.batch_size:
                self.load(endpoint, buffer, dry_run=dry_run)
                buffer.clear()

            if record_limit and processed >= record_limit:
                logging.info(
                    "Reached record limit (%s) for endpoint %s", record_limit, endpoint
                )
                break

        if buffer:
            self.load(endpoint, buffer, dry_run=dry_run)

        logging.info("Completed endpoint %s (%d URLs processed)", endpoint, processed)

    def _maybe_run_openphish_fallback(
        self, dry_run: bool = False, record_limit: Optional[int] = None
    ) -> None:
        """Trigger the OpenPhish feed exactly once when fallback is enabled."""

        if not self.config.openphish_fallback_enabled:
            logging.debug("OpenPhish fallback disabled via configuration; skipping.")
            return
        if self._openphish_fallback_used:
            logging.debug("OpenPhish fallback already executed; skipping.")
            return

        self._openphish_fallback_used = True
        logging.info("Running OpenPhish fallback feed.")
        success = self._run_openphish(
            dry_run=dry_run, record_limit=record_limit, reason="fallback"
        )
        if not success:
            self._openphish_fallback_used = False

    def _run_openphish(
        self,
        dry_run: bool = False,
        record_limit: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Ingest the OpenPhish community feed."""

        log_context = "Processing endpoint openphish"
        if reason:
            log_context = f"{log_context} ({reason})"
        logging.info(log_context)

        try:
            urls = self.extract_openphish()
        except requests.RequestException as exc:
            logging.error("Failed to fetch OpenPhish feed: %s", exc)
            return False

        self._openphish_executed = True

        processed = 0
        buffer: List[Dict[str, Any]] = []
        for url in urls:
            transformed = self.transform_openphish(url)
            if transformed is None:
                continue

            buffer.append(transformed)
            processed += 1

            if len(buffer) >= self.config.batch_size:
                self.load("openphish", buffer, dry_run=dry_run)
                buffer.clear()

            if record_limit and processed >= record_limit:
                logging.info(
                    "Reached record limit (%s) for endpoint openphish", record_limit
                )
                break

        if buffer:
            self.load("openphish", buffer, dry_run=dry_run)

        logging.info("Completed endpoint openphish (%d records processed)", processed)
        return True

    def extract_openphish(self) -> List[str]:
        """Fetch the OpenPhish community feed."""

        response = self.session.get(
            self.config.openphish_feed_url,
            headers={"User-Agent": self.config.openphish_user_agent},
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()

        return [line.strip() for line in response.text.splitlines() if line.strip()]

    def transform_openphish(self, url: str) -> Optional[Dict[str, Any]]:
        """Convert OpenPhish URLs into MongoDB-ready documents."""

        if not isinstance(url, str):
            return None

        cleaned = url.strip()
        if not cleaned:
            return None

        return {
            "url": cleaned,
            "source": "openphish",
            "source_endpoint": "openphish",
            "ingested_at": datetime.now(timezone.utc),
        }

    def _build_feed_url(self, endpoint: str) -> str:
        """Construct the feed URL, omitting the app key when not provided."""

        base = self.config.base_url.rstrip("/")
        segments = [base]
        if self.config.app_key:
            segments.append(self.config.app_key.strip("/"))
        segments.append(endpoint.lstrip("/"))
        return "/".join(segment for segment in segments if segment)

    def extract(self, endpoint: str) -> Iterable[Dict[str, Any]]:
        """Fetch and yield raw records from a single endpoint."""

        url = self._build_feed_url(endpoint)
        response = self.session.get(url, timeout=self.config.request_timeout)
        if response.status_code == 404:
            logging.error("Endpoint not found: %s", url)
            return

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logging.error("Failed to fetch %s: %s", url, exc)
            raise

        payload = self._decode_response(response, endpoint)
        yield from self._parse_payload(payload, endpoint, response.headers.get("Content-Type", ""))

    def extract_checkurl(self, target_url: str) -> Dict[str, Any]:
        """Submit a URL to the PhishTank CheckURL endpoint and return the raw response."""

        form_payload = {
            "url": target_url,
            "format": self.config.checkurl_format,
        }
        if self.config.app_key:
            form_payload["app_key"] = self.config.app_key

        response = self.session.post(
            self.config.checkurl_base_url,
            data=form_payload,
            timeout=self.config.request_timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logging.error("Failed to query checkurl for %s: %s", target_url, exc)
            raise

        parsed: Any
        if self.config.checkurl_format == "json":
            try:
                parsed = response.json()
            except json.JSONDecodeError:
                logging.error(
                    "Invalid JSON payload from checkurl for %s; storing raw text.", target_url
                )
                parsed = {"raw": response.text}
        else:
            parsed = {"raw": response.text}

        return {
            "target_url": target_url,
            "response": parsed,
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }

    def _decode_response(self, response: requests.Response, endpoint: str) -> bytes:
        """Decompress the payload when the feed is gzip encoded."""

        content_encoding = response.headers.get("Content-Encoding", "").lower()
        raw_bytes = response.content

        if endpoint.endswith(".gz") or "gzip" in content_encoding:
            try:
                return gzip.decompress(raw_bytes)
            except OSError:
                logging.warning("Failed to decompress gzip payload from %s; using raw content", endpoint)
        return raw_bytes

    def _parse_payload(
        self, payload: bytes, endpoint: str, content_type: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Parse the HTTP payload into dictionaries."""

        text_content_type = content_type.lower()
        if endpoint.endswith(".json") or "json" in text_content_type:
            text = payload.decode("utf-8", errors="replace").strip()
            if not text:
                logging.warning("Empty response for endpoint %s", endpoint)
                return

            if text.startswith("{") or text.startswith("["):
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    logging.debug("JSON decoding failed for %s; trying newline-delimited JSON", endpoint)
                    yield from self._parse_json_lines(text, endpoint)
                else:
                    if isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, dict):
                                yield item
                            else:
                                logging.debug("Skipping non-dict item in %s: %r", endpoint, item)
                    elif isinstance(parsed, dict):
                        yield parsed
                    else:
                        logging.error("Unexpected JSON root type (%s) for endpoint %s", type(parsed), endpoint)
            else:
                yield from self._parse_json_lines(text, endpoint)
            return

        if endpoint.endswith(".csv") or "csv" in text_content_type or "text/plain" in text_content_type:
            text_stream = StringIO(payload.decode("utf-8", errors="replace"))
            reader = csv.DictReader(text_stream)
            for row in reader:
                yield row
            return

        logging.warning(
            "Unhandled content type for endpoint %s (Content-Type: %s)", endpoint, content_type
        )

    def transform_checkurl(
        self, record: Dict[str, Any], endpoint: str
    ) -> Optional[Dict[str, Any]]:
        """Normalise the CheckURL response into a MongoDB document."""

        target_url = record.get("target_url")
        if not target_url:
            logging.debug("Skipping CheckURL record without target_url: %r", record)
            return None

        response = record.get("response", {})
        document: Dict[str, Any] = {
            "source_endpoint": endpoint,
            "queried_url": target_url,
            "ingested_at": datetime.now(timezone.utc),
            "status_code": record.get("status_code"),
            "response_headers": record.get("headers"),
            "raw_response": response,
        }

        document["url"] = target_url

        results = response.get("results") if isinstance(response, dict) else None
        if isinstance(results, dict):
            url_value = results.get("url")
            if isinstance(url_value, str) and url_value.strip():
                document["url"] = url_value.strip()

            if "phish_id" in results:
                document["phish_id"] = _safe_int(results["phish_id"])

            for key in ("verified", "in_database", "valid", "online"):
                if key in results:
                    document[key] = _to_bool(results[key])

            for key in (
                "submission_time",
                "verification_time",
                "targeted_brand_valid_since",
                "last_update",
            ):
                if key in results:
                    document[key] = _parse_datetime(results[key])

            for key in (
                "phish_detail_page",
                "targeted_brand",
                "targeted_brand_group",
                "targeted_brand_identifier",
            ):
                if key in results and results[key] not in (None, ""):
                    document[key] = results[key]

            # Preserve original boolean flags regardless of conversion
            document["results"] = results

        if isinstance(response, dict) and "meta" in response:
            document["meta"] = response["meta"]

        return document

    @staticmethod
    def _parse_json_lines(text: str, endpoint: str) -> Generator[Dict[str, Any], None, None]:
        """Yield records from a newline-delimited JSON payload."""

        for line in text.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                logging.debug("Skipping invalid JSON line in %s: %s", endpoint, candidate[:120])
                continue
            if isinstance(parsed, dict):
                yield parsed
            else:
                logging.debug("Skipping non-dict JSON item in %s: %r", endpoint, parsed)

    def transform(self, record: Dict[str, Any], endpoint: str) -> Optional[Dict[str, Any]]:
        """Normalise raw records into MongoDB-ready documents."""

        if not isinstance(record, dict):
            logging.debug("Skipping non-dict record from %s: %r", endpoint, record)
            return None

        document = dict(record)
        document["source_endpoint"] = endpoint
        document["ingested_at"] = datetime.now(timezone.utc)

        if "phish_id" in document:
            document["phish_id"] = _safe_int(document["phish_id"])
        elif "phishid" in document:
            document["phish_id"] = _safe_int(document.pop("phishid"))

        for key in ("verified", "online", "targeted_brand_valid"):
            if key in document:
                document[key] = _to_bool(document[key])

        for key in ("submission_time", "verification_time", "targeted_brand_valid_since", "last_update"):
            if key in document:
                document[key] = _parse_datetime(document[key])

        url = document.get("url")
        if isinstance(url, str):
            document["url"] = url.strip()

        return document

    def load(self, endpoint: str, documents: List[Dict[str, Any]], dry_run: bool = False) -> None:
        """Persist transformed documents in MongoDB."""

        if dry_run:
            logging.info("Dry run active: skipping insert of %d records for %s", len(documents), endpoint)
            return

        if not documents:
            logging.debug("No documents to load for %s", endpoint)
            return

        collection_name = self._collection_name(endpoint)
        collection = self._get_collection(collection_name)

        operations: List[UpdateOne] = []
        for document in documents:
            selector: Dict[str, Any] = {}
            phish_id = document.get("phish_id")
            if isinstance(phish_id, int):
                selector["phish_id"] = phish_id
            elif document.get("url"):
                selector["url"] = document["url"]
            else:
                logging.debug(
                    "Skipping document without a unique identifier for endpoint %s: %s",
                    endpoint,
                    repr(document)[:200],
                )
                continue

            operations.append(UpdateOne(selector, {"$set": document}, upsert=True))

        if not operations:
            logging.warning("No valid documents to load for %s after filtering identifiers", endpoint)
            return

        try:
            result = collection.bulk_write(operations, ordered=False)
        except errors.BulkWriteError as exc:
            logging.error("Bulk write error for endpoint %s: %s", endpoint, exc.details)
            raise
        else:
            logging.info(
                "Upserted %d documents into %s (matched=%d modified=%d upserted=%d)",
                len(operations),
                collection_name,
                result.matched_count,
                result.modified_count,
                len(result.upserted_ids),
            )

    def _collection_name(self, endpoint: str) -> str:
        """Generate a MongoDB collection name based on the endpoint."""

        slug = "".join(char if char.isalnum() else "_" for char in endpoint.lower()).strip("_")
        return f"{self.config.collection_prefix}_{slug}"

    def _get_collection(self, name: str):
        """Return (and cache) a collection instance with indexes in place."""

        if name not in self._collection_cache:
            collection = self.db[name]
            self._ensure_indexes(collection)
            self._collection_cache[name] = collection
        return self._collection_cache[name]

    def _ensure_indexes(self, collection) -> None:
        """Create indexes to de-duplicate records across runs."""

        if collection.name in self._indexed_collections:
            return

        try:
            collection.create_index([("phish_id", ASCENDING)], unique=True, sparse=True)
            collection.create_index([("url", ASCENDING)], unique=True, sparse=True)
            collection.create_index([("ingested_at", ASCENDING)])
        except errors.PyMongoError as exc:
            logging.warning("Index creation failed for %s: %s", collection.name, exc)
        finally:
            self._indexed_collections.add(collection.name)


def _coerce_positive_int(value: Optional[str], default: int, name: str) -> int:
    """Ensure configuration values resolve to integers."""

    if value is None:
        return default
    try:
        parsed = int(str(value).strip())
        if parsed <= 0:
            raise ValueError
        return parsed
    except (TypeError, ValueError):
        logging.debug("Could not coerce %s=%r to positive int; falling back to %d", name, value, default)
        return default


def _safe_int(value: Any) -> Any:
    """Best-effort integer conversion for identifiers."""

    try:
        return int(str(value))
    except (TypeError, ValueError):
        return value


def _to_bool(value: Any) -> Optional[bool]:
    """Normalise boolean-like values such as 'yes'/'no'."""

    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    normalised = str(value).strip().lower()
    if normalised in {"1", "true", "t", "yes", "y", "verified", "online"}:
        return True
    if normalised in {"0", "false", "f", "no", "n", "not verified", "offline"}:
        return False
    return None


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse timestamps commonly exposed by the PhishTank API."""

    if value in (None, "", "null"):
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    text = str(value).strip()
    if not text:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        logging.debug("Failed to parse datetime from value %r", value)
        return None


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """CLI argument parsing."""

    parser = argparse.ArgumentParser(
        description="Extract phishing intelligence from PhishTank feeds into MongoDB."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the ETL without writing to MongoDB.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of records to process per endpoint (useful for tests).",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args(argv)


def configure_logging(log_level: str) -> None:
    """Configure the global logging behaviour."""

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main(argv: Optional[List[str]] = None) -> None:
    """Entrypoint for command-line execution."""

    args = parse_args(argv)
    configure_logging(args.log_level)

    load_dotenv()
    try:
        config = ConnectorConfig.from_env()
    except ValueError as exc:
        logging.error("%s", exc)
        return

    connector = PhishTankConnector(config)
    connector.run(dry_run=args.dry_run, record_limit=args.limit)


if __name__ == "__main__":
    main()
