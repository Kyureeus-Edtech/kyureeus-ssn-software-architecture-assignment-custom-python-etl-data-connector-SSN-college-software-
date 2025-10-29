import json
from core.extractor import extract_data
from core.transformer import transform_data
from core.loader import load_to_mongodb
from core.utils import log

def run_etl():
    with open("config/endpoints.json", "r") as f:
        config = json.load(f)
    
    base_url = config["base_url"]
    feeds = config["feeds"]

    for name, endpoint in feeds.items():
        full_url = f"{base_url}{endpoint}"
        log(f"Starting ETL for {name}")
        data = extract_data(name, full_url)

        # only transform if data is a list or dict
        if isinstance(data, dict):
            data = [data]  # wrap single dicts

        if not data:
            log(f"No valid data returned for {name}, skipping...\n")
            continue

        transformed = transform_data(data, name)
        load_to_mongodb(transformed, name)
        log(f"Completed ETL for {name}\n")

if __name__ == "__main__":
    run_etl()
