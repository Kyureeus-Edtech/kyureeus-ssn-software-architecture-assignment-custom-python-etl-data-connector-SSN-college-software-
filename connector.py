"""
PublicWWW API ETL Connector
Author: Dharunika Sasikumar
Roll Number:3122225001026

Description: 
ETL pipeline to extract data from PublicWWW API endpoints,
transform the data, and load it into MongoDB collection.
"""

import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PublicWWWETL:
    """ETL Pipeline for PublicWWW API"""
    
    def __init__(self):
        """Initialize the ETL connector with environment variables"""
        load_dotenv()
        
        
        self.api_key = os.getenv('PUBLICWWW_API_KEY')
        
        self.base_url = 'https://publicwww.com/websites'
        
       
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGODB_DATABASE', 'etl_database')
        self.collection_name = 'publicwww_raw'
        
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
        
        self.mongo_client = None
        self.db = None
        self.collection = None
        
        self._validate_config()
        
    def _validate_config(self):
        """Validate that required environment variables are set"""
        if not self.api_key:
            logger.warning("PUBLICWWW_API_KEY not found. Using free tier endpoints.")
        else:
            logger.info(f"API Key loaded: {self.api_key[:8]}...")
        
        logger.info("Configuration validated successfully")
    
    def connect_mongodb(self):
        """Establish connection to MongoDB"""
        try:
            self.mongo_client = MongoClient(self.mongo_uri)
            self.db = self.mongo_client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            
            self.mongo_client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.db_name}.{self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            return False
    
    def _make_request(self, url, params=None):
        """
        Make HTTP request to PublicWWW
        
        Args:
            url (str): Full URL to request
            params (dict): Query parameters
            
        Returns:
            dict: Response data or None if failed
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/json,*/*',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        
        if self.api_key and params is None:
            params = {}
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            logger.info(f"Making GET request to: {url}")
            if params:
                logger.info(f"With API key: {bool(self.api_key)}")
            
            response = requests.get(
                url, 
                headers=headers, 
                params=params,
                timeout=30,
                allow_redirects=True
            )
            
            logger.info(f"Response status code: {response.status_code}")
            
           
            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting before retry...")
                time.sleep(self.rate_limit_delay * 5)
                return self._make_request(url, params)
            
            if response.status_code != 200:
                logger.error(f"Request failed with status code: {response.status_code}")
                return None
            
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                logger.info("Received JSON response")
                return response.json()
            else:
                logger.info(f"Received HTML response (length: {len(response.text)} chars)")
                return {
                    'content_type': 'html',
                    'url': url,
                    'status_code': response.status_code,
                    'html_content': response.text[:5000],  # First 5000 chars
                    'full_length': len(response.text),
                    'response_headers': dict(response.headers)
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {
                'content_type': 'text',
                'raw_text': response.text[:5000]
            }
    
    def extract_search_data(self, query):
        """
        Extract search results from PublicWWW
        
        Args:
            query (str): Search query (e.g., "google-analytics.com/analytics.js")
            
        Returns:
            dict: Search results data
        """
        
        search_url = f"https://publicwww.com/websites/{query}/"
        
        data = self._make_request(search_url)
        time.sleep(self.rate_limit_delay)
        
        return {
            'endpoint': 'search',
            'query': query,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data
        }
    
    def extract_all_endpoints(self):
        """
        Extract data from multiple PublicWWW endpoints
        
        Returns:
            dict: Combined data from all endpoints
        """
        logger.info("="*60)
        logger.info("Starting extraction from multiple endpoints")
        logger.info("="*60)
        
        all_data = {
            'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
            'endpoints': []
        }
        
        
        queries = [
            {'type': 'analytics', 'query': 'google-analytics.com/analytics.js'},
            {'type': 'technology', 'query': 'jquery'},
            {'type': 'cms', 'query': 'wordpress'},
            {'type': 'tracking', 'query': 'facebook.com/tr'},
            {'type': 'ad_network', 'query': 'googlesyndication.com'},
            # Add more endpoints below if needed:
            # {'type': 'framework', 'query': 'react'},
            # {'type': 'framework', 'query': 'vue.js'},
            # {'type': 'analytics', 'query': 'hotjar'},
            # {'type': 'cdn', 'query': 'cloudflare'},
            # {'type': 'payment', 'query': 'stripe'},
        ]
        
        for idx, item in enumerate(queries, 1):
            try:
                logger.info(f"\n[{idx}/{len(queries)}] Extracting: {item['type']} - {item['query']}")
                
                data = self.extract_search_data(item['query'])
                all_data['endpoints'].append(data)
                
                logger.info(f"✓ Successfully extracted data for: {item['query']}")
                
            except Exception as e:
                logger.error(f"✗ Failed to extract {item['query']}: {str(e)}")
                all_data['endpoints'].append({
                    'query': item['query'],
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        logger.info("="*60)
        logger.info(f"Extraction complete: {len(all_data['endpoints'])} endpoints processed")
        logger.info("="*60)
        
        return all_data
    
    def transform(self, raw_data):
        """
        Transform raw API data for MongoDB compatibility
        
        Args:
            raw_data (dict): Raw data from API
            
        Returns:
            dict: Transformed data
        """
        if not raw_data:
            logger.warning("No data to transform")
            return None
        
        try:
            
            endpoints = raw_data.get('endpoints', [])
            successful = sum(1 for e in endpoints if 'error' not in e)
            failed = sum(1 for e in endpoints if 'error' in e)
            
            transformed = {
                'source': 'publicwww_api',
                'ingestion_timestamp': datetime.now(timezone.utc),
                'raw_data': raw_data,
                'metadata': {
                    'data_version': '1.0',
                    'transformer': 'PublicWWWETL',
                    'endpoint_count': len(endpoints),
                    'extraction_time': raw_data.get('extraction_timestamp'),
                    'has_api_key': bool(self.api_key),
                    'summary': {
                        'total_queries': len(endpoints),
                        'successful_queries': successful,
                        'failed_queries': failed
                    }
                }
            }
            
            logger.info(f"Data transformed successfully:")
            logger.info(f"  - Total endpoints: {len(endpoints)}")
            logger.info(f"  - Successful: {successful}")
            logger.info(f"  - Failed: {failed}")
            
            return transformed
            
        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            return None
    
    def load(self, transformed_data):
        """
        Load transformed data into MongoDB
        
        Args:
            transformed_data (dict): Transformed data to load
            
        Returns:
            bool: Success status
        """
        if not transformed_data:
            logger.warning("No data to load")
            return False
        
        try:
            # Insert document into MongoDB
            result = self.collection.insert_one(transformed_data)
            
            logger.info(f"Data loaded successfully!")
            logger.info(f"  - Document ID: {result.inserted_id}")
            logger.info(f"  - Collection: {self.db_name}.{self.collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load data into MongoDB: {str(e)}")
            return False
    
    def validate_data(self):
        """Validate the loaded data in MongoDB"""
        try:
            # Count documents
            doc_count = self.collection.count_documents({})
            logger.info(f"\n{'='*60}")
            logger.info("DATA VALIDATION RESULTS")
            logger.info(f"{'='*60}")
            logger.info(f"Total documents in collection: {doc_count}")
            
            # Get  document
            latest_doc = self.collection.find_one(
                sort=[('ingestion_timestamp', -1)]
            )
            
            if latest_doc:
                logger.info(f"Latest document details:")
                logger.info(f"  - Timestamp: {latest_doc.get('ingestion_timestamp')}")
                logger.info(f"  - Source: {latest_doc.get('source')}")
                
                metadata = latest_doc.get('metadata', {})
                logger.info(f"  - Endpoints processed: {metadata.get('endpoint_count', 0)}")
                logger.info(f"  - Has API key: {metadata.get('has_api_key', False)}")
                
                summary = metadata.get('summary', {})
                logger.info(f"  - Successful queries: {summary.get('successful_queries', 0)}")
                logger.info(f"  - Failed queries: {summary.get('failed_queries', 0)}")
                
                endpoints = latest_doc.get('raw_data', {}).get('endpoints', [])
                if endpoints:
                    logger.info(f"\nSample queries extracted:")
                    for i, ep in enumerate(endpoints[:3], 1):
                        query = ep.get('query', 'Unknown')
                        has_data = 'data' in ep and ep['data'] is not None
                        logger.info(f"  {i}. {query} - {'✓ Data extracted' if has_data else '✗ No data'}")
            
            logger.info(f"{'='*60}\n")
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def run_etl_pipeline(self, single_query=None):
        """
        Execute the complete ETL pipeline
        
        Args:
            single_query (str): Optional single query for extraction
            
        Returns:
            bool: Success status
        """
        logger.info("Starting ETL pipeline execution")
        
        try:
            if not self.connect_mongodb():
                logger.error("ETL pipeline aborted: MongoDB connection failed")
                return False
            
            logger.info("\n" + "="*60)
            logger.info("STEP 1/3: EXTRACT - Fetching data from PublicWWW")
            logger.info("="*60)
            
            if single_query:
                raw_data = {
                    'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
                    'endpoints': [self.extract_search_data(single_query)]
                }
            else:
                raw_data = self.extract_all_endpoints()
            
            if not raw_data:
                logger.error("ETL pipeline aborted: Extraction failed")
                return False
            
            logger.info("\n" + "="*60)
            logger.info("STEP 2/3: TRANSFORM - Processing data")
            logger.info("="*60)
            transformed_data = self.transform(raw_data)
            
            if not transformed_data:
                logger.error("ETL pipeline aborted: Transformation failed")
                return False
            
            logger.info("\n" + "="*60)
            logger.info("STEP 3/3: LOAD - Storing data in MongoDB")
            logger.info("="*60)
            success = self.load(transformed_data)
            
            if success:
                logger.info("\n" + "="*60)
                logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY! ✓")
                logger.info("="*60)
                self.validate_data()
            else:
                logger.error("ETL pipeline failed at load stage")
            
            return success
            
        except Exception as e:
            logger.error(f"ETL pipeline failed with exception: {str(e)}")
            return False
        
        finally:
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("MongoDB connection closed")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("PublicWWW API ETL Connector - Enhanced Version")
    print("="*60 + "\n")
    
    etl = PublicWWWETL()
    
    success = etl.run_etl_pipeline()
    
    
    print("\n" + "="*60)
    print(f"FINAL STATUS: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()