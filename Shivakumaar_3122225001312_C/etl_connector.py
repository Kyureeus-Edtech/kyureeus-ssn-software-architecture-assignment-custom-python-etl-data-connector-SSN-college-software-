#!/usr/bin/env python3
"""
MalShare API ETL Connector
Author: [Shivakumaar] - [3122225001312]
Description: ETL pipeline to extract malware intelligence data from MalShare API,
            transform it for compatibility, and load into MongoDB collection.
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_connector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MalShareETLConnector:
    """
    ETL Connector for MalShare API
    Handles extraction, transformation, and loading of malware intelligence data
    """
    
    def __init__(self):
        """Initialize the ETL connector with configuration"""
        self.base_url = os.getenv('MALSHARE_BASE_URL', 'https://malshare.com')
        self.api_key = os.getenv('MALSHARE_API_KEY')
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGODB_DATABASE', 'malware_intelligence')
        self.collection_name = 'malshare_raw'
        
        # API configuration
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Validate required configuration
        if not self.api_key:
            raise ValueError("MALSHARE_API_KEY is required in .env file")
        
        # Initialize MongoDB connection
        self._init_mongo_connection()
        
        logger.info("MalShare ETL Connector initialized successfully")
    
    def _init_mongo_connection(self):
        """Initialize MongoDB connection and collection"""
        try:
            self.mongo_client = MongoClient(self.mongo_uri)
            # Test connection
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Create indexes for better performance
            self.collection.create_index("sha256", unique=True, sparse=True)
            self.collection.create_index("ingestion_timestamp")
            self.collection.create_index("sample_type")
            
            logger.info(f"Connected to MongoDB: {self.db_name}.{self.collection_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make authenticated API request with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        url = f"{self.base_url}/api.php"
        
        # Default parameters
        default_params = {
            'api_key': self.api_key,
            'action': endpoint
        }
        
        if params:
            default_params.update(params)
        
        headers = {
            'User-Agent': 'MalShare-ETL-Connector/1.0',
            'Accept': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making API request to {endpoint} (attempt {attempt + 1})")
                
                response = requests.get(
                    url,
                    params=default_params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = self.rate_limit_delay * (2 ** attempt)
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                # Handle different content types
                if response.headers.get('content-type', '').startswith('application/json'):
                    return response.json()
                else:
                    # Handle text responses (like getlist)
                    return {'data': response.text.strip().split('\n')}
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed for {endpoint}")
                    return None
                
                # Exponential backoff
                time.sleep(self.rate_limit_delay * (2 ** attempt))
        
        return None
    
    def extract_sample_list(self, limit: int = 100) -> List[str]:
        """
        Extract list of recent malware samples
        
        Args:
            limit: Maximum number of samples to retrieve
            
        Returns:
            List of sample hashes
        """
        logger.info(f"Extracting sample list (limit: {limit})")
        
        response = self._make_api_request('getlist')
        
        if not response or 'data' not in response:
            logger.error("Failed to retrieve sample list")
            return []
        
        samples = response['data']
        
        # Filter out empty lines and limit results
        samples = [s.strip() for s in samples if s.strip()][:limit]
        
        logger.info(f"Extracted {len(samples)} sample hashes")
        return samples
    
    def extract_sample_details(self, sample_hash: str) -> Optional[Dict]:
        """
        Extract detailed information for a specific sample
        
        Args:
            sample_hash: SHA256 hash of the sample
            
        Returns:
            Sample details or None if failed
        """
        logger.info(f"Extracting details for sample: {sample_hash}")
        
        response = self._make_api_request('details', {'hash': sample_hash})
        
        if not response:
            logger.error(f"Failed to retrieve details for {sample_hash}")
            return None
        
        return response
    
    def transform_data(self, raw_data: Dict, sample_hash: str) -> Dict:
        """
        Transform raw API data for MongoDB compatibility
        
        Args:
            raw_data: Raw data from API
            sample_hash: Sample hash for reference
            
        Returns:
            Transformed data ready for MongoDB insertion
        """
        logger.debug(f"Transforming data for sample: {sample_hash}")
        
        # Add metadata
        transformed = {
            'sha256': sample_hash,
            'ingestion_timestamp': datetime.now(timezone.utc),
            'source': 'malshare_api',
            'connector_version': '1.0',
            'raw_response': raw_data
        }
        
        # Extract and standardize common fields
        if isinstance(raw_data, dict):
            # Map API fields to standardized schema
            field_mapping = {
                'MD5': 'md5',
                'SHA1': 'sha1',
                'SHA256': 'sha256_confirmed',
                'SSDEEP': 'ssdeep',
                'F_TYPE': 'file_type',
                'SOURCES': 'sources',
                'ADDED': 'date_added'
            }
            
            for api_field, std_field in field_mapping.items():
                if api_field in raw_data:
                    transformed[std_field] = raw_data[api_field]
            
            # Parse date fields
            if 'ADDED' in raw_data:
                try:
                    transformed['date_added_parsed'] = datetime.strptime(
                        raw_data['ADDED'], '%Y-%m-%d %H:%M:%S'
                    )
                except ValueError:
                    logger.warning(f"Failed to parse date: {raw_data['ADDED']}")
            
            # Determine sample type
            file_type = raw_data.get('F_TYPE', '').lower()
            if 'pe32' in file_type or 'executable' in file_type:
                transformed['sample_type'] = 'executable'
            elif 'pdf' in file_type:
                transformed['sample_type'] = 'document'
            elif 'zip' in file_type or 'archive' in file_type:
                transformed['sample_type'] = 'archive'
            else:
                transformed['sample_type'] = 'unknown'
        
        # Add data quality metrics
        transformed['data_completeness'] = self._calculate_completeness(raw_data)
        
        logger.debug(f"Data transformation completed for {sample_hash}")
        return transformed
    
    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate data completeness score"""
        if not isinstance(data, dict):
            return 0.0
        
        expected_fields = ['MD5', 'SHA1', 'SHA256', 'F_TYPE', 'ADDED']
        present_fields = sum(1 for field in expected_fields if field in data and data[field])
        
        return present_fields / len(expected_fields)
    
    def load_data(self, transformed_data: Dict) -> bool:
        """
        Load transformed data into MongoDB
        
        Args:
            transformed_data: Data ready for insertion
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use upsert to handle duplicates
            filter_criteria = {'sha256': transformed_data['sha256']}
            
            result = self.collection.replace_one(
                filter_criteria,
                transformed_data,
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"Successfully loaded data for {transformed_data['sha256']}")
                return True
            else:
                logger.info(f"No changes for {transformed_data['sha256']} (already exists)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load data for {transformed_data['sha256']}: {e}")
            return False
    
    def run_etl_pipeline(self, sample_limit: int = 50):
        """
        Run the complete ETL pipeline
        
        Args:
            sample_limit: Maximum number of samples to process
        """
        logger.info("Starting MalShare ETL pipeline")
        start_time = datetime.now()
        
        try:
            # Extract phase
            logger.info("=== EXTRACT PHASE ===")
            sample_hashes = self.extract_sample_list(sample_limit)
            
            if not sample_hashes:
                logger.error("No samples extracted. Aborting pipeline.")
                return
            
            successful_loads = 0
            failed_loads = 0
            
            # Process each sample
            for i, sample_hash in enumerate(sample_hashes, 1):
                logger.info(f"Processing sample {i}/{len(sample_hashes)}: {sample_hash}")
                
                # Extract sample details
                raw_data = self.extract_sample_details(sample_hash)
                
                if not raw_data:
                    logger.warning(f"Skipping sample {sample_hash} - no data extracted")
                    failed_loads += 1
                    continue
                
                # Transform phase
                logger.info("=== TRANSFORM PHASE ===")
                transformed_data = self.transform_data(raw_data, sample_hash)
                
                # Load phase
                logger.info("=== LOAD PHASE ===")
                if self.load_data(transformed_data):
                    successful_loads += 1
                else:
                    failed_loads += 1
                
                # Rate limiting
                if i < len(sample_hashes):
                    time.sleep(self.rate_limit_delay)
            
            # Pipeline summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=== PIPELINE SUMMARY ===")
            logger.info(f"Total samples processed: {len(sample_hashes)}")
            logger.info(f"Successful loads: {successful_loads}")
            logger.info(f"Failed loads: {failed_loads}")
            logger.info(f"Success rate: {(successful_loads / len(sample_hashes)) * 100:.1f}%")
            logger.info(f"Total duration: {duration}")
            logger.info("MalShare ETL pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            raise
        finally:
            # Cleanup
            if hasattr(self, 'mongo_client'):
                self.mongo_client.close()
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the MongoDB collection"""
        try:
            stats = {
                'total_documents': self.collection.count_documents({}),
                'sample_types': list(self.collection.aggregate([
                    {'$group': {'_id': '$sample_type', 'count': {'$sum': 1}}}
                ])),
                'latest_ingestion': self.collection.find_one(
                    {}, sort=[('ingestion_timestamp', -1)]
                ),
                'collection_size': self.db.command('collstats', self.collection_name)['size']
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

def main():
    """Main function to run the ETL pipeline"""
    try:
        # Initialize connector
        connector = MalShareETLConnector()
        
        # Run pipeline
        sample_limit = int(os.getenv('SAMPLE_LIMIT', '25'))
        connector.run_etl_pipeline(sample_limit)
        
        # Show statistics
        stats = connector.get_collection_stats()
        if stats:
            logger.info("=== COLLECTION STATISTICS ===")
            logger.info(f"Total documents: {stats['total_documents']}")
            logger.info(f"Collection size: {stats.get('collection_size', 'N/A')} bytes")
            if stats['sample_types']:
                logger.info("Sample types distribution:")
                for item in stats['sample_types']:
                    logger.info(f"  {item['_id']}: {item['count']}")
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()