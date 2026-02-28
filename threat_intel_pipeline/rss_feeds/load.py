"""
RSS Loader Module
Loads RSS feed data into MongoDB
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient, errors, ASCENDING, DESCENDING
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class RSSLoader:
    """Loads RSS feed data into MongoDB"""
    
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
        logger.info(f"RSS Loader initialized for database: {db_name}")
    
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
            # Index on entry_id for duplicate detection
            collection.create_index([('entry_id', ASCENDING)], unique=True)
            
            # Index on published date
            collection.create_index([('published', DESCENDING)])
            
            # Index on feed_source
            collection.create_index([('feed_source', ASCENDING)])
            
            # Text index for full-text search
            collection.create_index([
                ('title', 'text'),
                ('content', 'text'),
                ('summary', 'text')
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
        entries: List[Dict],
        clean_before: bool = True,
        upsert: bool = False
    ) -> Dict[str, int]:
        """
        Load RSS entries into MongoDB
        
        Args:
            collection_name: Name of the collection
            entries: List of RSS entries
            clean_before: Whether to clean collection before loading
            upsert: Whether to upsert (update or insert) entries
            
        Returns:
            Dictionary with loading statistics
        """
        stats = {
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
        
        if not entries:
            logger.warning(f"No entries to load into {collection_name}")
            return stats
        
        try:
            collection = self.db[collection_name]
            
            # Create indexes
            self._create_indexes(collection)
            
            # Clean collection if requested
            if clean_before:
                self.clean_collection(collection_name)
            
            # Add load metadata
            for entry in entries:
                entry['loaded_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Loading {len(entries)} entries into '{collection_name}'...")
            
            if upsert:
                # Upsert each entry based on entry_id
                for entry in entries:
                    try:
                        result = collection.replace_one(
                            {'entry_id': entry['entry_id']},
                            entry,
                            upsert=True
                        )
                        if result.upserted_id:
                            stats['inserted'] += 1
                        elif result.modified_count > 0:
                            stats['updated'] += 1
                        else:
                            stats['skipped'] += 1
                    except Exception as e:
                        logger.error(f"Error upserting entry: {e}")
                        stats['errors'] += 1
            else:
                # Bulk insert
                try:
                    result = collection.insert_many(entries, ordered=False)
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
            stats['errors'] = len(entries)
        
        return stats
    
    def load_all_feeds(
        self,
        transformed_data: Dict[str, Optional[Dict]],
        clean_before: bool = True,
        upsert: bool = False
    ) -> Dict[str, Dict[str, int]]:
        """
        Load all transformed RSS feeds into MongoDB
        
        Args:
            transformed_data: Dictionary of transformed feed data
            clean_before: Whether to clean collections before loading
            upsert: Whether to upsert entries
            
        Returns:
            Dictionary with feed names and loading statistics
        """
        logger.info("Loading all RSS feeds into MongoDB")
        results = {}
        
        for feed_name, feed_data in transformed_data.items():
            if feed_data and feed_data.get('entries'):
                collection_name = f"rss_{feed_name}"
                entries = feed_data['entries']
                
                stats = self.load_feed_data(
                    collection_name,
                    entries,
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
            f"RSS load complete: {total_inserted} inserted, "
            f"{total_updated} updated across {len(results)} feeds"
        )
        
        return results
    
    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get statistics about stored RSS feed data
        
        Returns:
            Dictionary with collection names and document counts
        """
        stats = {}
        try:
            collections = self.db.list_collection_names()
            rss_collections = [c for c in collections if c.startswith('rss_')]
            
            for collection_name in rss_collections:
                count = self.db[collection_name].count_documents({})
                stats[collection_name] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_recent_entries(self, feed_name: str, limit: int = 10) -> List[Dict]:
        """
        Get recent entries from a specific feed
        
        Args:
            feed_name: Name of the feed
            limit: Maximum number of entries to return
            
        Returns:
            List of recent entries
        """
        try:
            collection_name = f"rss_{feed_name}"
            collection = self.db[collection_name]
            
            entries = collection.find(
                {},
                {'_id': 0}
            ).sort('published', DESCENDING).limit(limit)
            
            return list(entries)
            
        except Exception as e:
            logger.error(f"Error getting recent entries: {e}")
            return []