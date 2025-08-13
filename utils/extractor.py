import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY")
BASE_URL = "https://api.abuseipdb.com/api/v2"

HEADERS = {
    "Accept": "application/json",
    "Key": API_KEY
}

import time

def get_blacklist(limit=10):
    url = f"{BASE_URL}/blacklist"
    params = {"limit": limit}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=None)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"[Error] Blacklist API request failed: {e}")
        return []

def check_ip(ip):
    """
    Check details for a single IP address in AbuseIPDB.
    """
    url = f"{BASE_URL}/check"
    params = {"ipAddress": ip, "maxAgeInDays": "90"}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.RequestException as e:
        print(f"[Error] Check API request failed for {ip}: {e}")
        return {}
