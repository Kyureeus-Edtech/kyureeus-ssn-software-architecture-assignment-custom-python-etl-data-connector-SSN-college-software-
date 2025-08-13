import os
import requests
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

NVD_BASE_URL = os.getenv("NVD_BASE_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "security_feeds")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "nvd_cves_raw")
RESULTS_PER_PAGE = int(os.getenv("RESULTS_PER_PAGE", "200"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "5"))
PUB_START = os.getenv("PUB_START")
PUB_END = os.getenv("PUB_END")

def iso8601(dt: datetime) -> str:
    return dt.replace(microsecond=0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

def build_params(start_index: int) -> dict:
    params = {"startIndex": start_index, "resultsPerPage": RESULTS_PER_PAGE}
    if PUB_START and PUB_END:
        params["pubStartDate"] = PUB_START
        params["pubEndDate"] = PUB_END
    else:
        now = datetime.now(timezone.utc)
        params["pubStartDate"] = iso8601(now - timedelta(days=1))
        params["pubEndDate"] = iso8601(now)
    return params

def fetch_page(params: dict) -> list:
    print(f"Fetching: {params}")
    resp = requests.get(NVD_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("vulnerabilities", []), data.get("totalResults", 0)

def transform(v: dict, ingestion_ts: datetime) -> dict:
    cve = v.get("cve", {})
    cve_id = cve.get("id")
    desc = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), None)
    return {
        "_id": cve_id,
        "cveId": cve_id,
        "published": cve.get("published"),
        "lastModified": cve.get("lastModified"),
        "description": desc,
        "raw": v,
        "ingestionTimestamp": ingestion_ts.isoformat(),
    }

def save_to_mongo(docs: list):
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][MONGO_COLLECTION]
    for doc in docs:
        if doc["_id"]:
            col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
    client.close()

def run():
    ingestion_ts = datetime.now(timezone.utc)
    total_inserted = 0
    start_index = 0
    page_count = 0
    while page_count < MAX_PAGES:
        page_count += 1
        params = build_params(start_index)
        cves, total_results = fetch_page(params)
        if not cves:
            print("No more CVEs found.")
            break
        docs = [transform(v, ingestion_ts) for v in cves]
        save_to_mongo(docs)
        total_inserted += len(docs)
        print(f"Upserted {len(docs)} CVEs (total so far: {total_inserted})")
        start_index += RESULTS_PER_PAGE
        if total_results and start_index >= total_results:
            print("Reached end of results.")
            break
    print(f"ETL completed. Total CVEs processed: {total_inserted}")

if __name__ == "__main__":
    run()