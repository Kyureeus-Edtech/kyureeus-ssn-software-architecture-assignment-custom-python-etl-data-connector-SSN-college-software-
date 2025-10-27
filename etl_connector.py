#!/usr/bin/env python3
"""
ETL Data Connector for OSV (Open Source Vulnerabilities) API
Author: Janeshvar S
Roll Number: 3122225001047
Date: October 27, 2025

This script demonstrates 3 different ETL pipelines for OSV API:
1. OSV Query API - Search for vulnerabilities by package
2. OSV Get Vulnerability API - Get specific vulnerability details by ID  
3. OSV Batch Query API - Query multiple vulnerabilities in batch

OSV API Documentation: https://osv.dev/docs/
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

import requests
import pymongo
from dotenv import load_dotenv


class BaseOSVETLConnector(ABC):
    """
    Abstract base class for OSV ETL connectors.
    """
    
    def __init__(self, api_name: str):
        """Initialize the base ETL connector."""
        load_dotenv()
        
        # Setup logging
        self._setup_logging()
        
        # API Configuration
        self.api_name = api_name
        self.api_base_url = os.getenv('OSV_API_BASE_URL', 'https://api.osv.dev')
        self.api_key = os.getenv('OSV_API_KEY')
        self.api_secret = os.getenv('OSV_API_SECRET')
        
        # MongoDB Configuration
        self.mongodb_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        self.mongodb_database = os.getenv('MONGODB_DATABASE', 'osv_vulnerabilities_database')
        
        # ETL Configuration
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '100'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Initialize MongoDB client
        self.mongo_client = None
        self.database = None
        self.collection = None
        
        self.logger.info(f"{self.api_name} ETL Connector initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'osv_etl_{self.__class__.__name__.lower()}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def connect_to_mongodb(self, collection_name: str) -> bool:
        """
        Establish connection to MongoDB.
        
        Args:
            collection_name (str): Name of the collection to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mongo_client = pymongo.MongoClient(self.mongodb_connection_string)
            # Test the connection
            self.mongo_client.admin.command('ping')
            self.database = self.mongo_client[self.mongodb_database]
            self.collection = self.database[collection_name]
            self.logger.info(f"Successfully connected to MongoDB: {self.mongodb_database}.{collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _make_api_request(self, endpoint: str, method: str = 'GET', 
                         data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Union[Dict, List]]:
        """
        Make API request to OSV API with error handling and rate limiting.
        
        Args:
            endpoint (str): API endpoint
            method (str): HTTP method (GET, POST)
            data (Optional[Dict]): Request body data
            params (Optional[Dict]): Query parameters
            
        Returns:
            Optional[Union[Dict, List]]: API response data or None if failed
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            'User-Agent': f'OSV-ETL-Connector/{self.api_name}/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add API key to headers if available
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Making {method} request to OSV API: {url} (attempt {attempt + 1}/{self.max_retries})")
                
                if method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, 
                                           params=params, timeout=self.request_timeout)
                else:
                    response = requests.get(url, headers=headers, params=params, 
                                          timeout=self.request_timeout)
                
                # Check for rate limiting
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
    
    @abstractmethod
    def extract_data(self) -> List[Dict[str, Any]]:
        """Extract data from the OSV API. Must be implemented by subclasses."""
        pass
    
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform the extracted OSV data for MongoDB compatibility.
        
        Args:
            raw_data (List[Dict[str, Any]]): Raw extracted data
            
        Returns:
            List[Dict[str, Any]]: Transformed data
        """
        self.logger.info(f"Starting {self.api_name} data transformation...")
        transformed_data = []
        
        for record in raw_data:
            try:
                # Create a copy to avoid modifying original data
                transformed_record = record.copy()
                
                # Add transformation metadata
                transformed_record['_etl_transformed_at'] = datetime.now(timezone.utc).isoformat()
                transformed_record['_etl_api_name'] = self.api_name
                
                # Specific transformations based on OSV data structure
                if 'id' in transformed_record:
                    transformed_record['vulnerability_id'] = transformed_record['id']
                
                # Extract severity information if available
                if 'database_specific' in transformed_record:
                    db_specific = transformed_record['database_specific']
                    if 'severity' in db_specific:
                        transformed_record['extracted_severity'] = db_specific['severity']
                
                # Extract affected packages information
                if 'affected' in transformed_record:
                    affected_packages = []
                    for affected in transformed_record['affected']:
                        if 'package' in affected:
                            pkg_info = {
                                'name': affected['package'].get('name'),
                                'ecosystem': affected['package'].get('ecosystem'),
                                'purl': affected['package'].get('purl')
                            }
                            affected_packages.append(pkg_info)
                    transformed_record['extracted_affected_packages'] = affected_packages
                
                # Extract references
                if 'references' in transformed_record:
                    reference_urls = [ref.get('url') for ref in transformed_record['references'] if ref.get('url')]
                    transformed_record['extracted_reference_urls'] = reference_urls
                
                # Handle nested objects for MongoDB compatibility
                transformed_record = self._flatten_nested_objects(transformed_record)
                
                # Data validation and cleaning
                if self._validate_record(transformed_record):
                    transformed_data.append(transformed_record)
                else:
                    self.logger.warning(f"Invalid record skipped: {transformed_record.get('id', 'unknown')}")
                    
            except Exception as e:
                self.logger.error(f"Error transforming record: {str(e)}")
                continue
        
        self.logger.info(f"Transformed {len(transformed_data)} records for {self.api_name}")
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
            if key in ['affected', 'references', 'credits', 'database_specific', 'ecosystem_specific']:
                items.append((new_key, value))
            elif isinstance(value, dict) and len(str(value)) < 1000:  # Only flatten small dicts
                items.extend(self._flatten_nested_objects(value, new_key, separator).items())
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # For lists of dictionaries, keep them as-is
                items.append((new_key, value))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a record before loading into MongoDB.
        
        Args:
            record (Dict[str, Any]): Record to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation rules
        if not isinstance(record, dict):
            return False
        
        # Check if record has required ETL metadata
        required_fields = ['_etl_api_name', '_etl_extracted_at']
        for field in required_fields:
            if field not in record:
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
                'api_name': self.api_name,
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
    
    def run_etl_pipeline(self, collection_name: str) -> tuple[bool, Dict[str, Any]]:
        """
        Execute the complete ETL pipeline.
        
        Args:
            collection_name (str): MongoDB collection name
            
        Returns:
            tuple[bool, Dict[str, Any]]: Success status and collection statistics
        """
        self.logger.info(f"Starting {self.api_name} ETL Pipeline...")
        start_time = time.time()
        
        try:
            # Step 1: Connect to MongoDB
            if not self.connect_to_mongodb(collection_name):
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
            
            self.logger.info(f"{self.api_name} ETL Pipeline completed successfully in {duration:.2f} seconds")
            self.logger.info(f"Total records processed: {len(transformed_data)}")
            
            # Get collection statistics before closing connection
            stats = self.get_collection_stats()
            
            return True, stats
            
        except Exception as e:
            self.logger.error(f"{self.api_name} ETL Pipeline failed: {str(e)}")
            return False, {}
        
        finally:
            # Clean up MongoDB connection
            if self.mongo_client:
                self.mongo_client.close()
                self.logger.info("MongoDB connection closed")


