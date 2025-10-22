"""
CERT.AT Advanced ETL Data Connector - Enterprise Edition
Author: Kowshika
Roll Number: 3122225001063
Description: Production-grade ETL pipeline for CERT.AT threat intelligence feeds
Features: Multi-feed support, advanced error handling, data validation, 
          incremental loading, metrics tracking, and comprehensive logging
"""

import os
import sys
import logging
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from time import sleep
from pathlib import Path
from collections import defaultdict

import requests
import pymongo
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError, ConnectionFailure
from dotenv import load_dotenv

# ==============================
# CONFIGURATION & CONSTANTS
# ==============================
load_dotenv()

# API Feed Configuration
FEEDS_CONFIG = {
    "open_elasticsearch": {
        "url": os.getenv(
            "CERTAT_FEED_ELASTICSEARCH",
            "https://threatintel.circl.lu/projects/certat/feeds/json/open-elasticsearch.json"
        ),
        "collection": "elasticsearch_raw",
        "description": "Publicly accessible Elasticsearch instances",
        "enabled": True
    },
    "open_redis": {
        "url": os.getenv(
            "CERTAT_FEED_REDIS",
            "https://threatintel.circl.lu/projects/certat/feeds/json/open-redis.json"
        ),
        "collection": "redis_raw",
        "description": "Publicly accessible Redis instances",
        "enabled": True
    },
    "open_ipmi": {
        "url": os.getenv(
            "CERTAT_FEED_IPMI",
            "https://threatintel.circl.lu/projects/certat/feeds/json/open-ipmi.json"
        ),
        "collection": "ipmi_raw",
        "description": "Publicly accessible IPMI interfaces",
        "enabled": True
    },
    "open_mongodb": {
        "url": os.getenv(
            "CERTAT_FEED_MONGODB",
            "https://threatintel.circl.lu/projects/certat/feeds/json/open-mongodb.json"
        ),
        "collection": "mongodb_raw",
        "description": "Publicly accessible MongoDB instances",
        "enabled": True
    }
}

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "certat_threat_intelligence")
MONGO_TIMEOUT = int(os.getenv("MONGO_TIMEOUT", "30000"))

