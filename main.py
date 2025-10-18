import logging
from pipeline.extract import extract_data
from pipeline.transform import transform_data
from pipeline.load import load_to_mongo

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("STARTING Abuse.ch ETL pipeline\n")

    raw = extract_data()
    transformed = transform_data(raw)
    load_to_mongo(transformed)

    logging.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()
