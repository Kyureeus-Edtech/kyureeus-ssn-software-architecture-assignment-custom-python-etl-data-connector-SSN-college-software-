import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cve_data")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["cve_records"]

HEADERS = {"User-Agent": "Simple CVE Fetcher Script"}

def save_to_mongo(data):
    """Save response to MongoDB."""
    try:
        collection.insert_one(data)
        print(f"✅ Saved to MongoDB: {data.get('cve', data.get('vendorproduct', 'N/A'))}")
    except Exception as e:
        print(f"⚠️ MongoDB Insert Error: {e}")

def circllu_cveinfo(cve):
    url = f"http://cve.circl.lu/api/cve/{cve.upper()}"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            reply = res.json()
            if reply:
                result = {
                    "type": "cveinfo",
                    "cve": cve.upper(),
                    "summary": reply.get("summary"),
                    "references": reply.get("references", []),
                    "url": url
                }
                save_to_mongo(result)
                return result
        return {"success": False, "reason": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "exception": str(e)}

def circllu_cverecent(maxcves=0):
    url = "http://cve.circl.lu/api/last"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            reply = res.json()
            cves = [r["id"] for r in reply if "REJECT" not in r.get("summary", "")]
            result = {
                "type": "recent",
                "cves": cves if maxcves == 0 else cves[:maxcves],
                "url": url
            }
            save_to_mongo(result)
            return result
        return {"success": False, "reason": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "exception": str(e)}

def circllu_cvesearch(vendorproduct, maxcves=0):
    if not vendorproduct:
        return {"success": False, "usage": "<vendor> <product>"}
    path = "/".join(vendorproduct.lower().split())
    url = f"http://cve.circl.lu/api/search/{path}"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            reply = res.json()
            cves = [r["id"] for r in reply if "REJECT" not in r.get("summary", "")]
            result = {
                "type": "search",
                "vendorproduct": path.title(),
                "cves": sorted(cves, reverse=True) if maxcves == 0 else sorted(cves, reverse=True)[:maxcves],
                "url": url
            }
            save_to_mongo(result)
            return result
        return {"success": False, "reason": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "exception": str(e)}

def circllu_dbinfo():
    url = "https://cve.circl.lu/api/dbInfo"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            result = {
                "type": "dbinfo",
                "url": url,
                "result": res.json()
            }
            save_to_mongo(result)
            return result
        return {"success": False, "reason": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "exception": str(e)}

if __name__ == "__main__":
    print("Fetching CVE info for CVE-2021-44228...")
    print(circllu_cveinfo("CVE-2021-44228"))

    print("\nFetching recent CVEs...")
    print(circllu_cverecent(5))

    print("\nSearching CVEs for Adobe Reader...")
    print(circllu_cvesearch("Adobe Reader", 5))

    print("\nFetching database info...")
    print(circllu_dbinfo())