# ETL Configuration
LOCAL_OUTPUT_DIR = Path(os.getenv("LOCAL_OUTPUT_DIR", "output_data"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "backups"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "10"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
ENABLE_DEDUPLICATION = os.getenv("ENABLE_DEDUPLICATION", "true").lower() == "true"
ENABLE_INCREMENTAL = os.getenv("ENABLE_INCREMENTAL", "true").lower() == "true"
ENABLE_ARCHIVAL = os.getenv("ENABLE_ARCHIVAL", "true").lower() == "true"

# Create necessary directories
for directory in [LOCAL_OUTPUT_DIR, LOG_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==============================
# ADVANCED LOGGING SETUP
# ==============================
class ETLLogger:
    """Custom logger with file and console handlers"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # File handler (DEBUG level)
        log_file = LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] [%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self):
        return self.logger

logger = ETLLogger(__name__).get_logger()

# ==============================
# DATA VALIDATION & SANITIZATION
# ==============================
class DataValidator:
    """Validates and sanitizes data for MongoDB"""
    
    @staticmethod
    def sanitize_for_mongo(obj: Any) -> Any:
        """Recursively sanitize MongoDB-incompatible characters"""
        if isinstance(obj, dict):
            sanitized = {}
            for k, v in obj.items():
                # Replace problematic characters
                safe_key = str(k).replace('.', '_dot_').replace('$', '_dollar_')
                sanitized[safe_key] = DataValidator.sanitize_for_mongo(v)
            return sanitized
        elif isinstance(obj, list):
            return [DataValidator.sanitize_for_mongo(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert other types to string
            return str(obj)
    
    @staticmethod
    def validate_record(record: Dict[str, Any], feed_name: str) -> Tuple[bool, Optional[str]]:
        """Validate individual record"""
        if not isinstance(record, dict):
            return False, "Record is not a dictionary"
        
        # Check for required fields based on feed type
        required_fields = ["ip", "timestamp"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Validate IP address format (basic check)
        ip = record.get("ip", "")
        if not isinstance(ip, str) or len(ip.split('.')) != 4:
            return False, f"Invalid IP address format: {ip}"
        
        return True, None
    
    @staticmethod
    def generate_record_hash(record: Dict[str, Any]) -> str:
        """Generate unique hash for deduplication"""
        # Create deterministic string from record
        key_string = json.dumps(record, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()

# ==============================
# METRICS TRACKING
# ==============================
class ETLMetrics:
    """Track ETL pipeline metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            "extracted": 0,
            "transformed": 0,
            "loaded": 0,
            "failed": 0,
            "duplicates": 0,
            "start_time": None,
            "end_time": None,
            "errors": []
        })
    
    def start_feed(self, feed_name: str):
        self.metrics[feed_name]["start_time"] = datetime.now(timezone.utc)
    
    def end_feed(self, feed_name: str):
        self.metrics[feed_name]["end_time"] = datetime.now(timezone.utc)
    
    def add_extracted(self, feed_name: str, count: int):
        self.metrics[feed_name]["extracted"] += count
    
    def add_transformed(self, feed_name: str, count: int):
        self.metrics[feed_name]["transformed"] += count
    
    def add_loaded(self, feed_name: str, count: int):
        self.metrics[feed_name]["loaded"] += count
    
    def add_failed(self, feed_name: str, count: int):
        self.metrics[feed_name]["failed"] += count
    
    def add_duplicates(self, feed_name: str, count: int):
        self.metrics[feed_name]["duplicates"] += count
    
    def add_error(self, feed_name: str, error: str):
        self.metrics[feed_name]["errors"].append(error)
    
    def get_duration(self, feed_name: str) -> Optional[float]:
        start = self.metrics[feed_name]["start_time"]
        end = self.metrics[feed_name]["end_time"]
        if start and end:
            return (end - start).total_seconds()
        return None
    
    def print_summary(self):
        """Print comprehensive metrics summary"""
        logger.info("\n" + "="*80)
        logger.info("ETL PIPELINE EXECUTION SUMMARY")
        logger.info("="*80)
        
        total_extracted = 0
        total_loaded = 0
        total_failed = 0
        
        for feed_name, metrics in self.metrics.items():
            duration = self.get_duration(feed_name)
            duration_str = f"{duration:.2f}s" if duration else "N/A"
            
            logger.info(f"\n📊 Feed: {feed_name.upper()}")
            logger.info(f"   ├─ Extracted:   {metrics['extracted']:,} records")
            logger.info(f"   ├─ Transformed: {metrics['transformed']:,} records")
            logger.info(f"   ├─ Loaded:      {metrics['loaded']:,} records")
            logger.info(f"   ├─ Duplicates:  {metrics['duplicates']:,} records")
            logger.info(f"   ├─ Failed:      {metrics['failed']:,} records")
            logger.info(f"   ├─ Duration:    {duration_str}")
            
            if metrics['errors']:
                logger.info(f"   └─ Errors:      {len(metrics['errors'])} errors")
                for i, error in enumerate(metrics['errors'][:3], 1):
                    logger.info(f"      {i}. {error}")
            else:
                logger.info(f"   └─ Errors:      None")
            
            total_extracted += metrics['extracted']
            total_loaded += metrics['loaded']
            total_failed += metrics['failed']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL RECORDS: Extracted={total_extracted:,}, Loaded={total_loaded:,}, Failed={total_failed:,}")
        logger.info(f"{'='*80}\n")

# ==============================
# MONGODB HANDLER
# ==============================
class MongoDBHandler:
    """Advanced MongoDB operations with connection pooling"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.connected = False
    
    def connect(self) -> bool:
        """Establish MongoDB connection"""
        try:
            logger.info(f"Connecting to MongoDB at {MONGO_URI}")
            self.client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=MONGO_TIMEOUT,
                maxPoolSize=50
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[MONGO_DB]
            self.connected = True
            logger.info(f"✅ Successfully connected to MongoDB database: {MONGO_DB}")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    def ensure_indexes(self, feed_name: str, collection_name: str):
        """Create indexes for optimal query performance"""
        try:
            collection = self.db[collection_name]
            
            # Create indexes
            indexes = [
                ("ip", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING),
                ("_ingested_at", pymongo.DESCENDING),
                ("_record_hash", pymongo.ASCENDING)
            ]
            
            for field, direction in indexes:
                collection.create_index([(field, direction)], background=True)
            
            # Compound index for deduplication
            collection.create_index(
                [("ip", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)],
                background=True
            )
            
            logger.debug(f"✅ Indexes created for collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Index creation warning for {collection_name}: {e}")
    
    def bulk_upsert(self, feed_name: str, collection_name: str, 
                    documents: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Bulk insert with upsert capability"""
        if not documents:
            return 0, 0
        
        try:
            collection = self.db[collection_name]
            
            # Prepare bulk operations
            operations = []
            for doc in documents:
                if ENABLE_DEDUPLICATION and "_record_hash" in doc:
                    # Use upsert to avoid duplicates
                    filter_query = {"_record_hash": doc["_record_hash"]}
                    operations.append(
                        UpdateOne(filter_query, {"$set": doc}, upsert=True)
                    )
                else:
                    operations.append(UpdateOne({}, {"$set": doc}, upsert=True))
            
            # Execute bulk write
            result = collection.bulk_write(operations, ordered=False)
            
            inserted = result.upserted_count
            modified = result.modified_count
            
            logger.info(f"✅ Bulk write completed: {inserted} inserted, {modified} updated")
            return inserted, modified
            
        except BulkWriteError as bwe:
            logger.error(f"Bulk write error: {bwe.details}")
            # Return partial success counts
            return bwe.details.get('nInserted', 0), bwe.details.get('nModified', 0)
        except Exception as e:
            logger.exception(f"❌ Bulk upsert failed: {e}")
            return 0, 0
    
    def get_latest_timestamp(self, collection_name: str) -> Optional[str]:
        """Get latest ingestion timestamp for incremental loading"""
        try:
            collection = self.db[collection_name]
            latest_doc = collection.find_one(
                {},
                sort=[("_ingested_at", pymongo.DESCENDING)]
            )
            return latest_doc["_ingested_at"] if latest_doc else None
        except Exception as e:
            logger.warning(f"Could not retrieve latest timestamp: {e}")
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = self.db[collection_name]
            stats = {
                "total_documents": collection.count_documents({}),
                "latest_ingestion": self.get_latest_timestamp(collection_name),
                "collection_size_mb": self.db.command("collstats", collection_name).get("size", 0) / (1024*1024)
            }
            return stats
        except Exception as e:
            logger.warning(f"Could not retrieve stats for {collection_name}: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔒 MongoDB connection closed")
            self.connected = False

# ==============================
# HTTP REQUEST HANDLER
# ==============================
class HTTPHandler:
    """Robust HTTP request handler with retry logic"""
    
    @staticmethod
    def fetch_with_retry(url: str, retries: int = MAX_RETRIES, 
                        delay: int = RETRY_DELAY) -> Optional[List[Dict[str, Any]]]:
        """Fetch data with exponential backoff retry"""
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"🌐 Fetching from {url} (Attempt {attempt}/{retries})")
                
                headers = {
                    'User-Agent': 'CERT.AT-ETL-Connector/2.0 (SSN-CSE-Student)',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
                
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                data = response.json()
                
                if not isinstance(data, list):
                    logger.error(f"❌ Expected list, got {type(data)}")
                    return None
                
                logger.info(f"✅ Successfully fetched {len(data):,} records")
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️  Request timeout (attempt {attempt}/{retries})")
            except requests.exceptions.HTTPError as e:
                logger.warning(f"🚫 HTTP error {e.response.status_code}: {e}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️  Request failed: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON response: {e}")
                return None
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
            
            if attempt < retries:
                wait_time = delay * (2 ** (attempt - 1))  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                sleep(wait_time)
        
        logger.error(f"❌ All {retries} attempts failed for {url}")
        return None

# ==============================
# ETL PIPELINE ORCHESTRATOR
# ==============================
class CERTATETLPipeline:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self):
        self.mongo_handler = MongoDBHandler()
        self.validator = DataValidator()
        self.metrics = ETLMetrics()
        self.http_handler = HTTPHandler()
    
    def extract(self, feed_name: str, feed_config: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Extract phase: Fetch data from API"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📥 EXTRACT PHASE: {feed_name.upper()}")
        logger.info(f"   Description: {feed_config['description']}")
        logger.info(f"   URL: {feed_config['url']}")
        logger.info(f"{'='*80}")
        
        raw_data = self.http_handler.fetch_with_retry(feed_config['url'])
        
        if raw_data:
            self.metrics.add_extracted(feed_name, len(raw_data))
        
        return raw_data
    
    def transform(self, feed_name: str, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform phase: Validate, sanitize, and enrich data"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 TRANSFORM PHASE: {feed_name.upper()}")
        logger.info(f"{'='*80}")
        
        if not raw_data:
            logger.warning("⚠️  No data to transform")
            return []
        
        transformed = []
        failed_count = 0
        
        for idx, record in enumerate(raw_data, 1):
            try:
                # Validate record
                is_valid, error_msg = self.validator.validate_record(record, feed_name)
                if not is_valid:
                    logger.debug(f"❌ Record {idx} validation failed: {error_msg}")
                    failed_count += 1
                    self.metrics.add_error(feed_name, f"Validation error: {error_msg}")
                    continue
                
                # Sanitize for MongoDB
                sanitized = self.validator.sanitize_for_mongo(record)
                
                # Enrich with metadata
                enriched = {
                    **sanitized,
                    "_ingested_at": datetime.now(timezone.utc).isoformat(),
                    "_feed_name": feed_name,
                    "_feed_description": FEEDS_CONFIG[feed_name]["description"],
                    "_connector_version": "2.0",
                    "_student_name": "Kowshika",
                    "_student_roll": "3122225001063"
                }
                
                # Add hash for deduplication
                if ENABLE_DEDUPLICATION:
                    enriched["_record_hash"] = self.validator.generate_record_hash(record)
                
                transformed.append(enriched)
                
            except Exception as e:
                logger.warning(f"⚠️  Error transforming record {idx}: {e}")
                failed_count += 1
                self.metrics.add_error(feed_name, str(e))
        
        self.metrics.add_transformed(feed_name, len(transformed))
        self.metrics.add_failed(feed_name, failed_count)
        
        logger.info(f"✅ Transformed {len(transformed):,} records ({failed_count} failed)")
        return transformed
    
    def load(self, feed_name: str, feed_config: Dict[str, Any], 
             transformed_data: List[Dict[str, Any]]):
        """Load phase: Insert data into MongoDB"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📤 LOAD PHASE: {feed_name.upper()}")
        logger.info(f"{'='*80}")
        
        if not transformed_data:
            logger.warning("⚠️  No data to load")
            return
        
        collection_name = feed_config["collection"]
        
        # Ensure indexes exist
        self.mongo_handler.ensure_indexes(feed_name, collection_name)
        
        # Batch insert
        total_inserted = 0
        total_modified = 0
        
        for i in range(0, len(transformed_data), BATCH_SIZE):
            batch = transformed_data[i:i + BATCH_SIZE]
            logger.info(f"Loading batch {i//BATCH_SIZE + 1} ({len(batch)} records)...")
            
            inserted, modified = self.mongo_handler.bulk_upsert(
                feed_name, collection_name, batch
            )
            
            total_inserted += inserted
            total_modified += modified
        
        self.metrics.add_loaded(feed_name, total_inserted)
        
        logger.info(f"✅ Load complete: {total_inserted:,} inserted, {total_modified:,} updated")
    
    def save_local_backup(self, feed_name: str, data: List[Dict[str, Any]]):
        """Save data to local JSON file"""
        if not ENABLE_ARCHIVAL or not data:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = LOCAL_OUTPUT_DIR / f"{feed_name}_{timestamp}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Saved backup to {file_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save local backup: {e}")
    
    def process_feed(self, feed_name: str, feed_config: Dict[str, Any]):
        """Process a single feed through ETL pipeline"""
        self.metrics.start_feed(feed_name)
        
        try:
            # Extract
            raw_data = self.extract(feed_name, feed_config)
            if not raw_data:
                return
            
            # Transform
            transformed_data = self.transform(feed_name, raw_data)
            if not transformed_data:
                return
            
            # Load
            self.load(feed_name, feed_config, transformed_data)
            
            # Backup
            self.save_local_backup(feed_name, transformed_data)
            
        except Exception as e:
            logger.exception(f"❌ Critical error processing feed {feed_name}: {e}")
            self.metrics.add_error(feed_name, str(e))
        finally:
            self.metrics.end_feed(feed_name)
    
    def run(self):
        """Execute full ETL pipeline for all feeds"""
        logger.info("\n" + "="*80)
        logger.info("🚀 CERT.AT ETL PIPELINE - ENTERPRISE EDITION")
        logger.info(f"   Author: Kowshika | Roll: 3122225001063")
        logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")
        
        # Connect to MongoDB
        if not self.mongo_handler.connect():
            logger.error("❌ Cannot proceed without MongoDB connection")
            return False
        
        # Process each enabled feed
        enabled_feeds = {k: v for k, v in FEEDS_CONFIG.items() if v.get("enabled", True)}
        
        logger.info(f"📋 Processing {len(enabled_feeds)} feeds: {list(enabled_feeds.keys())}\n")
        
        for feed_name, feed_config in enabled_feeds.items():
            self.process_feed(feed_name, feed_config)
        
        # Generate summary
        self.metrics.print_summary()
        
        # Collection statistics
        logger.info("\n" + "="*80)
        logger.info("📊 MONGODB COLLECTION STATISTICS")
        logger.info("="*80)
        
        for feed_name, feed_config in enabled_feeds.items():
            stats = self.mongo_handler.get_collection_stats(feed_config["collection"])
            logger.info(f"\n{feed_name.upper()}:")
            logger.info(f"   ├─ Total Documents: {stats.get('total_documents', 0):,}")
            logger.info(f"   ├─ Collection Size: {stats.get('collection_size_mb', 0):.2f} MB")
            logger.info(f"   └─ Latest Ingestion: {stats.get('latest_ingestion', 'N/A')}")
        
        logger.info("\n" + "="*80)
        
        # Cleanup
        self.mongo_handler.close()
        
        logger.info("\n✅ ETL Pipeline execution completed!")
        return True

# ==============================
# ENTRY POINT
# ==============================
def main():
    """Main entry point"""
    try:
        pipeline = CERTATETLPipeline()
        success = pipeline.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()