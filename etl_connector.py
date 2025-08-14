#!/usr/bin/env python3
"""
MITRE ATT&CK ETL Connector
Author: Prathiyangira Devi V C
College: Sri Sivasubramaniya Nadar College of Engineering
Description: ETL pipeline to fetch threat intelligence data from MITRE ATT&CK TAXII server
"""

from taxii2client.v21 import Server
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load and validate environment variables"""
    load_dotenv()
    
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")
    
    if not mongo_uri or not mongo_db:
        logger.error("Missing required environment variables (MONGO_URI, MONGO_DB)")
        logger.info("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    
    return mongo_uri, mongo_db

def connect_to_mongodb(mongo_uri, mongo_db):
    """Connect to MongoDB with error handling"""
    try:
        logger.info("Connecting to MongoDB...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.server_info()
        db = client[mongo_db]
        collection = db["mitre_attack_raw"]
        logger.info("Successfully connected to MongoDB")
        return client, db, collection
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.info("Please check your MongoDB URI and ensure the database is accessible")
        sys.exit(1)

def connect_to_taxii_server():
    """Connect to MITRE ATT&CK TAXII server with retry logic"""
    taxii_url = "https://cti-taxii.mitre.org/taxii/"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to MITRE TAXII server... (Attempt {attempt + 1}/{max_retries})")
            server = Server(taxii_url)
            
            if not server.api_roots:
                raise Exception("No API roots found on TAXII server")
            
            api_root = server.api_roots[0]
            logger.info(f"Connected to API Root: {api_root.title}")
            return server, api_root
            
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error("Cannot connect to TAXII server after multiple attempts")
                logger.info("Please check your network connection and try using a VPN if needed")
                sys.exit(1)

def get_enterprise_collection(api_root):
    """Find and return the Enterprise ATT&CK collection"""
    logger.info("Looking for Enterprise ATT&CK collection...")
    
    try:
        collections = api_root.collections
        if not collections:
            raise Exception("No collections found in API root")
        
        enterprise_collection = None
        for coll in collections:
            if "Enterprise ATT&CK" in coll.title:
                enterprise_collection = coll
                break
        
        if enterprise_collection is None:
            logger.error("Enterprise ATT&CK collection not found")
            logger.info("Available collections:")
            for coll in collections:
                logger.info(f"   - {coll.title}")
            sys.exit(1)
        
        logger.info(f"Found collection: {enterprise_collection.title}")
        return enterprise_collection
        
    except Exception as e:
        logger.error(f"Error accessing collections: {e}")
        sys.exit(1)

def fetch_and_transform_data(enterprise_collection):
    """Fetch objects from TAXII server and transform for MongoDB"""
    logger.info("Fetching data from MITRE ATT&CK...")
    
    try:
        # Fetch all objects from the collection
        response = enterprise_collection.get_objects()
        
        if not response or "objects" not in response:
            logger.error("No data received from TAXII server")
            return []
        
        objects = response["objects"]
        logger.info(f"Retrieved {len(objects)} total objects")
        
        # Filter and transform relevant objects
        target_types = ["attack-pattern", "intrusion-set", "malware"]
        transformed = []
        
        for obj in objects:
            obj_type = obj.get("type")
            if obj_type in target_types:
                # Transform object for MongoDB compatibility
                transformed_obj = {
                    "mitre_id": obj.get("id"),
                    "name": obj.get("name", "Unknown"),
                    "description": obj.get("description", ""),
                    "object_type": obj_type,
                    "created": obj.get("created"),
                    "modified": obj.get("modified"),
                    "labels": obj.get("labels", []),
                    "external_references": obj.get("external_references", []),
                    "kill_chain_phases": obj.get("kill_chain_phases", []),
                    "ingested_at": datetime.utcnow(),
                    "source": "MITRE ATT&CK TAXII Server",
                    "raw_object": obj
                }
                transformed.append(transformed_obj)
        
        logger.info(f"Transformed {len(transformed)} relevant objects")
        
        # Log object type breakdown
        type_counts = {}
        for obj in transformed:
            obj_type = obj["object_type"]
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        logger.info("Object type breakdown:")
        for obj_type, count in type_counts.items():
            logger.info(f"   - {obj_type}: {count}")
        
        return transformed
        
    except Exception as e:
        logger.error(f"Error fetching/transforming data: {e}")
        return []

def load_to_mongodb(collection, transformed_data):
    """Load transformed data into MongoDB with error handling"""
    if not transformed_data:
        logger.warning("No data to insert into MongoDB")
        return False
    
    try:
        logger.info(f"Loading {len(transformed_data)} objects into MongoDB...")
        
        # Clear existing data (optional - remove if you want to append)
        existing_count = collection.count_documents({})
        if existing_count > 0:
            logger.info(f"Clearing {existing_count} existing documents...")
            collection.delete_many({})
        
        # Insert new data
        result = collection.insert_many(transformed_data)
        
        if result.inserted_ids:
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents")
            
            # Verify insertion
            final_count = collection.count_documents({})
            logger.info(f"Total documents in collection: {final_count}")
            
            return True
        else:
            logger.error("No documents were inserted")
            return False
            
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}")
        return False

def print_summary(collection):
    """Print summary of data in MongoDB"""
    try:
        print("\n" + "="*50)
        print("DATA SUMMARY")
        print("="*50)
        
        total_docs = collection.count_documents({})
        print(f"Total documents: {total_docs}")
        
        # Count by object type
        pipeline = [
            {"$group": {"_id": "$object_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        type_counts = list(collection.aggregate(pipeline))
        print("\nBreakdown by type:")
        for item in type_counts:
            print(f"  {item['_id']}: {item['count']}")
        
        # Show latest ingestion time
        latest_doc = collection.find_one({}, sort=[("ingested_at", -1)])
        if latest_doc:
            print(f"\nLatest ingestion: {latest_doc['ingested_at']}")
        
        print("="*50)
        
    except Exception as e:
        logger.warning(f"Could not generate summary: {e}")

def main():
    """Main ETL pipeline execution"""
    print("MITRE ATT&CK ETL Connector Started")
    print("="*50)
    
    start_time = datetime.now()
    
    try:
        # Step 1: Load environment variables
        mongo_uri, mongo_db = load_environment()
        
        # Step 2: Connect to MongoDB
        client, db, collection = connect_to_mongodb(mongo_uri, mongo_db)
        
        # Step 3: Connect to TAXII server
        server, api_root = connect_to_taxii_server()
        
        # Step 4: Get Enterprise collection
        enterprise_collection = get_enterprise_collection(api_root)
        
        # Step 5: Extract and Transform data
        transformed_data = fetch_and_transform_data(enterprise_collection)
        
        # Step 6: Load data into MongoDB
        success = load_to_mongodb(collection, transformed_data)
        
        if success:
            # Step 7: Print summary
            print_summary(collection)
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"ETL pipeline completed successfully in {duration.total_seconds():.2f} seconds")
        else:
            logger.error("ETL pipeline failed during data loading")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("ETL pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in ETL pipeline: {e}")
        sys.exit(1)
    finally:
        # Clean up MongoDB connection
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()