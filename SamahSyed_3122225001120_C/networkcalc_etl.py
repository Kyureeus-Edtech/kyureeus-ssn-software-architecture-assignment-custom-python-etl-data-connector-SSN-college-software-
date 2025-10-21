#!/usr/bin/env python3
"""
Custom ETL Data Connector for NetworkCalc API
Author: Samah Syed 3122225001120 C
Updated: Added enhanced transformation logic, data enrichment, and pretty printing of MongoDB content
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

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkcalc_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ---------------------- ETL Connector ----------------------
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
            'User-Agent': 'NetworkCalc-ETL/1.1',
            'Accept': 'application/json'
        })

        # Multiple queries per endpoint
        self.queries = {
            "subnet": ["192.168.1.1/24", "10.0.0.1/16"],
            "binary": [{"value": 255, "from": 10, "to": 2}, {"value": 128, "from": 10, "to": 2}],
            "security": ["example.com", "google.com"]
        }

    # ---------------------- MongoDB Connection ----------------------
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

    # ---------------------- Data Extraction ----------------------
    def extract_data(self) -> List[Dict[str, Any]]:
        extracted = []
        for endpoint, queries in self.queries.items():
            for q in queries:
                try:
                    url = self.build_endpoint_url(endpoint, q)
                    logger.info(f"Fetching {endpoint} data for query: {q}")
                    response = self.session.get(url, timeout=20)
                    response.raise_for_status()
                    data = response.json()
                    extracted.append({
                        'endpoint': endpoint,
                        'query': q,
                        'fetched_at': datetime.now(timezone.utc),
                        'data': data
                    })
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to fetch {endpoint} data for {q}: {e}")
                    continue
        logger.info(f"Extracted data from {len(extracted)} queries")
        return extracted

    def build_endpoint_url(self, endpoint: str, query: Any) -> str:
        if endpoint == "subnet":
            return f"https://networkcalc.com/api/ip/{query}"
        elif endpoint == "binary":
            return f"https://networkcalc.com/api/binary/{query['value']}?from={query['from']}&to={query['to']}"
        elif endpoint == "security":
            return f"https://networkcalc.com/api/security/certificate/{query}"
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

    # ---------------------- Data Transformation ----------------------
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

            # ---------------- Transform Logic per Endpoint ----------------
            if endpoint == 'subnet':
                summary = {
                    'network': data.get('network', ''),
                    'broadcast': data.get('broadcast', ''),
                    'host_count': data.get('host_count', 0),
                    'mask': data.get('mask', ''),
                    'subnet_bits': self.calculate_subnet_bits(data.get('host_count', 0))
                }
                transformed_record['summary'] = summary

            elif endpoint == 'binary':
                summary = {
                    'input': data.get('input', ''),
                    'from_base': data.get('from_base', ''),
                    'to_base': data.get('to_base', ''),
                    'output': data.get('output', ''),
                    'parity': self.calculate_parity(data.get('output', ''))
                }
                transformed_record['summary'] = summary

            elif endpoint == 'security':
                cert = data.get('certificate', {})
                valid_from = self.parse_date(cert.get('valid_from'))
                valid_to = self.parse_date(cert.get('valid_to'))
                summary = {
                    'subject': cert.get('subject', {}),
                    'issuer': cert.get('issuer', {}),
                    'valid_from': valid_from,
                    'valid_to': valid_to,
                    'validity_days': (valid_to - valid_from).days if valid_from and valid_to else None,
                    'serial_number': cert.get('serial_number')
                }
                transformed_record['summary'] = summary

            transformed.append(transformed_record)

        logger.info("Transformed records (preview of first 5):")
        for rec in transformed[:5]:
            pprint(rec)

        logger.info(f"Transformed {len(transformed)} records")
        return transformed

    # ---------------------- Helper Transformation Methods ----------------------
    @staticmethod
    def calculate_subnet_bits(host_count: int) -> int:
        """Calculate subnet size in bits from host count"""
        if host_count <= 0:
            return 0
        bits = 32
        while (2 ** (32 - bits) - 2) < host_count:
            bits -= 1
        return 32 - bits

    @staticmethod
    def calculate_parity(binary_str: str) -> str:
        """Return parity of binary string"""
        if not binary_str:
            return 'unknown'
        ones_count = binary_str.count('1')
        return 'even' if ones_count % 2 == 0 else 'odd'

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None

    # ---------------------- Data Loading ----------------------
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

    # ---------------------- Run ETL ----------------------
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

# ---------------------- Main Execution ----------------------
def main():
    connector = NetworkCalcETLConnector()
    success = connector.run_etl_pipeline()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
