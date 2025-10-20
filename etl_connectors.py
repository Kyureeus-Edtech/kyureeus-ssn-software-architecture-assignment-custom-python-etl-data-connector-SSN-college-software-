"""
Simplified ETL Connectors for CERT.at Threat Intelligence
Consolidated ETL pipeline for processing CSV and RSS feeds
"""

import os
import csv
import logging
import hashlib
import feedparser
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from html import unescape
import re
import random

# MongoDB imports
from pymongo import MongoClient, errors, ASCENDING, DESCENDING
from pymongo.collection import Collection

# Date parsing
from email.utils import parsedate_to_datetime
from dateutil import parser

# Environment
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLConnectors:
    """Simplified ETL pipeline for CERT.at threat intelligence data"""
    
    def __init__(self, mongo_uri: str = None, db_name: str = None, data_dir: str = 'data'):
        """Initialize ETL connectors"""
        load_dotenv()
        
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name or os.getenv('DB_NAME', 'certat_intelligence_db')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.client = None
        self.db = None
        
        # CSV feed definitions
        self.csv_feeds = {
            'malware_infections': 'certat_malware_infections.csv',
            'vulnerable_systems': 'certat_vulnerable_systems.csv',
            'brute_force_attacks': 'certat_brute_force_attacks.csv'
        }
        
        # RSS feed endpoints
        self.rss_feeds = {
            'warnings': 'https://www.cert.at/cert-at.de.warnings.rss_2.0.xml',
            'blog': 'https://www.cert.at/cert-at.de.blog.rss_2.0.xml',
            'blog_en': 'https://www.cert.at/cert-at.en.blog.rss_2.0.xml',
            'daily_reports': 'https://www.cert.at/cert-at.de.daily.rss_2.0.xml',
            'current': 'https://www.cert.at/cert-at.de.current.rss_2.0.xml',
            'specials': 'https://www.cert.at/cert-at.de.specials.rss_2.0.xml'
        }
        
        # Severity mapping
        self.severity_rules = {
            'malicious-code': {'default': 'high', 'infected-system': 'high', 'ransomware': 'critical'},
            'intrusion-attempts': {'default': 'medium', 'brute-force': 'medium', 'exploit': 'high'},
            'vulnerable': {'default': 'low', 'vulnerable-service': 'low', 'exposed-service': 'medium'}
        }
        
        logger.info(f"ETL Connectors initialized - DB: {self.db_name}, Data: {self.data_dir}")
    
    def connect_mongodb(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.server_info()
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    def close_mongodb(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    def generate_sample_csv_data(self, count: int = 30):
        """Generate sample CSV data for testing"""
        logger.info(f"Generating {count} sample records...")
        
        # CSV headers
        headers = [
            'time.source', 'source.ip', 'protocol.transport', 'source.port',
            'protocol.application', 'source.fqdn', 'source.asn', 'source.geolocation.cc',
            'source.geolocation.city', 'classification.taxonomy', 'classification.type',
            'classification.identifier', 'destination.ip', 'destination.port',
            'destination.fqdn', 'malware.name', 'malware.hash.md5', 'malware.hash.sha256',
            'event_description.text', 'feed.name', 'feed.provider'
        ]
        
        # Generate malware infections
        malware_file = self.data_dir / 'certat_malware_infections.csv'
        with open(malware_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for i in range(count):
                writer.writerow({
                    'time.source': (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                    'source.ip': f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                    'protocol.transport': 'tcp',
                    'source.port': str(random.randint(49152, 65535)),
                    'protocol.application': random.choice(['http', 'https', 'smtp']),
                    'source.fqdn': f"host{i}.example.com",
                    'source.asn': str(random.randint(1000, 65000)),
                    'source.geolocation.cc': random.choice(['AT', 'DE', 'CH', 'US']),
                    'source.geolocation.city': random.choice(['Vienna', 'Berlin', 'Zurich', 'New York']),
                    'classification.taxonomy': 'malicious-code',
                    'classification.type': 'infected-system',
                    'classification.identifier': f'malware-{i}',
                    'destination.ip': f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                    'destination.port': '443',
                    'destination.fqdn': f"c2-{i}.malicious.com",
                    'malware.name': random.choice(['Emotet', 'TrickBot', 'Dridex', 'Qakbot']),
                    'malware.hash.md5': ''.join(random.choices('0123456789abcdef', k=32)),
                    'malware.hash.sha256': ''.join(random.choices('0123456789abcdef', k=64)),
                    'event_description.text': f'Malware infection detected',
                    'feed.name': 'CERT.at Malware Feed',
                    'feed.provider': 'CERT.at'
                })
        
        logger.info(f"Generated {malware_file} with {count} records")
    
    def extract_csv_feeds(self) -> Dict[str, List[Dict]]:
        """Extract data from CSV feeds"""
        logger.info("Extracting CSV feeds...")
        results = {}
        
        for feed_name, filename in self.csv_feeds.items():
            file_path = self.data_dir / filename
            if not file_path.exists():
                logger.warning(f"CSV file not found: {filename}")
                results[feed_name] = []
                continue
            
            records = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Clean empty strings
                        cleaned_row = {k: (v.strip() if v and v.strip() else None) for k, v in row.items()}
                        records.append(cleaned_row)
                
                logger.info(f"Extracted {len(records)} records from {feed_name}")
                results[feed_name] = records
            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")
                results[feed_name] = []
        
        return results
    
    def transform_csv_data(self, csv_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Transform CSV data into normalized format"""
        logger.info("Transforming CSV data...")
        results = {}
        
        for feed_name, records in csv_data.items():
            transformed = []
            
            for record in records:
                # Generate unique ID
                id_components = [
                    record.get('time.source', ''),
                    record.get('source.ip', ''),
                    record.get('classification.identifier', ''),
                    feed_name
                ]
                record_id = hashlib.sha256('|'.join(str(c) for c in id_components).encode()).hexdigest()[:16]
                
                # Calculate severity
                taxonomy = (record.get('classification.taxonomy') or '').lower()
                threat_type = (record.get('classification.type') or '').lower()
                severity = 'medium'
                
                if taxonomy in self.severity_rules:
                    rules = self.severity_rules[taxonomy]
                    for key, sev in rules.items():
                        if key in threat_type:
                            severity = sev
                            break
                    else:
                        severity = rules['default']
                
                # Normalize record
                normalized = {
                    'record_id': record_id,
                    'feed_source': feed_name,
                    'timestamp': record.get('time.source'),
                    'source': {
                        'ip': record.get('source.ip'),
                        'port': record.get('source.port'),
                        'fqdn': record.get('source.fqdn'),
                        'geolocation': {
                            'country_code': record.get('source.geolocation.cc'),
                            'city': record.get('source.geolocation.city'),
                            'asn': record.get('source.asn')
                        }
                    },
                    'destination': {
                        'ip': record.get('destination.ip'),
                        'port': record.get('destination.port'),
                        'fqdn': record.get('destination.fqdn')
                    },
                    'classification': {
                        'taxonomy': record.get('classification.taxonomy'),
                        'type': record.get('classification.type'),
                        'identifier': record.get('classification.identifier')
                    },
                    'malware': {
                        'name': record.get('malware.name'),
                        'md5': record.get('malware.hash.md5'),
                        'sha256': record.get('malware.hash.sha256')
                    } if record.get('malware.name') else None,
                    'severity': severity,
                    'description': record.get('event_description.text'),
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                transformed.append(normalized)
            
            results[feed_name] = transformed
            logger.info(f"Transformed {len(transformed)} records for {feed_name}")
        
        return results
    
    def extract_rss_feeds(self) -> Dict[str, List[Dict]]:
        """Extract data from RSS feeds"""
        logger.info("Extracting RSS feeds...")
        results = {}
        
        for feed_name, url in self.rss_feeds.items():
            try:
                logger.info(f"Fetching RSS feed: {feed_name}")
                feed = feedparser.parse(url)
                
                if not feed.entries:
                    logger.warning(f"No entries found in {feed_name}")
                    results[feed_name] = []
                    continue
                
                entries = []
                for entry in feed.entries:
                    # Clean HTML content
                    def clean_html(text):
                        if not text:
                            return ""
                        text = unescape(text)
                        text = re.sub(r'<[^>]+>', '', text)
                        return ' '.join(text.split()).strip()
                    
                    # Parse date
                    def parse_date(date_str):
                        if not date_str:
                            return None
                        try:
                            return parsedate_to_datetime(date_str).isoformat()
                        except:
                            try:
                                return parser.parse(date_str).isoformat()
                            except:
                                return date_str
                    
                    # Generate entry ID
                    guid = entry.get('id') or entry.get('guid') or entry.get('link', '')
                    entry_id = hashlib.sha256(f"{feed_name}|{guid}".encode()).hexdigest()[:16]
                    
                    normalized_entry = {
                        'entry_id': entry_id,
                        'feed_source': feed_name,
                        'title': clean_html(entry.get('title', '')),
                        'link': entry.get('link', ''),
                        'content': clean_html(entry.get('description', '')),
                        'author': entry.get('author', ''),
                        'published': parse_date(entry.get('published', '')),
                        'tags': [tag.get('term', '') for tag in entry.get('tags', []) if tag.get('term')],
                        'extracted_at': datetime.utcnow().isoformat()
                    }
                    
                    entries.append(normalized_entry)
                
                results[feed_name] = entries
                logger.info(f"Extracted {len(entries)} entries from {feed_name}")
                
            except Exception as e:
                logger.error(f"Error fetching {feed_name}: {e}")
                results[feed_name] = []
        
        return results
    
    def load_csv_data(self, transformed_data: Dict[str, List[Dict]], clean_before: bool = True):
        """Load CSV data into MongoDB"""
        logger.info("Loading CSV data into MongoDB...")
        
        if not self.connect_mongodb():
            return False
        
        try:
            for feed_name, records in transformed_data.items():
                if not records:
                    continue
                
                collection_name = f"threats_csv_{feed_name}"
                collection = self.db[collection_name]
                
                # Create indexes
                try:
                    collection.create_index([('record_id', ASCENDING)], unique=True)
                    collection.create_index([('timestamp', ASCENDING)])
                    collection.create_index([('severity', ASCENDING)])
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                # Clean collection if requested
                if clean_before:
                    collection.delete_many({})
                
                # Add load timestamp
                for record in records:
                    record['loaded_at'] = datetime.utcnow().isoformat()
                
                # Insert records
                try:
                    collection.insert_many(records, ordered=False)
                    logger.info(f"Loaded {len(records)} records into {collection_name}")
                except errors.BulkWriteError as e:
                    inserted = e.details.get('nInserted', 0)
                    logger.warning(f"Bulk write errors: {inserted} inserted, {len(e.details.get('writeErrors', []))} errors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            return False
        finally:
            self.close_mongodb()
    
    def load_rss_data(self, rss_data: Dict[str, List[Dict]], clean_before: bool = True):
        """Load RSS data into MongoDB"""
        logger.info("Loading RSS data into MongoDB...")
        
        if not self.connect_mongodb():
            return False
        
        try:
            for feed_name, entries in rss_data.items():
                if not entries:
                    continue
                
                collection_name = f"rss_{feed_name}"
                collection = self.db[collection_name]
                
                # Create indexes
                try:
                    collection.create_index([('entry_id', ASCENDING)], unique=True)
                    collection.create_index([('published', DESCENDING)])
                    collection.create_index([('feed_source', ASCENDING)])
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
                
                # Clean collection if requested
                if clean_before:
                    collection.delete_many({})
                
                # Add load timestamp
                for entry in entries:
                    entry['loaded_at'] = datetime.utcnow().isoformat()
                
                # Insert entries
                try:
                    collection.insert_many(entries, ordered=False)
                    logger.info(f"Loaded {len(entries)} entries into {collection_name}")
                except errors.BulkWriteError as e:
                    inserted = e.details.get('nInserted', 0)
                    logger.warning(f"Bulk write errors: {inserted} inserted, {len(e.details.get('writeErrors', []))} errors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading RSS data: {e}")
            return False
        finally:
            self.close_mongodb()
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about stored data"""
        if not self.connect_mongodb():
            return {}
        
        try:
            stats = {}
            collections = self.db.list_collection_names()
            
            for collection_name in collections:
                if collection_name.startswith(('threats_csv_', 'rss_')):
                    count = self.db[collection_name].count_documents({})
                    stats[collection_name] = count
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
        finally:
            self.close_mongodb()
    
    def run_csv_pipeline(self, generate_sample: bool = False):
        """Run complete CSV pipeline"""
        logger.info("=" * 60)
        logger.info("RUNNING CSV PIPELINE")
        logger.info("=" * 60)
        
        # Generate sample data if requested
        if generate_sample:
            self.generate_sample_csv_data()
        
        # Extract CSV data
        csv_data = self.extract_csv_feeds()
        
        # Transform data
        transformed_data = self.transform_csv_data(csv_data)
        
        # Load data
        success = self.load_csv_data(transformed_data)
        
        if success:
            stats = self.get_collection_stats()
            logger.info("CSV Pipeline completed successfully!")
            for collection, count in stats.items():
                if collection.startswith('threats_csv_'):
                    logger.info(f"  {collection}: {count} documents")
        else:
            logger.error("CSV Pipeline failed!")
        
        return success
    
    def run_rss_pipeline(self):
        """Run complete RSS pipeline"""
        logger.info("=" * 60)
        logger.info("RUNNING RSS PIPELINE")
        logger.info("=" * 60)
        
        # Extract RSS data
        rss_data = self.extract_rss_feeds()
        
        # Load data
        success = self.load_rss_data(rss_data)
        
        if success:
            stats = self.get_collection_stats()
            logger.info("RSS Pipeline completed successfully!")
            for collection, count in stats.items():
                if collection.startswith('rss_'):
                    logger.info(f"  {collection}: {count} documents")
        else:
            logger.error("RSS Pipeline failed!")
        
        return success
    
    def run_complete_pipeline(self, generate_sample: bool = False):
        """Run both CSV and RSS pipelines"""
        logger.info("=" * 60)
        logger.info("RUNNING COMPLETE ETL PIPELINE")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Run CSV pipeline
        csv_success = self.run_csv_pipeline(generate_sample)
        
        # Run RSS pipeline
        rss_success = self.run_rss_pipeline()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"CSV Pipeline: {'✓ SUCCESS' if csv_success else '✗ FAILED'}")
        logger.info(f"RSS Pipeline: {'✓ SUCCESS' if rss_success else '✗ FAILED'}")
        
        # Final stats
        stats = self.get_collection_stats()
        total_docs = sum(stats.values())
        logger.info(f"Total documents stored: {total_docs}")
        
        return csv_success and rss_success


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CERT.at ETL Pipeline')
    parser.add_argument('--csv-only', action='store_true', help='Run only CSV pipeline')
    parser.add_argument('--rss-only', action='store_true', help='Run only RSS pipeline')
    parser.add_argument('--generate-sample', action='store_true', help='Generate sample CSV data')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    
    args = parser.parse_args()
    
    # Initialize ETL connectors
    etl = ETLConnectors(data_dir=args.data_dir)
    
    try:
        if args.csv_only:
            etl.run_csv_pipeline(generate_sample=args.generate_sample)
        elif args.rss_only:
            etl.run_rss_pipeline()
        else:
            etl.run_complete_pipeline(generate_sample=args.generate_sample)
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
