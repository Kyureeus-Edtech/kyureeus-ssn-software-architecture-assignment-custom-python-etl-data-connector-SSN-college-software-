import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

class VirusTotalETL:
    
    def __init__(self):
        self.base_url = "https://www.virustotal.com/api/v3"
        self.api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGODB_DATABASE', 'threat_intelligence')
        self.collection_name = 'virustotal_raw'
        
        self.sample_hashes = [
            "44d88612fea8a8f36de82e1278abb02f",
            "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ]
        
    def extract(self):
        headers = {'x-apikey': self.api_key}
        all_data = []
        
        for file_hash in self.sample_hashes:
            url = f"{self.base_url}/files/{file_hash}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                all_data.append(response.json())
                time.sleep(1)
            
        return all_data
    
    def transform(self, raw_data):
        transformed = []
        
        for item in raw_data:
            if 'data' in item:
                data = item['data']
                attrs = data.get('attributes', {})
                
                record = {
                    'file_id': data.get('id'),
                    'md5': attrs.get('md5'),
                    'sha256': attrs.get('sha256'),
                    'file_size': attrs.get('size'),
                    'scan_results': attrs.get('last_analysis_stats', {}),
                    'ingestion_time': datetime.utcnow(),
                    'source': 'virustotal'
                }
                transformed.append(record)
                
        return transformed
    
    def load(self, data):
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.collection_name]
        
        collection.insert_many(data)
        client.close()
        
    def run(self):
        print("Starting ETL...")
        
        raw_data = self.extract()
        print(f"Extracted {len(raw_data)} records")
        
        transformed_data = self.transform(raw_data)
        print(f"Transformed {len(transformed_data)} records")
        
        self.load(transformed_data)
        print("Data loaded to MongoDB")
        
        print("ETL Complete!")

if __name__ == "__main__":
    etl = VirusTotalETL()
    etl.run()