import os
import time
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

API_KEY = os.getenv("NVD_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://services.nvd.nist.gov")
API_ENDPOINT = os.getenv("API_ENDPOINT", "/rest/json/cves/2.0")

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB", "etl_db")
MONGO_COLLECTION = os.getenv("COLLECTION_NAME", "nvd_raw")

ENDPOINT_URL = f"{BASE_URL}{API_ENDPOINT}"


def get_cve_data(start_index=0, results_per_page=2000):
    params = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page
    }

    headers = {"apiKey": API_KEY} if API_KEY else None

    try:
        response = requests.get(ENDPOINT_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {}


def transform_cve_data(raw_data):
    transformed = []
    for vuln in raw_data.get("vulnerabilities", []):
        cve = vuln["cve"]

        desc = next(
            (d["value"] for d in cve.get("descriptions", []) if d["lang"] == "en"), ""
        )

        severity = None
        score = None
        if "metrics" in cve:
            if "cvssMetricV31" in cve["metrics"]:
                metric = cve["metrics"]["cvssMetricV31"][0]
                severity = metric.get("cvssData", {}).get("baseSeverity")
                score = metric.get("cvssData", {}).get("baseScore")
            elif "cvssMetricV2" in cve["metrics"]:
                metric = cve["metrics"]["cvssMetricV2"][0]
                severity = metric.get("baseSeverity")
                score = metric.get("cvssData", {}).get("baseScore")

        transformed.append({
            "cve_id": cve["id"],
            "published": cve["published"],
            "lastModified": cve["lastModified"],
            "description": desc,
            "severity": severity,
            "score": score,
            "references": [ref["url"] for ref in cve.get("references", [])],
            "ingestion_timestamp": datetime.now(timezone.utc)
        })
    return transformed


def load_to_mongo(data):
    if not data:
        print("[INFO] No data to insert.")
        return

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            collection.insert_many(data)
            print(f"[INFO] Inserted {len(data)} records into '{MONGO_COLLECTION}'.")
    except Exception as e:
        print(f"[ERROR] Failed to insert into MongoDB: {e}")


def run_etl():
    start_index = 0
    results_per_page = 2000
    total_results = None

    while True:
        raw_data = get_cve_data(start_index, results_per_page)

        if not raw_data:
            break

        if total_results is None:
            total_results = raw_data.get("totalResults", 0)
            print(f"[INFO] Total CVEs to fetch: {total_results}")

        transformed = transform_cve_data(raw_data)
        load_to_mongo(transformed)

        start_index += results_per_page
        if start_index >= total_results:
            break

        # rate limits
        time.sleep(0.6) 


if __name__ == "__main__":
    run_etl()
    print("[INFO] ETL pipeline completed.")
