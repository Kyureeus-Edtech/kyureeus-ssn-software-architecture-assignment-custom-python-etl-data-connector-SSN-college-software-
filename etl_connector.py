import os
import time
import requests
import logging
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME")

DOMAIN_QUERIES = ["ssn.edu.in", "google.com"]
IP_QUERIES = ["8.8.8.8", "1.1.1.1"]
ASN_QUERIES = ["15169", "13335"]


# Logging setup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# MongoDB setup

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collections = {
    "domain": db["rdap_domain_raw"],
    "ip": db["rdap_ip_raw"],
    "asn": db["rdap_asn_raw"]
}


# Extract Function

def fetch_rdap(endpoint_type, query):
    """Fetch data from RDAP API with retries"""
    url = f"https://rdap.org/{endpoint_type}/{query.strip()}"
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json(), url
            elif response.status_code == 429:
                logging.warning("Rate limit hit. Retrying...")
                time.sleep(2 ** attempt)
            else:
                logging.error(f"{endpoint_type} {query}: Error {response.status_code}")
                return None, url
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            time.sleep(2 ** attempt)
    return None, url


# Transform Function

def transform_rdap(data, source_type, api_url):
    """Extract minimal but useful fields from RDAP response"""
    if not data:
        return None

    # Flattened entities (just  name, email, roles)
    entities = []
    for ent in data.get("entities", []):
        ent_data = {}
        vcard = ent.get("vcardArray")
        if vcard and len(vcard) > 1:
            for field in vcard[1]:
                if field[0] == "fn":
                    ent_data["name"] = field[3]
                elif field[0] == "email":
                    ent_data["email"] = field[3]
                elif field[0] == "org":
                    ent_data["organization"] = field[3]
        if ent.get("roles"):
            ent_data["roles"] = ent.get("roles")
        if ent_data:  # only add non-empty
            entities.append(ent_data)

    
    record = {
        "handle": data.get("handle"),
        "status": data.get("status"),
        "name": data.get("name") or data.get("ldhName"),
        "entities": entities[:3],  # only keep first 3 entities to avoid bloat
        "_type": source_type,
        "_url": api_url,
        "_at": datetime.utcnow().isoformat()
    }

    # Add type-specific essentials
    if source_type == "domain":
        record["nameservers"] = [ns.get("ldhName") for ns in data.get("nameservers", [])[:3]]
    elif source_type == "ip":
        record["range"] = f"{data.get('startAddress')} - {data.get('endAddress')}"
        record["version"] = data.get("ipVersion")
    elif source_type == "asn":
        record["asn_range"] = f"{data.get('startAutnum')} - {data.get('endAutnum')}"

    # Drop keys with None or empty lists
    record = {k: v for k, v in record.items() if v not in [None, [], ""]}

    return record


# Load Function

def load_to_mongo(records, source_type):
    """Insert multiple records into MongoDB"""
    if records:
        collections[source_type].insert_many(records)
        logging.info(f"Inserted {len(records)} records into {source_type} collection")

        # Show first inserted record
        sample = collections[source_type].find_one(sort=[("_id", -1)])
        #print(f"\n📥 Sample loaded {source_type} record in MongoDB:")
        #print(json.dumps(sample, indent=2, default=str))

    else:
        logging.warning(f"No valid records to insert for {source_type}")


# ETL Runner

def run_etl():
    logging.info("Starting RDAP ETL pipeline...")

    domain_records, ip_records, asn_records = [], [], []

    # Domain ETL
    for i, d in enumerate(DOMAIN_QUERIES):
        raw, url = fetch_rdap("domain", d)
        if raw and i == 0:  # print only first domain fetched
            print("\nRaw Fetched Domain Data:")
            print(json.dumps({k: raw[k] for k in list(raw.keys())[:5]}, indent=2))

        record = transform_rdap(raw, "domain", url)
        if record:
            if i == 0:  # print only first transformed domain
                print("\nTransformed Domain Data:")
                print(json.dumps(record, indent=2, default=str))
            domain_records.append(record)

    # IP ETL
    for i, ip in enumerate(IP_QUERIES):
        raw, url = fetch_rdap("ip", ip)
        if raw and i == 0:
            print("\nRaw Fetched IP Data:")
            print(json.dumps({k: raw[k] for k in list(raw.keys())[:5]}, indent=2))

        record = transform_rdap(raw, "ip", url)
        if record:
            if i == 0:
                print("\nTransformed IP Data:")
                print(json.dumps(record, indent=2, default=str))
            ip_records.append(record)

    # ASN ETL
    for i, asn in enumerate(ASN_QUERIES):
        raw, url = fetch_rdap("autnum", asn)
        if raw and i == 0:
            print("\nRaw Fetched ASN Data:")
            print(json.dumps({k: raw[k] for k in list(raw.keys())[:5]}, indent=2))

        record = transform_rdap(raw, "asn", url)
        if record:
            if i == 0:
                print("\nTransformed ASN Data:")
                print(json.dumps(record, indent=2, default=str))
            asn_records.append(record)

    # Load all data and show one sample per collection
    load_to_mongo(domain_records, "domain")
    load_to_mongo(ip_records, "ip")
    load_to_mongo(asn_records, "asn")

    logging.info("RDAP ETL pipeline finished ")

# -----------------------
# Validation & Testing
# -----------------------
def validate_pipeline():
    logging.info("Running validation tests...")

    # Invalid domain
    raw, url = fetch_rdap("domain", "notarealdomain.abcxyz")
    assert raw is None, "Invalid domain should return None"

    # Invalid IP
    raw, url = fetch_rdap("ip", "999.999.999.999")
    assert raw is None, "Invalid IP should return None"

    # Invalid ASN
    raw, url = fetch_rdap("autnum", "999999999999")
    assert raw is None, "Invalid ASN should return None"

    # Empty data handling
    transformed = transform_rdap({}, "domain", "test_url")
    assert transformed is None, "Empty JSON should not be transformed"

    # Check Mongo insertions
    count_domain = collections["domain"].count_documents({})
    count_ip = collections["ip"].count_documents({})
    count_asn = collections["asn"].count_documents({})

    assert count_domain >= 0, "Domain collection should exist"
    assert count_ip >= 0, "IP collection should exist"
    assert count_asn >= 0, "ASN collection should exist"

    logging.info("All validation tests passed")

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    run_etl()
    validate_pipeline()
