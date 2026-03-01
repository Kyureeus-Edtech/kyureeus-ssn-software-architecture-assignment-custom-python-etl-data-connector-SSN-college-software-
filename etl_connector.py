"""
SSL Labs API ETL Pipeline
Extracts data from SSL Labs API, transforms it, and loads into MongoDB
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import Dict, List, Optional
import json

# Load environment variables
load_dotenv()

class SSLLabsETL:
    """ETL Pipeline for SSL Labs API"""
    
    def __init__(self):
        self.base_url = "https://api.ssllabs.com/api/v3"
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DATABASE")
        self.client = None
        self.db = None
        self.rate_limit_delay = 2  # seconds between requests
        
    def connect_mongodb(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            print(f"✓ Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            return False
    
    def close_mongodb(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     return_json: bool = True) -> Optional[Dict]:
        """
        Make HTTP request to SSL Labs API with error handling
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            return_json: If True, parse as JSON; if False, return text
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            print(f"→ Requesting: {endpoint}")
            response = requests.get(url, params=params, timeout=30)
            
            # Check rate limiting
            if response.status_code == 429:
                print("⚠ Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return self.make_request(endpoint, params, return_json)
            
            # Check for successful response
            if response.status_code == 200:
                print(f"✓ Success: {endpoint}")
                time.sleep(self.rate_limit_delay)  # Respect rate limits
                
                if return_json:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        print(f"⚠ Response is not JSON, returning as text")
                        return {"raw_data": response.text}
                else:
                    return response.text
            elif response.status_code == 400:
                print(f"✗ Bad request for {endpoint}: {response.text}")
                return None
            else:
                print(f"✗ Error {response.status_code}: {endpoint}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"✗ Timeout error for {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error for {endpoint}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error for {endpoint}: {e}")
            return None
    
    def transform_data(self, data: Dict, endpoint: str) -> Dict:
        """
        Transform API response for MongoDB compatibility
        """
        if data is None:
            return None
        
        # Add metadata
        transformed = {
            "endpoint": endpoint,
            "ingestion_timestamp": datetime.utcnow(),
            "data": data
        }
        
        return transformed
    
    def load_to_mongodb(self, collection_name: str, data: Dict) -> bool:
        """
        Load transformed data into MongoDB collection
        """
        if data is None:
            print(f"✗ No data to load for {collection_name}")
            return False
        
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            print(f"✓ Inserted into {collection_name}: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"✗ MongoDB insert failed for {collection_name}: {e}")
            return False
    
    # ========== ENDPOINT 1: Get API Info ==========
    def extract_info(self):
        """Extract API information and version details"""
        print("\n=== Extracting API Info ===")
        data = self.make_request("info")
        
        if data:
            transformed = self.transform_data(data, "info")
            self.load_to_mongodb("ssllabs_info_raw", transformed)
            return data
        return None
    
    # ========== ENDPOINT 2: Get Status Codes ==========
    def extract_status_codes(self):
        """Extract status codes and their meanings"""
        print("\n=== Extracting Status Codes ===")
        data = self.make_request("getStatusCodes")
        
        if data:
            transformed = self.transform_data(data, "getStatusCodes")
            self.load_to_mongodb("ssllabs_statuscodes_raw", transformed)
            return data
        return None
    
    # ========== ENDPOINT 3: Analyze Host ==========
    def extract_host_analysis(self, host: str, publish: str = "off", 
                             start_new: str = "on", all_data: str = "done"):
        """
        Analyze a specific host's SSL/TLS configuration
        
        Args:
            host: Hostname to analyze (e.g., 'www.google.com')
            publish: 'on' to publish results, 'off' to keep private
            start_new: 'on' to start new scan, 'off' to retrieve cached
            all_data: 'on' for full data, 'done' to wait for completion
        """
        print(f"\n=== Analyzing Host: {host} ===")
        
        params = {
            "host": host,
            "publish": publish,
            "startNew": start_new,
            "all": all_data
        }
        
        # Initial request
        data = self.make_request("analyze", params)
        
        if not data:
            return None
        
        # Wait for scan to complete if status is not READY or ERROR
        max_attempts = 30
        attempts = 0
        
        while data.get("status") not in ["READY", "ERROR"] and attempts < max_attempts:
            print(f"⏳ Scan in progress... Status: {data.get('status')}")
            time.sleep(10)
            params["startNew"] = "off"  # Don't start new scan, just check status
            data = self.make_request("analyze", params)
            attempts += 1
        
        if data:
            transformed = self.transform_data(data, f"analyze/{host}")
            self.load_to_mongodb("ssllabs_hostanalysis_raw", transformed)
            return data
        return None
    
    # ========== ENDPOINT 4: Get Endpoint Data ==========
    def extract_endpoint_data(self, host: str, endpoint_ip: str):
        """
        Get detailed endpoint information for a specific IP
        
        Args:
            host: Hostname
            endpoint_ip: IP address of the endpoint
        """
        print(f"\n=== Extracting Endpoint Data: {host} ({endpoint_ip}) ===")
        
        params = {
            "host": host,
            "s": endpoint_ip
        }
        
        data = self.make_request("getEndpointData", params)
        
        if data:
            transformed = self.transform_data(data, f"getEndpointData/{host}/{endpoint_ip}")
            self.load_to_mongodb("ssllabs_endpointdata_raw", transformed)
            return data
        return None
    
    # ========== ENDPOINT 5: Get Root Certificates ==========
    def extract_root_certificates(self):
        """Extract list of root certificates trusted by SSL Labs"""
        print("\n=== Extracting Root Certificates ===")
        
        # Try the trustStore endpoint instead (returns JSON)
        data = self.make_request("getRootCertsRaw", return_json=False)
        
        if data:
            # Parse the certificate data
            cert_count = data.count("-----BEGIN CERTIFICATE-----")
            print(f"  Found {cert_count} certificates")
            
            # Store as structured data
            structured_data = {
                "certificate_count": cert_count,
                "raw_certificates": data,
                "certificates": []
            }
            
            # Split individual certificates
            certs = data.split("-----BEGIN CERTIFICATE-----")
            for i, cert in enumerate(certs[1:], 1):  # Skip first empty split
                if "-----END CERTIFICATE-----" in cert:
                    cert_data = "-----BEGIN CERTIFICATE-----" + cert.split("-----END CERTIFICATE-----")[0] + "-----END CERTIFICATE-----"
                    structured_data["certificates"].append({
                        "index": i,
                        "certificate": cert_data.strip()
                    })
            
            transformed = self.transform_data(structured_data, "getRootCertsRaw")
            self.load_to_mongodb("ssllabs_rootcerts_raw", transformed)
            return structured_data
        
        # Fallback: Try alternative endpoint for cert info
        print("  Trying alternative endpoint: /getRootCertsRaw with trustStore param")
        alt_data = self.make_request("getRootCertsRaw", params={"trustStore": "1"}, return_json=True)
        
        if alt_data:
            transformed = self.transform_data(alt_data, "getRootCertsRaw")
            self.load_to_mongodb("ssllabs_rootcerts_raw", transformed)
            return alt_data
        
        print("⚠ Could not retrieve root certificates from any endpoint")
        return None
    
    
    def run_full_pipeline(self, test_hosts: List[str] = None):
        """
        Run the complete ETL pipeline for all endpoints
        
        Args:
            test_hosts: List of hostnames to analyze (default: ['www.google.com'])
        """
        if test_hosts is None:
            test_hosts = ['www.google.com']
        
        print("="*60)
        print("SSL LABS ETL PIPELINE STARTED")
        print("="*60)
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            print("✗ Pipeline aborted due to MongoDB connection failure")
            return
        
        try:
            # Endpoint 1: API Info (once per run)
            self.extract_info()
            
            # Endpoint 2: Status Codes (once per run)
            self.extract_status_codes()
            
            # Endpoint 5: Root Certificates (once per run)
            self.extract_root_certificates()
            
            # Process each host
            print(f"\n{'='*60}")
            print(f"Processing {len(test_hosts)} host(s)")
            print(f"{'='*60}")
            
            for idx, host in enumerate(test_hosts, 1):
                print(f"\n--- HOST {idx}/{len(test_hosts)}: {host} ---")
                
                # Endpoint 3: Host Analysis
                host_data = self.extract_host_analysis(host)
                
                # Endpoint 4: Endpoint Data (for each endpoint in host)
                if host_data and host_data.get("endpoints"):
                    endpoints = host_data["endpoints"]
                    print(f"  Found {len(endpoints)} endpoint(s) for {host}")
                    
                    for ep_idx, endpoint in enumerate(endpoints, 1):
                        endpoint_ip = endpoint.get("ipAddress")
                        if endpoint_ip:
                            print(f"  Processing endpoint {ep_idx}/{len(endpoints)}: {endpoint_ip}")
                            self.extract_endpoint_data(host, endpoint_ip)
                        else:
                            print(f"  ⚠ No IP address for endpoint {ep_idx}")
                else:
                    print(f"  ⚠ No endpoints found for {host}")
            
            print("\n" + "="*60)
            print("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            
            # Print summary
            self._print_summary(test_hosts)
            
        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
        finally:
            self.close_mongodb()
    
    def _print_summary(self, test_hosts: List[str]):
        """Print execution summary"""
        print("\n📊 EXECUTION SUMMARY:")
        print(f"  Hosts analyzed: {len(test_hosts)}")
        print(f"  Hosts: {', '.join(test_hosts)}")
        print(f"\n  Per-host data collected:")
        print(f"    - Host Analyses: {len(test_hosts)} documents")
        print(f"    - Endpoint Data: Varies by host IPs")

    
    def validate_collections(self):
        """Validate data in MongoDB collections"""
        print("\n=== Validating MongoDB Collections ===")
        
        if not self.connect_mongodb():
            return
        
        collections = [
            "ssllabs_info_raw",
            "ssllabs_statuscodes_raw",
            "ssllabs_hostanalysis_raw",
            "ssllabs_endpointdata_raw",
            "ssllabs_rootcerts_raw",
        ]
        
        for coll_name in collections:
            count = self.db[coll_name].count_documents({})
            print(f"  {coll_name}: {count} documents")
        
        self.close_mongodb()


def main():
    """Main execution function"""
    
    # Initialize ETL pipeline
    etl = SSLLabsETL()
    
    # Define hosts to analyze (you can add more)
    test_hosts = [
        'www.google.com',
        'github.com'
    ]
    
    # Run full pipeline
    etl.run_full_pipeline(test_hosts=test_hosts)
    
    # Validate results
    etl.validate_collections()


if __name__ == "__main__":
    main()