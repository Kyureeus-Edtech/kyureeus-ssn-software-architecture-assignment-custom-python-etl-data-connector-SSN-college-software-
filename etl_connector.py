import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("NVD_API_KEY")

BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def fetch_cves(start_index=0, results_per_page=50):
    headers = {}
    if API_KEY:
        headers["apiKey"] = API_KEY
    
    params = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page
    }
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def transform_cve_data(raw_data):
    transformed = []
    for vuln in raw_data.get("vulnerabilities", []):
        cve = vuln["cve"]

        desc = ""
        for d in cve.get("descriptions", []):
            if d["lang"] == "en":
                desc = d["value"]
                break

        severity = None
        score = None
        if "metrics" in cve and "cvssMetricV2" in cve["metrics"]:
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
            "ingestion_timestamp": datetime.utcnow()
        })
    return transformed

def load_to_mongo(data):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["etl_project"]
    collection = db["nvd_cves_raw"]
    if data:
        collection.insert_many(data)
        print(f"Inserted {len(data)} records into MongoDB.")
    else:
        print("No data to insert.")

if __name__ == "__main__":
    raw = fetch_cves(start_index=0, results_per_page=50)
    transformed = transform_cve_data(raw)
    load_to_mongo(transformed)
    print("ETL pipeline completed.")