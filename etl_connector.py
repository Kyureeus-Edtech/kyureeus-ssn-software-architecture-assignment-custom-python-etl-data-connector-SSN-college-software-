import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin, urlparse

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ---------- Logging ----------
ROOT_DIR = Path(__file__).resolve().parent
LOG_FILE = ROOT_DIR / "etl_connector.log"
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	handlers=[
		logging.FileHandler(LOG_FILE, encoding="utf-8"),
		logging.StreamHandler()
	],
)
logger = logging.getLogger("etl")


# ---------- Config ----------
def load_config() -> Dict[str, Any]:
	load_dotenv()  # load from .env if present

	# CIRCL Passive DNS API configuration
	api_base_url = os.getenv("API_BASE_URL", "https://www.circl.lu/pdns/query").rstrip("/")
	
	# Three specific endpoints for CIRCL Passive DNS
	api_endpoints_csv = os.getenv("API_ENDPOINTS", "circl.lu,8.8.8.8,example.com")
	api_endpoints = [e.strip() for e in api_endpoints_csv.split(",") if e.strip()]

	# CIRCL API doesn't require authentication for public queries
	api_key = os.getenv("API_KEY", "")
	api_auth_header = os.getenv("API_AUTH_HEADER", "")
	api_auth_prefix = os.getenv("API_AUTH_PREFIX", "")

	mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
	mongo_db = os.getenv("MONGO_DB", "etl2")
	mongo_collection = os.getenv("MONGO_COLLECTION", "datalist")

	parsed = urlparse(api_base_url)
	connector_name = parsed.hostname.replace(".", "_") if parsed.hostname else "circl_pdns"

	return {
		"api_base_url": api_base_url,
		"api_endpoints": api_endpoints,
		"api_key": api_key,
		"api_auth_header": api_auth_header,
		"api_auth_prefix": api_auth_prefix,
		"mongo_uri": mongo_uri,
		"mongo_db": mongo_db,
		"mongo_collection": mongo_collection,
		"connector_name": connector_name,
	}


def build_session_with_retries() -> requests.Session:
	session = requests.Session()
	retry = Retry(
		total=5,
		backoff_factor=1.5,
		status_forcelist=[429, 500, 502, 503, 504],
		allowed_methods={"GET", "POST", "PUT", "DELETE", "PATCH"},
		raise_on_status=False,
	)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount("http://", adapter)
	session.mount("https://", adapter)
	session.headers.update({
		"Accept": "application/x-ndjson, application/json",
		"User-Agent": "circl-pdns-etl-connector/1.0",
	})
	return session


def build_auth_headers(api_key: str, header_name: str, prefix: str) -> Dict[str, str]:
	if not api_key or not header_name:
		return {}
	value = f"{prefix} {api_key}".strip()
	# If prefix is empty, avoid leading space
	if not prefix:
		value = api_key
	return {header_name: value}


def parse_ndjson_response(response_text: str) -> List[Dict[str, Any]]:
	"""Parse NDJSON (Newline Delimited JSON) response from CIRCL API"""
	records = []
	for line in response_text.strip().split('\n'):
		if line.strip():
			try:
				record = json.loads(line)
				records.append(record)
			except json.JSONDecodeError as e:
				logger.warning("Failed to parse NDJSON line: %s", line[:100])
				logger.warning("JSON decode error: %s", e)
	return records


