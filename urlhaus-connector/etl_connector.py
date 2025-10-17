"""
Abuse.ch URLhaus ETL Pipeline - Multi-Format Data Extraction
Author: KEERTHANA.G.S - 3122225001059
Date: October 2025

This script extracts malware URL intelligence from THREE different URLhaus endpoints:
1. Recent URLs CSV - Latest malware distribution URLs (CSV format)
2. Online URLs CSV - Currently active malware URLs (CSV format)
3. Recent URLs Text - Plain text URL list (TEXT format)

All data sources are publicly accessible without authentication.
Three different formats: CSV, CSV, TEXT
"""

import os
import sys
import requests
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

class URLhausMultiFormatETL:
    """ETL Pipeline for Abuse.ch URLhaus Multiple Data Formats"""
    
    def __init__(self):
        """Initialize the ETL pipeline"""
        self.urlhaus_endpoints = {
            "recent_csv": "https://urlhaus.abuse.ch/downloads/csv_recent/",
            "online_csv": "https://urlhaus.abuse.ch/downloads/csv_online/",
            "text_urls": "https://urlhaus.abuse.ch/downloads/text_recent/"
        }
        
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.mongo_db = os.getenv("MONGO_DATABASE", "threat_intelligence")
        
        self.collection_names = {
            "recent_urls_csv": "urlhaus_recent_urls_csv",
            "online_urls_csv": "urlhaus_online_urls_csv",
            "text_urls": "urlhaus_text_urls"
        }
        
        self.client = None
        self.db = None
        self._connect_mongodb()
    
    def _connect_mongodb(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.mongo_db]
            self.client.server_info()
            print(f"✓ Connected to MongoDB: {self.mongo_db}")
        except errors.ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            sys.exit(1)
        except errors.ServerSelectionTimeoutError as e:
            print(f"✗ MongoDB connection timeout: {e}")
            print("  Make sure MongoDB is running")
            sys.exit(1)
    
    def _download_data(self, url: str) -> Optional[str]:
        """Download data from URLhaus"""
        try:
            print(f"  Downloading from: {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            if len(response.text) < 50:
                print(f"  ⚠ Response too short")
                return None
                
            return response.text
            
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return None
    
    def _parse_csv(self, csv_text: str) -> List[Dict]:
        """Parse CSV text into list of dictionaries"""
        lines = csv_text.strip().split('\n')
        
        # Skip comment lines (lines starting with #)
        data_lines = [line for line in lines if not line.startswith('#')]
        
        if len(data_lines) < 2:
            return []
        
        try:
            csv_reader = csv.DictReader(io.StringIO('\n'.join(data_lines)))
            return list(csv_reader)
        except Exception as e:
            print(f"  ⚠ CSV parsing error: {e}")
            return []
    
    def _parse_text(self, text_data: str) -> List[str]:
        """Parse plain text URL list"""
        lines = text_data.strip().split('\n')
        
        # Skip comment lines and empty lines
        urls = [
            line.strip() 
            for line in lines 
            if line.strip() and not line.startswith('#')
        ]
        
        return urls
    
    def extract_recent_urls_csv(self, limit: int = 50) -> Optional[List[Dict]]:
        """
        ENDPOINT 1: Extract recent malware URLs from URLhaus CSV
        Format: CSV with full metadata
        """
        print(f"\n{'='*60}")
        print(f"ENDPOINT 1: Recent Malware URLs (CSV Format)")
        print(f"{'='*60}")
        
        csv_data = self._download_data(self.urlhaus_endpoints["recent_csv"])
        
        if not csv_data:
            print("✗ Failed to download recent URLs CSV")
            return None
        
        urls = self._parse_csv(csv_data)
        urls = urls[:limit]
        
        print(f"✓ Extracted {len(urls)} recent URLs from CSV")
        return urls
    
    def extract_online_urls_csv(self, limit: int = 50) -> Optional[List[Dict]]:
        """
        ENDPOINT 2: Extract currently online malware URLs from URLhaus CSV
        Format: CSV with full metadata
        """
        print(f"\n{'='*60}")
        print(f"ENDPOINT 2: Online Malware URLs (CSV Format)")
        print(f"{'='*60}")
        
        csv_data = self._download_data(self.urlhaus_endpoints["online_csv"])
        
        if not csv_data:
            print("✗ Failed to download online URLs CSV")
            return None
        
        urls = self._parse_csv(csv_data)
        urls = urls[:limit]
        
        print(f"✓ Extracted {len(urls)} online URLs from CSV")
        return urls
    
    def extract_text_urls(self, limit: int = 50) -> Optional[List[str]]:
        """
        ENDPOINT 3: Extract recent URLs from plain text format
        Format: Plain text, one URL per line
        """
        print(f"\n{'='*60}")
        print(f"ENDPOINT 3: Recent URLs (Plain Text Format)")
        print(f"{'='*60}")
        
        text_data = self._download_data(self.urlhaus_endpoints["text_urls"])
        
        if not text_data:
            print("✗ Failed to download text URL list")
            return None
        
        urls = self._parse_text(text_data)
        urls = urls[:limit]
        
        print(f"✓ Extracted {len(urls)} URLs from text file")
        return urls
    
    def transform_csv_urls(self, urls: List[Dict], source: str) -> List[Dict]:
        """Transform CSV URLs data for MongoDB"""
        print(f"\n--- Transforming CSV URLs Data ({source}) ---")
        
        transformed = []
        timestamp = datetime.utcnow()
        
        for url_data in urls:
            try:
                transformed_doc = {
                    "url_id": url_data.get("id", ""),
                    "dateadded": url_data.get("dateadded", ""),
                    "url": url_data.get("url", ""),
                    "url_status": url_data.get("url_status", ""),
                    "last_online": url_data.get("last_online", ""),
                    "threat": url_data.get("threat", ""),
                    "tags": url_data.get("tags", "").split(",") if url_data.get("tags") else [],
                    "urlhaus_link": url_data.get("urlhaus_link", ""),
                    "reporter": url_data.get("reporter", ""),
                    "ingestion_timestamp": timestamp,
                    "data_source": "abuse.ch_urlhaus",
                    "data_format": "csv",
                    "endpoint": source
                }
                transformed.append(transformed_doc)
            except Exception as e:
                print(f"  ⚠ Error transforming URL: {e}")
                continue
        
        print(f"✓ Transformed {len(transformed)}/{len(urls)} URLs")
        return transformed
    
    def transform_text_urls(self, urls: List[str]) -> List[Dict]:
        """Transform plain text URLs for MongoDB"""
        print(f"\n--- Transforming Text URLs Data ---")
        
        transformed = []
        timestamp = datetime.utcnow()
        
        for idx, url in enumerate(urls):
            try:
                transformed_doc = {
                    "sequence_id": idx + 1,
                    "url": url,
                    "ingestion_timestamp": timestamp,
                    "data_source": "abuse.ch_urlhaus",
                    "data_format": "text",
                    "endpoint": "text_recent"
                }
                transformed.append(transformed_doc)
            except Exception as e:
                print(f"  ⚠ Error transforming URL: {e}")
                continue
        
        print(f"✓ Transformed {len(transformed)}/{len(urls)} URLs")
        return transformed
    
    def load_to_mongodb(self, data: List[Dict], collection_name: str) -> bool:
        """Load data into MongoDB collection"""
        if not data or len(data) == 0:
            print(f"⚠ No data to load into {collection_name}")
            return False
        
        print(f"\n--- Loading Data to MongoDB: {collection_name} ---")
        
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(data, ordered=False)
            inserted_count = len(result.inserted_ids)
            print(f"✓ Inserted {inserted_count} document(s) into {collection_name}")
            return True
        
        except errors.BulkWriteError as e:
            inserted = e.details.get('nInserted', 0)
            print(f"⚠ Bulk write error. Inserted {inserted} documents")
            return inserted > 0
        
        except Exception as e:
            print(f"✗ Failed to load data: {e}")
            return False
    
    def run_etl_pipeline(self):
        """Execute complete ETL pipeline for all three endpoints"""
        print("\n" + "="*60)
        print("URLHAUS MULTI-FORMAT ETL PIPELINE - STARTING")
        print("="*60)
        print("Data Source: abuse.ch URLhaus")
        print("Formats: CSV + CSV + TEXT")
        print("Endpoints: 3 (Recent CSV, Online CSV, Text URLs)")
        print("="*60)
        
        success_count = 0
        total_endpoints = 3
        
        # PIPELINE 1: Recent URLs (CSV)
        print("\n" + "="*60)
        print("PIPELINE 1/3: RECENT MALWARE URLS (CSV)")
        print("="*60)
        try:
            urls = self.extract_recent_urls_csv(limit=50)
            if urls and len(urls) > 0:
                transformed = self.transform_csv_urls(urls, "recent_csv")
                if self.load_to_mongodb(transformed, self.collection_names["recent_urls_csv"]):
                    success_count += 1
                    print("✓ Pipeline 1 completed successfully")
        except Exception as e:
            print(f"✗ Error in Pipeline 1: {e}")
        
        # PIPELINE 2: Online URLs (CSV)
        print("\n" + "="*60)
        print("PIPELINE 2/3: ONLINE MALWARE URLS (CSV)")
        print("="*60)
        try:
            urls = self.extract_online_urls_csv(limit=50)
            if urls and len(urls) > 0:
                transformed = self.transform_csv_urls(urls, "online_csv")
                if self.load_to_mongodb(transformed, self.collection_names["online_urls_csv"]):
                    success_count += 1
                    print("✓ Pipeline 2 completed successfully")
        except Exception as e:
            print(f"✗ Error in Pipeline 2: {e}")
        
        # PIPELINE 3: Text URLs
        print("\n" + "="*60)
        print("PIPELINE 3/3: RECENT MALWARE URLS (TEXT)")
        print("="*60)
        try:
            urls = self.extract_text_urls(limit=50)
            if urls and len(urls) > 0:
                transformed = self.transform_text_urls(urls)
                if self.load_to_mongodb(transformed, self.collection_names["text_urls"]):
                    success_count += 1
                    print("✓ Pipeline 3 completed successfully")
        except Exception as e:
            print(f"✗ Error in Pipeline 3: {e}")
        
        # Summary
        print("\n" + "="*60)
        print(f"ETL PIPELINE SUMMARY")
        print("="*60)
        print(f"Total Endpoints: {total_endpoints}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_endpoints - success_count}")
        print(f"Success Rate: {(success_count/total_endpoints)*100:.1f}%")
        print("="*60 + "\n")
        
        if success_count == total_endpoints:
            print("🎉 All pipelines completed successfully!")
            print("✓ 100% Success Rate Achieved!")
        elif success_count > 0:
            print(f"⚠ {success_count} out of {total_endpoints} pipelines completed")
        else:
            print("✗ Pipeline failed. Check errors above.")
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("ABUSE.CH URLHAUS MULTI-FORMAT ETL CONNECTOR")
    print("="*60)
    print("Author: KEERTHANA.G.S")
    print("Roll Number: 3122225001059")
    print("="*60 + "\n")
    
    try:
        etl = URLhausMultiFormatETL()
        etl.run_etl_pipeline()
        etl.close_connection()
        
        print("\n✓ ETL process completed. Check MongoDB for data.")
        
    except KeyboardInterrupt:
        print("\n⚠ Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()