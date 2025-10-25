import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# --- Load environment variables ---
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "filterlists_data")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["filterlists_records"]

BASE_URL = "https://api.filterlists.com"
HEADERS = {"User-Agent": "Simple FilterLists Fetcher"}

def save_to_mongo(data_type, data):
    """Save response data to MongoDB."""
    try:
        collection.insert_one({
            "type": data_type,
            "data": data
        })
        print(f"✅ Saved '{data_type}' data to MongoDB.")
    except Exception as e:
        print(f"⚠️ MongoDB Insert Error: {e}")

def fetch_data(endpoint, data_type):
    """Generic function to fetch data from FilterLists API."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            save_to_mongo(data_type, data)
            return {"success": True, "url": url, "count": len(data) if isinstance(data, list) else 1}
        else:
            return {"success": False, "reason": f"HTTP {res.status_code}", "url": url}
    except Exception as e:
        return {"success": False, "exception": str(e), "url": url}

def get_languages():
    return fetch_data("languages", "languages")

def get_licenses():
    return fetch_data("licenses", "licenses")

def get_filterlists():
    return fetch_data("lists", "filterlists")

def get_filterlist_by_id(list_id):
    return fetch_data(f"lists/{list_id}", f"filterlist_{list_id}")

def get_maintainers():
    return fetch_data("maintainers", "maintainers")

def get_software():
    return fetch_data("software", "software")

def get_syntaxes():
    return fetch_data("syntaxes", "syntaxes")

def get_tags():
    return fetch_data("tags", "tags")

if __name__ == "__main__":
    print("Fetching FilterLists data...")

    print(get_languages())
    print(get_licenses())
    print(get_filterlists())
    print(get_maintainers())
    print(get_software())
    print(get_syntaxes())
    print(get_tags())

    # Example for a single list (optional)
    print("\nFetching details of FilterList ID 1:")
    print(get_filterlist_by_id(1))