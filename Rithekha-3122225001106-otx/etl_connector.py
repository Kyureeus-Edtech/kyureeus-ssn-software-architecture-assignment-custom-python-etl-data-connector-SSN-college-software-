import os
import requests
import json
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class OTXETLConnector:
    def __init__(self):
        self.api_key = os.getenv('OTX_API_KEY')
        self.base_url = "https://otx.alienvault.com"
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('DATABASE_NAME')
        self.collection_name = os.getenv('COLLECTION_NAME')
        
        # MongoDB setup
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        
        # Headers for API requests
        self.headers = {
            'X-OTX-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def extract_data(self, endpoint="/api/v1/pulses/subscribed", limit=50):
        """Extract data from OTX API"""
        try:
            url = f"{self.base_url}{endpoint}"
            params = {'limit': limit}
            
            print(f"Extracting data from: {url}")
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                response = requests.get(url, headers=self.headers, params=params)
            
            response.raise_for_status()
            data = response.json()
            
            print(f"Successfully extracted {len(data.get('results', []))} records")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error during extraction: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def transform_data(self, raw_data):
        """Transform data for MongoDB compatibility"""
        if not raw_data or 'results' not in raw_data:
            print("No data to transform")
            return []
        
        transformed_records = []
        
        for pulse in raw_data['results']:
            try:
                # Create transformed record
                transformed_record = {
                    'pulse_id': pulse.get('id'),
                    'name': pulse.get('name', ''),
                    'description': pulse.get('description', ''),
                    'author_name': pulse.get('author_name', ''),
                    'created': pulse.get('created'),
                    'modified': pulse.get('modified'),
                    'tags': pulse.get('tags', []),
                    'references': pulse.get('references', []),
                    'public': pulse.get('public', False),
                    'indicators_count': len(pulse.get('indicators', [])),
                    'indicators': pulse.get('indicators', []),
                    'malware_families': pulse.get('malware_families', []),
                    'attack_ids': pulse.get('attack_ids', []),
                    # Add ingestion timestamp (timezone-aware)
                    'ingestion_timestamp': datetime.now(timezone.utc),
                    'source': 'otx_alienvault',
                    'raw_data': pulse  # Keep original data for reference
                }
                
                transformed_records.append(transformed_record)
                
            except Exception as e:
                print(f"Error transforming record: {e}")
                continue
        
        print(f"Successfully transformed {len(transformed_records)} records")
        return transformed_records
    
    def load_data(self, transformed_data):
        """Load transformed data into MongoDB"""
        if not transformed_data:
            print("No data to load")
            return 0
        
        try:
            # Insert data into MongoDB
            result = self.collection.insert_many(transformed_data)
            inserted_count = len(result.inserted_ids)
            
            print(f"Successfully loaded {inserted_count} records into MongoDB")
            return inserted_count
            
        except Exception as e:
            print(f"Error during loading: {e}")
            return 0
    
    def run_etl_pipeline(self):
        """Run the complete ETL pipeline"""
        print("=== Starting OTX ETL Pipeline ===")
        start_time = datetime.now(timezone.utc)
        
        # Extract
        print("\n1. EXTRACT Phase")
        raw_data = self.extract_data()
        
        if not raw_data:
            print("Extraction failed. Stopping pipeline.")
            return False
        
        # Transform
        print("\n2. TRANSFORM Phase")
        transformed_data = self.transform_data(raw_data)
        
        if not transformed_data:
            print("Transformation failed. Stopping pipeline.")
            return False
        
        # Load
        print("\n3. LOAD Phase")
        loaded_count = self.load_data(transformed_data)
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n=== Pipeline Complete ===")
        print(f"Duration: {duration} seconds")
        print(f"Records processed: {loaded_count}")
        
        return loaded_count > 0
    
    def test_connection(self):
        """Test API and MongoDB connections"""
        print("Testing connections...")
        
        # Test API connection
        try:
            response = requests.get(f"{self.base_url}/api/v1/user/me", headers=self.headers)
            if response.status_code == 200:
                print("✅ API connection successful")
            else:
                print(f"❌ API connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection error: {e}")
            return False
        
        # Test MongoDB connection
        try:
            self.client.admin.command('ping')
            print("✅ MongoDB connection successful")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False

def main():
    # Initialize connector
    connector = OTXETLConnector()
    
    # Test connections first
    if not connector.test_connection():
        print("Connection tests failed. Please check your configuration.")
        return
    
    # Run ETL pipeline
    success = connector.run_etl_pipeline()
    
    if success:
        print("ETL pipeline completed successfully! ✅")
    else:
        print("ETL pipeline failed! ❌")

if __name__ == "__main__":
    main()
