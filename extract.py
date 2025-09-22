import requests
import logging
import time
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

API_BASE = os.getenv("API_BASE")

def fetch_url(url, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                return None

def extract(endpoint):
    url = API_BASE + endpoint
    return fetch_url(url)

def extract_list_detail(list_id):
    url = f"{API_BASE}lists/{list_id}"
    return fetch_url(url)