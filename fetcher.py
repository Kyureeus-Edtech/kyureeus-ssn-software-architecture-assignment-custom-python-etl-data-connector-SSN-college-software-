# fetcher.py
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import JSON_ENDPOINT, CSV_ENDPOINT, BATCH_ENDPOINT, REQUEST_TIMEOUT, USER_AGENT, MAX_RETRIES
from typing import List, Dict, Any

HEADERS = {"User-Agent": USER_AGENT}

@retry(wait=wait_exponential(multiplier=1, min=2, max=30),
       stop=stop_after_attempt(MAX_RETRIES),
       retry=retry_if_exception_type(Exception))
def fetch_single(query: str = "") -> Dict[str, Any]:
    """Fetch a single IP/domain from ip-api JSON endpoint."""
    url = f"{JSON_ENDPOINT}/{query}" if query else JSON_ENDPOINT
    resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
    if resp.status_code == 429:
        raise Exception("Rate limited (429)")
    resp.raise_for_status()
    return resp.json()

@retry(wait=wait_exponential(multiplier=1, min=2, max=30),
       stop=stop_after_attempt(MAX_RETRIES),
       retry=retry_if_exception_type(Exception))
def fetch_csv(query: str = "", fields: str = "") -> str:
    """Fetch CSV as text (optional fields)."""
    url = f"{CSV_ENDPOINT}/{query}" if query else CSV_ENDPOINT
    if fields:
        url = f"{url}?fields={fields}"
    resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
    if resp.status_code == 429:
        raise Exception("Rate limited (429)")
    resp.raise_for_status()
    return resp.text

@retry(wait=wait_exponential(multiplier=1, min=2, max=30),
       stop=stop_after_attempt(MAX_RETRIES),
       retry=retry_if_exception_type(Exception))
def fetch_batch(queries: List[str]) -> List[Dict]:
    """Fetch batch of IPs/domains."""
    url = BATCH_ENDPOINT
    resp = requests.post(url, json=queries, timeout=REQUEST_TIMEOUT, headers=HEADERS)
    if resp.status_code == 429:
        raise Exception("Batch rate limited (429)")
    resp.raise_for_status()
    return resp.json()

def chunked_iterable(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]
