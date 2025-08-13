from utils.extractor import get_blacklist, check_ip
from utils.transformer import transform_ip_data
from utils.loader import insert_many
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import time
import logging

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION_NAME")

RATE_LIMIT_SLEEP = 65  # seconds to wait after hitting rate limit


def run_pipeline():
    logging.info("[Info] Starting AbuseIPDB ETL pipeline...")

    # --- Connect to MongoDB ---
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        client.admin.command('ping')  # test connection
        logging.info("[Info] MongoDB connection successful.")
    except Exception as e:
        logging.error(f"[Error] Could not connect to MongoDB: {e}")
        return

    # --- Extract Blacklist ---
    blacklist_data = get_blacklist(limit=10)  # adjust as needed
    if not blacklist_data or not isinstance(blacklist_data, list):
        logging.warning("[Warning] Blacklist API returned no data or invalid format.")
        return

    # Deduplicate & Filter out already stored IPs
    ip_list = list({item["ipAddress"] for item in blacklist_data if "ipAddress" in item})
    existing_ips = set(doc["ipAddress"] for doc in collection.find({}, {"ipAddress": 1}))
    new_ips = [ip for ip in ip_list if ip not in existing_ips]

    if not new_ips:
        logging.info("[Info] No new IPs to check. Exiting.")
        return

    # --- Check each new IP ---
    all_ip_details = []
    for ip in new_ips:
        logging.info(f"[Info] Checking IP: {ip}")
        try:
            details = check_ip(ip)

            # --- Handle rate limits ---
            if details is None:
                logging.warning(f"[Warning] No response for {ip}, skipping.")
                continue

            if isinstance(details, dict) and details.get("errors"):
                error_msg = details["errors"][0].get("detail", "").lower()
                if "rate limit" in error_msg:
                    logging.warning("[Warning] Rate limit hit, sleeping...")
                    time.sleep(RATE_LIMIT_SLEEP)
                    continue

            # --- Transform & Validate ---
            transformed = transform_ip_data(details)
            if transformed:
                transformed["ingestedAt"] = datetime.now(timezone.utc).isoformat()
                all_ip_details.append(transformed)
            else:
                logging.warning(f"[Warning] Invalid payload for IP {ip}, skipping.")

        except Exception as e:
            logging.error(f"[Error] Failed to process {ip}: {e}")
            continue

    # --- Load into MongoDB ---
    if all_ip_details:
        try:
            insert_many(all_ip_details)
            logging.info(f"[Info] Inserted {len(all_ip_details)} new documents.")
        except Exception as e:
            logging.error(f"[Error] Failed to insert documents: {e}")
    else:
        logging.warning("[Warning] No valid IP data to insert.")

    logging.info("[Info] Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
