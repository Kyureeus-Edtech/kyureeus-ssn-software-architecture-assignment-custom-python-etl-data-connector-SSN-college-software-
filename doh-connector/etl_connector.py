"""
DNS over HTTPS (DoH) ETL Connector using AdGuard DNS
Extracts DNS data from AdGuard DoH API, transforms it, and loads into MongoDB

Author: Shankari S R
Roll Number: 3122225001125
Date: October 19, 2025

API: AdGuard DNS - Free DNS over HTTPS API
No authentication required
"""

import os
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
import time

# Load environment variables
load_dotenv()

# Configuration
ADGUARD_DNS_BASE_URL = "https://dns.adguard-dns.com/resolve"
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "dns_etl_db")
COLLECTION_NAME = "adguard_dns_raw"

# DNS Record Types for three different endpoints
DNS_QUERIES = [
    {"name": "google.com", "type": "A", "description": "IPv4 Address Record"},
    {"name": "google.com", "type": "AAAA", "description": "IPv6 Address Record"},
    {"name": "google.com", "type": "MX", "description": "Mail Exchange Record"}
]


class AdGuardDNSETLConnector:
    """ETL Connector for AdGuard DNS over HTTPS API"""
    
    def __init__(self):
        """Initialize MongoDB connection and setup"""
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[MONGODB_DB]
            self.collection = self.db[COLLECTION_NAME]
            print(f"✓ Connected to MongoDB: {MONGODB_DB}.{COLLECTION_NAME}")
            print(f"✓ Using DNS Provider: AdGuard DNS over HTTPS")
            print(f"✓ Base URL: {ADGUARD_DNS_BASE_URL}")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
    
    def extract(self, domain, record_type, retry_count=3):
        """
        Extract DNS data from AdGuard DoH API
        
        Args:
            domain (str): Domain name to query
            record_type (str): DNS record type (A, AAAA, MX, etc.)
            retry_count (int): Number of retries on failure
            
        Returns:
            dict: JSON response from API or None if failed
        """
        headers = {
            "Accept": "application/dns-json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        params = {
            "name": domain,
            "type": record_type
        }
        
        for attempt in range(retry_count):
            try:
                print(f"\n[EXTRACT] Querying {record_type} record for {domain}... (Attempt {attempt + 1}/{retry_count})")
                
                response = requests.get(
                    ADGUARD_DNS_BASE_URL,
                    headers=headers,
                    params=params,
                    timeout=20
                )
                
                # Check rate limits
                if response.status_code == 429:
                    print(f"✗ Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                # Check if we got valid DNS response
                answer_count = len(data.get("Answer", []))
                print(f"✓ Successfully extracted {record_type} record data")
                print(f"  Response Status: {data.get('Status', 'Unknown')}")
                print(f"  Answers Received: {answer_count}")
                
                return data
                
            except requests.exceptions.Timeout as e:
                print(f"✗ Timeout error (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
            except requests.exceptions.ConnectionError as e:
                print(f"✗ Connection error: {e}")
                if attempt < retry_count - 1:
                    print(f"  Retrying...")
                    time.sleep(3)
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ API request failed: {e}")
                return None
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON parsing failed: {e}")
                return None
        
        print(f"✗ All retry attempts failed for {record_type} record")
        return None
    
    def transform(self, raw_data, query_info):
        """
        Transform raw DNS data for MongoDB storage
        
        Args:
            raw_data (dict): Raw API response
            query_info (dict): Original query information
            
        Returns:
            dict: Transformed document ready for MongoDB
        """
        if not raw_data:
            return None
        
        print(f"[TRANSFORM] Processing {query_info['type']} record data...")
        
        # Extract relevant fields
        transformed = {
            "ingestion_timestamp": datetime.now(timezone.utc),
            "dns_provider": "AdGuard DNS",
            "query": {
                "domain": query_info["name"],
                "record_type": query_info["type"],
                "record_description": query_info["description"],
                "query_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "response": {
                "status": raw_data.get("Status", None),
                "status_description": self._get_status_description(raw_data.get("Status")),
                "truncated": raw_data.get("TC", False),
                "recursion_desired": raw_data.get("RD", True),
                "recursion_available": raw_data.get("RA", True),
                "authenticated_data": raw_data.get("AD", False),
                "checking_disabled": raw_data.get("CD", False)
            },
            "answers": [],
            "metadata": {
                "answer_count": len(raw_data.get("Answer", [])),
                "authority_count": len(raw_data.get("Authority", [])),
                "additional_count": len(raw_data.get("Additional", [])),
                "question_count": len(raw_data.get("Question", []))
            }
        }
        
        # Transform answer records
        for answer in raw_data.get("Answer", []):
            transformed_answer = {
                "name": answer.get("name"),
                "type": answer.get("type"),
                "type_name": self._get_record_type_name(answer.get("type")),
                "ttl": answer.get("TTL"),
                "data": answer.get("data")
            }
            
            # Add priority for MX records
            if answer.get("priority") is not None:
                transformed_answer["priority"] = answer.get("priority")
            
            transformed["answers"].append(transformed_answer)
        
        # Add question section
        if raw_data.get("Question"):
            transformed["question"] = [
                {
                    "name": q.get("name"),
                    "type": q.get("type"),
                    "type_name": self._get_record_type_name(q.get("type"))
                }
                for q in raw_data.get("Question", [])
            ]
        
        # Add authority records if present
        if raw_data.get("Authority"):
            transformed["authority"] = [
                {
                    "name": auth.get("name"),
                    "type": auth.get("type"),
                    "type_name": self._get_record_type_name(auth.get("type")),
                    "ttl": auth.get("TTL"),
                    "data": auth.get("data")
                }
                for auth in raw_data.get("Authority", [])
            ]
        
        # Add additional records if present
        if raw_data.get("Additional"):
            transformed["additional"] = [
                {
                    "name": add.get("name"),
                    "type": add.get("type"),
                    "type_name": self._get_record_type_name(add.get("type")),
                    "ttl": add.get("TTL"),
                    "data": add.get("data")
                }
                for add in raw_data.get("Additional", [])
            ]
        
        # Store raw response for reference
        transformed["raw_response"] = raw_data
        
        print(f"✓ Transformation complete - {len(transformed['answers'])} answers processed")
        return transformed
    
    def _get_status_description(self, status_code):
        """Map DNS status codes to descriptions"""
        status_map = {
            0: "NOERROR - No error condition",
            1: "FORMERR - Format error",
            2: "SERVFAIL - Server failure",
            3: "NXDOMAIN - Non-existent domain",
            4: "NOTIMP - Not implemented",
            5: "REFUSED - Query refused"
        }
        return status_map.get(status_code, f"Unknown status: {status_code}")
    
    def _get_record_type_name(self, type_code):
        """Map DNS record type codes to names"""
        type_map = {
            1: "A",
            2: "NS",
            5: "CNAME",
            6: "SOA",
            15: "MX",
            16: "TXT",
            28: "AAAA",
            33: "SRV"
        }
        return type_map.get(type_code, f"TYPE{type_code}")
    
    def load(self, transformed_data):
        """
        Load transformed data into MongoDB
        
        Args:
            transformed_data (dict): Transformed document
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not transformed_data:
            print("✗ No data to load")
            return False
        
        try:
            print(f"[LOAD] Inserting into MongoDB collection: {COLLECTION_NAME}")
            result = self.collection.insert_one(transformed_data)
            print(f"✓ Document inserted with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"✗ MongoDB insert failed: {e}")
            return False
    
    def test_connectivity(self):
        """Test AdGuard DNS API connectivity"""
        print("\n[TEST] Testing AdGuard DNS API connectivity...")
        
        try:
            response = requests.get(
                ADGUARD_DNS_BASE_URL,
                params={"name": "example.com", "type": "A"},
                headers={"Accept": "application/dns-json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ AdGuard DNS API is reachable (Status: {response.status_code})")
                print(f"  Test query successful - Status: {data.get('Status', 'Unknown')}")
                return True
            else:
                print(f"✗ AdGuard DNS API returned status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ AdGuard DNS API unreachable: {e}")
            return False
    
    def run_etl(self):
        """Execute complete ETL pipeline for all DNS query types"""
        print("=" * 70)
        print("DNS over HTTPS ETL Pipeline - Starting")
        print("=" * 70)
        
        # Test connectivity first
        if not self.test_connectivity():
            print("\n⚠️  WARNING: AdGuard DNS API connectivity test failed")
            print("   Proceeding with queries anyway...\n")
        
        success_count = 0
        failure_count = 0
        
        for query in DNS_QUERIES:
            print(f"\n{'=' * 70}")
            print(f"Processing Query: {query['name']} - Type: {query['type']} ({query['description']})")
            print(f"{'=' * 70}")
            
            # EXTRACT
            raw_data = self.extract(query["name"], query["type"])
            if not raw_data:
                failure_count += 1
                print(f"✗ ETL failed for {query['type']} record")
                continue
            
            # TRANSFORM
            transformed_data = self.transform(raw_data, query)
            if not transformed_data:
                failure_count += 1
                print(f"✗ ETL failed for {query['type']} record")
                continue
            
            # LOAD
            if self.load(transformed_data):
                success_count += 1
                print(f"✓ ETL completed successfully for {query['type']} record")
            else:
                failure_count += 1
                print(f"✗ ETL failed for {query['type']} record")
            
            # Rate limiting courtesy delay
            time.sleep(2)
        
        # Summary
        print(f"\n{'=' * 70}")
        print(f"ETL Pipeline Summary")
        print(f"{'=' * 70}")
        print(f"DNS Provider: AdGuard DNS over HTTPS")
        print(f"Total queries processed: {len(DNS_QUERIES)}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {failure_count}")
        
        if success_count > 0:
            print(f"\n✓ Pipeline completed successfully!")
            print(f"  Check MongoDB collection '{COLLECTION_NAME}' for results")
            print(f"\n📊 Verify Data:")
            print(f"  mongosh")
            print(f"  use {MONGODB_DB}")
            print(f"  db.{COLLECTION_NAME}.find().pretty()")
        
        if failure_count > 0:
            print(f"\n⚠️  Some queries failed. Troubleshooting tips:")
            print(f"   1. Check your internet connection")
            print(f"   2. Verify firewall settings")
            print(f"   3. Try the test URL in browser: {ADGUARD_DNS_BASE_URL}?name=google.com&type=A")
        
        print(f"{'=' * 70}")
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("\n✓ MongoDB connection closed")


def main():
    """Main execution function"""
    connector = None
    try:
        connector = AdGuardDNSETLConnector()
        connector.run_etl()
    except KeyboardInterrupt:
        print("\n\n✗ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if connector:
            connector.close()


if __name__ == "__main__":
    main()