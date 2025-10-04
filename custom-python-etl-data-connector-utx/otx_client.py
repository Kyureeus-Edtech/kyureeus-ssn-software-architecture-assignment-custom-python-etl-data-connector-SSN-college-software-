import os
import requests
from dotenv import load_dotenv

load_dotenv()

OTX_BASE_URL = "https://otx.alienvault.com/api/v1"
API_KEY = os.getenv("OTX_API_KEY")

HEADERS = {"X-OTX-API-KEY": API_KEY}

def _request(method, endpoint, data=None, params=None):
    url = f"{OTX_BASE_URL}{endpoint}"
    try:
        resp = requests.request(method, url, headers=HEADERS, json=data, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error on {endpoint}: {e}")
        return None

# --- PULSES ---
def get_subscribed_pulses():
    return _request("get", "/pulses/subscribed")

def get_my_pulses():
    return _request("get", "/pulses/my")

def get_pulse_activity():
    return _request("get", "/pulses/activity")

# --- INDICATORS ---
def get_indicator_by_ip(ip, section="general"):
    return _request("get", f"/indicators/IPv4/{ip}/{section}")

def get_indicator_by_domain(domain, section="general"):
    return _request("get", f"/indicators/domain/{domain}/{section}")

def get_indicator_by_cve(cve, section="general"):
    return _request("get", f"/indicators/cve/{cve}/{section}")
