#!/usr/bin/env python3
"""
CIRCL Passive DNS ETL Data Connector
====================================

This script implements a complete ETL pipeline for the CIRCL Passive DNS API.
It extracts DNS data, transforms it for MongoDB compatibility, and loads it into a MongoDB collection.

Author: Kavin (Roll Number: 302004)
Assignment: Software Architecture - Custom Python ETL Data Connector
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class CIRCLPassiveDNSError(Exception):
    """Custom exception for CIRCL Passive DNS API errors."""
    pass


class CIRCLPassiveDNSConnector:
    """
    ETL Connector for CIRCL Passive DNS API.
    
    This class handles the complete ETL pipeline:
    - Extract: Connect to CIRCL Passive DNS API and retrieve data
    - Transform: Clean and format data for MongoDB compatibility
    - Load: Store transformed data in MongoDB collection
    """
    
    def __init__(self):
        """Initialize the connector with environment variables."""
        load_dotenv()
        
        # API Configuration
        self.base_url = os.getenv('CIRCL_BASE_URL', 'https://www.circl.lu')
        self.username = os.getenv('CIRCL_USERNAME')
        self.password = os.getenv('CIRCL_PASSWORD')
        self.timeout = int(os.getenv('API_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # MongoDB Configuration
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.mongodb_database = os.getenv('MONGODB_DATABASE', 'etl_data')
        self.mongodb_collection = os.getenv('MONGODB_COLLECTION', 'circl_passivedns_raw')
        
        # Validate required credentials
        if not self.username or not self.password:
            raise ValueError("CIRCL_USERNAME and CIRCL_PASSWORD must be set in environment variables")
        
        # Initialize MongoDB connection
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_collection = None
        
        # Session for API requests
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            'User-Agent': 'CIRCL-PassiveDNS-ETL-Connector/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        logger.info("CIRCL Passive DNS Connector initialized", 
                   base_url=self.base_url,
                   mongodb_database=self.mongodb_database,
                   mongodb_collection=self.mongodb_collection)
    
    def connect_mongodb(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.mongo_client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.mongo_client.admin.command('ping')
            self.mongo_db = self.mongo_client[self.mongodb_database]
            self.mongo_collection = self.mongo_db[self.mongodb_collection]
            
            # Create index on timestamp for better query performance
            self.mongo_collection.create_index("ingestion_timestamp")
            self.mongo_collection.create_index("rrname")
            self.mongo_collection.create_index("rdata")
            
            logger.info("MongoDB connection established", 
                       database=self.mongodb_database,
                       collection=self.mongodb_collection)
            return True
            
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error connecting to MongoDB", error=str(e))
            return False
    
    def extract_data(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Extract data from CIRCL Passive DNS API.
        
        Args:
            query (str): DNS query to search for
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[Dict[str, Any]]: Raw data from API
            
        Raises:
            CIRCLPassiveDNSError: If API request fails
        """
        endpoint = "/pdb/query"
        url = urljoin(self.base_url, endpoint)
        
        params = {
            'q': query,
            'limit': limit
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info("Extracting data from CIRCL Passive DNS API", 
                           query=query, attempt=attempt + 1)
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Data extraction successful", 
                               records_count=len(data) if isinstance(data, list) else 0)
                    return data if isinstance(data, list) else [data]
                
                elif response.status_code == 401:
                    raise CIRCLPassiveDNSError("Authentication failed. Check credentials.")
                
                elif response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning("Rate limit exceeded, waiting", wait_time=wait_time)
                    time.sleep(wait_time)
                    continue
                
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                logger.warning("Request timeout", attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise CIRCLPassiveDNSError("Request timeout after all retries")
            
            except requests.exceptions.ConnectionError:
                logger.warning("Connection error", attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise CIRCLPassiveDNSError("Connection failed after all retries")
            
            except requests.exceptions.RequestException as e:
                raise CIRCLPassiveDNSError(f"API request failed: {str(e)}")
        
        raise CIRCLPassiveDNSError("Failed to extract data after all retries")
    
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw API data for MongoDB compatibility.
        
        Args:
            raw_data (List[Dict[str, Any]]): Raw data from API
            
        Returns:
            List[Dict[str, Any]]: Transformed data ready for MongoDB
        """
        transformed_data = []
        current_timestamp = datetime.now(timezone.utc)
        
        for record in raw_data:
            try:
                # Create transformed record with standard fields
                transformed_record = {
                    'ingestion_timestamp': current_timestamp,
                    'source': 'circl_passive_dns',
                    'rrname': record.get('rrname', ''),
                    'rrtype': record.get('rrtype', ''),
                    'rdata': record.get('rdata', ''),
                    'time_first': record.get('time_first', ''),
                    'time_last': record.get('time_last', ''),
                    'count': record.get('count', 0),
                    'bailiwick': record.get('bailiwick', ''),
                    'raw_record': record  # Keep original for debugging
                }
                
                # Clean and validate data
                transformed_record = self._clean_record(transformed_record)
                transformed_data.append(transformed_record)
                
            except Exception as e:
                logger.warning("Failed to transform record", 
                             record=record, error=str(e))
                continue
        
        logger.info("Data transformation completed", 
                   input_records=len(raw_data),
                   output_records=len(transformed_data))
        
        return transformed_data
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate individual record.
        
        Args:
            record (Dict[str, Any]): Record to clean
            
        Returns:
            Dict[str, Any]: Cleaned record
        """
        # Ensure required fields are strings
        for field in ['rrname', 'rrtype', 'rdata', 'bailiwick']:
            if field in record:
                record[field] = str(record[field]).strip()
        
        # Convert count to integer
        if 'count' in record:
            try:
                record['count'] = int(record['count'])
            except (ValueError, TypeError):
                record['count'] = 0
        
        # Validate timestamps
        for time_field in ['time_first', 'time_last']:
            if time_field in record and record[time_field]:
                try:
                    # Convert to ISO format if needed
                    if isinstance(record[time_field], (int, float)):
                        record[time_field] = datetime.fromtimestamp(
                            record[time_field], tz=timezone.utc
                        ).isoformat()
                except (ValueError, TypeError):
                    record[time_field] = None
        
        return record
    
    def load_data(self, transformed_data: List[Dict[str, Any]]) -> bool:
        """
        Load transformed data into MongoDB.
        
        Args:
            transformed_data (List[Dict[str, Any]]): Transformed data to load
            
        Returns:
            bool: True if all data loaded successfully, False otherwise
        """
        if not self.mongo_collection:
            logger.error("MongoDB collection not initialized")
            return False
        
        if not transformed_data:
            logger.warning("No data to load")
            return True
        
        try:
            # Insert documents in batches for better performance
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(transformed_data), batch_size):
                batch = transformed_data[i:i + batch_size]
                
                try:
                    result = self.mongo_collection.insert_many(batch, ordered=False)
                    total_inserted += len(result.inserted_ids)
                    logger.info("Batch inserted successfully", 
                               batch_size=len(batch),
                               total_inserted=total_inserted)
                
                except DuplicateKeyError:
                    # Handle duplicate documents gracefully
                    logger.warning("Some documents were duplicates, continuing...")
                    continue
                
                except Exception as e:
                    logger.error("Failed to insert batch", 
                               batch_start=i, error=str(e))
                    continue
            
            logger.info("Data loading completed", 
                       total_records=len(transformed_data),
                       inserted_records=total_inserted)
            
            return total_inserted > 0
            
        except Exception as e:
            logger.error("Failed to load data into MongoDB", error=str(e))
            return False
    
    def run_etl_pipeline(self, query: str, limit: int = 100) -> bool:
        """
        Run the complete ETL pipeline.
        
        Args:
            query (str): DNS query to process
            limit (int): Maximum number of records to process
            
        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        try:
            logger.info("Starting ETL pipeline", query=query, limit=limit)
            
            # Connect to MongoDB
            if not self.connect_mongodb():
                return False
            
            # Extract data
            raw_data = self.extract_data(query, limit)
            if not raw_data:
                logger.warning("No data extracted from API")
                return True
            
            # Transform data
            transformed_data = self.transform_data(raw_data)
            if not transformed_data:
                logger.warning("No data after transformation")
                return True
            
            # Load data
            success = self.load_data(transformed_data)
            
            if success:
                logger.info("ETL pipeline completed successfully")
            else:
                logger.error("ETL pipeline failed during data loading")
            
            return success
            
        except Exception as e:
            logger.error("ETL pipeline failed", error=str(e))
            return False
        
        finally:
            # Close MongoDB connection
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("MongoDB connection closed")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the MongoDB collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        if not self.mongo_collection:
            return {"error": "MongoDB not connected"}
        
        try:
            stats = {
                "total_documents": self.mongo_collection.count_documents({}),
                "latest_ingestion": None,
                "unique_domains": 0,
                "collection_size_mb": 0
            }
            
            # Get latest ingestion timestamp
            latest = self.mongo_collection.find_one(
                {}, sort=[("ingestion_timestamp", -1)]
            )
            if latest:
                stats["latest_ingestion"] = latest.get("ingestion_timestamp")
            
            # Get unique domain count
            stats["unique_domains"] = len(
                self.mongo_collection.distinct("rrname")
            )
            
            # Get collection size
            db_stats = self.mongo_db.command("collStats", self.mongodb_collection)
            stats["collection_size_mb"] = round(
                db_stats.get("size", 0) / (1024 * 1024), 2
            )
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {"error": str(e)}


def main():
    """Main function to run the ETL pipeline."""
    try:
        # Initialize connector
        connector = CIRCLPassiveDNSConnector()
        
        # Example queries to process
        queries = [
            "example.com",
            "google.com",
            "github.com"
        ]
        
        # Process each query
        for query in queries:
            logger.info("Processing query", query=query)
            success = connector.run_etl_pipeline(query, limit=50)
            
            if success:
                logger.info("Query processed successfully", query=query)
            else:
                logger.error("Query processing failed", query=query)
        
        # Get collection statistics
        stats = connector.get_collection_stats()
        logger.info("Collection statistics", stats=stats)
        
    except Exception as e:
        logger.error("Application failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

