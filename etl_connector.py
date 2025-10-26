"""
abuse.ch ETL Data Connector
Author: Rithick R Rahul (3122225001107)
Description:
    Connects to abuse.ch APIs (URLhaus and MalwareBazaar),
    extracts threat intelligence data from 2 endpoints,
    transforms it, and loads into MongoDB.
"""

import os
import requests
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

ABUSECH_API_KEY = os.getenv("ABUSECH_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# -------------------------
# MongoDB Connection
# -------------------------
def connect_to_mongodb(uri):
    """Initialize MongoDB connection."""
    try:
        client = MongoClient(uri)
        client.admin.command('ismaster')
        logging.info("MongoDB connection successful.")
        db = client['threat_intelligence']
        return client, db
    except ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        return None, None

# -------------------------
# Step 1: Extract Data from abuse.ch APIs
# -------------------------
def extract_urlhaus_data(api_key):
    """Fetches recent URL submissions from URLhaus."""
    try:
        logging.info("Extracting recent URLs from URLhaus...")
        headers = {'Auth-Key': api_key} if api_key else {}
        response = requests.get("https://urlhaus-api.abuse.ch/v1/urls/recent/", headers=headers, timeout=30)
        response.raise_for_status()
        logging.info("Successfully extracted data from URLhaus.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from URLhaus: {e}")
        return None

def extract_malwarebazaar_data(api_key):
    """Fetches recent malware samples from MalwareBazaar."""
    try:
        logging.info("Extracting recent samples from MalwareBazaar...")
        headers = {'Auth-Key': api_key} if api_key else {}
        data = {'query': 'get_recent', 'selector': '100'}
        response = requests.post("https://mb-api.abuse.ch/api/v1/", data=data, headers=headers, timeout=30)
        response.raise_for_status()
        logging.info("Successfully extracted data from MalwareBazaar.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from MalwareBazaar: {e}")
        return None

# -------------------------
# Step 2: Transform Data
# -------------------------
def transform_urlhaus_data(raw_data):
    """Transforms URLhaus data into a standard format."""
    if not raw_data or 'urls' not in raw_data:
        logging.warning("No URLhaus data to transform.")
        return []
    
    transformed = []
    for item in raw_data['urls']:
        try:
            # Example transformation: add a threat_level based on tags
            threat_level = 'high' if 'exe' in (item.get('tags') or []) else 'medium'
            
            doc = {
                '_id': item['id'],
                'source': 'URLhaus',
                'ioc_type': 'url',
                'ioc_value': item['url'],
                'threat_type': item.get('threat'),
                'tags': item.get('tags', []),
                'threat_level': threat_level,
                'date_added': item.get('date_added'),
                'url_status': item.get('url_status'),
                'ingested_at': datetime.utcnow()
            }
            
            # Parse date if available
            if item.get('date_added'):
                try:
                    doc['first_seen'] = datetime.strptime(item['date_added'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    doc['first_seen'] = None
            
            transformed.append(doc)
        except Exception as e:
            logging.error(f"Error transforming URLhaus record: {e}")
            continue
    
    logging.info(f"Transformed {len(transformed)} records from URLhaus.")
    return transformed

def transform_malwarebazaar_data(raw_data):
    """Transforms MalwareBazaar data into a standard format."""
    if not raw_data or 'data' not in raw_data:
        logging.warning("No MalwareBazaar data to transform.")
        return []
    
    transformed = []
    for item in raw_data['data']:
        try:
            # Example transformation: Classify file type
            file_class = 'document' if item.get('file_type') in ['docx', 'pdf'] else 'executable'
            
            # Handle first_seen date parsing
            first_seen_val = item.get('first_seen')
            first_seen_dt = None
            
            if first_seen_val:
                # Check if the string is a number (Unix timestamp)
                if str(first_seen_val).isdigit():
                    first_seen_dt = datetime.fromtimestamp(int(first_seen_val))
                else:
                    # Try to parse it as a date string
                    try:
                        first_seen_dt = datetime.strptime(first_seen_val, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logging.warning(f"Could not parse date: {first_seen_val}")
            
            doc = {
                '_id': item['sha256_hash'],
                'source': 'MalwareBazaar',
                'ioc_type': 'hash_sha256',
                'ioc_value': item['sha256_hash'],
                'file_type': item.get('file_type'),
                'file_size': item.get('file_size'),
                'signature': item.get('signature'),
                'tags': item.get('tags', []),
                'file_class': file_class,
                'first_seen': first_seen_dt,
                'ingested_at': datetime.utcnow()
            }
            
            transformed.append(doc)
        except Exception as e:
            logging.error(f"Error transforming MalwareBazaar record: {e}")
            continue
    
    logging.info(f"Transformed {len(transformed)} records from MalwareBazaar.")
    return transformed

# -------------------------
# Step 3: Load Data to MongoDB
# -------------------------
def load_to_mongodb(db, collection_name, data):
    """
    Inserts or updates data in a specified collection.
    Uses upsert to prevent duplicate records on repeated runs.
    """
    if not db or not data:
        logging.warning("No data to load or database not connected.")
        return
    
    collection = db[collection_name]
    count = 0
    
    for record in data:
        try:
            # Update the record if _id matches, otherwise insert it
            collection.update_one(
                {'_id': record['_id']},
                {'$set': record},
                upsert=True
            )
            count += 1
        except OperationFailure as e:
            logging.error(f"Error upserting data: {e}")
    
    logging.info(f"Upserted {count} records into '{collection_name}' collection.")

# -------------------------
# Step 4: Run Complete ETL Pipeline
# -------------------------
def run_abusech_etl():
    """Main ETL pipeline function."""
    
    logging.info("="*60)
    logging.info("Starting abuse.ch ETL Pipeline")
    logging.info("="*60)
    
    # Validate API key (optional for abuse.ch - some endpoints work without key)
    if not ABUSECH_API_KEY or ABUSECH_API_KEY == "YOUR_API_KEY_HERE":
        logging.warning("API Key not configured. Proceeding without authentication.")
        logging.warning("Some endpoints may have reduced limits.")
        api_key = None
    else:
        api_key = ABUSECH_API_KEY
        logging.info("Using API key for authentication.")
    
    # Connect to MongoDB
    client, db = connect_to_mongodb(MONGO_URI)
    if not client:
        logging.error("Cannot proceed without MongoDB connection.")
        return
    
    try:
        # --- Endpoint 1: URLhaus ETL ---
        logging.info("="*60)
        logging.info("Processing Endpoint 1: URLhaus")
        logging.info("="*60)
        
        urlhaus_raw = extract_urlhaus_data(api_key)
        if urlhaus_raw:
            urlhaus_transformed = transform_urlhaus_data(urlhaus_raw)
            load_to_mongodb(db, 'urlhaus_iocs', urlhaus_transformed)
        else:
            logging.warning("No data extracted from URLhaus.")
        
        # --- Endpoint 2: MalwareBazaar ETL ---
        logging.info("="*60)
        logging.info("Processing Endpoint 2: MalwareBazaar")
        logging.info("="*60)
        
        malwarebazaar_raw = extract_malwarebazaar_data(api_key)
        if malwarebazaar_raw:
            malwarebazaar_transformed = transform_malwarebazaar_data(malwarebazaar_raw)
            load_to_mongodb(db, 'malwarebazaar_iocs', malwarebazaar_transformed)
        else:
            logging.warning("No data extracted from MalwareBazaar.")
        
        # Print summary
        print_summary(db)
        
    finally:
        # Clean up
        if client:
            client.close()
            logging.info("MongoDB connection closed.")
    
    logging.info("="*60)
    logging.info("ETL process completed for all endpoints")
    logging.info("="*60)

# -------------------------
# Step 5: Print Summary Statistics
# -------------------------
def print_summary(db):
    """Print summary of data in MongoDB collections."""
    logging.info("="*60)
    logging.info("MONGODB COLLECTION SUMMARY")
    logging.info("="*60)
    
    collections = ['urlhaus_iocs', 'malwarebazaar_iocs']
    
    for collection_name in collections:
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            logging.info(f"Collection '{collection_name}': {count} records")
            
            if count > 0:
                # Show sample document
                sample = collection.find_one()
                if sample:
                    logging.info(f"  Sample IOC: {sample.get('ioc_value', 'N/A')[:50]}...")
                    logging.info(f"  Source: {sample.get('source', 'N/A')}")
        except Exception as e:
            logging.error(f"Error getting summary for {collection_name}: {e}")

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    run_abusech_etl()