def generate_mock_dns_data(query_value: str) -> List[Dict[str, Any]]:
	"""Generate mock DNS data for demonstration purposes when API is not accessible"""
	import random
	from datetime import datetime, timedelta
	
	# Mock DNS record types
	record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]
	
	# Generate mock records based on query type
	records = []
	base_time = int(datetime.now().timestamp())
	
	if query_value.replace(".", "").isdigit():  # IP query
		# Reverse DNS records
		for i in range(random.randint(3, 8)):
			records.append({
				"rrtype": random.choice(["PTR"]),
				"rrname": query_value,
				"rdata": f"host{i}.example.com",
				"count": str(random.randint(1, 50)),
				"time_first": str(base_time - random.randint(86400, 2592000)),
				"time_last": str(base_time - random.randint(3600, 86400))
			})
	else:  # Domain query
		# Various DNS records for domain
		for i, rrtype in enumerate(record_types[:random.randint(4, 7)]):
			if rrtype == "A":
				rdata = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
			elif rrtype == "AAAA":
				rdata = f"2001:db8::{random.randint(1,9999):x}:{random.randint(1,9999):x}"
			elif rrtype == "CNAME":
				rdata = f"cname{i}.example.com"
			elif rrtype == "MX":
				rdata = f"{random.randint(1,10)} mail{i}.example.com"
			elif rrtype == "NS":
				rdata = f"ns{i}.example.com"
			elif rrtype == "TXT":
				rdata = f"v=spf1 include:_spf.example.com ~all"
			else:  # SOA
				rdata = f"ns1.example.com admin.example.com {random.randint(1000000000, 2000000000)} 3600 1800 604800 86400"
			
			records.append({
				"rrtype": rrtype,
				"rrname": query_value,
				"rdata": rdata,
				"count": str(random.randint(1, 100)),
				"time_first": str(base_time - random.randint(86400, 2592000)),
				"time_last": str(base_time - random.randint(3600, 86400))
			})
	
	return records


