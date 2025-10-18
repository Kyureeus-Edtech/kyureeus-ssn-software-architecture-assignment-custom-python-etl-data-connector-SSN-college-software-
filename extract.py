# extract.py
import requests
from config import API_BASE, USER_AUTH

# Add authentication if needed
HEADERS = {"Authorization": f"Bearer {USER_AUTH}"} if USER_AUTH else {}


#BROWSE ENDPOINTS
def get_vendors():
    return requests.get(f"{API_BASE}/browse/", headers=HEADERS).json()

def get_products(vendor):
    return requests.get(f"{API_BASE}/browse/{vendor}", headers=HEADERS).json()

#VULNERABILITY ENDPOINTS
def search_vulnerabilities(vendor, product):
    return requests.get(f"{API_BASE}/vulnerability/search/{vendor}/{product}", headers=HEADERS).json()

def get_vulnerability(vuln_id):
    return requests.get(f"{API_BASE}/vulnerability/{vuln_id}", headers=HEADERS).json()

def get_last_vulnerabilities(n=None):
    url = f"{API_BASE}/vulnerability/last" + (f"/{n}" if n else "")
    return requests.get(url, headers=HEADERS).json()

def get_recent_vulnerabilities():
    return requests.get(f"{API_BASE}/vulnerability/recent", headers=HEADERS).json()

#COMMENT ENDPOINTS
def get_comments():
    return requests.get(f"{API_BASE}/comment/", headers=HEADERS).json()

def get_comment(comment_uuid):
    return requests.get(f"{API_BASE}/comment/{comment_uuid}", headers=HEADERS).json()

#SIGHTING ENDPOINTS
def get_sightings():
    return requests.get(f"{API_BASE}/sighting/", headers=HEADERS).json()

#STATISTICS ENDPOINTS
def get_stats_most_commented():
    return requests.get(f"{API_BASE}/stats/vulnerability/most_commented", headers=HEADERS).json()

def get_stats_most_sighted():
    return requests.get(f"{API_BASE}/stats/vulnerability/most_sighted", headers=HEADERS).json()
