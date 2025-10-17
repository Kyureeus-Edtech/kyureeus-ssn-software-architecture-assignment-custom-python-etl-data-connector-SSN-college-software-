from core.extractor import extract_single, extract_batch, extract_custom
from core.transformer import transform_record, transform_batch
from core.loader import load_to_mongo
from utils.db import get_mongo_collection
from utils.logger import logger

def run_etl():
    logger.info("Starting IP-API ETL Pipeline ....")

    collection = get_mongo_collection()

    # --- Single IP Extraction ---
    single_data = extract_single("8.8.8.8")
    transformed_single = transform_record(single_data)
    if transformed_single:
        load_to_mongo(collection, [transformed_single])

    # --- Batch Extraction ---
    batch_data = extract_batch(["8.8.8.8", "1.1.1.1", "208.67.222.222"])
    transformed_batch = transform_batch(batch_data)
    load_to_mongo(collection, transformed_batch)

    # --- Custom Fields Extraction ---
    custom_data = extract_custom("13.233.173.48", fields="66846719", lang="en")
    transformed_custom = transform_record(custom_data)
    if transformed_custom:
        load_to_mongo(collection, [transformed_custom])

    logger.info("ETL Pipeline completed successfully !")

if __name__ == "__main__":
    run_etl()