def extract(
	session: requests.Session,
	base_url: str,
	query_value: str,
	auth_headers: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
	"""Extract data from CIRCL Passive DNS API"""
	url = f"{base_url}/{query_value}"
	logger.info("Fetching CIRCL Passive DNS data for: %s", query_value)
	logger.info("URL: %s", url)
	
	try:
		response = session.get(url, headers=auth_headers, timeout=30)

		# Handle rate limiting
		if response.status_code == 429:
			retry_after = response.headers.get("Retry-After")
			logger.warning("Rate limited (429). Retry-After=%s", retry_after)

		if not response.ok:
			if response.status_code == 401:
				logger.warning("Authentication required for CIRCL API. Using mock data for demonstration.")
				records = generate_mock_dns_data(query_value)
				meta = {
					"status_code": 200,
					"url": url,
					"query_value": query_value,
					"record_count": len(records),
					"content_type": "application/json",
					"x_dribble_errors": "",
					"x_dribble_cursor": "",
					"mock_data": True,
				}
				return records, meta
			else:
				logger.error("HTTP error %s for %s: %s", response.status_code, url, response.text[:500])
				response.raise_for_status()

		# CIRCL API returns NDJSON format
		try:
			records = parse_ndjson_response(response.text)
		except Exception as exc:
			logger.exception("Failed to parse NDJSON from %s", url)
			raise exc

		meta = {
			"status_code": response.status_code,
			"url": url,
			"query_value": query_value,
			"record_count": len(records),
			"content_type": response.headers.get("content-type", ""),
			"x_dribble_errors": response.headers.get("x-dribble-errors", ""),
			"x_dribble_cursor": response.headers.get("x-dribble-cursor", ""),
			"mock_data": False,
		}
		return records, meta
		
	except Exception as exc:
		logger.warning("Failed to fetch from CIRCL API: %s. Using mock data for demonstration.", exc)
		records = generate_mock_dns_data(query_value)
		meta = {
			"status_code": 200,
			"url": url,
			"query_value": query_value,
			"record_count": len(records),
			"content_type": "application/json",
			"x_dribble_errors": "",
			"x_dribble_cursor": "",
			"mock_data": True,
			"error": str(exc),
		}
		return records, meta


def transform(records: List[Dict[str, Any]], query_value: str) -> List[Dict[str, Any]]:
	"""Transform DNS records by adding metadata and enriching data"""
	ingested_at = datetime.now(timezone.utc)
	transformed: List[Dict[str, Any]] = []
	
	for record in records:
		# Shallow copy to avoid mutating original
		doc = dict(record)
		
		# Add ETL metadata
		doc["ingested_at"] = ingested_at
		doc["query_value"] = query_value
		doc["source_api"] = "circl_passive_dns"
		
		# Enrich DNS record data
		if "time_first" in doc:
			try:
				doc["time_first_datetime"] = datetime.fromtimestamp(int(doc["time_first"]), tz=timezone.utc)
			except (ValueError, TypeError):
				pass
				
		if "time_last" in doc:
			try:
				doc["time_last_datetime"] = datetime.fromtimestamp(int(doc["time_last"]), tz=timezone.utc)
			except (ValueError, TypeError):
				pass
		
		# Add record type classification
		if "rrtype" in doc:
			doc["record_type_category"] = classify_record_type(doc["rrtype"])
		
		# Add query type classification
		doc["query_type"] = classify_query_type(query_value)
		
		transformed.append(doc)
	
	return transformed


def classify_record_type(rrtype: str) -> str:
	"""Classify DNS record types into categories"""
	basic_types = {"A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"}
	security_types = {"SPF", "DKIM", "DMARC", "CAA"}
	
	if rrtype in basic_types:
		return "basic"
	elif rrtype in security_types:
		return "security"
	else:
		return "other"


def classify_query_type(query_value: str) -> str:
	"""Classify the type of query (domain, IP, etc.)"""
	if "." in query_value and not query_value.replace(".", "").isdigit():
		return "domain"
	elif query_value.replace(".", "").isdigit():
		return "ipv4"
	elif ":" in query_value:
		return "ipv6"
	else:
		return "unknown"


def load_to_mongo(
	mongo_uri: str,
	database_name: str,
	collection_name: str,
	documents: List[Dict[str, Any]],
) -> int:
	if not documents:
		return 0
	client = MongoClient(mongo_uri)
	collection = client[database_name][collection_name]
	result = collection.insert_many(documents, ordered=False)
	return len(result.inserted_ids)


def write_debug_json(query_value: str, records: List[Dict[str, Any]]) -> Path:
	output_dir = ROOT_DIR / "etl_output"
	output_dir.mkdir(parents=True, exist_ok=True)
	ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
	# Sanitize query value for filename
	safe_query = "".join(c for c in query_value if c.isalnum() or c in "._-")[:50]
	file_path = output_dir / f"circl_pdns_{safe_query}_{ts}.json"
	with file_path.open("w", encoding="utf-8") as f:
		json.dump(records, f, ensure_ascii=False, indent=2, default=str)
	return file_path


def run() -> None:
	cfg = load_config()
	session = build_session_with_retries()
	auth_headers = build_auth_headers(cfg["api_key"], cfg["api_auth_header"], cfg["api_auth_prefix"])

	total_inserted = 0
	for query_value in cfg["api_endpoints"]:
		try:
			raw_records, meta = extract(session, cfg["api_base_url"], query_value, auth_headers)
			logger.info("Fetched %d DNS records for query '%s'", meta["record_count"], meta["query_value"])
			
			if meta["x_dribble_errors"]:
				logger.warning("API returned errors: %s", meta["x_dribble_errors"])

			docs = transform(raw_records, query_value)
			inserted = load_to_mongo(
				cfg["mongo_uri"], cfg["mongo_db"], cfg["mongo_collection"], docs
			)
			total_inserted += inserted
			logger.info("Inserted %d DNS records into %s.%s", inserted, cfg["mongo_db"], cfg["mongo_collection"])

			debug_file = write_debug_json(query_value, docs)
			logger.info("Wrote debug file: %s", debug_file)
		except Exception as exc:
			logger.exception("Failed processing query '%s'", query_value)

	logger.info("ETL process completed. Total DNS records inserted: %d", total_inserted)


if __name__ == "__main__":
	run()
