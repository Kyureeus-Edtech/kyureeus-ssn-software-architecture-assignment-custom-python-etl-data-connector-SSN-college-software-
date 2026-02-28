"""
CSV Loader Module
Loads threat intelligence data into MongoDB
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient, errors, ASCENDING
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class CSVLoader:
    """Loads CSV threat intelligence data into MongoDB"""
    
    def __init__(self, mongo_uri: str, db_name: str):
        """
        Initialize MongoDB connection
        
        Args:
            mongo_uri: MongoDB connection string
            db_name: Database name
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        logger.info(f"CSV Loader initialized for database: {db_name}")
    
    def connect(self) -> bool:
        """
        Establish MongoDB connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to MongoDB...")
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection
            self.client.server_info()
            
            self.db = self.client[self.db_name]
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
            return True
            
        except errors.ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
    
    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def _create_indexes(self, collection: Collection) -> None:
        """
        Create indexes for efficient querying
        
        Args:
            collection: MongoDB collection
        """
        try:
            # Index on record_id for duplicate detection
            collection.create_index([('record_id', ASCENDING)], unique=True)
            
            # Index on timestamp for time-based queries
            collection.create_index([('timestamp', ASCENDING)])
            
            # Index on severity for filtering
            collection.create_index([('severity', ASCENDING)])
            
            # Compound index for common queries
            collection.create_index([
                ('feed_source', ASCENDING),
                ('timestamp', ASCENDING)
            ])
            
            logger.debug(f"Indexes created for collection: {collection.name}")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def clean_collection(self, collection_name: str) -> int:
        """
        Remove all documents from a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents deleted
        """
        try:
            collection = self.db[collection_name]
            result = collection.delete_many({})
            deleted = result.deleted_count
            logger.info(f"Cleaned collection '{collection_name}': {deleted} documents deleted")
            return deleted
        except Exception as e:
            logger.error(f"Error cleaning collection {collection_name}: {e}")
            return 0
    
    def load_feed_data(
        self, 
        collection_name: str, 
        records: List[Dict], 
        clean_before: bool = True,
        upsert: bool = False
    ) -> Dict[str, int]:
        """
        Load threat records into MongoDB
        
        Args:
            collection_name: Name of the collection
            records: List of threat records
            clean_before: Whether to clean collection before loading
            upsert: Whether to upsert (update or insert) records
            
        Returns:
            Dictionary with loading statistics
        """
        stats = {
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
        
        if not records:
            logger.warning(f"No records to load into {collection_name}")
            return stats
        
        try:
            collection = self.db[collection_name]
            
            # Create indexes
            self._create_indexes(collection)
            
            # Clean collection if requested
            if clean_before:
                self.clean_collection(collection_name)
            
            # Add load metadata
            for record in records:
                record['loaded_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Loading {len(records)} records into '{collection_name}'...")
            
            if upsert:
                # Upsert each record based on record_id
                for record in records:
                    try:
                        result = collection.replace_one(
                            {'record_id': record['record_id']},
                            record,
                            upsert=True
                        )
                        if result.upserted_id:
                            stats['inserted'] += 1
                        elif result.modified_count > 0:
                            stats['updated'] += 1
                        else:
                            stats['skipped'] += 1
                    except Exception as e:
                        logger.error(f"Error upserting record: {e}")
                        stats['errors'] += 1
            else:
                # Bulk insert
                try:
                    result = collection.insert_many(records, ordered=False)
                    stats['inserted'] = len(result.inserted_ids)
                except errors.BulkWriteError as e:
                    # Handle duplicate key errors
                    stats['inserted'] = e.details.get('nInserted', 0)
                    stats['errors'] = len(e.details.get('writeErrors', []))
                    logger.warning(f"Bulk write errors: {stats['errors']} duplicates/errors")
            
            logger.info(
                f"Load complete for '{collection_name}': "
                f"{stats['inserted']} inserted, {stats['updated']} updated, "
                f"{stats['errors']} errors, {stats['skipped']} skipped"
            )
            
        except Exception as e:
            logger.error(f"Error loading data into {collection_name}: {e}", exc_info=True)
            stats['errors'] = len(records)
        
        return stats
    
    def load_all_feeds(
        self, 
        transformed_data: Dict[str, Optional[Dict]], 
        clean_before: bool = True,
        upsert: bool = False
    ) -> Dict[str, Dict[str, int]]:
        """
        Load all transformed feeds into MongoDB
        
        Args:
            transformed_data: Dictionary of transformed feed data
            clean_before: Whether to clean collections before loading
            upsert: Whether to upsert records
            
        Returns:
            Dictionary with feed names and loading statistics
        """
        logger.info("Loading all CSV feeds into MongoDB")
        results = {}
        
        for feed_name, feed_data in transformed_data.items():
            if feed_data and feed_data.get('records'):
                collection_name = f"threats_csv_{feed_name}"
                records = feed_data['records']
                
                stats = self.load_feed_data(
                    collection_name, 
                    records, 
                    clean_before=clean_before,
                    upsert=upsert
                )
                results[feed_name] = stats
            else:
                logger.warning(f"Skipping {feed_name} (no data)")
                results[feed_name] = {
                    'inserted': 0,
                    'updated': 0,
                    'errors': 0,
                    'skipped': 0
                }
        
        total_inserted = sum(stats['inserted'] for stats in results.values())
        total_updated = sum(stats['updated'] for stats in results.values())
        
        logger.info(
            f"CSV load complete: {total_inserted} inserted, "
            f"{total_updated} updated across {len(results)} feeds"
        )
        
        return results
    
    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get statistics about stored CSV threat data
        
        Returns:
            Dictionary with collection names and document counts
        """
        stats = {}
        try:
            collections = self.db.list_collection_names()
            csv_collections = [c for c in collections if c.startswith('threats_csv_')]
            
            for collection_name in csv_collections:
                count = self.db[collection_name].count_documents({})
                stats[collection_name] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_severity_distribution(self, feed_name: str) -> Dict[str, int]:
        """
        Get severity distribution for a specific feed
        
        Args:
            feed_name: Name of the feed
            
        Returns:
            Dictionary with severity counts
        """
        try:
            collection_name = f"threats_csv_{feed_name}"
            collection = self.db[collection_name]
            
            pipeline = [
                {'$group': {
                    '_id': '$severity',
                    'count': {'$sum': 1}
                }}
            ]
            
            results = collection.aggregate(pipeline)
            return {doc['_id']: doc['count'] for doc in results}
            
        except Exception as e:
            logger.error(f"Error getting severity distribution: {e}")
            return {}