"""
RSS Transformer Module
Transforms and normalizes CERT.at RSS feed data
"""

import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from html import unescape
import re

logger = logging.getLogger(__name__)


class RSSTransformer:
    """Transforms and normalizes RSS feed data"""
    
    def __init__(self, max_records: int = 100):
        """
        Initialize transformer
        
        Args:
            max_records: Maximum number of records to process per feed
        """
        self.max_records = max_records
        logger.info(f"RSS Transformer initialized with max_records={max_records}")
    
    @staticmethod
    def clean_html(text: str) -> str:
        """
        Remove HTML tags and decode HTML entities
        
        Args:
            text: Raw HTML text
            
        Returns:
            Clean text
        """
        if not text:
            return ""
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        Parse and normalize date strings
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            ISO format date string or None
        """
        if not date_str:
            return None
        
        try:
            # Try parsing with email utils
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            try:
                # Fallback to dateutil parser
                from dateutil import parser
                dt = parser.parse(date_str)
                return dt.isoformat()
            except:
                logger.warning(f"Could not parse date: {date_str}")
                return date_str
    
    def _generate_entry_id(self, entry: Dict, feed_name: str) -> str:
        """
        Generate unique ID for RSS entry
        
        Args:
            entry: RSS entry
            feed_name: Name of the feed
            
        Returns:
            Unique entry identifier
        """
        # Use GUID if available, otherwise create from link and title
        guid = entry.get('id') or entry.get('guid') or entry.get('link', '')
        
        id_string = f"{feed_name}|{guid}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    def _extract_tags(self, entry: Dict) -> List[str]:
        """
        Extract tags from entry
        
        Args:
            entry: RSS entry
            
        Returns:
            List of tags
        """
        tags = []
        
        if 'tags' in entry:
            tags = [tag.get('term', '') for tag in entry['tags'] if tag.get('term')]
        
        # Also check for categories
        if 'categories' in entry:
            for category in entry.get('categories', []):
                if isinstance(category, str):
                    tags.append(category)
                elif isinstance(category, dict):
                    tags.append(category.get('term', ''))
        
        return [tag for tag in tags if tag]  # Remove empty strings
    
    def _extract_content(self, entry: Dict) -> str:
        """
        Extract full content from entry
        
        Args:
            entry: RSS entry
            
        Returns:
            Content text
        """
        # Try to get full content
        if 'content' in entry and entry['content']:
            content_list = entry['content']
            if content_list:
                return self.clean_html(content_list[0].get('value', ''))
        
        # Fallback to description
        if 'description' in entry:
            return self.clean_html(entry.get('description', ''))
        
        # Fallback to summary
        if 'summary' in entry:
            return self.clean_html(entry.get('summary', ''))
        
        return ""
    
    def normalize_entry(self, entry: Dict, feed_name: str) -> Dict:
        """
        Normalize a single RSS entry
        
        Args:
            entry: Raw RSS entry
            feed_name: Name of the source feed
            
        Returns:
            Normalized entry dictionary
        """
        # Generate unique ID
        entry_id = self._generate_entry_id(entry, feed_name)
        
        # Extract content
        content = self._extract_content(entry)
        summary = self.clean_html(entry.get('summary', ''))
        
        # Use summary if content is empty
        if not content:
            content = summary
        
        normalized = {
            # Identifiers
            'entry_id': entry_id,
            'feed_source': feed_name,
            'guid': entry.get('id', entry.get('link', '')),
            
            # Core content
            'title': self.clean_html(entry.get('title', '')),
            'link': entry.get('link', ''),
            'content': content,
            'summary': summary,
            
            # Metadata
            'author': entry.get('author', ''),
            'published': self.parse_date(entry.get('published', '')),
            'updated': self.parse_date(entry.get('updated', '')),
            
            # Classification
            'tags': self._extract_tags(entry),
            
            # Processing metadata
            'extracted_at': datetime.utcnow().isoformat(),
            'data_type': 'rss_feed'
        }
        
        return normalized
    
    def transform_feed(self, feed_data: Dict) -> Optional[Dict]:
        """
        Transform a single feed's data
        
        Args:
            feed_data: Extracted feed data
            
        Returns:
            Transformed feed data or None
        """
        if not feed_data or 'entries' not in feed_data:
            logger.warning("No valid data to transform")
            return None
        
        feed_name = feed_data['feed_name']
        entries = feed_data['entries']
        
        # Limit entries
        entries = entries[:self.max_records]
        
        logger.info(f"Transforming {len(entries)} entries from {feed_name}")
        
        normalized_entries = []
        errors = 0
        
        for entry in entries:
            try:
                normalized = self.normalize_entry(entry, feed_name)
                normalized_entries.append(normalized)
            except Exception as e:
                logger.error(f"Error transforming entry: {e}")
                errors += 1
                continue
        
        logger.info(
            f"Successfully transformed {len(normalized_entries)} entries "
            f"from {feed_name} ({errors} errors)"
        )
        
        return {
            'feed_name': feed_name,
            'feed_info': feed_data.get('feed_info', {}),
            'original_count': feed_data['entry_count'],
            'transformed_count': len(normalized_entries),
            'error_count': errors,
            'entries': normalized_entries,
            'transformed_at': datetime.utcnow().isoformat()
        }
    
    def transform_all_feeds(self, feeds_data: Dict[str, Optional[Dict]]) -> Dict[str, Optional[Dict]]:
        """
        Transform all feeds data
        
        Args:
            feeds_data: Dictionary of extracted feed data
            
        Returns:
            Dictionary of transformed feed data
        """
        logger.info("Starting transformation of all RSS feeds")
        results = {}
        
        for feed_name, feed_data in feeds_data.items():
            if feed_data is not None:
                results[feed_name] = self.transform_feed(feed_data)
            else:
                logger.warning(f"Skipping transformation for {feed_name} (no data)")
                results[feed_name] = None
        
        successful = sum(1 for v in results.values() if v is not None)
        total_entries = sum(v['transformed_count'] for v in results.values() if v)
        
        logger.info(
            f"RSS transformation complete: {successful} feeds, {total_entries} total entries"
        )
        
        return results
    
    def get_feed_summary(self, transformed_data: Dict) -> Dict[str, Dict]:
        """
        Get summary statistics for transformed feeds
        
        Args:
            transformed_data: Transformed feed data
            
        Returns:
            Dictionary with feed summaries
        """
        summary = {}
        
        for feed_name, feed_data in transformed_data.items():
            if feed_data:
                summary[feed_name] = {
                    'entry_count': feed_data.get('transformed_count', 0),
                    'error_count': feed_data.get('error_count', 0),
                    'has_data': len(feed_data.get('entries', [])) > 0
                }
        
        return summary