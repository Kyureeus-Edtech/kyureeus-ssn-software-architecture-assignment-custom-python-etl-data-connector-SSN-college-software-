#!/usr/bin/env python3
"""
ETL Data Connector for NVD CVE API
Author: Janeshvar S
Roll Number: 3122225001047
Date: August 13, 2025

This script demonstrates a complete ETL pipeline that:
1. Extracts CVE (Common Vulnerabilities and Exposures) data from NVD API
2. Transforms the data for MongoDB compatibility
3. Loads the data into a MongoDB collection

NVD API Documentation: https://nvd.nist.gov/developers/vulnerabilities
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import requests
import pymongo
from dotenv import load_dotenv


class ETLConnector:
    """
    A comprehensive ETL connector class for data extraction, transformation, and loading.
    """
    
    def __init__(self):
        """Initialize the ETL connector with configuration from environment variables."""
        load_dotenv()
        
        # Setup logging
        self._setup_logging()
        
        # API Configuration
        self.api_base_url = os.getenv('API_BASE_URL', 'https://services.nvd.nist.gov/rest/json/cves/2.0')
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        
        # MongoDB Configuration
        self.mongodb_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        self.mongodb_database = os.getenv('MONGODB_DATABASE', 'nvd_cve_database')
        self.mongodb_collection = os.getenv('MONGODB_COLLECTION', 'nvd_cve_raw')
        
        # ETL Configuration
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '2'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '50'))
        self.results_per_page = int(os.getenv('RESULTS_PER_PAGE', '100'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # NVD API Specific Configuration
        self.start_index = int(os.getenv('START_INDEX', '0'))
        self.total_results = int(os.getenv('TOTAL_RESULTS', '500'))
        
        # Initialize MongoDB client
        self.mongo_client = None
        self.database = None
        self.collection = None
        
        self.logger.info("ETL Connector initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('etl_connector.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_to_mongodb(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mongo_client = pymongo.MongoClient(self.mongodb_connection_string)
            # Test the connection
            self.mongo_client.admin.command('ping')
            self.database = self.mongo_client[self.mongodb_database]
            self.collection = self.database[self.mongodb_collection]
            self.logger.info(f"Successfully connected to MongoDB: {self.mongodb_database}.{self.mongodb_collection}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _make_api_request(self, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request to NVD CVE API with error handling and rate limiting.
        
        Args:
            params (Optional[Dict]): Query parameters for the API request
            
        Returns:
            Optional[Dict]: API response data or None if failed
        """
        url = self.api_base_url
        
        headers = {
            'User-Agent': 'NVD-ETL-Connector/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add API key to headers if available (NVD API key is optional but recommended)
        if self.api_key:
            headers['apiKey'] = self.api_key
        
        # Default parameters for NVD API
        default_params = {
            'resultsPerPage': self.results_per_page,
            'startIndex': params.get('startIndex', 0) if params else 0
        }
        
        if params:
            default_params.update(params)
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Making API request to NVD CVE API (attempt {attempt + 1}/{self.max_retries})")
                self.logger.info(f"Request parameters: {default_params}")
                
                response = requests.get(url, headers=headers, params=default_params, timeout=60)
                
                # Check for rate limiting (NVD API has rate limits)
                if response.status_code == 429:
                    wait_time = self.rate_limit_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Rate limit reached, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                # Rate limiting delay
                time.sleep(self.rate_limit_delay)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.rate_limit_delay * (attempt + 1))
                continue
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON response: {str(e)}")
                return None
        
        self.logger.error(f"All {self.max_retries} API request attempts failed")
        return None
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extract CVE data from the NVD API.
        
        Returns:
            List[Dict[str, Any]]: List of extracted CVE records
        """
        self.logger.info("Starting CVE data extraction from NVD API...")
        extracted_data = []
        
        # Calculate total pages needed
        total_pages = (self.total_results + self.results_per_page - 1) // self.results_per_page
        
        for page in range(total_pages):
            start_index = page * self.results_per_page
            
            # Don't exceed the total results limit
            if start_index >= self.total_results:
                break
            
            self.logger.info(f"Extracting page {page + 1}/{total_pages} (startIndex: {start_index})")
            
            params = {
                'startIndex': start_index,
                'resultsPerPage': min(self.results_per_page, self.total_results - start_index)
            }
            
            response_data = self._make_api_request(params)
            
            if response_data and 'vulnerabilities' in response_data:
                cve_items = response_data['vulnerabilities']
                
                # Add metadata to each CVE record
                batch_id = f"nvd_batch_{int(time.time())}_{page}"
                extraction_time = datetime.now(timezone.utc).isoformat()
                
                for cve_item in cve_items:
                    # Extract the CVE data from the nested structure
                    if 'cve' in cve_item:
                        cve_data = cve_item['cve']
                        
                        # Add ETL metadata
                        cve_data['_etl_source'] = 'nvd_cve_api'
                        cve_data['_etl_extracted_at'] = extraction_time
                        cve_data['_etl_batch_id'] = batch_id
                        cve_data['_etl_page_number'] = page + 1
                        cve_data['_etl_start_index'] = start_index
                        
                        extracted_data.append(cve_data)
                
                self.logger.info(f"Extracted {len(cve_items)} CVE records from page {page + 1}")
                
                # Check if we've reached the end of available data
                total_results_available = response_data.get('totalResults', 0)
                if start_index + len(cve_items) >= total_results_available:
                    self.logger.info(f"Reached end of available data. Total available: {total_results_available}")
                    break
                    
            else:
                self.logger.warning(f"No CVE data received for page {page + 1}")
                # Don't break here, might be a temporary issue
        
        self.logger.info(f"Total CVE records extracted: {len(extracted_data)}")
        return extracted_data
    
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform the extracted CVE data for MongoDB compatibility.
        
        Args:
            raw_data (List[Dict[str, Any]]): Raw extracted CVE data
            
        Returns:
            List[Dict[str, Any]]: Transformed data
        """
        self.logger.info("Starting CVE data transformation...")
        transformed_data = []
        
        for record in raw_data:
            try:
                # Create a copy to avoid modifying original data
                transformed_record = record.copy()
                
                # Add transformation metadata
                transformed_record['_etl_transformed_at'] = datetime.now(timezone.utc).isoformat()
                
                # Extract key CVE information for easier querying
                cve_id = transformed_record.get('id', '')
                transformed_record['cve_id'] = cve_id
                
                # Extract CVSS scores if available
                metrics = transformed_record.get('metrics', {})
                if metrics:
                    # CVSS v3.x scores
                    cvss_v3 = metrics.get('cvssMetricV31', []) or metrics.get('cvssMetricV30', [])
                    if cvss_v3:
                        primary_cvss = cvss_v3[0] if cvss_v3 else {}
                        cvss_data = primary_cvss.get('cvssData', {})
                        transformed_record['cvss_v3_base_score'] = cvss_data.get('baseScore')
                        transformed_record['cvss_v3_base_severity'] = cvss_data.get('baseSeverity')
                        transformed_record['cvss_v3_vector_string'] = cvss_data.get('vectorString')
                    
                    # CVSS v2 scores
                    cvss_v2 = metrics.get('cvssMetricV2', [])
                    if cvss_v2:
                        primary_cvss_v2 = cvss_v2[0] if cvss_v2 else {}
                        cvss_v2_data = primary_cvss_v2.get('cvssData', {})
                        transformed_record['cvss_v2_base_score'] = cvss_v2_data.get('baseScore')
                        transformed_record['cvss_v2_vector_string'] = cvss_v2_data.get('vectorString')
                
                # Extract CWE (Common Weakness Enumeration) information
                weaknesses = transformed_record.get('weaknesses', [])
                cwe_ids = []
                for weakness in weaknesses:
                    descriptions = weakness.get('description', [])
                    for desc in descriptions:
                        if desc.get('lang') == 'en':
                            cwe_ids.append(desc.get('value', ''))
                transformed_record['cwe_ids'] = cwe_ids
                
                # Extract CPE (Common Platform Enumeration) information
                configurations = transformed_record.get('configurations', [])
                cpe_names = []
                for config in configurations:
                    nodes = config.get('nodes', [])
                    for node in nodes:
                        cpe_match = node.get('cpeMatch', [])
                        for cpe in cpe_match:
                            if cpe.get('vulnerable', False):
                                cpe_names.append(cpe.get('criteria', ''))
                transformed_record['vulnerable_cpe_names'] = list(set(cpe_names))  # Remove duplicates
                
                # Extract publication and modification dates
                published = transformed_record.get('published')
                last_modified = transformed_record.get('lastModified')
                transformed_record['published_date'] = published
                transformed_record['last_modified_date'] = last_modified
                
                # Extract description
                descriptions = transformed_record.get('descriptions', [])
                english_description = ''
                for desc in descriptions:
                    if desc.get('lang') == 'en':
                        english_description = desc.get('value', '')
                        break
                transformed_record['description_english'] = english_description
                
                # Extract references
                references = transformed_record.get('references', [])
                reference_urls = [ref.get('url', '') for ref in references]
                transformed_record['reference_urls'] = reference_urls
                
                # Handle nested objects for MongoDB compatibility
                transformed_record = self._flatten_nested_objects(transformed_record)
                
                # Data validation and cleaning
                if self._validate_cve_record(transformed_record):
                    transformed_data.append(transformed_record)
                else:
                    self.logger.warning(f"Invalid CVE record skipped: {cve_id}")
                    
            except Exception as e:
                self.logger.error(f"Error transforming CVE record: {str(e)}")
                continue
        
        self.logger.info(f"Transformed {len(transformed_data)} CVE records")
        return transformed_data
    
    def _flatten_nested_objects(self, record: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
        """
        Flatten nested objects for MongoDB compatibility.
        
        Args:
            record (Dict[str, Any]): Record to flatten
            parent_key (str): Parent key for nested objects
            separator (str): Separator for flattened keys
            
        Returns:
            Dict[str, Any]: Flattened record
        """
        items = []
        for key, value in record.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            # Skip certain complex nested structures that are better kept as-is
            if key in ['metrics', 'configurations', 'weaknesses', 'references', 'descriptions']:
                items.append((new_key, value))
            elif isinstance(value, dict):
                items.extend(self._flatten_nested_objects(value, new_key, separator).items())
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # For lists of dictionaries, keep them as-is for now
                items.append((new_key, value))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def _validate_cve_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a CVE record before loading into MongoDB.
        
        Args:
            record (Dict[str, Any]): CVE record to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation rules
        if not isinstance(record, dict):
            return False
        
        # Check if record has required ETL metadata
        required_fields = ['_etl_source', '_etl_extracted_at']
        for field in required_fields:
            if field not in record:
                return False
        
        # Check for CVE ID
        if 'id' not in record or not record['id']:
            return False
        
        # Validate CVE ID format (should start with CVE-)
        cve_id = record.get('id', '')
        if not cve_id.startswith('CVE-'):
            return False
        
        return True
    
    def load_data(self, transformed_data: List[Dict[str, Any]]) -> bool:
        """
        Load transformed data into MongoDB.
        
        Args:
            transformed_data (List[Dict[str, Any]]): Transformed data to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not transformed_data:
            self.logger.warning("No data to load")
            return False
        
        if self.collection is None:
            self.logger.error("MongoDB collection not initialized")
            return False
        
        self.logger.info(f"Starting data load of {len(transformed_data)} records...")
        
        try:
            # Load data in batches
            total_inserted = 0
            
            for i in range(0, len(transformed_data), self.batch_size):
                batch = transformed_data[i:i + self.batch_size]
                
                # Add load timestamp to each record in the batch
                for record in batch:
                    record['_etl_loaded_at'] = datetime.now(timezone.utc).isoformat()
                
                # Insert batch into MongoDB
                result = self.collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                
                self.logger.info(f"Inserted batch {i//self.batch_size + 1}: {len(result.inserted_ids)} records")
            
            self.logger.info(f"Successfully loaded {total_inserted} records into MongoDB")
            return True
            
        except pymongo.errors.BulkWriteError as e:
            self.logger.error(f"Bulk write error: {str(e)}")
            # Continue with partial success
            return True
        except Exception as e:
            self.logger.error(f"Failed to load data into MongoDB: {str(e)}")
            return False
    
    def run_etl_pipeline(self) -> tuple[bool, Dict[str, Any]]:
        """
        Execute the complete ETL pipeline.
        
        Returns:
            tuple[bool, Dict[str, Any]]: Success status and collection statistics
        """
        self.logger.info("Starting ETL Pipeline...")
        start_time = time.time()
        
        try:
            # Step 1: Connect to MongoDB
            if not self.connect_to_mongodb():
                return False, {}
            
            # Step 2: Extract data
            raw_data = self.extract_data()
            if not raw_data:
                self.logger.error("No data extracted, pipeline aborted")
                return False, {}
            
            # Step 3: Transform data
            transformed_data = self.transform_data(raw_data)
            if not transformed_data:
                self.logger.error("No data after transformation, pipeline aborted")
                return False, {}
            
            # Step 4: Load data
            load_success = self.load_data(transformed_data)
            if not load_success:
                self.logger.error("Data loading failed, pipeline aborted")
                return False, {}
            
            # Pipeline completed successfully
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"ETL Pipeline completed successfully in {duration:.2f} seconds")
            self.logger.info(f"Total records processed: {len(transformed_data)}")
            
            # Get collection statistics before closing connection
            stats = self.get_collection_stats()
            
            return True, stats
            
        except Exception as e:
            self.logger.error(f"ETL Pipeline failed: {str(e)}")
            return False, {}
        
        finally:
            # Clean up MongoDB connection
            if self.mongo_client:
                self.mongo_client.close()
                self.logger.info("MongoDB connection closed")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the MongoDB collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        if self.collection is None:
            return {}
        
        try:
            stats = {
                'total_documents': self.collection.count_documents({}),
                'collection_name': self.collection.name,
                'database_name': self.database.name,
                'last_update': datetime.now(timezone.utc).isoformat()
            }
            
            # Get sample document
            sample = self.collection.find_one()
            if sample:
                stats['sample_document_keys'] = list(sample.keys())
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {}


def main():
    """Main function to run the ETL connector."""
    print("=" * 60)
    print("ETL Data Connector - NVD CVE API")
    print("Author: Janeshvar S")
    print("Roll Number: 3122225001047")
    print("=" * 60)
    
    # Initialize ETL connector
    etl_connector = ETLConnector()
    
    # Run the ETL pipeline
    success, stats = etl_connector.run_etl_pipeline()
    
    if success:
        print("\n✅ ETL Pipeline completed successfully!")
        
        # Display collection statistics
        if stats:
            print("\n📊 Collection Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
    else:
        print("\n❌ ETL Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
