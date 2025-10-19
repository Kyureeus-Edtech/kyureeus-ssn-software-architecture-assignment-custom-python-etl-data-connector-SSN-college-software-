"""
Verification Script for PublicWWW ETL Pipeline
Run this after your ETL pipeline to verify data extraction
"""

from pymongo import MongoClient
from datetime import datetime
import json

def verify_extraction():
    """Verify that data was extracted correctly"""
    
    print("\n" + "="*70)
    print("PublicWWW ETL - Data Extraction Verification")
    print("="*70 + "\n")
    
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['etl_database']  
        collection = db['publicwww_raw']
        
        print("✓ Connected to MongoDB")
        
        doc_count = collection.count_documents({})
        print(f"✓ Total documents in collection: {doc_count}")
        
        if doc_count == 0:
            print("\n❌ ERROR: No documents found in collection!")
            print("   Please run the ETL pipeline first: python connector.py")
            return False
        
        latest_doc = collection.find_one(
            sort=[('ingestion_timestamp', -1)]
        )
        
        if not latest_doc:
            print("\n❌ ERROR: Could not retrieve latest document!")
            return False
        
        print(f"✓ Retrieved latest document (ID: {latest_doc['_id']})")
        
        print("\n" + "-"*70)
        print("DOCUMENT STRUCTURE VERIFICATION")
        print("-"*70)
        
        source = latest_doc.get('source', 'MISSING')
        print(f"Source: {source}")
        if source != 'publicwww_api':
            print("  ⚠ Warning: Expected 'publicwww_api'")
        else:
            print("  ✓ Correct source")
        
        timestamp = latest_doc.get('ingestion_timestamp')
        print(f"Ingestion Timestamp: {timestamp}")
        if timestamp:
            print("  ✓ Timestamp present")
        else:
            print("  ❌ Missing timestamp")
        
        print("\n" + "-"*70)
        print("METADATA VERIFICATION")
        print("-"*70)
        
        metadata = latest_doc.get('metadata', {})
        
        endpoint_count = metadata.get('endpoint_count', 0)
        print(f"Endpoint Count: {endpoint_count}")
        if endpoint_count >= 5:
            print(f"  ✓ Found {endpoint_count} endpoints (minimum 5 required)")
        else:
            print(f"  ❌ Only {endpoint_count} endpoints found (need at least 5)")
        
        has_api_key = metadata.get('has_api_key', False)
        print(f"Has API Key: {has_api_key}")
        if has_api_key:
            print("  ✓ API key is being used")
        else:
            print("  ⚠ Using free tier (no API key)")
        
        summary = metadata.get('summary', {})
        total_queries = summary.get('total_queries', 0)
        successful = summary.get('successful_queries', 0)
        failed = summary.get('failed_queries', 0)
        
        print(f"\nQuery Summary:")
        print(f"  Total Queries: {total_queries}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        if successful >= 5:
            print(f"  ✓ At least 5 successful queries")
        else:
            print(f"  ❌ Only {successful} successful queries")
        
        print("\n" + "-"*70)
        print("RAW DATA VERIFICATION")
        print("-"*70)
        
        raw_data = latest_doc.get('raw_data', {})
        endpoints = raw_data.get('endpoints', [])
        
        print(f"Number of endpoints in raw_data: {len(endpoints)}")
        
        if len(endpoints) == 0:
            print("  ❌ No endpoint data found!")
            return False
        
        print("\nDetailed Endpoint Analysis:")
        print("-"*70)
        
        for i, endpoint in enumerate(endpoints, 1):
            query = endpoint.get('query', 'Unknown')
            endpoint_type = endpoint.get('endpoint', 'Unknown')
            has_data = 'data' in endpoint
            has_error = 'error' in endpoint
            
            print(f"\n[{i}] Query: {query}")
            print(f"    Type: {endpoint_type}")
            
            if has_error:
                error = endpoint.get('error')
                print(f"    ❌ Error: {error}")
            elif has_data:
                data = endpoint.get('data', {})
                
                if data is None:
                    print(f"    ❌ Data is None")
                elif isinstance(data, dict):
                    content_type = data.get('content_type', 'unknown')
                    print(f"    Content Type: {content_type}")
                    
                    if content_type == 'html':
                        html_length = data.get('full_length', 0)
                        preview_length = len(data.get('html_content', ''))
                        print(f"    Full Length: {html_length} chars")
                        print(f"    Preview Length: {preview_length} chars")
                        
                        if html_length > 0:
                            print(f"    ✓ Data extracted successfully")
                        else:
                            print(f"    ⚠ No HTML content")
                    else:
                        print(f"    Data keys: {list(data.keys())}")
                        print(f"    ✓ Data present")
                else:
                    print(f"    ⚠ Unexpected data type: {type(data)}")
            else:
                print(f"    ❌ No data or error field")
        
     
        print("\n" + "="*70)
        print("FINAL VERIFICATION SUMMARY")
        print("="*70)
        
        checks_passed = 0
        total_checks = 5
        
        
        if doc_count > 0:
            print("✓ [1/5] Documents exist in collection")
            checks_passed += 1
        else:
            print("❌ [1/5] No documents in collection")
        
        if metadata:
            print("✓ [2/5] Metadata structure present")
            checks_passed += 1
        else:
            print("❌ [2/5] Missing metadata")
        
       
        if endpoint_count >= 5:
            print(f"✓ [3/5] Has {endpoint_count} endpoints (minimum 5)")
            checks_passed += 1
        else:
            print(f"❌ [3/5] Only {endpoint_count} endpoints (need 5)")
        
        
        if successful >= 5:
            print(f"✓ [4/5] {successful} successful queries")
            checks_passed += 1
        else:
            print(f"❌ [4/5] Only {successful} successful queries")
        
        
        endpoints_with_data = sum(1 for ep in endpoints if 'data' in ep and ep['data'])
        if endpoints_with_data >= 5:
            print(f"✓ [5/5] {endpoints_with_data} endpoints have data")
            checks_passed += 1
        else:
            print(f"❌ [5/5] Only {endpoints_with_data} endpoints have data")
        
        print("\n" + "="*70)
        print(f"RESULT: {checks_passed}/{total_checks} checks passed")
        
        if checks_passed == total_checks:
            print("🎉 ALL CHECKS PASSED! Data extraction is working correctly!")
            print("="*70 + "\n")
            return True
        elif checks_passed >= 3:
            print("⚠ PARTIAL SUCCESS: Some issues detected but core functionality works")
            print("="*70 + "\n")
            return True
        else:
            print("❌ FAILED: Multiple issues detected. Please review the ETL pipeline.")
            print("="*70 + "\n")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    verify_extraction()