"""
MongoDB Query Examples
Demonstrates how to query threat intelligence data
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment
load_dotenv()


def connect_to_db():
    """Connect to MongoDB"""
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'certat_intelligence_db')
    
    if not mongo_uri:
        print("Error: MONGO_URI not configured in .env")
        sys.exit(1)
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    print(f"Connected to database: {db_name}\n")
    return db


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_collection_stats(db):
    """Example 1: Get collection statistics"""
    print_header("Example 1: Collection Statistics")
    
    collections = db.list_collection_names()
    threat_collections = [c for c in collections if c.startswith(('threats_csv_', 'rss_'))]
    
    print(f"Found {len(threat_collections)} collections:\n")
    
    for collection_name in threat_collections:
        count = db[collection_name].count_documents({})
        print(f"  {collection_name:<40} {count:>8} documents")
    
    total = sum(db[c].count_documents({}) for c in threat_collections)
    print(f"\n  {'TOTAL':<40} {total:>8} documents")


def example_2_severity_distribution(db):
    """Example 2: Threat severity distribution"""
    print_header("Example 2: Threat Severity Distribution (CSV Feeds)")
    
    # Aggregate severity across all CSV threat collections
    collections = ['threats_csv_malware_infections', 
                   'threats_csv_vulnerable_systems',
                   'threats_csv_brute_force_attacks']
    
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            pipeline = [
                {'$group': {
                    '_id': '$severity',
                    'count': {'$sum': 1}
                }}
            ]
            
            results = db[collection_name].aggregate(pipeline)
            for doc in results:
                severity = doc['_id']
                count = doc['count']
                severity_counts[severity] = severity_counts.get(severity, 0) + count
    
    print("Severity distribution:")
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts[severity]
        bar = '█' * (count // 2)
        print(f"  {severity.upper():<10} {count:>4}  {bar}")


def example_3_recent_threats(db):
    """Example 3: Recent high-severity threats"""
    print_header("Example 3: Recent High-Severity Threats")
    
    collection = db['threats_csv_malware_infections']
    
    threats = collection.find(
        {'severity': {'$in': ['critical', 'high']}}
    ).sort('timestamp', -1).limit(5)
    
    print("Top 5 recent high-severity malware threats:\n")
    
    for i, threat in enumerate(threats, 1):
        print(f"{i}. {threat.get('timestamp', 'N/A')}")
        print(f"   Malware: {threat.get('malware', {}).get('name', 'Unknown')}")
        print(f"   Source: {threat.get('source', {}).get('ip', 'Unknown')}")
        print(f"   Country: {threat.get('source', {}).get('geolocation', {}).get('country_code', 'Unknown')}")
        print(f"   Severity: {threat.get('severity', 'Unknown').upper()}")
        print()


def example_4_geographic_distribution(db):
    """Example 4: Geographic distribution of threats"""
    print_header("Example 4: Geographic Distribution of Threats")
    
    collection = db['threats_csv_malware_infections']
    
    pipeline = [
        {'$group': {
            '_id': '$source.geolocation.country_code',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    
    results = collection.aggregate(pipeline)
    
    print("Top 10 countries with infected systems:\n")
    
    for i, doc in enumerate(results, 1):
        country = doc['_id'] or 'Unknown'
        count = doc['count']
        bar = '█' * (count // 2)
        print(f"  {i:>2}. {country:<5} {count:>4}  {bar}")


def example_5_malware_families(db):
    """Example 5: Most common malware families"""
    print_header("Example 5: Most Common Malware Families")
    
    collection = db['threats_csv_malware_infections']
    
    pipeline = [
        {'$match': {'malware.name': {'$exists': True, '$ne': None}}},
        {'$group': {
            '_id': '$malware.name',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    
    results = collection.aggregate(pipeline)
    
    print("Top 10 malware families:\n")
    
    for i, doc in enumerate(results, 1):
        malware = doc['_id']
        count = doc['count']
        bar = '█' * count
        print(f"  {i:>2}. {malware:<20} {count:>4}  {bar}")


def example_6_vulnerable_services(db):
    """Example 6: Most vulnerable services"""
    print_header("Example 6: Most Vulnerable Services")
    
    collection = db['threats_csv_vulnerable_systems']
    
    pipeline = [
        {'$group': {
            '_id': '$protocol.application',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}}
    ]
    
    results = collection.aggregate(pipeline)
    
    print("Vulnerable services:\n")
    
    for i, doc in enumerate(results, 1):
        service = doc['_id'] or 'Unknown'
        count = doc['count']
        bar = '█' * count
        print(f"  {i:>2}. {service:<15} {count:>4}  {bar}")


def example_7_recent_rss_warnings(db):
    """Example 7: Recent RSS security warnings"""
    print_header("Example 7: Recent Security Warnings (RSS)")
    
    collection = db.get_collection('rss_warnings')
    
    # Check if collection exists and has data
    if collection is None or collection.count_documents({}) == 0:
        print("No RSS warnings found. Run the RSS pipeline to fetch data.")
        return
    
    warnings = collection.find().sort('published', -1).limit(5)
    
    print("Latest 5 security warnings:\n")
    
    for i, warning in enumerate(warnings, 1):
        print(f"{i}. {warning.get('title', 'No title')}")
        print(f"   Published: {warning.get('published', 'N/A')}")
        print(f"   Link: {warning.get('link', 'N/A')}")
        print(f"   Summary: {warning.get('summary', 'N/A')[:100]}...")
        print()


def example_8_text_search(db):
    """Example 8: Full-text search in RSS feeds"""
    print_header("Example 8: Full-Text Search (RSS)")
    
    collection = db.get_collection('rss_warnings')
    
    if collection is None or collection.count_documents({}) == 0:
        print("No RSS warnings found. Run the RSS pipeline to fetch data.")
        return
    
    search_term = "vulnerability"
    
    results = collection.find(
        {'$text': {'$search': search_term}}
    ).limit(5)
    
    print(f"Search results for '{search_term}':\n")
    
    found = 0
    for result in results:
        found += 1
        print(f"{found}. {result.get('title', 'No title')}")
        print(f"   {result.get('link', 'N/A')}")
        print()
    
    if found == 0:
        print(f"No results found for '{search_term}'")


def example_9_attack_timeline(db):
    """Example 9: Attack timeline (last 7 days)"""
    print_header("Example 9: Brute Force Attack Timeline")
    
    collection = db['threats_csv_brute_force_attacks']
    
    # Group by date
    pipeline = [
        {'$project': {
            'date': {
                '$dateToString': {
                    'format': '%Y-%m-%d',
                    'date': {'$dateFromString': {'dateString': '$timestamp'}}
                }
            }
        }},
        {'$group': {
            '_id': '$date',
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    
    try:
        results = collection.aggregate(pipeline)
        
        print("Brute force attacks by date:\n")
        
        for doc in results:
            date = doc['_id']
            count = doc['count']
            bar = '█' * count
            print(f"  {date}  {count:>3}  {bar}")
    except Exception as e:
        print(f"Error: {e}")
        print("Data may not have valid timestamps")


def example_10_custom_query(db):
    """Example 10: Custom query template"""
    print_header("Example 10: Custom Query Template")
    
    print("Template for creating your own queries:\n")
    
    code = '''
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME', 'certat_intelligence_db')]

# Example: Find all critical threats from a specific country
collection = db['threats_csv_malware_infections']

query = {
    'severity': 'critical',
    'source.geolocation.country_code': 'AT'
}

results = collection.find(query).limit(10)

for doc in results:
    print(doc)
'''
    
    print(code)


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  CERT.at Threat Intelligence - MongoDB Query Examples")
    print("=" * 70)
    
    try:
        db = connect_to_db()
        
        # Check if there's any data
        collections = db.list_collection_names()
        if not any(c.startswith(('threats_csv_', 'rss_')) for c in collections):
            print("\n⚠ Warning: No threat intelligence data found in database")
            print("Run the ETL pipeline first to load data:\n")
            print("  python threat_intel_pipeline/etl_orchestrator.py\n")
            sys.exit(1)
        
        # Run examples
        example_1_collection_stats(db)
        example_2_severity_distribution(db)
        example_3_recent_threats(db)
        example_4_geographic_distribution(db)
        example_5_malware_families(db)
        example_6_vulnerable_services(db)
        example_7_recent_rss_warnings(db)
        example_8_text_search(db)
        example_9_attack_timeline(db)
        example_10_custom_query(db)
        
        print("\n" + "=" * 70)
        print("  All examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()