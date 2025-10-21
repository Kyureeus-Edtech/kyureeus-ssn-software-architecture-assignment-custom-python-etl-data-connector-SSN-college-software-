# main.py
import config
from connectors.abusech_api import AbuseCHConnector
from transformations.data_transformer import (
    standardize_urlhaus_data,
    standardize_malwarebazaar_data
)
from database.mongo_loader import MongoLoader

def main():
    """Main ETL pipeline function."""
    # Initialize connector with the API key and the loader

    print(f"DEBUG: The API key being used is: '{config.ABUSECH_API_KEY}'")
    try:
        connector = AbuseCHConnector(api_key=config.ABUSECH_API_KEY)
    except ValueError as e:
        print(f"Error: {e}")
        return

    loader = MongoLoader(config.MONGO_URI)

    # --- URLhaus ETL ---
    urlhaus_raw = connector.get_urlhaus_recent()
    if urlhaus_raw:
        urlhaus_transformed = standardize_urlhaus_data(urlhaus_raw)
        loader.upsert_data('urlhaus_iocs', urlhaus_transformed)

    # --- MalwareBazaar ETL ---
    malwarebazaar_raw = connector.get_malwarebazaar_recent()
    if malwarebazaar_raw:
        malwarebazaar_transformed = standardize_malwarebazaar_data(malwarebazaar_raw)
        loader.upsert_data('malwarebazaar_iocs', malwarebazaar_transformed)

    # Clean up
    loader.close_connection()

if __name__ == "__main__":
    main()