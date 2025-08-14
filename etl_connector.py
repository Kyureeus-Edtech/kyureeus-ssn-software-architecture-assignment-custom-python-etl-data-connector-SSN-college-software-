import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(funcName)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

class CISAVulnerabilityETL:
   
    CISA_API_ENDPOINT = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    TARGET_COLLECTION = "cisa_vulnerabilities_raw"
    REQUEST_TIMEOUT = 20
    
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.database_name = os.getenv("DB_NAME", "security_intelligence")
        
        if not self.mongo_uri:
            raise EnvironmentError("MONGO_URI environment variable must be set")
        
        logger.info("CISA Vulnerability ETL Pipeline initialized")
        logger.info(f"MongoDB URI configured: {self.mongo_uri[:20]}...")
    
    def fetch_vulnerability_data(self):

        logger.info("Initiating data fetch from CISA KEV API...")
        
        request_headers = {
            'User-Agent': 'Educational-ETL-Pipeline/1.0',
            'Accept': 'application/json, text/plain, /',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        try:
            api_response = requests.get(
                self.CISA_API_ENDPOINT,
                headers=request_headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            # Check if request was successful
            api_response.raise_for_status()
            
            # Parse JSON response
            vulnerability_data = api_response.json()
            
            # Validate response structure
            if not isinstance(vulnerability_data, dict):
                raise ValueError("API returned invalid data format")
            
            if 'vulnerabilities' not in vulnerability_data:
                raise KeyError("Missing 'vulnerabilities' key in API response")
            
            vuln_list = vulnerability_data.get('vulnerabilities', [])
            catalog_version = vulnerability_data.get('catalogVersion', 'Unknown')
            
            logger.info(f"Data fetch successful - Catalog: {catalog_version}, Records: {len(vuln_list)}")
            return vulnerability_data
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout - CISA API did not respond within time limit")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - Unable to reach CISA API")
            return None
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return None
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response from API")
            return None
        except Exception as general_error:
            logger.error(f"Unexpected error during data fetch: {general_error}")
            return None
    
    def process_vulnerability_records(self, api_data):

        if not api_data or not isinstance(api_data, dict):
            logger.warning("No valid data provided for processing")
            return []
        
        vulnerability_records = api_data.get('vulnerabilities', [])
        
        if not vulnerability_records:
            logger.warning("No vulnerability records found in API data")
            return []
        
        logger.info(f"Processing {len(vulnerability_records)} vulnerability records...")
        
        # Extract catalog metadata
        catalog_metadata = {
            'source_catalog_version': api_data.get('catalogVersion'),
            'catalog_release_date': api_data.get('dateReleased'),
            'total_vulnerabilities': api_data.get('count'),
            'data_extraction_time': datetime.utcnow().isoformat()
        }
        
        processed_vulnerabilities = []
        
        for index, vulnerability in enumerate(vulnerability_records):
            try:
                enhanced_record = self._enhance_vulnerability_record(
                    vulnerability, catalog_metadata, index
                )
                
                if enhanced_record:
                    processed_vulnerabilities.append(enhanced_record)
                    
            except Exception as processing_error:
                logger.warning(f"Failed to process record {index}: {processing_error}")
                continue
        
        logger.info(f"Successfully processed {len(processed_vulnerabilities)} records")
        return processed_vulnerabilities
    
    def _enhance_vulnerability_record(self, vuln_record, catalog_info, record_position):

        enhanced_vuln = dict(vuln_record)
        
        processing_time = datetime.utcnow()
        enhanced_vuln.update({
            'record_processed_at': processing_time,
            'processing_date': processing_time.date().isoformat(),
            'record_position': record_position,
            'source_system': 'cisa_kev_catalog',
            'catalog_information': catalog_info
        })
        
        # Parse date fields if they exist
        date_fields_to_parse = ['dateAdded', 'dueDate']
        for date_field in date_fields_to_parse:
            if date_field in vuln_record and vuln_record[date_field]:
                try:
                    parsed_date = datetime.strptime(vuln_record[date_field], '%Y-%m-%d')
                    enhanced_vuln[f'{date_field}_datetime'] = parsed_date
                except ValueError as date_error:
                    logger.debug(f"Could not parse {date_field}: {date_error}")
        
        return enhanced_vuln
    
    def store_in_mongodb(self, processed_records):
        if not processed_records:
            logger.warning("No records provided for storage")
            return False
        
        logger.info(f"Storing {len(processed_records)} records in MongoDB...")
        
        mongo_client = None
        try:
            mongo_client = MongoClient(self.mongo_uri)
            target_database = mongo_client[self.database_name]
            vulnerability_collection = target_database[self.TARGET_COLLECTION]
            
            # Clear existing data for fresh load
            existing_record_count = vulnerability_collection.count_documents({})
            if existing_record_count > 0:
                vulnerability_collection.delete_many({})
                logger.info(f"Removed {existing_record_count} existing records")
            
            insertion_result = vulnerability_collection.insert_many(processed_records)
            records_inserted = len(insertion_result.inserted_ids)
            
            self._create_collection_indexes(vulnerability_collection)
            
            logger.info(f"Successfully stored {records_inserted} vulnerability records")
            return True
            
        except Exception as storage_error:
            logger.error(f"MongoDB storage operation failed: {storage_error}")
            return False
        finally:
            if mongo_client:
                mongo_client.close()
                logger.info("MongoDB connection closed")
    
    def _create_collection_indexes(self, collection):
        try:
            # Index on CVE ID for fast lookups
            collection.create_index("cveID", unique=True)
            # Index on vendor for filtering
            collection.create_index("vendorProject")
            # Index on processing timestamp for time-based queries
            collection.create_index("record_processed_at")
            logger.info("Database indexes created successfully")
        except Exception as index_error:
            logger.warning(f"Index creation failed: {index_error}")
    
    def execute_complete_pipeline(self):
        pipeline_start_time = datetime.utcnow()
        
        logger.info("=" * 60)
        logger.info("CISA VULNERABILITY ETL PIPELINE STARTING")
        logger.info("=" * 60)
        
        try:
            logger.info("PHASE 1: Data Extraction")
            raw_vulnerability_data = self.fetch_vulnerability_data()
            
            if not raw_vulnerability_data:
                logger.error("Data extraction failed - terminating pipeline")
                return False
            
            logger.info("PHASE 2: Data Transformation")
            processed_data = self.process_vulnerability_records(raw_vulnerability_data)
            
            if not processed_data:
                logger.error("Data transformation failed - terminating pipeline")
                return False
            
            logger.info("PHASE 3: Data Storage")
            storage_success = self.store_in_mongodb(processed_data)
            
            if not storage_success:
                logger.error("Data storage failed - pipeline incomplete")
                return False
            
            # Calculate pipeline execution time
            pipeline_duration = (datetime.utcnow() - pipeline_start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {pipeline_duration:.1f} seconds")
            logger.info(f"Total vulnerabilities processed: {len(processed_data)}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as pipeline_error:
            logger.error(f"Pipeline execution failed: {pipeline_error}")
            return False

def main():
    print("\nCISA Vulnerability Intelligence ETL Pipeline")
    print("Extracting Known Exploited Vulnerabilities Data")
    print("-" * 50)
    
    try:
        etl_pipeline = CISAVulnerabilityETL()
        
        pipeline_success = etl_pipeline.execute_complete_pipeline()
        
        print("-" * 50)
        if pipeline_success:
            print("ETL Pipeline completed successfully!")
            print("Vulnerability data is now available in MongoDB")
        else:
            print("ETL Pipeline encountered errors!")
            print("Check logs for detailed error information")
            
    except Exception as app_error:
        logger.error(f"Application startup failed: {app_error}")
        print(f"Application error: {app_error}")

if __name__ == "__main__":
    main()