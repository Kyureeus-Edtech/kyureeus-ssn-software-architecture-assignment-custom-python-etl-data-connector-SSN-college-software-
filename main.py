from etl_connector.extractor import TorExitNodeExtractor
from etl_connector.transformer import TorExitNodeTransformer
from etl_connector.loader import TorExitNodeLoader
from etl_connector.utils import log

def run_etl():
    log("🚀 Starting Tor Exit Node ETL Pipeline")

    # Extract
    extractor = TorExitNodeExtractor()
    raw_data = extractor.fetch_data()
    log("✅ Data extraction complete.")

    # Transform
    transformer = TorExitNodeTransformer()
    structured_data = transformer.parse_exit_nodes(raw_data)
    log(f"✅ Data transformation complete. Parsed {len(structured_data)} nodes.")

    # Load
    loader = TorExitNodeLoader()
    inserted_count = loader.save_to_mongodb(structured_data)
    log(f"✅ Successfully inserted {inserted_count} records into MongoDB.")

if __name__ == "__main__":
    run_etl()
