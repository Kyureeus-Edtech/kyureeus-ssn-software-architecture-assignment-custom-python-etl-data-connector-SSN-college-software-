#!/usr/bin/env python3
"""
Custom ETL Data Connector for NetworkCalc API
Updated: Multiple queries per endpoint and pretty printing of MongoDB content
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkcalc_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NetworkCalcETLConnector:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGO_DATABASE', 'etl_database')
        self.collection_name = os.getenv('MONGO_COLLECTION', 'networkcalc_raw')
        self.mongo_client: Optional[MongoClient] = None
        self.database = None
        self.collection = None

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NetworkCalc-ETL/1.0',
            'Accept': 'application/json'
        })

        # Multiple queries per endpoint
        self.queries = {
            "subnet": ["192.168.1.1/24", "10.0.0.1/16"],
            "binary": [{"value": 255, "from": 10, "to": 2}, {"value": 128, "from": 10, "to": 2}],
            "security": ["example.com", "google.com"]
        }

    def connect_to_mongodb(self) -> bool:
        try:
            self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            self.database = self.mongo_client[self.database_name]
            self.collection = self.database[self.collection_name]
            logger.info(f"Connected to MongoDB: {self.database_name}.{self.collection_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False

    def extract_data(self) -> List[Dict[str, Any]]:
        extracted = []
        for endpoint, queries in self.queries.items():
            for q in queries:
                try:
                    if endpoint == "subnet":
                        url = f"https://networkcalc.com/api/ip/{q}"
                    elif endpoint == "binary":
                        url = f"https://networkcalc.com/api/binary/{q['value']}?from={q['from']}&to={q['to']}"
                    elif endpoint == "security":
                        url = f"https://networkcalc.com/api/security/certificate/{q}"
                    else:
                        continue

                    logger.info(f"Fetching {endpoint} data for query {q}")
                    response = self.session.get(url, timeout=20)
                    response.raise_for_status()
                    data = response.json()
                    extracted.append({'endpoint': endpoint, 'query': q, 'fetched_at': datetime.now(timezone.utc), 'data': data})
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to fetch data from {endpoint} ({q}): {e}")
                    continue
        logger.info(f"Extracted data from {len(extracted)} queries")
        return extracted

    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info("MongoDB content BEFORE transformation (first 5 records):")
        for doc in self.collection.find().limit(5):
            pprint(doc)

        transformed = []
        for record in raw_data:
            endpoint = record['endpoint']
            data = record['data']
            transformed_record = {
                'endpoint': endpoint,
                'query': record['query'],
                'ingestion_time': record['fetched_at'],
                'original_data': data,
                'summary': {}
            }

            if endpoint == 'subnet':
                transformed_record['summary'] = {
                    'network': data.get('network', ''),
                    'broadcast': data.get('broadcast', ''),
                    'host_count': data.get('host_count', 0),
                    'mask': data.get('mask', ''),
                }
            elif endpoint == 'binary':
                transformed_record['summary'] = {
                    'input': data.get('input', ''),
                    'from_base': data.get('from_base', ''),
                    'to_base': data.get('to_base', ''),
                    'output': data.get('output', '')
                }
            elif endpoint == 'security':
                cert = data.get('certificate', {})
                transformed_record['summary'] = {
                    'subject': cert.get('subject', {}),
                    'issuer': cert.get('issuer', {}),
                    'valid_from': cert.get('valid_from'),
                    'valid_to': cert.get('valid_to'),
                    'serial_number': cert.get('serial_number')
                }

            transformed.append(transformed_record)

        logger.info("Transformed records (preview of first 5):")
        for rec in transformed[:5]:
            pprint(rec)

        logger.info(f"Transformed {len(transformed)} records")
        return transformed

    def load_data(self, transformed_data: List[Dict[str, Any]]) -> bool:
        if not transformed_data:
            logger.warning("No data to load")
            return True
        try:
            self.collection.create_index("endpoint")
            self.collection.create_index("ingestion_time")
            self.collection.insert_many(transformed_data)
            logger.info("Data loaded into MongoDB successfully. Latest 5 records:")
            for doc in self.collection.find().sort("ingestion_time", -1).limit(5):
                pprint(doc)
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

    def run_etl_pipeline(self) -> bool:
        logger.info("Starting NetworkCalc ETL pipeline")
        if not self.connect_to_mongodb():
            return False
        raw_data = self.extract_data()
        if not raw_data:
            logger.error("No data extracted")
            return False
        transformed_data = self.transform_data(raw_data)
        if not transformed_data:
            logger.error("No data transformed")
            return False
        if not self.load_data(transformed_data):
            logger.error("Data load failed")
            return False
        logger.info("ETL pipeline completed successfully")
        return True

def main():
    connector = NetworkCalcETLConnector()
    success = connector.run_etl_pipeline()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
