import os
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')  # from your .env

def extract():
    # Example: FireHOL blocklist
    url = 'https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset'
    response = requests.get(url)
    # Parse response—ignore comments and empty lines
    ips = [line for line in response.text.splitlines() if not line.startswith('#') and line.strip()]
    # Turn each IP into a dictionary so MongoDB can store it properly
    return [{'ip': ip, 'ingestion_ts': datetime.utcnow()} for ip in ips]

def load(data):
    client = MongoClient(MONGO_URI)
    db = client['software-assignment']  # Change to your actual DB name in Atlas
    coll = db['firehol_raw']     # Collection name
    if data:
        coll.insert_many(data)
        print(f"Inserted {len(data)} records.")
    else:
        print("No data to insert.")

if __name__ == '__main__':
    firehol_data = extract()
    load(firehol_data)