class OSVQueryConnector(BaseOSVETLConnector):
    """
    ETL connector for OSV Query API - Search for vulnerabilities by package.
    """
    
    def __init__(self):
        super().__init__("OSV_Query")
        
        # Query-specific configuration
        self.query_package_name = os.getenv('QUERY_PACKAGE_NAME', 'numpy')
        self.query_ecosystem = os.getenv('QUERY_ECOSYSTEM', 'PyPI')
        self.query_version = os.getenv('QUERY_VERSION', '1.21.0')
        
        self.logger.info(f"OSV Query Connector initialized for package: {self.query_package_name}")
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extract vulnerability data by querying for a specific package.
        
        Returns:
            List[Dict[str, Any]]: List of extracted vulnerability records
        """
        self.logger.info(f"Extracting vulnerabilities for package: {self.query_package_name}")
        
        # Prepare query data
        query_data = {
            "package": {
                "name": self.query_package_name,
                "ecosystem": self.query_ecosystem
            }
        }
        
        # Add version if specified
        if self.query_version:
            query_data["version"] = self.query_version
        
        extracted_data = []
        
        # Make API request
        response_data = self._make_api_request('v1/query', method='POST', data=query_data)
        
        if response_data and 'vulns' in response_data:
            vulnerabilities = response_data['vulns']
            
            # Add metadata to each vulnerability record
            extraction_time = datetime.now(timezone.utc).isoformat()
            
            for vuln in vulnerabilities:
                # Add ETL metadata
                vuln['_etl_source'] = 'osv_query_api'
                vuln['_etl_extracted_at'] = extraction_time
                vuln['_etl_query_package'] = self.query_package_name
                vuln['_etl_query_ecosystem'] = self.query_ecosystem
                vuln['_etl_query_version'] = self.query_version
                
                extracted_data.append(vuln)
            
            self.logger.info(f"Extracted {len(vulnerabilities)} vulnerabilities for {self.query_package_name}")
        else:
            self.logger.warning(f"No vulnerability data received for package: {self.query_package_name}")
        
        return extracted_data


class OSVVulnerabilityConnector(BaseOSVETLConnector):
    """
    ETL connector for OSV Get Vulnerability API - Get specific vulnerability details by ID.
    """
    
    def __init__(self):
        super().__init__("OSV_Vulnerability")
        
        # Vulnerability-specific configuration
        vulnerability_ids = os.getenv('VULNERABILITY_ID_LIST', 'GHSA-cfnp-24c3-hf38,GHSA-489w-9rhx-hjp8')
        self.vulnerability_ids = [vid.strip() for vid in vulnerability_ids.split(',') if vid.strip()]
        
        self.logger.info(f"OSV Vulnerability Connector initialized for {len(self.vulnerability_ids)} vulnerability IDs")
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extract detailed vulnerability data by ID.
        
        Returns:
            List[Dict[str, Any]]: List of extracted vulnerability records
        """
        self.logger.info(f"Extracting details for {len(self.vulnerability_ids)} vulnerabilities")
        
        extracted_data = []
        extraction_time = datetime.now(timezone.utc).isoformat()
        
        for vuln_id in self.vulnerability_ids:
            self.logger.info(f"Extracting vulnerability: {vuln_id}")
            
            # Make API request for specific vulnerability
            response_data = self._make_api_request(f'v1/vulns/{vuln_id}')
            
            if response_data:
                # Add ETL metadata
                response_data['_etl_source'] = 'osv_vulnerability_api'
                response_data['_etl_extracted_at'] = extraction_time
                response_data['_etl_requested_id'] = vuln_id
                
                extracted_data.append(response_data)
                self.logger.info(f"Successfully extracted vulnerability: {vuln_id}")
            else:
                self.logger.warning(f"Failed to extract vulnerability: {vuln_id}")
        
        self.logger.info(f"Total vulnerabilities extracted: {len(extracted_data)}")
        return extracted_data


