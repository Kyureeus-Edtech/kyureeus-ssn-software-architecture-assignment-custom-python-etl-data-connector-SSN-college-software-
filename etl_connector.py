import logging
import sys
from extract import extract, extract_list_detail
from transform import transform
from load import load, load_list_details

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

endpoints = [
    "languages",
    "licenses",
    "lists",
    "maintainers",
    "syntaxes",
    "tags",
    "software"
]

def run_etl():
    for ep in endpoints:
        logging.info(f"Fetching {ep}")
        data = extract(ep)
        if not data:
            logging.error(f"No data fetched for {ep}")
            continue
        limit = 10 if ep == "lists" else 100
        records = transform(data, limit=limit)
        load(ep, records)
        if ep == "lists":
            load_list_details(records, extract_list_detail)

if __name__ == "__main__":
    try:
        run_etl()
        logging.info("ETL process completed successfully")
    except Exception as e:
        logging.critical(f"Fatal error: {e}")