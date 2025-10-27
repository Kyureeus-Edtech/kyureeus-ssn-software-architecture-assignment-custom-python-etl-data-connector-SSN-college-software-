import requests

BASE_URL = "https://haveibeenpwned.com/api/v3"
USER_AGENT = "custom-hibp-etl-client"

HEADERS = {
    "user-agent": USER_AGENT
}

def get_with_retry(endpoint, retries=3, timeout=15):
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            # For password range API, return text (not JSON)
            if endpoint.startswith("/range/"):
                return resp.text
            return resp.json()
        except Exception as e:
            if attempt < retries - 1:
                continue
            else:
                print(f"❌ Error fetching {url}: {e}")
                return None

# Free endpoints
def list_breaches():
    return get_with_retry("/breaches")

def breach_by_name(name="Adobe"):
    return get_with_retry(f"/breach/{name}")

def data_classes():
    return get_with_retry("/dataclasses")

def pwned_password_range(first5hash="21BD1"):
    url = f"https://api.pwnedpasswords.com/range/{first5hash}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None
