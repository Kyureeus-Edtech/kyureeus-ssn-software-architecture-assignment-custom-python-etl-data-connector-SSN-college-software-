#!/usr/bin/env python3
import sys
import json
import requests
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "submissions")  

def store_in_mongodb(data):
    """Store data in MongoDB with timestamp."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Add timestamp field
        data["timestamp"] = datetime.now(timezone.utc)

        collection.insert_one(data)
        print("[INFO] Stored response in MongoDB.")
    except Exception as e:
        print("[ERROR] MongoDB insertion failed:", e)
    finally:
        client.close()


def report_urlhaus(auth_key, url, anonymous=False, tags=None):
    if tags is None:
        tags = []

    jsonData = {
        'anonymous': '1' if anonymous else '0',
        'submission': [
            {
                'url': url,
                'threat': 'malware_download',
                'tags': tags
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Auth-Key": auth_key
    }

    try:
        r = requests.post(
            'https://urlhaus.abuse.ch/api/',
            json=jsonData,
            timeout=15,
            headers=headers
        )
        r.raise_for_status()

        response_data = {
            "url": url,
            "status_code": r.status_code,
            "response_body": r.text,
            "anonymous": anonymous,
            "tags": tags
        }

        print("[INFO] Response status:", r.status_code)
        print("[INFO] Response body:", r.text)

        # Store in MongoDB
        store_in_mongodb(response_data)

    except requests.exceptions.RequestException as e:
        print("[ERROR] Submission failed:", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Report a malware URL to URLhaus")
        print("Usage: python3 submit_url.py <YOUR-AUTH-KEY> <URL> [anonymous] [tag1,tag2,...]")
        print("Example: python3 submit_url.py mykey123 https://malicious.example.com 1 Emotet,doc")
    else:
        auth_key = sys.argv[1]
        url = sys.argv[2]
        anonymous = len(sys.argv) > 3 and sys.argv[3] == "1"
        tags = sys.argv[4].split(",") if len(sys.argv) > 4 else []
        report_urlhaus(auth_key, url, anonymous, tags)
