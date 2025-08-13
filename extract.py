import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

if not API_URL:
    raise RuntimeError("Missing API_URL in environment variables.")

def fetch_greynoise(ip):
    url = API_URL + ip
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()
