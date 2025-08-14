import os
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import time


load_dotenv()

class ETLOtxConnector:
    def __init__(self):
        self.api_key = os.getenv('OTX_API_KEY')  
        if not self.api_key:
            raise ValueError("OTX_API_KEY not found in environment variables")
            
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {
            'X-OTX-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        
        try:
            self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
            self.db = self.client[os.getenv('DB_NAME', 'threat_intelligence')]
            self.collection = self.db[os.getenv('COLLECTION_NAME', 'otx_pulses')]
           
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            raise
    
    def extract(self):
        """Extract data from OTX API with retry logic"""
        max_retries = 3
        retry_delay = 2  
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/pulses/subscribed"
                print(f"Attempt {attempt + 1}: Fetching from {url}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                print("Successfully fetched data from OTX")
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    print("Authentication failed. Please verify your API key.")
                    return None
                elif response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', retry_delay))
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        print(f"Failed after {max_retries} attempts")
        return None

    def transform(self, data):
        """Transform data for MongoDB storage with validation"""
        if not data:
            print("No data to transform")
            return None
            
        try:
            pulses = data.get('results', [])
            if not pulses:
                print("No pulses found in response")
                return None
                
            transformed = []
            for pulse in pulses:
                if not isinstance(pulse, dict):
                    continue
                    
                transformed.append({
                    'pulse_id': pulse.get('id', 'unknown'),
                    'name': pulse.get('name', 'untitled'),
                    'description': pulse.get('description', ''),
                    'author': pulse.get('author', {}).get('username', 'anonymous'),
                    'tags': pulse.get('tags', []),
                    'indicators_count': pulse.get('indicator_count', 0),
                    'references': pulse.get('references', []),
                    'ingestion_time': datetime.utcnow(),
                    'otx_modified': pulse.get('modified', '')
                })
                
            print(f"Transformed {len(transformed)} pulses")
            return transformed
            
        except Exception as e:
            print(f"Transformation error: {e}")
            return None

    def load(self, data):
        """Load transformed data into MongoDB with error handling"""
        if not data:
            print("No data to load")
            return False
            
        try:
            result = self.collection.insert_many(data)
            print(f"Successfully inserted {len(result.inserted_ids)} documents")
            return True
        except Exception as e:
            print(f"MongoDB insertion error: {e}")
            return False

    def run_pipeline(self):
        """Run complete ETL pipeline with status reporting"""
        print("\n" + "="*50)
        print("Starting ETL Pipeline")
        print("="*50)
        
        # Extract
        print("\n[1/3] Extracting data from OTX...")
        raw_data = self.extract()
        if not raw_data:
            print("Extraction failed")
            return False
        
        # Transform
        print("\n[2/3] Transforming data...")
        transformed_data = self.transform(raw_data)
        if not transformed_data:
            print("Transformation failed")
            return False
        
        # Load
        print("\n[3/3] Loading data to MongoDB...")
        if self.load(transformed_data):
            print("\nETL pipeline completed successfully")
            return True
        else:
            print("\nETL pipeline failed at loading stage")
            return False

if __name__ == "__main__":
    try:
        connector = ETLOtxConnector()
        connector.run_pipeline()
    except Exception as e:
        print(f"Fatal error: {e}")