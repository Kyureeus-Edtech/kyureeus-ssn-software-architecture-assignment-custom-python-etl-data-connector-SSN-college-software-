import requests
from pymongo import MongoClient

# ---------------- CONNECT TO MONGODB ----------------
client = MongoClient("mongodb://localhost:27017/") 
db = client["etl_database"]
spamhaus_collection = db["spamhaus_drop"]
cve_collection = db["nvd_cve"]

# ---------------- EXTRACT ----------------
def fetch_spamhaus():
    url = "https://www.spamhaus.org/drop/drop.txt"  # Spamhaus DROP List
    response = requests.get(url)
    response.raise_for_status()  
    return response.text.splitlines()

def fetch_nvd():
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# ---------------- TRANSFORM ----------------
def transform_spamhaus(lines):
    transformed = []
    for line in lines:
        if not line.strip() or line.startswith(";"):
            continue  # skip comments/empty
        parts = line.split(";")
        transformed.append({
            "network": parts[0].strip(),
            "description": parts[1].strip() if len(parts) > 1 else ""
        })
    return transformed

def transform_nvd(data):
    transformed = []
    vulnerabilities = data.get("vulnerabilities", [])
    for item in vulnerabilities:
        cve = item.get("cve", {})
        transformed.append({
            "cve_id": cve.get("id", ""),
            "description": (cve.get("descriptions", [{}])[0].get("value", "")) if cve.get("descriptions") else ""
        })
    return transformed

# ---------------- LOAD ----------------
def load_to_mongo(collection, data):
    if data:
        result = collection.insert_many(data)
        print(f"{len(result.inserted_ids)} documents inserted into '{collection.name}'")
    else:
        print(f"No data to insert into '{collection.name}'")

# ---------------- MAIN ETL PROCESS ----------------
def run_etl():
    print("Extracting data...")
    spamhaus_data = fetch_spamhaus()
    nvd_data = fetch_nvd()

    print("Transforming data...")
    transformed_spamhaus = transform_spamhaus(spamhaus_data)
    transformed_nvd = transform_nvd(nvd_data)

    print("Loading data into MongoDB...")
    load_to_mongo(spamhaus_collection, transformed_spamhaus)
    load_to_mongo(cve_collection, transformed_nvd)

    print("ETL process completed!")

if __name__ == "__main__":
    run_etl()
