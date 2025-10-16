# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoints
IPAPI_BASE = os.getenv("IPAPI_BASE", "http://ip-api.com")
JSON_ENDPOINT = f"{IPAPI_BASE}/json"
CSV_ENDPOINT = f"{IPAPI_BASE}/csv"
BATCH_ENDPOINT = f"{IPAPI_BASE}/batch"
EDNS_ENDPOINT = f"{IPAPI_BASE}/edns"

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ipapi_etl")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "lookups")

# ETL parameters
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
RATE_LIMIT_SINGLE = int(os.getenv("RATE_LIMIT_SINGLE", 45))
RATE_LIMIT_BATCH = int(os.getenv("RATE_LIMIT_BATCH", 15))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
RETRY_BACKOFF_SECONDS = int(os.getenv("RETRY_BACKOFF_SECONDS", 2))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))
USER_AGENT = os.getenv("IPAPI_USER_AGENT", "ipapi-etl/1.0 (student-assignment)")
