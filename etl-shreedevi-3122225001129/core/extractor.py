import requests
import json
from core.utils import log

def extract_data(feed_name, url):
    log(f"Fetching data from {url}")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            with open(f"data_raw_{feed_name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            log(f"Saved raw data: data_raw_{feed_name}.json")
            return data
        else:
            log(f"Failed to fetch {feed_name}: {response.status_code}")
            return None
    except Exception as e:
        log(f"Error fetching {feed_name}: {e}")
        return None