class OSVBatchQueryConnector(BaseOSVETLConnector):
    """
    ETL connector for OSV Batch Query API - Query multiple vulnerabilities in batch.
    """
    
    def __init__(self):
        super().__init__("OSV_Batch")
        
        # Batch-specific configuration
        self.batch_query_limit = int(os.getenv('BATCH_QUERY_LIMIT', '1000'))
        
        # Define multiple packages to query in batch
        self.batch_queries = [
            {"package": {"name": "numpy", "ecosystem": "PyPI"}},
            {"package": {"name": "requests", "ecosystem": "PyPI"}},
            {"package": {"name": "flask", "ecosystem": "PyPI"}},
            {"package": {"name": "django", "ecosystem": "PyPI"}},
            {"package": {"name": "pandas", "ecosystem": "PyPI"}}
        ]
        
        self.logger.info(f"OSV Batch Connector initialized for {len(self.batch_queries)} packages")
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extract vulnerability data using batch queries.
        
        Returns:
            List[Dict[str, Any]]: List of extracted vulnerability records
        """
        self.logger.info(f"Extracting vulnerabilities for {len(self.batch_queries)} packages in batch")
        
        # Prepare batch query data
        batch_data = {
            "queries": self.batch_queries
        }
        
        extracted_data = []
        
        # Make batch API request
        response_data = self._make_api_request('v1/querybatch', method='POST', data=batch_data)
        
        if response_data and 'results' in response_data:
            results = response_data['results']
            extraction_time = datetime.now(timezone.utc).isoformat()
            
            for i, result in enumerate(results):
                if 'vulns' in result:
                    vulnerabilities = result['vulns']
                    query_info = self.batch_queries[i] if i < len(self.batch_queries) else {}
                    
                    for vuln in vulnerabilities:
                        # Add ETL metadata
                        vuln['_etl_source'] = 'osv_batch_api'
                        vuln['_etl_extracted_at'] = extraction_time
                        vuln['_etl_batch_query_index'] = i
                        vuln['_etl_batch_package'] = query_info.get('package', {}).get('name')
                        vuln['_etl_batch_ecosystem'] = query_info.get('package', {}).get('ecosystem')
                        
                        extracted_data.append(vuln)
            
            self.logger.info(f"Extracted {len(extracted_data)} vulnerabilities from batch query")
        else:
            self.logger.warning("No vulnerability data received from batch query")
        
        return extracted_data


def main():
    """Main function to run all three OSV ETL connectors."""
    print("=" * 80)
    print("OSV (Open Source Vulnerabilities) ETL Data Connectors")
    print("Author: Janeshvar S")
    print("Roll Number: 3122225001047")
    print("=" * 80)
    
    # Get MongoDB collection names from environment
    collection_query = os.getenv('MONGODB_COLLECTION_QUERY', 'osv_query_raw')
    collection_vuln = os.getenv('MONGODB_COLLECTION_VULN', 'osv_vulnerability_raw')
    collection_batch = os.getenv('MONGODB_COLLECTION_BATCH', 'osv_batch_raw')
    
    connectors = [
        (OSVQueryConnector(), collection_query, "OSV Query API"),
        (OSVVulnerabilityConnector(), collection_vuln, "OSV Vulnerability API"),
        (OSVBatchQueryConnector(), collection_batch, "OSV Batch Query API")
    ]
    
    all_stats = {}
    
    for connector, collection_name, api_name in connectors:
        print(f"\n🚀 Running {api_name} ETL Pipeline...")
        print("-" * 50)
        
        success, stats = connector.run_etl_pipeline(collection_name)
        
        if success:
            print(f"✅ {api_name} ETL Pipeline completed successfully!")
            all_stats[api_name] = stats
            
            # Display collection statistics
            if stats:
                print(f"\n📊 {api_name} Collection Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
        else:
            print(f"❌ {api_name} ETL Pipeline failed!")
            all_stats[api_name] = {"status": "failed"}
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 ETL PIPELINE SUMMARY")
    print("=" * 80)
    
    for api_name, stats in all_stats.items():
        status = "✅ SUCCESS" if "total_documents" in stats else "❌ FAILED"
        doc_count = stats.get("total_documents", "N/A")
        print(f"{api_name}: {status} | Documents: {doc_count}")
    
    print("\n🎉 All OSV ETL pipelines completed!")


if __name__ == "__main__":
    main()