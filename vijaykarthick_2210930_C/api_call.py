import os
import time
import requests
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
NVD_CVE_URL = os.getenv("NVD_CVE_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
NVD_CPE_URL = os.getenv("NVD_CPE_URL", "https://services.nvd.nist.gov/rest/json/cpes/2.0")
NVD_CVEHISTORY_URL = os.getenv("NVD_CVEHISTORY_URL", "https://services.nvd.nist.gov/rest/json/cvehistory/2.0")
NVD_API_KEY = os.getenv("NVD_API_KEY")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "security_feeds")
COLLECTIONS = {
    "nvd_cves_raw": os.getenv("MONGO_CVE_COLLECTION", "nvd_cves_raw"),
    "nvd_cpes_raw": os.getenv("MONGO_CPE_COLLECTION", "nvd_cpes_raw"),
    "nvd_cvehistory_raw": os.getenv("MONGO_CPEMATCH_COLLECTION", "nvd_cvehistory_raw"),
}

RESULTS_PER_PAGE = int(os.getenv("RESULTS_PER_PAGE", 200))
MAX_PAGES = int(os.getenv("MAX_PAGES", 20))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_SLEEP_SECONDS = int(os.getenv("RETRY_SLEEP_SECONDS", 3))

# --- MongoDB connection ---
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# --- Helper functions ---
def fetch_page(url, params):
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Fetching from {url}: {params}")
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("vulnerabilities") or data.get("products") or data.get("matches") or []
            total_results = data.get("totalResults", len(items))
            return items, total_results
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS)
            else:
                print(f"Skipping {url} after {MAX_RETRIES} failed attempts.")
                return [], 0

def upsert_many(collection_name, items, id_key="cve.id"):
    if not items:
        return 0
    collection = db[collection_name]
    operations = []
    for item in items:
        unique_id = None
        if id_key == "cve.id":
            unique_id = item.get("cve", {}).get("id")
        elif id_key == "cpeName":
            unique_id = item.get("cpe", {}).get("cpeName")
        elif id_key == "matchString":
            unique_id = item.get("matchString", {}).get("matchCriteriaId")
        if unique_id:
            operations.append(UpdateOne({"_id": unique_id}, {"$set": item}, upsert=True))
    if operations:
        result = collection.bulk_write(operations, ordered=False)
        return result.upserted_count + result.modified_count
    return 0

def run():
    ENDPOINTS = {
        "nvd_cves_raw": (NVD_CVE_URL, "cve.id"),
        "nvd_cpes_raw": (NVD_CPE_URL, "cpeName"),
        "nvd_cvehistory_raw": (NVD_CVEHISTORY_URL, "cve.id"),
    }

    for collection_name, (endpoint, id_key) in ENDPOINTS.items():
        print(f"\nProcessing endpoint: {endpoint}")
        total_processed = 0
        start_index = 0

        for page in range(MAX_PAGES):
            params = {"startIndex": start_index, "resultsPerPage": RESULTS_PER_PAGE}
            items, total_results = fetch_page(endpoint, params)
            if not items:
                print("No more records found or endpoint unavailable.")
                break
            count = upsert_many(collection_name, items, id_key=id_key)
            total_processed += count
            print(f"Upserted {count} records (total so far: {total_processed})")
            start_index += RESULTS_PER_PAGE
            if start_index >= total_results:
                print("Reached end of results.")
                break

        print(f"ETL completed for {collection_name}. Total processed: {total_processed}")

if __name__ == "__main__":
    run()