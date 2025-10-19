import os
import requests
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

collections = {
    "cloudflare": db["varshini_doh_cloudflare_raw"],
    "google": db["varshini_doh_google_raw"],
    "nextdns": db["varshini_doh_nextdns_raw"]
}

CLOUDFLARE_DOHE_URL = "https://cloudflare-dns.com/dns-query"
GOOGLE_DOHE_URL = "https://dns.google/resolve"
NEXTDNS_PROFILE_ID = os.getenv("NEXTDNS_PROFILE_ID")
NEXTDNS_DOHE_URL = f"https://dns.nextdns.io/{NEXTDNS_PROFILE_ID}"

domains = ["example.com", "cloudflare.com", "google.com", "openai.com"]

def extract(provider, domain):
    try:
        if provider == "cloudflare":
            response = requests.get(CLOUDFLARE_DOHE_URL, params={"name": domain, "type": "A"}, headers={"accept": "application/dns-json"}, timeout=10)
        elif provider == "google":
            response = requests.get(GOOGLE_DOHE_URL, params={"name": domain, "type": "A"}, headers={"accept": "application/dns-json"}, timeout=10)
        elif provider == "nextdns":
            response = requests.get(NEXTDNS_DOHE_URL, params={"name": domain, "type": "A"}, headers={"accept": "application/dns-json"}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"{provider.capitalize()} error for {domain}: {e}")
        return None

def transform(dns_json):
    if not dns_json:
        return []
    answers = dns_json.get("Answer") or dns_json.get("answer") or []
    transformed = []
    for ans in answers:
        transformed.append({
            "name": ans.get("name"),
            "type": ans.get("type"),
            "TTL": ans.get("TTL"),
            "data": ans.get("data")
        })
    return transformed

def load(provider, records):
    if records:
        for record in records:
            try:
                collections[provider].update_one(
                    {"name": record["name"], "type": record["type"], "provider": provider},
                    {"$set": {**record, "provider": provider}},
                    upsert=True
                )
            except Exception as e:
                print(f"Failed to insert/update into MongoDB ({provider}): {e}")

def main():
    for provider in collections:
        for domain in tqdm(domains, desc=f"Processing {provider} domains"):
            data = extract(provider, domain)
            transformed = transform(data)
            load(provider, transformed)

if __name__ == "__main__":
    main()
