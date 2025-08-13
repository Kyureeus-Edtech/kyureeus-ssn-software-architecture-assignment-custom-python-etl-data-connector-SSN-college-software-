"""
USed GreyNoise API for IP Lookup and performed ETL
- Extracting data from GreyNoise Community API
- Transforming by adding fetching timestamp and source
- Loading into MongoDB compass
"""

import sys
import logging
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from requests.exceptions import RequestException

from extract import fetch_greynoise
from transform import transform_data
from load import save_results, get_db_col

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("greynoise_etl")

# Main ETL function
def run_etl(ip_list):
    """Run ETL for a list of IPs."""
    col = get_db_col()
    docs = []

    for ip in ip_list:
        try:
            logger.info(f"Processing IP: {ip}")
            raw_data = fetch_greynoise(ip)
            doc = transform_data(ip, raw_data)
            docs.append(doc)
        except RequestException as e:
            logger.error(f"API request failed for {ip}: {e}")
        except ValueError as e:
            logger.warning(str(e))
        except Exception as e:
            logger.exception(f"Unexpected error for {ip}: {e}")

    if docs:
        try:
            inserted_count = save_results(col, docs)
            logger.info(f"Inserted {inserted_count} new records into MongoDB.")
        except PyMongoError as e:
            logger.exception(f"MongoDB write failed: {e}")
    else:
        logger.info("No valid IP data to insert.")

if __name__ == "__main__":
    load_dotenv()
    ips = input("Enter IP addresses (comma-separated): ").split(",")
    ips = [ip.strip() for ip in ips if ip.strip()]
    if not ips:
        logger.error("No IPs provided. Exiting.")
        sys.exit(1)
    run_etl(ips)