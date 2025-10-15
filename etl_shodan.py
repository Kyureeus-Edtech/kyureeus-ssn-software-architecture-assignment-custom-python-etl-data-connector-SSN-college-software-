import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser

# =============================
# Load configuration
# =============================
load_dotenv()
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

if not SHODAN_API_KEY:
    raise ValueError("SHODAN_API_KEY not found in .env file")

client = MongoClient("mongodb://localhost:27017/")
db = client["etl_database"]

# MongoDB Collections
collection_host = db["shodan_host_raw"]
collection_count = db["shodan_host_count"]
collection_search = db["shodan_host_search"]
collection_facets = db["shodan_host_facets"]
collection_filters = db["shodan_host_filters"]
collection_tokens = db["shodan_host_tokens"]


# =============================
# Helper - API Request
# =============================
def fetch_json(url):
    """Generic helper to make GET requests."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch from {url}: {e}")
        return None


# =============================
# Extract Functions
# =============================
def extract_shodan_host(ip_address):
    url = f"https://api.shodan.io/shodan/host/{ip_address}?key={SHODAN_API_KEY}"
    return fetch_json(url)


def extract_shodan_host_count(query):
    url = f"https://api.shodan.io/shodan/host/count?key={SHODAN_API_KEY}&query={query}"
    return fetch_json(url)


def extract_shodan_host_search(query):
    url = f"https://api.shodan.io/shodan/host/search?key={SHODAN_API_KEY}&query={query}"
    return fetch_json(url)


def extract_shodan_host_facets(query, facets="country,org,port"):
    url = f"https://api.shodan.io/shodan/host/search/facets?key={SHODAN_API_KEY}&query={query}&facets={facets}"
    return fetch_json(url)


def extract_shodan_host_filters():
    url = f"https://api.shodan.io/shodan/host/search/filters?key={SHODAN_API_KEY}"
    return fetch_json(url)


def extract_shodan_host_tokens(query):
    url = f"https://api.shodan.io/shodan/host/search/tokens?key={SHODAN_API_KEY}&query={query}"
    return fetch_json(url)


# =============================
# Transform Functions
# =============================
def transform_host_data(data):
    if not data:
        return None

    return {
        "ip": data.get("ip_str"),
        "asn": data.get("asn"),
        "org": data.get("org"),
        "isp": data.get("isp"),
        "country": data.get("country_name"),
        "country_code": data.get("country_code"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "last_update": parser.parse(data["last_update"]) if data.get("last_update") else None,
        "domains": data.get("domains", []),
        "hostnames": data.get("hostnames", []),
        "ports": data.get("ports", []),
        "services": [
            {
                "port": s.get("port"),
                "transport": s.get("transport"),
                "org": s.get("org"),
                "asn": s.get("asn"),
                "domains": s.get("domains", []),
                "timestamp": parser.parse(s["timestamp"]) if s.get("timestamp") else None
            }
            for s in data.get("data", [])
        ],
        "_etl_source": "shodan_host",
        "_etl_ingested_at": datetime.utcnow(),
        "_etl_version": "2.0"
    }


def transform_count_data(data, query):
    if not data:
        return None
    return {
        "query": query,
        "total": data.get("total"),
        "facets": data.get("facets", {}),
        "_etl_source": "shodan_host_count",
        "_etl_ingested_at": datetime.utcnow()
    }


def transform_search_data(data, query):
    if not data:
        return None
    return {
        "query": query,
        "total": data.get("total"),
        "matches": data.get("matches", []),
        "_etl_source": "shodan_host_search",
        "_etl_ingested_at": datetime.utcnow()
    }


def transform_facets_data(data, query):
    if not data:
        return None
    return {
        "query": query,
        "facets": data.get("facets", {}),
        "_etl_source": "shodan_host_facets",
        "_etl_ingested_at": datetime.utcnow()
    }


def transform_filters_data(data):
    if not data:
        return None
    return {
        "filters": data,
        "_etl_source": "shodan_host_filters",
        "_etl_ingested_at": datetime.utcnow()
    }


def transform_tokens_data(data, query):
    if not data:
        return None
    return {
        "query": query,
        "tokens": data,
        "_etl_source": "shodan_host_tokens",
        "_etl_ingested_at": datetime.utcnow()
    }


# =============================
# Load Function
# =============================
def load_to_mongodb(collection, data):
    """Insert transformed data into MongoDB."""
    if data:
        collection.insert_one(data)
        print(f"[INFO] Inserted document into {collection.name}")
    else:
        print(f"[WARN] No data to insert for {collection.name}")


# =============================
# Main ETL Flow
# =============================
if __name__ == "__main__":
    test_ip = "8.8.8.8"
    test_query = "apache port:80 country:IN"

    # 1️⃣ Host
    raw_host = extract_shodan_host(test_ip)
    doc_host = transform_host_data(raw_host)
    load_to_mongodb(collection_host, doc_host)

    # 2️⃣ Host Count
    raw_count = extract_shodan_host_count(test_query)
    doc_count = transform_count_data(raw_count, test_query)
    load_to_mongodb(collection_count, doc_count)

    # 3️⃣ Host Search
    raw_search = extract_shodan_host_search(test_query)
    doc_search = transform_search_data(raw_search, test_query)
    load_to_mongodb(collection_search, doc_search)

    # 4️⃣ Host Search Facets
    raw_facets = extract_shodan_host_facets(test_query)
    doc_facets = transform_facets_data(raw_facets, test_query)
    load_to_mongodb(collection_facets, doc_facets)

    # 5️⃣ Host Search Filters
    raw_filters = extract_shodan_host_filters()
    doc_filters = transform_filters_data(raw_filters)
    load_to_mongodb(collection_filters, doc_filters)

    # 6️⃣ Host Search Tokens
    raw_tokens = extract_shodan_host_tokens(test_query)
    doc_tokens = transform_tokens_data(raw_tokens, test_query)
    load_to_mongodb(collection_tokens, doc_tokens)
