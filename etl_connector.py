import os
import sys
import time
import datetime as dt
from typing import List, Optional
import requests
from pymongo import MongoClient, errors
from dotenv import load_dotenv


def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def fetch_cves(
    api_url: str,
    api_key: Optional[str] = None,
    limit: int = 100,
    max_retries: int = 3
) -> List[dict]:
    """Fetch CVEs with error handling for invalid responses, empty payloads, rate limits, and connectivity errors."""
    headers = {"User-Agent": "SSN-ETL-Connector/1.0"}
    if api_key:
        headers["apiKey"] = api_key
    params = {"resultsPerPage": limit}

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(api_url, headers=headers, params=params, timeout=60)
        except requests.RequestException as e:
            print(f"[Error] API connectivity issue (attempt {attempt}): {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
            continue

        # Handle API rate limit
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else 5 * attempt
            print(f"[Rate Limit] Waiting {wait} seconds before retry...", file=sys.stderr)
            time.sleep(wait)
            continue

        # Invalid response status
        if resp.status_code != 200:
            print(f"[Error] HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            time.sleep(2 ** attempt)
            continue

        # Parse JSON safely
        try:
            data = resp.json()
        except ValueError:
            print("[Error] Invalid JSON response", file=sys.stderr)
            time.sleep(2 ** attempt)
            continue

        # Empty or missing vulnerabilities field
        vulns = data.get("vulnerabilities")
        if vulns is None:
            print("[Error] Missing 'vulnerabilities' field in API response", file=sys.stderr)
            time.sleep(2 ** attempt)
            continue

        if not vulns:
            print("[Warning] No vulnerabilities found in API response", file=sys.stderr)

        return vulns

    raise RuntimeError("Failed to fetch CVEs after multiple retries.")


def insert_cves_into_mongo(collection, cves: List[dict]) -> None:
    """Insert CVEs into MongoDB with acknowledgment and error checks."""
    inserted_count = 0
    for vuln in cves:
        vuln["ingestionTimestamp"] = now_utc_iso()
        try:
            result = collection.insert_one(vuln)
            if not result.acknowledged:
                print(f"[Warning] Insert not acknowledged for CVE: {vuln.get('cve', {}).get('id', 'unknown')}", file=sys.stderr)
            else:
                inserted_count += 1
        except errors.PyMongoError as e:
            print(f"[MongoDB Error] Could not insert CVE: {e}", file=sys.stderr)

    print(f"[Done] Successfully inserted {inserted_count} out of {len(cves)} CVEs.")


def main():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")
    mongo_col = os.getenv("MONGO_COLLECTION")
    api_url = os.getenv("NVD_API_URL")
    api_key = os.getenv("NVD_API_KEY")

    if not mongo_uri:
        print("[Fatal Error] MONGO_URI is required", file=sys.stderr)
        sys.exit(1)

    # Test MongoDB connectivity
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
    except errors.ServerSelectionTimeoutError as e:
        print(f"[Fatal Error] Cannot connect to MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

    collection = client[mongo_db][mongo_col]

    print("[Run] Fetching CVEs...")
    try:
        cves = fetch_cves(api_url, api_key)
    except Exception as e:
        print(f"[Fatal Error] Failed to fetch CVEs: {e}", file=sys.stderr)
        sys.exit(1)

    if not cves:
        print("[Info] No CVEs to insert. Exiting.")
        return

    insert_cves_into_mongo(collection, cves)


if __name__ == "__main__":
    main()
