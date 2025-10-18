import os
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Tuple

import requests
from pymongo import MongoClient, errors as mongo_errors
from dotenv import load_dotenv

# ----- Logging -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ----- Config -----
load_dotenv()

URL = "https://www.dshield.org/ipsascii.html"

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "kyureeus_ssn")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "dshield_top_attackers_raw")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing in .env")

# ----- Mongo Client -----
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def ensure_indexes():
    """Create useful indexes for auditing."""
    try:
        collection.create_index("ingested_at")
    except mongo_errors.PyMongoError as e:
        logging.warning(f"Index creation failed: {e}")

# ----- API Request with Retry -----
def request_with_retry(
    url: str,
    max_retries: int = 3,
    backoff_sec: float = 1.5
) -> Tuple[int, str]:
    """
    Fetch raw text with retry and exponential backoff.
    Returns (status_code, text_content_or_empty).
    """
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 429:
                wait_for = int(resp.headers.get("Retry-After", attempt * backoff_sec))
                logging.warning(f"Rate limited (429). Backing off {wait_for}s...")
                time.sleep(wait_for)
                continue

            if 200 <= resp.status_code < 300:
                return resp.status_code, resp.text
            else:
                logging.warning(f"HTTP {resp.status_code}: {resp.text[:200]}")

        except requests.RequestException as e:
            logging.warning(f"Request error (attempt {attempt}/{max_retries}): {e}")

        time.sleep(backoff_sec * attempt)

    return 0, ""

# ----- ETL Stages -----
def extract() -> str:
    """Fetch raw TXT data from DShield."""
    status, text_data = request_with_retry(URL)
    if status == 0 or not text_data.strip():
        logging.error("Failed to fetch or empty payload.")
        return ""
    return text_data

def transform(raw_text: str) -> List[Dict]:
    """Parse plain text into a list of dicts."""
    docs = []
    ingested_at = datetime.now(timezone.utc).isoformat()

    for line in raw_text.splitlines():
        if not line.strip():
            continue
        if line.startswith("#") or line.lower().startswith("ip"):
            continue

        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            try:
                attacks = int(parts[1])
            except ValueError:
                attacks = None
            country = parts[2]

            docs.append({
                "ip": ip,
                "attacks": attacks,
                "country": country,
                "ingested_at": ingested_at
            })
    logging.info(f"Transformed {len(docs)} records.")
    return docs

def load(docs: List[Dict]) -> int:
    """Insert into MongoDB."""
    if not docs:
        logging.warning("No documents to insert.")
        return 0
    try:
        result = collection.insert_many(docs, ordered=False)
        logging.info(f"Inserted {len(result.inserted_ids)} documents.")
        return len(result.inserted_ids)
    except mongo_errors.BulkWriteError as e:
        logging.error(f"Bulk write error: {e.details}")
    except mongo_errors.PyMongoError as e:
        logging.error(f"Mongo error: {e}")
    return 0

def run():
    ensure_indexes()
    raw_text = extract()
    if not raw_text:
        logging.error("No data to process. Exiting.")
        return
    docs = transform(raw_text)
    load(docs)

if __name__ == "__main__":
    run()
