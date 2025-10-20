"""
MongoDB Query Examples for RIPEstat ETL Pipeline
Student: Seetharam Killivalavan
Roll Number: 3122225001124

This script demonstrates various ways to query the data loaded by the ETL pipeline.
Run this AFTER executing the main ETL pipeline to explore your data.

Usage: python query_examples.py
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import json

# Load environment variables
load_dotenv()

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class RIPEstatQueryExamples:
    """
    Demonstrates various query patterns for RIPEstat data in MongoDB.
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'etl_database')
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            self.collections = {
                'asn': 'ripestat_asn_overview',
                'network': 'ripestat_network_info',
                'geo': 'ripestat_geolocation'
            }
            
            print(f"{Colors.GREEN}✓ Connected to MongoDB: {self.database_name}{Colors.END}\n")
            
        except ServerSelectionTimeoutError:
            print(f"{Colors.RED}✗ MongoDB connection failed. Is MongoDB running?{Colors.END}")
            sys.exit(1)
    
    def print_header(self, text):
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    def print_query(self, query_description, query_dict):
        """Print the query being executed."""
        print(f"{Colors.CYAN}Query: {query_description}{Colors.END}")
        print(f"{Colors.YELLOW}Filter: {json.dumps(query_dict, indent=2, default=str)}{Colors.END}\n")
    
    def print_document(self, doc, fields=None):
        """Print a MongoDB document in a readable format."""
        if fields:
            doc = {k: doc.get(k) for k in fields if k in doc}
        
        print(json.dumps(doc, indent=2, default=str))
        print()
    
    # ==================== BASIC QUERIES ====================
    
    def example_1_count_documents(self):
        """Count total documents in each collection."""
        self.print_header("Example 1: Count Documents in Each Collection")
        
        for name, collection in self.collections.items():
            count = self.db[collection].count_documents({})
            print(f"{collection}: {Colors.GREEN}{count}{Colors.END} documents")
        print()
    
    def example_2_find_all_asns(self):
        """Retrieve all ASN records."""
        self.print_header("Example 2: Find All ASN Overview Records")
        
        collection = self.db[self.collections['asn']]
        query = {}
        
        self.print_query("Find all ASN records", query)
        
        cursor = collection.find(query).limit(5)
        
        print("Results (showing first 5):")
        for doc in cursor:
            fields = ['asn', 'holder', 'announced', 'block_name']
            self.print_document(doc, fields)
    
    def example_3_find_specific_asn(self):
        """Find a specific ASN by number."""
        self.print_header("Example 3: Find Specific ASN (AS3333 - RIPE NCC)")
        
        collection = self.db[self.collections['asn']]
        query = {'asn': '3333'}
        
        self.print_query("Find ASN 3333", query)
        
        doc = collection.find_one(query)
        
        if doc:
            print("Result:")
            fields = ['asn', 'holder', 'announced', 'type', 'block_name', 'block_desc']
            self.print_document(doc, fields)
        else:
            print(f"{Colors.RED}No document found{Colors.END}\n")
    
    # ==================== FILTERING QUERIES ====================
    
    def example_4_filter_by_announced_status(self):
        """Filter ASNs by announcement status."""
        self.print_header("Example 4: Filter ASNs by Announced Status")
        
        collection = self.db[self.collections['asn']]
        
        # Count announced ASNs
        announced_query = {'announced': True}
        announced_count = collection.count_documents(announced_query)
        
        # Count unannounced ASNs
        unannounced_query = {'announced': False}
        unannounced_count = collection.count_documents(unannounced_query)
        
        print(f"Announced ASNs: {Colors.GREEN}{announced_count}{Colors.END}")
        print(f"Unannounced ASNs: {Colors.YELLOW}{unannounced_count}{Colors.END}\n")
        
        # Show announced ASNs
        self.print_query("Find announced ASNs", announced_query)
        
        cursor = collection.find(announced_query, {'asn': 1, 'holder': 1, 'announced': 1, '_id': 0})
        
        print("Announced ASNs:")
        for doc in cursor:
            print(f"  AS{doc.get('asn')}: {doc.get('holder')} (Announced: {doc.get('announced')})")
        print()
    
    def example_5_filter_by_country(self):
        """Filter geolocation records by country."""
        self.print_header("Example 5: Filter Geolocation by Country")
        
        collection = self.db[self.collections['geo']]
        
        # Get unique countries
        countries = collection.distinct('country')
        print(f"Countries found: {Colors.GREEN}{', '.join(countries)}{Colors.END}\n")
        
        # Filter by specific country (if 'US' exists)
        if 'US' in countries:
            query = {'country': 'US'}
            self.print_query("Find US-based resources", query)
            
            cursor = collection.find(query, {'resource': 1, 'country': 1, 'city': 1, '_id': 0})
            
            print("US Resources:")
            for doc in cursor:
                print(f"  {doc.get('resource')}: {doc.get('city')}, {doc.get('country')}")
            print()
    
    # ==================== PROJECTION QUERIES ====================
    
    def example_6_projection_specific_fields(self):
        """Query with field projection to retrieve specific fields only."""
        self.print_header("Example 6: Projection - Retrieve Specific Fields Only")
        
        collection = self.db[self.collections['network']]
        
        query = {}
        projection = {
            'prefix': 1,
            'num_asns': 1,
            'ingestion_timestamp': 1,
            '_id': 0
        }
        
        self.print_query("Find all networks with specific fields", query)
        print(f"{Colors.YELLOW}Projection: {json.dumps(projection, indent=2)}{Colors.END}\n")
        
        cursor = collection.find(query, projection)
        
        print("Results:")
        for doc in cursor:
            self.print_document(doc)
    
    # ==================== SORTING QUERIES ====================
    
    def example_7_sort_by_ingestion_time(self):
        """Sort documents by ingestion timestamp."""
        self.print_header("Example 7: Sort by Ingestion Timestamp (Most Recent First)")
        
        collection = self.db[self.collections['asn']]
        
        query = {}
        
        self.print_query("Find all ASNs sorted by ingestion time", query)
        
        cursor = collection.find(
            query,
            {'asn': 1, 'holder': 1, 'ingestion_timestamp': 1, '_id': 0}
        ).sort('ingestion_timestamp', -1).limit(3)
        
        print("Results (3 most recent):")
        for doc in cursor:
            timestamp = doc.get('ingestion_timestamp', 'Unknown')
            print(f"  AS{doc.get('asn')}: {doc.get('holder')}")
            print(f"    Ingested: {timestamp}\n")
    
    # ==================== AGGREGATION QUERIES ====================
    
    def example_8_aggregation_count_by_country(self):
        """Use aggregation to count resources by country."""
        self.print_header("Example 8: Aggregation - Count Resources by Country")
        
        collection = self.db[self.collections['geo']]
        
        pipeline = [
            {
                '$group': {
                    '_id': '$country',
                    'count': {'$sum': 1},
                    'resources': {'$push': '$resource'}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        print(f"{Colors.YELLOW}Pipeline: {json.dumps(pipeline, indent=2)}{Colors.END}\n")
        
        results = list(collection.aggregate(pipeline))
        
        print("Results:")
        for result in results:
            country = result.get('_id', 'Unknown')
            count = result.get('count', 0)
            resources = ', '.join(result.get('resources', []))
            print(f"  {country}: {Colors.GREEN}{count}{Colors.END} resources ({resources})")
        print()
    
    def example_9_aggregation_average_quality_score(self):
        """Calculate average data quality score per collection."""
        self.print_header("Example 9: Aggregation - Average Data Quality Scores")
        
        for name, collection_name in self.collections.items():
            collection = self.db[collection_name]
            
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'avg_quality': {'$avg': '$data_quality_score'},
                        'min_quality': {'$min': '$data_quality_score'},
                        'max_quality': {'$max': '$data_quality_score'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            if results:
                stats = results[0]
                print(f"{collection_name}:")
                print(f"  Average Quality: {Colors.GREEN}{stats.get('avg_quality', 0):.2f}{Colors.END}")
                print(f"  Min Quality: {stats.get('min_quality', 0):.2f}")
                print(f"  Max Quality: {stats.get('max_quality', 0):.2f}")
                print(f"  Total Records: {stats.get('count', 0)}\n")
    
    # ==================== ADVANCED QUERIES ====================
    
    def example_10_time_range_query(self):
        """Query documents within a specific time range."""
        self.print_header("Example 10: Time Range Query - Last 24 Hours")
        
        collection = self.db[self.collections['asn']]
        
        # Calculate time 24 hours ago
        time_24h_ago = datetime.utcnow() - timedelta(hours=24)
        
        query = {
            'ingestion_timestamp': {
                '$gte': time_24h_ago
            }
        }
        
        self.print_query("Find records ingested in last 24 hours", query)
        
        count = collection.count_documents(query)
        print(f"Records found: {Colors.GREEN}{count}{Colors.END}\n")
        
        if count > 0:
            cursor = collection.find(
                query,
                {'asn': 1, 'holder': 1, 'ingestion_timestamp': 1, '_id': 0}
            ).limit(5)
            
            print("Sample results:")
            for doc in cursor:
                self.print_document(doc)
    
    def example_11_complex_filter(self):
        """Complex query with multiple conditions."""
        self.print_header("Example 11: Complex Query - High Quality Announced ASNs")
        
        collection = self.db[self.collections['asn']]
        
        query = {
            '$and': [
                {'announced': True},
                {'data_quality_score': {'$gte': 0.8}}
            ]
        }
        
        self.print_query("Find announced ASNs with quality score >= 0.8", query)
        
        count = collection.count_documents(query)
        print(f"Records found: {Colors.GREEN}{count}{Colors.END}\n")
        
        cursor = collection.find(
            query,
            {'asn': 1, 'holder': 1, 'announced': 1, 'data_quality_score': 1, '_id': 0}
        ).limit(5)
        
        print("Results:")
        for doc in cursor:
            self.print_document(doc)
    
    def example_12_text_search(self):
        """Search for text in holder field."""
        self.print_header("Example 12: Text Search - Find Specific Organizations")
        
        collection = self.db[self.collections['asn']]
        
        # Search for organizations containing "Google" or "RIPE"
        search_term = 'RIPE'
        query = {
            'holder': {'$regex': search_term, '$options': 'i'}  # Case-insensitive
        }
        
        self.print_query(f"Search for '{search_term}' in holder field", query)
        
        cursor = collection.find(
            query,
            {'asn': 1, 'holder': 1, '_id': 0}
        )
        
        print("Results:")
        for doc in cursor:
            print(f"  AS{doc.get('asn')}: {doc.get('holder')}")
        print()
    
    def example_13_join_like_query(self):
        """Simulate a join by correlating data across collections."""
        self.print_header("Example 13: Cross-Collection Query - ASN with Geolocation")
        
        # Get an ASN
        asn_collection = self.db[self.collections['asn']]
        asn_doc = asn_collection.find_one({}, {'asn': 1, 'holder': 1, '_id': 0})
        
        if asn_doc:
            asn = asn_doc.get('asn')
            holder = asn_doc.get('holder')
            
            print(f"Looking up geolocation for AS{asn} ({holder})")
            
            # Find geolocation for this ASN
            geo_collection = self.db[self.collections['geo']]
            geo_query = {'resource': f'AS{asn}'}
            
            geo_docs = list(geo_collection.find(
                geo_query,
                {'resource': 1, 'country': 1, 'city': 1, 'latitude': 1, 'longitude': 1, '_id': 0}
            ))
            
            if geo_docs:
                print(f"\n{Colors.GREEN}Found {len(geo_docs)} location(s):{Colors.END}")
                for doc in geo_docs:
                    self.print_document(doc)
            else:
                print(f"\n{Colors.YELLOW}No geolocation data found for AS{asn}{Colors.END}\n")
    
    # ==================== INDEX INFORMATION ====================
    
    def example_14_show_indexes(self):
        """Display all indexes on collections."""
        self.print_header("Example 14: Show Collection Indexes")
        
        for name, collection_name in self.collections.items():
            collection = self.db[collection_name]
            indexes = list(collection.list_indexes())
            
            print(f"{collection_name}:")
            for idx in indexes:
                index_name = idx.get('name', 'Unknown')
                index_keys = idx.get('key', {})
                unique = idx.get('unique', False)
                
                print(f"  - {index_name}: {index_keys} {'(UNIQUE)' if unique else ''}")
            print()
    
    # ==================== COLLECTION STATISTICS ====================
    
    def example_15_collection_stats(self):
        """Get detailed statistics about collections."""
        self.print_header("Example 15: Collection Statistics")
        
        for name, collection_name in self.collections.items():
            stats = self.db.command('collstats', collection_name)
            
            print(f"{collection_name}:")
            print(f"  Total Documents: {Colors.GREEN}{stats.get('count', 0)}{Colors.END}")
            print(f"  Storage Size: {stats.get('storageSize', 0) / 1024:.2f} KB")
            print(f"  Average Document Size: {stats.get('avgObjSize', 0)} bytes")
            print(f"  Indexes: {stats.get('nindexes', 0)}")
            print()
    
    def run_all_examples(self):
        """Execute all query examples."""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("="*70)
        print("RIPEstat ETL Pipeline - MongoDB Query Examples".center(70))
        print("Student: Seetharam Killivalavan | Roll: 3122225001124".center(70))
        print("="*70)
        print(f"{Colors.END}\n")
        
        examples = [
            self.example_1_count_documents,
            self.example_2_find_all_asns,
            self.example_3_find_specific_asn,
            self.example_4_filter_by_announced_status,
            self.example_5_filter_by_country,
            self.example_6_projection_specific_fields,
            self.example_7_sort_by_ingestion_time,
            self.example_8_aggregation_count_by_country,
            self.example_9_aggregation_average_quality_score,
            self.example_10_time_range_query,
            self.example_11_complex_filter,
            self.example_12_text_search,
            self.example_13_join_like_query,
            self.example_14_show_indexes,
            self.example_15_collection_stats
        ]
        
        for i, example in enumerate(examples, 1):
            try:
                example()
                input(f"{Colors.CYAN}Press Enter to continue to next example...{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}Error in example {i}: {e}{Colors.END}\n")
                continue
        
        print(f"\n{Colors.GREEN}✓ All examples completed!{Colors.END}\n")
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print(f"{Colors.GREEN}✓ MongoDB connection closed{Colors.END}")

def main():
    """Main entry point."""
    try:
        query_examples = RIPEstatQueryExamples()
        query_examples.run_all_examples()
        query_examples.close()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Examples interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()