"""
RSS Extractor Module
Extracts CERT.at RSS feeds for security warnings and updates
"""

import feedparser
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RSSExtractor:
    """Extracts RSS feed data from CERT.at endpoints"""
    
    # CERT.at RSS feed endpoints
    FEED_ENDPOINTS = {
        'warnings': {
            'url': 'https://www.cert.at/cert-at.de.warnings.rss_2.0.xml',
            'description': 'Security warnings and alerts'
        },
        'blog': {
            'url': 'https://www.cert.at/cert-at.de.blog.rss_2.0.xml',
            'description': 'Blog posts (German)'
        },
        'blog_en': {
            'url': 'https://www.cert.at/cert-at.en.blog.rss_2.0.xml',
            'description': 'Blog posts (English)'
        },
        'daily_reports': {
            'url': 'https://www.cert.at/cert-at.de.daily.rss_2.0.xml',
            'description': 'Daily security reports'
        },
        'current': {
            'url': 'https://www.cert.at/cert-at.de.current.rss_2.0.xml',
            'description': 'Current security news'
        },
        'specials': {
            'url': 'https://www.cert.at/cert-at.de.specials.rss_2.0.xml',
            'description': 'Special security topics'
        }
    }
    
    def __init__(self, timeout: int = 30):
        """
        Initialize RSS extractor
        
        Args:
            timeout: Timeout for feed requests in seconds
        """
        self.timeout = timeout
        logger.info(f"RSS Extractor initialized with timeout={timeout}s")
    
    def fetch_feed(self, feed_name: str) -> Optional[Dict]:
        """
        Fetch a single RSS feed
        
        Args:
            feed_name: Name of the feed to fetch
            
        Returns:
            Dictionary with feed data or None if error
        """
        if feed_name not in self.FEED_ENDPOINTS:
            logger.error(
                f"Unknown feed: {feed_name}. "
                f"Available: {list(self.FEED_ENDPOINTS.keys())}"
            )
            return None
        
        feed_config = self.FEED_ENDPOINTS[feed_name]
        feed_url = feed_config['url']
        
        try:
            logger.info(f"Fetching RSS feed: {feed_name} from {feed_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            # Check for parsing errors
            if feed.bozo:
                logger.warning(
                    f"Feed parsing warning for {feed_name}: {feed.bozo_exception}"
                )
            
            # Check if feed has entries
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_name}")
                return None
            
            logger.info(
                f"Successfully fetched {len(feed.entries)} entries from {feed_name}"
            )
            
            return {
                'feed_name': feed_name,
                'feed_url': feed_url,
                'description': feed_config['description'],
                'feed_info': {
                    'title': feed.feed.get('title', ''),
                    'link': feed.feed.get('link', ''),
                    'description': feed.feed.get('description', ''),
                    'updated': feed.feed.get('updated', ''),
                    'language': feed.feed.get('language', '')
                },
                'entries': feed.entries,
                'entry_count': len(feed.entries),
                'extracted_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_name}: {e}", exc_info=True)
            return None
    
    def fetch_all_feeds(self) -> Dict[str, Optional[Dict]]:
        """
        Fetch all available RSS feeds
        
        Returns:
            Dictionary with feed names as keys and feed data as values
        """
        logger.info("Starting extraction of all RSS feeds")
        results = {}
        
        for feed_name in self.FEED_ENDPOINTS.keys():
            results[feed_name] = self.fetch_feed(feed_name)
        
        successful = sum(1 for v in results.values() if v is not None)
        total = len(self.FEED_ENDPOINTS)
        
        logger.info(
            f"RSS extraction complete: {successful}/{total} feeds extracted successfully"
        )
        
        return results
    
    def fetch_specific_feeds(self, feed_names: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch specific RSS feeds
        
        Args:
            feed_names: List of feed names to fetch
            
        Returns:
            Dictionary with feed names as keys and feed data as values
        """
        logger.info(f"Fetching specific RSS feeds: {feed_names}")
        results = {}
        
        for feed_name in feed_names:
            results[feed_name] = self.fetch_feed(feed_name)
        
        return results
    
    def get_available_feeds(self) -> List[str]:
        """Get list of available feed names"""
        return list(self.FEED_ENDPOINTS.keys())
    
    def get_feed_info(self, feed_name: str) -> Optional[Dict]:
        """
        Get information about a specific feed
        
        Args:
            feed_name: Name of the feed
            
        Returns:
            Feed configuration or None
        """
        return self.FEED_ENDPOINTS.get(feed_name)