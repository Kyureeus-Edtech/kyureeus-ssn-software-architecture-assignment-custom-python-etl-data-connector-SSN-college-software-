#!/usr/bin/env python3
"""
Custom ETL Data Connector for CISA KEV Catalog
File: etl_connector.py
Author: Rohith Arumugam S - 3122225001110
Description: ETL pipeline to extract Known Exploited Vulnerabilities data from CISA KEV Catalog,
             transform it for MongoDB compatibility, and load into MongoDB collection.
Data Source: Entry #16 from provided connector list - CISA KEV Catalog
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_connector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CISAKEVETLConnector:
    """
    ETL Connector class for extracting Known Exploited Vulnerabilities data from CISA KEV Catalog
    and loading it into MongoDB - Based on Entry #16 from connector requirements
    """
    
    def __init__(self):
        """Initialize the ETL connector with configuration"""
        # Load environment variables
        load_dotenv()
        
        # API Configuration (CISA KEV Catalog - Entry #16 from connector list)
        self.base_url = os.getenv('API_BASE_URL', 'https://www.cisa.gov')
        self.endpoint = os.getenv('API_ENDPOINT', '/sites/default/files/feeds/known_exploited_vulnerabilities.json')
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '2.0'))  # Conservative rate limiting
        
        # MongoDB Configuration
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGO_DATABASE', 'etl_database')
        self.collection_name = os.getenv('MONGO_COLLECTION', 'cisa_kev_raw')
        
        # Initialize MongoDB client
        self.mongo_client = None
        self.database = None
        self.collection = None
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETL-Connector/1.0 (Educational Purpose)',
            'Accept': 'application/json'
        })
    
    def connect_to_mongodb(self) -> bool:
        """
        Establish connection to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.mongo_client.admin.command('ping')
            self.database = self.mongo_client[self.database_name]
            self.collection = self.database[self.collection_name]
            logger.info(f"Successfully connected to MongoDB: {self.database_name}.{self.collection_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extract Known Exploited Vulnerabilities data from CISA KEV Catalog (Entry #16 from connector list)
        
        Returns:
            List[Dict]: Extracted KEV data or empty list on failure
        """
        try:
            # Build full URL from connector list specification
            url = f"{self.base_url}{self.endpoint}"
            
            logger.info(f"Extracting KEV data from: {url}")
            
            response = self.session.get(url, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Rate limit hit, waiting...")
                time.sleep(self.rate_limit_delay * 2)
                response = self.session.get(url, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            # Extract vulnerabilities from CISA KEV format
            catalog_version = data.get('catalogVersion', 'unknown')
            date_released = data.get('dateReleased', 'unknown')
            count = data.get('count', 0)
            vulnerabilities = data.get('vulnerabilities', [])
            
            logger.info(f"CISA KEV Catalog Version: {catalog_version}")
            logger.info(f"Date Released: {date_released}")
            logger.info(f"Total vulnerabilities in catalog: {count}")
            logger.info(f"Successfully extracted {len(vulnerabilities)} KEV records")
            
            # Add catalog metadata to each vulnerability
            for vuln in vulnerabilities:
                vuln['catalog_metadata'] = {
                    'catalog_version': catalog_version,
                    'date_released': date_released,
                    'total_count': count
                }
            
            return vulnerabilities
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}")
            return []
    
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw CISA KEV data for MongoDB compatibility
        
        Args:
            raw_data (List[Dict]): Raw KEV data from CISA API
            
        Returns:
            List[Dict]: Transformed data
        """
        transformed_data = []
        current_timestamp = datetime.now(timezone.utc)
        
        for kev_record in raw_data:
            try:
                # Extract KEV details
                cve_id = kev_record.get('cveID', 'unknown')
                vendor_project = kev_record.get('vendorProject', '')
                product = kev_record.get('product', '')
                vulnerability_name = kev_record.get('vulnerabilityName', '')
                date_added = kev_record.get('dateAdded', '')
                short_description = kev_record.get('shortDescription', '')
                required_action = kev_record.get('requiredAction', '')
                due_date = kev_record.get('dueDate', '')
                known_ransomware = kev_record.get('knownRansomwareCampaignUse', 'Unknown')
                notes = kev_record.get('notes', '')
                
                # Parse dates
                date_added_parsed = self._parse_date(date_added)
                due_date_parsed = self._parse_date(due_date)
                
                # Calculate derived fields
                is_recent = self._is_recent_addition(date_added_parsed)
                is_overdue = self._is_overdue(due_date_parsed)
                risk_level = self._calculate_risk_level(known_ransomware, is_overdue, vulnerability_name)
                
                # Create transformed record
                transformed_record = {
                    # Original data
                    'original_data': kev_record,
                    
                    # ETL metadata
                    'etl_metadata': {
                        'ingestion_timestamp': current_timestamp,
                        'source': 'cisa_kev_catalog',
                        'version': '1.0',
                        'record_id': cve_id,
                        'data_quality_score': self._calculate_kev_quality(kev_record)
                    },
                    
                    # Flatten and clean important fields
                    'cve_id': cve_id,
                    'vendor_project': vendor_project.strip(),
                    'product': product.strip(),
                    'vulnerability_name': vulnerability_name.strip(),
                    'short_description': short_description.strip(),
                    'required_action': required_action.strip(),
                    'date_added': date_added,
                    'due_date': due_date,
                    'date_added_parsed': date_added_parsed,
                    'due_date_parsed': due_date_parsed,
                    'known_ransomware_use': known_ransomware,
                    'notes': notes.strip(),
                    
                    # Derived fields
                    'is_recent_addition': is_recent,
                    'is_overdue': is_overdue,
                    'risk_level': risk_level,
                    'description_length': len(short_description),
                    'has_notes': bool(notes.strip()),
                    'vendor_product_combined': f"{vendor_project} {product}".strip(),
                    'days_since_added': self._days_since_date(date_added_parsed),
                    'days_until_due': self._days_until_date(due_date_parsed),
                    
                    # Catalog metadata
                    'catalog_version': kev_record.get('catalog_metadata', {}).get('catalog_version'),
                    'catalog_date_released': kev_record.get('catalog_metadata', {}).get('date_released'),
                    'catalog_total_count': kev_record.get('catalog_metadata', {}).get('total_count')
                }
                
                transformed_data.append(transformed_record)
                
            except Exception as e:
                logger.warning(f"Failed to transform KEV record {kev_record.get('cveID', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully transformed {len(transformed_data)} KEV records")
        return transformed_data
    
    def _calculate_kev_quality(self, kev: Dict[str, Any]) -> float:
        """
        Calculate a simple data quality score for KEV record (0-1)
        
        Args:
            kev (Dict): KEV data
            
        Returns:
            float: Quality score
        """
        score = 0.0
        total_checks = 6
        
        # Check for required fields
        if kev.get('cveID'):
            score += 1/total_checks
        if kev.get('vendorProject'):
            score += 1/total_checks
        if kev.get('product'):
            score += 1/total_checks
        if kev.get('vulnerabilityName'):
            score += 1/total_checks
        if kev.get('shortDescription'):
            score += 1/total_checks
        if kev.get('requiredAction'):
            score += 1/total_checks
        
        return round(score, 2)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                return None
    
    def _is_recent_addition(self, date_added: Optional[datetime]) -> bool:
        """Check if KEV was added recently (within last 30 days)"""
        if not date_added:
            return False
        cutoff = datetime.now() - timedelta(days=30)
        return date_added > cutoff
    
    def _is_overdue(self, due_date: Optional[datetime]) -> bool:
        """Check if the required action due date has passed"""
        if not due_date:
            return False
        return datetime.now() > due_date
    
    def _calculate_risk_level(self, ransomware_use: str, is_overdue: bool, vuln_name: str) -> str:
        """Calculate risk level based on various factors"""
        if ransomware_use == 'Known':
            return 'CRITICAL'
        elif is_overdue:
            return 'HIGH'
        elif any(keyword in vuln_name.lower() for keyword in ['remote', 'execution', 'bypass', 'privilege']):
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def _days_since_date(self, date_obj: Optional[datetime]) -> Optional[int]:
        """Calculate days since a given date"""
        if not date_obj:
            return None
        return (datetime.now() - date_obj).days
    
    def _days_until_date(self, date_obj: Optional[datetime]) -> Optional[int]:
        """Calculate days until a given date"""
        if not date_obj:
            return None
        return (date_obj - datetime.now()).days
    
    def load_data(self, transformed_data: List[Dict[str, Any]]) -> bool:
        """
        Load transformed CISA KEV data into MongoDB
        
        Args:
            transformed_data (List[Dict]): Transformed data to load
            
        Returns:
            bool: True if load successful, False otherwise
        """
        if not transformed_data:
            logger.warning("No data to load")
            return True
        
        try:
            # Create indexes for better query performance
            self.collection.create_index("etl_metadata.ingestion_timestamp")
            self.collection.create_index("cve_id", unique=True)
            self.collection.create_index("risk_level")
            self.collection.create_index("known_ransomware_use")
            self.collection.create_index("is_overdue")
            self.collection.create_index("date_added")
            
            # Use direct insert/update operations
            inserted_count = 0
            updated_count = 0
            
            for record in transformed_data:
                try:
                    # Try to update existing record, insert if not found
                    result = self.collection.replace_one(
                        {'cve_id': record['cve_id']},
                        record,
                        upsert=True
                    )
                    
                    if result.upserted_id:
                        inserted_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to process KEV {record.get('cve_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Data load completed: {inserted_count} inserted, {updated_count} updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def run_etl_pipeline(self) -> bool:
        """
        Execute the complete ETL pipeline for CISA KEV data
        
        Returns:
            bool: True if pipeline completed successfully
        """
        logger.info("Starting CISA KEV ETL pipeline execution")
        start_time = time.time()
        
        try:
            # Step 1: Connect to MongoDB
            if not self.connect_to_mongodb():
                return False
            
            # Step 2: Extract data from CISA KEV Catalog
            raw_data = self.extract_data()
            if not raw_data:
                logger.error("No data extracted, stopping pipeline")
                return False
            
            # Step 3: Transform data
            transformed_data = self.transform_data(raw_data)
            if not transformed_data:
                logger.error("No data transformed, stopping pipeline")
                return False
            
            # Step 4: Load data
            if not self.load_data(transformed_data):
                logger.error("Data load failed, stopping pipeline")
                return False
            
            execution_time = time.time() - start_time
            logger.info(f"ETL pipeline completed successfully in {execution_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return False
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the CISA KEV data in MongoDB collection
        
        Returns:
            Dict: Pipeline statistics
        """
        if self.collection is None:
            return {}
        
        try:
            total_records = self.collection.count_documents({})
            
            stats = {
                'total_kevs': total_records,
                'critical_risk_count': self.collection.count_documents({'risk_level': 'CRITICAL'}),
                'high_risk_count': self.collection.count_documents({'risk_level': 'HIGH'}),
                'ransomware_known_count': self.collection.count_documents({'known_ransomware_use': 'Known'}),
                'overdue_count': self.collection.count_documents({'is_overdue': True}),
                'recent_additions': self.collection.count_documents({'is_recent_addition': True}),
                'latest_ingestion': None,
                'avg_days_since_added': 0
            }
            
            # Only get additional stats if we have records
            if total_records > 0:
                # Get latest ingestion record
                latest_record = self.collection.find_one(
                    {}, sort=[('etl_metadata.ingestion_timestamp', -1)]
                )
                if latest_record:
                    stats['latest_ingestion'] = latest_record.get('etl_metadata', {}).get('ingestion_timestamp')
                
                # Get average days since added
                avg_result = list(self.collection.aggregate([
                    {'$match': {'days_since_added': {'$ne': None}}},
                    {'$group': {'_id': None, 'avg_days': {'$avg': '$days_since_added'}}}
                ]))
                if avg_result:
                    stats['avg_days_since_added'] = round(avg_result[0].get('avg_days', 0), 1)
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get pipeline stats: {e}")
            return {}


def main():
    """Main function to run the CISA KEV ETL connector"""
    connector = CISAKEVETLConnector()
    
    try:
        # Run the ETL pipeline
        success = connector.run_etl_pipeline()
        
        if success:
            logger.info("ETL process completed successfully")
            
            # Display stats (before closing connections)
            stats = connector.get_pipeline_stats()
            if stats:
                logger.info(f"Pipeline Statistics: {json.dumps(stats, indent=2, default=str)}")
            
            sys.exit(0)
        else:
            logger.error("ETL process failed")
            sys.exit(1)
    
    finally:
        # Cleanup connections after everything is done
        if connector.mongo_client:
            connector.mongo_client.close()
        if connector.session:
            connector.session.close()


if __name__ == "__main__":
    main()