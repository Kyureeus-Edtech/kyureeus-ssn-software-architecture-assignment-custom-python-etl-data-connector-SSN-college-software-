from src.api_client import get_ip_info
from src.transformer import transform_ip_data
from src.loader import get_mongo_client, load_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_ip_pipeline(client: "MongoClient", ips_to_process: list):
    """
    Runs the full ETL pipeline for the /ip/{ip} endpoint.
    """
    logger.info("--- Starting /ip/{ip} Pipeline ---")
    for ip in ips_to_process:
        # 1. EXTRACT
        raw_data = get_ip_info(ip)
        
        if raw_data:
            # 2. TRANSFORM
            transformed_data = transform_ip_data(raw_data)
            
            # 3. LOAD
            if transformed_data:
                load_data(client, 
                          collection_name="subnet_info", 
                          data=transformed_data, 
                          unique_key="cidr_notation") 
    logger.info("--- /ip/{ip} Pipeline Finished ---")


if __name__ == "__main__":
    # --- Define your data to process ---
    IPS_TO_CHECK = ["8.8.8.8", "1.1.1.1", "192.168.1.1", "9.9.9.9", "104.26.10.229"]

    # --- Run the pipeline ---
    mongo_client = get_mongo_client()
    
    if mongo_client:
        # Run the one and only pipeline
        run_ip_pipeline(mongo_client, IPS_TO_CHECK)
        
        # Close the connection
        mongo_client.close()
        logger.info("All pipelines finished. MongoDB connection closed.")
    else:
        logger.critical("Failed to connect to MongoDB. ETL process aborted.")