"""
CSV Extractor Module
Extracts CERT.at threat intelligence from CSV feeds
"""

import os
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVExtractor:
    """Extracts threat intelligence data from CERT.at CSV feeds"""
    
    # CERT.at feed definitions
    FEED_DEFINITIONS = {
        'malware_infections': {
            'filename': 'certat_malware_infections.csv',
            'description': 'Malware infected systems and C2 communications'
        },
        'vulnerable_systems': {
            'filename': 'certat_vulnerable_systems.csv',
            'description': 'Systems with known vulnerabilities'
        },
        'brute_force_attacks': {
            'filename': 'certat_brute_force_attacks.csv',
            'description': 'Brute force attack attempts'
        }
    }
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize CSV extractor
        
        Args:
            data_dir: Directory containing CSV feed files
        """
        self.data_dir = Path(data_dir)
        self._validate_data_dir()
        logger.info(f"CSV Extractor initialized with data_dir: {self.data_dir}")
    
    def _validate_data_dir(self) -> None:
        """Validate that data directory exists"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        if not self.data_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.data_dir}")
    
    def _read_csv_file(self, file_path: Path) -> Optional[List[Dict]]:
        """
        Read and parse a CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries or None if error
        """
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            logger.info(f"Reading CSV file: {file_path}")
            
            records = []
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    # Clean empty strings to None
                    cleaned_row = {
                        k: (v.strip() if v and v.strip() else None) 
                        for k, v in row.items()
                    }
                    cleaned_row['_row_number'] = row_num
                    records.append(cleaned_row)
            
            logger.info(f"Successfully read {len(records)} records from {file_path.name}")
            return records
            
        except csv.Error as e:
            logger.error(f"CSV parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}", exc_info=True)
            return None
    
    def extract_feed(self, feed_name: str) -> Optional[Dict]:
        """
        Extract a single threat feed
        
        Args:
            feed_name: Name of the feed to extract
            
        Returns:
            Dictionary with feed data or None if error
        """
        if feed_name not in self.FEED_DEFINITIONS:
            logger.error(f"Unknown feed: {feed_name}. Available: {list(self.FEED_DEFINITIONS.keys())}")
            return None
        
        feed_def = self.FEED_DEFINITIONS[feed_name]
        file_path = self.data_dir / feed_def['filename']
        
        logger.info(f"Extracting feed: {feed_name} ({feed_def['description']})")
        
        records = self._read_csv_file(file_path)
        
        if records is None:
            return None
        
        return {
            'feed_name': feed_name,
            'filename': feed_def['filename'],
            'description': feed_def['description'],
            'records': records,
            'record_count': len(records),
            'extracted_at': datetime.utcnow().isoformat()
        }
    
    def extract_all_feeds(self) -> Dict[str, Optional[Dict]]:
        """
        Extract all available threat feeds
        
        Returns:
            Dictionary with feed names as keys and feed data as values
        """
        logger.info("Starting extraction of all CSV feeds")
        results = {}
        
        for feed_name in self.FEED_DEFINITIONS.keys():
            results[feed_name] = self.extract_feed(feed_name)
        
        successful = sum(1 for v in results.values() if v is not None)
        total = len(self.FEED_DEFINITIONS)
        
        logger.info(f"CSV extraction complete: {successful}/{total} feeds extracted successfully")
        
        return results
    
    def get_available_feeds(self) -> List[str]:
        """Get list of available feed names"""
        return list(self.FEED_DEFINITIONS.keys())
    
    def validate_feed_files(self) -> Dict[str, bool]:
        """
        Validate that all feed files exist
        
        Returns:
            Dictionary with feed names and existence status
        """
        results = {}
        for feed_name, feed_def in self.FEED_DEFINITIONS.items():
            file_path = self.data_dir / feed_def['filename']
            results[feed_name] = file_path.exists()
        
        return results