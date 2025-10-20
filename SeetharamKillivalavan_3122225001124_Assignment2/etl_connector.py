"""
RIPEstat ETL Data Connector - Assignment 2
Student: Seetharam Killivalavan
Roll Number: 3122225001124
Section: C
Data Source: RIPEstat (RIPE NCC)

This ETL pipeline extracts data from THREE RIPEstat endpoints:
1. ASN Overview - Autonomous System Number information
2. Network Info - IP prefix and network details
3. Geolocation - Geographic location data for resources

All data is transformed and loaded into separate MongoDB collections.
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, errors as mongo_errors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ripestat_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RIPEstatETLPipeline:
    """
    ETL Pipeline for extracting, transforming, and loading data from RIPEstat API.
    Implements three separate endpoints for comprehensive network data collection.
    """
    
    def __init__(self):
        """Initialize the ETL pipeline with configuration from environment variables."""
        load_dotenv()
        
        # MongoDB Configuration
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'etl_database')
        
        # RIPEstat API Configuration
        self.base_url = 'https://stat.ripe.net/data'
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
        
        # MongoDB collections for each endpoint
        self.collections = {
            'asn_overview': 'ripestat_asn_overview',
            'network_info': 'ripestat_network_info',
            'geolocation': 'ripestat_geolocation'
        }
        
        # Initialize MongoDB client
        self.mongo_client = None
        self.db = None
        
        # Statistics tracking
        self.stats = {
            'asn_overview': {'extracted': 0, 'transformed': 0, 'loaded': 0, 'errors': 0},
            'network_info': {'extracted': 0, 'transformed': 0, 'loaded': 0, 'errors': 0},
            'geolocation': {'extracted': 0, 'transformed': 0, 'loaded': 0, 'errors': 0}
        }
        
        self.start_time = None
        
    def connect_mongodb(self) -> bool:
        """
        Establish connection to MongoDB and create necessary indexes.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[self.database_name]
            
            # Create indexes for each collection
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            return True
            
        except mongo_errors.ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            return False
    
    def _create_indexes(self):
        """Create appropriate indexes for all collections."""
        try:
            # ASN Overview collection indexes
            asn_collection = self.db[self.collections['asn_overview']]
            asn_collection.create_index([('asn', ASCENDING)], unique=True)
            asn_collection.create_index([('ingestion_timestamp', ASCENDING)])
            
            # Network Info collection indexes
            network_collection = self.db[self.collections['network_info']]
            network_collection.create_index([('prefix', ASCENDING)], unique=True)
            network_collection.create_index([('ingestion_timestamp', ASCENDING)])
            
            # Geolocation collection indexes
            geo_collection = self.db[self.collections['geolocation']]
            geo_collection.create_index([('resource', ASCENDING), ('ingestion_timestamp', ASCENDING)])
            geo_collection.create_index([('country', ASCENDING)])
            
            logger.info("Successfully created MongoDB indexes for all collections")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Make a request to the RIPEstat API with error handling and rate limiting.
        
        Args:
            endpoint: API endpoint name
            params: Query parameters
            
        Returns:
            Optional[Dict]: API response data or None if error
        """
        url = f"{self.base_url}/{endpoint}/data.json"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Respect rate limiting
            time.sleep(self.rate_limit_delay)
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return data
            else:
                logger.warning(f"API returned non-OK status for {endpoint}: {data.get('status')}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for endpoint: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from {endpoint}: {e}")
            return None
    
    # ==================== ENDPOINT 1: ASN OVERVIEW ====================
    
    def extract_asn_overview(self, asn_list: List[str]) -> List[Dict]:
        """
        Extract ASN overview data for given Autonomous System Numbers.
        
        Args:
            asn_list: List of ASN numbers (e.g., ['3333', '15169'])
            
        Returns:
            List[Dict]: Extracted ASN data
        """
        logger.info(f"Extracting ASN overview data for {len(asn_list)} ASNs")
        extracted_data = []
        
        for asn in asn_list:
            try:
                params = {'resource': f'AS{asn}'}
                data = self._make_api_request('as-overview', params)
                
                if data:
                    extracted_data.append({
                        'asn': asn,
                        'raw_data': data,
                        'extraction_timestamp': datetime.utcnow()
                    })
                    self.stats['asn_overview']['extracted'] += 1
                else:
                    self.stats['asn_overview']['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error extracting ASN {asn}: {e}")
                self.stats['asn_overview']['errors'] += 1
        
        logger.info(f"Successfully extracted {len(extracted_data)} ASN records")
        return extracted_data
    
    def transform_asn_overview(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Transform ASN overview data into MongoDB-compatible format.
        
        Args:
            raw_data: Raw extracted data
            
        Returns:
            List[Dict]: Transformed documents
        """
        logger.info(f"Transforming {len(raw_data)} ASN records")
        transformed_docs = []
        
        for record in raw_data:
            try:
                api_data = record['raw_data'].get('data', {})
                
                # Extract holder information
                holder = api_data.get('holder', 'Unknown')
                
                # Extract announced status
                announced = api_data.get('announced', False)
                
                # Extract block information
                block = api_data.get('block', {})
                
                # Create transformed document
                doc = {
                    'asn': record['asn'],
                    'holder': holder,
                    'announced': announced,
                    'block_resource': block.get('resource', ''),
                    'block_name': block.get('name', ''),
                    'block_desc': block.get('desc', ''),
                    'type': api_data.get('type', ''),
                    'extraction_timestamp': record['extraction_timestamp'],
                    'ingestion_timestamp': datetime.utcnow(),
                    'data_quality_score': self._calculate_quality_score(api_data),
                    'raw_data': record['raw_data']
                }
                
                transformed_docs.append(doc)
                self.stats['asn_overview']['transformed'] += 1
                
            except Exception as e:
                logger.error(f"Error transforming ASN record: {e}")
                self.stats['asn_overview']['errors'] += 1
        
        logger.info(f"Successfully transformed {len(transformed_docs)} ASN records")
        return transformed_docs
    
    # ==================== ENDPOINT 2: NETWORK INFO ====================
    
    def extract_network_info(self, prefix_list: List[str]) -> List[Dict]:
        """
        Extract network information for given IP prefixes.
        
        Args:
            prefix_list: List of IP prefixes (e.g., ['193.0.0.0/21', '8.8.8.0/24'])
            
        Returns:
            List[Dict]: Extracted network data
        """
        logger.info(f"Extracting network info for {len(prefix_list)} prefixes")
        extracted_data = []
        
        for prefix in prefix_list:
            try:
                params = {'resource': prefix}
                data = self._make_api_request('network-info', params)
                
                if data:
                    extracted_data.append({
                        'prefix': prefix,
                        'raw_data': data,
                        'extraction_timestamp': datetime.utcnow()
                    })
                    self.stats['network_info']['extracted'] += 1
                else:
                    self.stats['network_info']['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error extracting network info for {prefix}: {e}")
                self.stats['network_info']['errors'] += 1
        
        logger.info(f"Successfully extracted {len(extracted_data)} network records")
        return extracted_data
    
    def transform_network_info(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Transform network info data into MongoDB-compatible format.
        
        Args:
            raw_data: Raw extracted data
            
        Returns:
            List[Dict]: Transformed documents
        """
        logger.info(f"Transforming {len(raw_data)} network records")
        transformed_docs = []
        
        for record in raw_data:
            try:
                api_data = record['raw_data'].get('data', {})
                
                # Extract ASN information
                asns = api_data.get('asns', [])
                
                # Extract prefix information
                prefix_data = api_data.get('prefix', '')
                
                # Create transformed document
                doc = {
                    'prefix': record['prefix'],
                    'asns': asns,
                    'prefix_info': prefix_data,
                    'num_asns': len(asns),
                    'extraction_timestamp': record['extraction_timestamp'],
                    'ingestion_timestamp': datetime.utcnow(),
                    'data_quality_score': self._calculate_quality_score(api_data),
                    'raw_data': record['raw_data']
                }
                
                transformed_docs.append(doc)
                self.stats['network_info']['transformed'] += 1
                
            except Exception as e:
                logger.error(f"Error transforming network record: {e}")
                self.stats['network_info']['errors'] += 1
        
        logger.info(f"Successfully transformed {len(transformed_docs)} network records")
        return transformed_docs
    
    # ==================== ENDPOINT 3: GEOLOCATION ====================
    
    def extract_geolocation(self, resource_list: List[str]) -> List[Dict]:
        """
        Extract geolocation data for given resources (IPs or ASNs).
        
        Args:
            resource_list: List of resources (e.g., ['8.8.8.8', 'AS15169'])
            
        Returns:
            List[Dict]: Extracted geolocation data
        """
        logger.info(f"Extracting geolocation data for {len(resource_list)} resources")
        extracted_data = []
        
        for resource in resource_list:
            try:
                params = {'resource': resource}
                data = self._make_api_request('geoloc', params)
                
                if data:
                    extracted_data.append({
                        'resource': resource,
                        'raw_data': data,
                        'extraction_timestamp': datetime.utcnow()
                    })
                    self.stats['geolocation']['extracted'] += 1
                else:
                    self.stats['geolocation']['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error extracting geolocation for {resource}: {e}")
                self.stats['geolocation']['errors'] += 1
        
        logger.info(f"Successfully extracted {len(extracted_data)} geolocation records")
        return extracted_data
    
    def transform_geolocation(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Transform geolocation data into MongoDB-compatible format.
        
        Args:
            raw_data: Raw extracted data
            
        Returns:
            List[Dict]: Transformed documents
        """
        logger.info(f"Transforming {len(raw_data)} geolocation records")
        transformed_docs = []
        
        for record in raw_data:
            try:
                api_data = record['raw_data'].get('data', {})
                
                # Extract location information
                locations = api_data.get('locations', [])
                
                # Process each location
                for location in locations:
                    doc = {
                        'resource': record['resource'],
                        'country': location.get('country', 'Unknown'),
                        'city': location.get('city', ''),
                        'latitude': location.get('latitude'),
                        'longitude': location.get('longitude'),
                        'covered_percentage': location.get('covered_percentage', 0),
                        'extraction_timestamp': record['extraction_timestamp'],
                        'ingestion_timestamp': datetime.utcnow(),
                        'data_quality_score': self._calculate_quality_score(location),
                        'raw_data': record['raw_data']
                    }
                    
                    transformed_docs.append(doc)
                    self.stats['geolocation']['transformed'] += 1
                
            except Exception as e:
                logger.error(f"Error transforming geolocation record: {e}")
                self.stats['geolocation']['errors'] += 1
        
        logger.info(f"Successfully transformed {len(transformed_docs)} geolocation records")
        return transformed_docs
    
    # ==================== LOAD FUNCTIONS ====================
    
    def load_data(self, collection_name: str, documents: List[Dict], endpoint_type: str) -> Dict[str, int]:
        """
        Load transformed data into MongoDB collection.
        
        Args:
            collection_name: MongoDB collection name
            documents: List of documents to insert
            endpoint_type: Type of endpoint for statistics
            
        Returns:
            Dict with insert/update counts
        """
        if not documents:
            logger.warning(f"No documents to load for {collection_name}")
            return {'inserted': 0, 'updated': 0}
        
        collection = self.db[collection_name]
        inserted_count = 0
        updated_count = 0
        
        for doc in documents:
            try:
                # Determine unique key based on endpoint type
                if endpoint_type == 'asn_overview':
                    unique_key = {'asn': doc['asn']}
                elif endpoint_type == 'network_info':
                    unique_key = {'prefix': doc['prefix']}
                else:  # geolocation
                    unique_key = {
                        'resource': doc['resource'],
                        'country': doc['country'],
                        'city': doc['city']
                    }
                
                # Upsert document
                result = collection.update_one(
                    unique_key,
                    {'$set': doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1
                
                self.stats[endpoint_type]['loaded'] += 1
                
            except Exception as e:
                logger.error(f"Error loading document into {collection_name}: {e}")
                self.stats[endpoint_type]['errors'] += 1
        
        logger.info(f"Data load completed for {collection_name}: {inserted_count} inserted, {updated_count} updated")
        return {'inserted': inserted_count, 'updated': updated_count}
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def _calculate_quality_score(self, data: Dict) -> float:
        """
        Calculate data quality score based on completeness.
        
        Args:
            data: Data dictionary to evaluate
            
        Returns:
            float: Quality score between 0 and 1
        """
        if not data:
            return 0.0
        
        total_fields = len(data)
        non_empty_fields = sum(1 for v in data.values() if v not in [None, '', [], {}])
        
        return round(non_empty_fields / total_fields, 2) if total_fields > 0 else 0.0
    
    def print_statistics(self):
        """Print comprehensive pipeline statistics."""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("RIPEstat ETL Pipeline - Execution Summary")
        print("="*70)
        
        for endpoint, stats in self.stats.items():
            print(f"\n{endpoint.upper().replace('_', ' ')}:")
            print(f"  Extracted: {stats['extracted']}")
            print(f"  Transformed: {stats['transformed']}")
            print(f"  Loaded: {stats['loaded']}")
            print(f"  Errors: {stats['errors']}")
        
        total_processed = sum(s['loaded'] for s in self.stats.values())
        total_errors = sum(s['errors'] for s in self.stats.values())
        
        print(f"\nTOTAL RECORDS PROCESSED: {total_processed}")
        print(f"TOTAL ERRORS: {total_errors}")
        print(f"EXECUTION TIME: {elapsed_time:.2f} seconds")
        print("="*70 + "\n")
    
    def run_pipeline(self):
        """Execute the complete ETL pipeline for all three endpoints."""
        self.start_time = time.time()
        logger.info("Starting RIPEstat ETL pipeline execution")
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            logger.error("Failed to connect to MongoDB. Exiting pipeline.")
            return False
        
        try:
            # ===== ENDPOINT 1: ASN OVERVIEW =====
            logger.info("\n" + "="*50)
            logger.info("Processing Endpoint 1: ASN Overview")
            logger.info("="*50)
            
            asn_list = ['3333', '15169', '13335', '16509', '8075']  # Sample ASNs
            
            asn_raw = self.extract_asn_overview(asn_list)
            asn_transformed = self.transform_asn_overview(asn_raw)
            self.load_data(self.collections['asn_overview'], asn_transformed, 'asn_overview')
            
            # ===== ENDPOINT 2: NETWORK INFO =====
            logger.info("\n" + "="*50)
            logger.info("Processing Endpoint 2: Network Info")
            logger.info("="*50)
            
            prefix_list = ['193.0.0.0/21', '8.8.8.0/24', '1.1.1.0/24']  # Sample prefixes
            
            network_raw = self.extract_network_info(prefix_list)
            network_transformed = self.transform_network_info(network_raw)
            self.load_data(self.collections['network_info'], network_transformed, 'network_info')
            
            # ===== ENDPOINT 3: GEOLOCATION =====
            logger.info("\n" + "="*50)
            logger.info("Processing Endpoint 3: Geolocation")
            logger.info("="*50)
            
            resource_list = ['8.8.8.8', '1.1.1.1', 'AS15169']  # Sample resources
            
            geo_raw = self.extract_geolocation(resource_list)
            geo_transformed = self.transform_geolocation(geo_raw)
            self.load_data(self.collections['geolocation'], geo_transformed, 'geolocation')
            
            # Print final statistics
            self.print_statistics()
            
            logger.info("ETL pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            return False
            
        finally:
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("MongoDB connection closed")


def main():
    """Main entry point for the ETL pipeline."""
    print("\n" + "="*70)
    print("RIPEstat ETL Data Connector - Assignment 2")
    print("Student: Seetharam Killivalavan | Roll: 3122225001124")
    print("="*70 + "\n")
    
    pipeline = RIPEstatETLPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n✅ Pipeline execution completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Pipeline execution failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()