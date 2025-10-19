"""
Cloudflare ETL Data Connector
Author: Rithika S
Roll Number: 3122225001705
Assignment: ETL2 - Cloudflare Trace API Integration

This script extracts data from three Cloudflare endpoints, transforms it,
and loads it into MongoDB for further analysis.
"""

import os
import requests
import json
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv()


class CloudflareETLConnector:
    """
    ETL Connector for Cloudflare API endpoints
    Extracts data from multiple Cloudflare endpoints, transforms it,
    and loads it into MongoDB
    """

    def __init__(self):
        """Initialize the connector with MongoDB connection and API settings"""
        # MongoDB Configuration
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'cloudflare_etl_db')
        self.collection_name = os.getenv('COLLECTION_NAME', 'cloudflare_trace_raw')
        
        # Cloudflare API Configuration (optional for authenticated endpoints)
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.email = os.getenv('CLOUDFLARE_EMAIL')
        
        # Initialize MongoDB client
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            # Test connection
            self.client.server_info()
            print(f"✓ Successfully connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {str(e)}")
            sys.exit(1)

        # Define API Endpoints
        self.endpoints = {
            'trace': {
                'url': 'https://www.cloudflare.com/cdn-cgi/trace',
                'method': 'GET',
                'description': 'Cloudflare Trace - Returns client IP, location, and connection info'
            },
            'trace_alternate': {
                'url': 'https://1.1.1.1/cdn-cgi/trace',
                'method': 'GET',
                'description': 'Cloudflare DNS Trace - Returns trace info via 1.1.1.1'
            },
            'ipinfo': {
                'url': 'https://cloudflare.com/cdn-cgi/trace',
                'method': 'GET',
                'description': 'Cloudflare IP Information - Returns detailed connection metadata'
            }
        }

    def extract_trace_endpoint(self, endpoint_name):
        """
        Extract data from a Cloudflare trace endpoint
        
        Args:
            endpoint_name (str): Name of the endpoint to call
            
        Returns:
            dict: Extracted data from the endpoint
        """
        endpoint = self.endpoints.get(endpoint_name)
        if not endpoint:
            raise ValueError(f"Endpoint '{endpoint_name}' not found")

        try:
            print(f"\n→ Extracting data from {endpoint_name}...")
            print(f"  URL: {endpoint['url']}")
            
            response = requests.get(
                endpoint['url'],
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (ETL Connector)'}
            )
            
            response.raise_for_status()
            
            # Parse the trace response (key=value format)
            data = {}
            for line in response.text.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    data[key.strip()] = value.strip()
            
            print(f"✓ Successfully extracted {len(data)} fields from {endpoint_name}")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error extracting from {endpoint_name}: {str(e)}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return None

    def extract_all_endpoints(self):
        """
        Extract data from all configured endpoints
        
        Returns:
            dict: Dictionary containing data from all endpoints
        """
        print("\n" + "="*70)
        print("EXTRACTION PHASE - Fetching data from Cloudflare endpoints")
        print("="*70)
        
        extracted_data = {}
        
        for endpoint_name in self.endpoints.keys():
            data = self.extract_trace_endpoint(endpoint_name)
            if data:
                extracted_data[endpoint_name] = data
            # Rate limiting - be respectful to the API
            time.sleep(1)
        
        print(f"\n✓ Extraction complete: {len(extracted_data)}/{len(self.endpoints)} endpoints successful")
        return extracted_data

    def transform_data(self, raw_data):
        """
        Transform the raw data from Cloudflare endpoints
        
        Args:
            raw_data (dict): Raw data from all endpoints
            
        Returns:
            dict: Transformed data ready for MongoDB insertion
        """
        print("\n" + "="*70)
        print("TRANSFORMATION PHASE - Processing and cleaning data")
        print("="*70)
        
        try:
            transformed_document = {
                'ingestion_timestamp': datetime.utcnow(),
                'ingestion_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'source': 'Cloudflare API',
                'endpoints_data': {},
                'metadata': {
                    'total_endpoints': len(raw_data),
                    'connector_version': '1.0',
                    'student_name': 'Rithika S',
                    'roll_number': '3122225001705'
                }
            }
            
            # Transform each endpoint's data
            for endpoint_name, data in raw_data.items():
                print(f"\n→ Transforming data from {endpoint_name}...")
                
                transformed_endpoint_data = {
                    'endpoint_name': endpoint_name,
                    'endpoint_url': self.endpoints[endpoint_name]['url'],
                    'raw_data': data,
                    'processed_data': self._process_trace_data(data)
                }
                
                transformed_document['endpoints_data'][endpoint_name] = transformed_endpoint_data
                print(f"✓ Transformed {endpoint_name} data")
            
            # Add aggregated information
            transformed_document['aggregated_info'] = self._aggregate_data(raw_data)
            
            print(f"\n✓ Transformation complete: Document ready for MongoDB")
            return transformed_document
            
        except Exception as e:
            print(f"✗ Error during transformation: {str(e)}")
            return None

    def _process_trace_data(self, data):
        """
        Process individual trace data with type conversions and enrichment
        
        Args:
            data (dict): Raw trace data
            
        Returns:
            dict: Processed data with proper types and enrichment
        """
        processed = {}
        
        # Known numeric fields
        numeric_fields = ['visit_scheme', 'http', 'tls']
        
        for key, value in data.items():
            # Convert numeric fields
            if key in numeric_fields:
                try:
                    processed[key] = int(value)
                except ValueError:
                    processed[key] = value
            # Keep other fields as strings
            else:
                processed[key] = value
        
        # Add enriched fields
        if 'loc' in data:
            processed['location_code'] = data['loc']
            processed['location_description'] = f"Data center location: {data['loc']}"
        
        if 'ip' in data:
            processed['client_ip'] = data['ip']
            # Determine IP version
            processed['ip_version'] = 'IPv6' if ':' in data['ip'] else 'IPv4'
        
        return processed

    def _aggregate_data(self, raw_data):
        """
        Aggregate data from multiple endpoints
        
        Args:
            raw_data (dict): Raw data from all endpoints
            
        Returns:
            dict: Aggregated information
        """
        aggregated = {
            'unique_ips': set(),
            'locations': set(),
            'common_fields': {}
        }
        
        # Collect unique values across endpoints
        for endpoint_data in raw_data.values():
            if 'ip' in endpoint_data:
                aggregated['unique_ips'].add(endpoint_data['ip'])
            if 'loc' in endpoint_data:
                aggregated['locations'].add(endpoint_data['loc'])
        
        # Convert sets to lists for MongoDB compatibility
        return {
            'unique_ips': list(aggregated['unique_ips']),
            'locations': list(aggregated['locations']),
            'total_unique_ips': len(aggregated['unique_ips']),
            'total_locations': len(aggregated['locations'])
        }

    def load_to_mongodb(self, transformed_data):
        """
        Load transformed data into MongoDB
        
        Args:
            transformed_data (dict): Transformed data to insert
            
        Returns:
            bool: Success status
        """
        print("\n" + "="*70)
        print("LOAD PHASE - Inserting data into MongoDB")
        print("="*70)
        
        try:
            if not transformed_data:
                print("✗ No data to load")
                return False
            
            print(f"\n→ Inserting document into collection: {self.collection_name}")
            
            # Insert the document
            result = self.collection.insert_one(transformed_data)
            
            print(f"✓ Successfully inserted document")
            print(f"  Document ID: {result.inserted_id}")
            print(f"  Collection: {self.collection_name}")
            print(f"  Database: {self.database_name}")
            
            # Display summary
            self._display_summary(transformed_data)
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading data to MongoDB: {str(e)}")
            return False

    def _display_summary(self, data):
        """Display a summary of the loaded data"""
        print("\n" + "-"*70)
        print("DATA SUMMARY")
        print("-"*70)
        print(f"Ingestion Time: {data['ingestion_timestamp']}")
        print(f"Total Endpoints: {data['metadata']['total_endpoints']}")
        print(f"Unique IPs: {data['aggregated_info']['total_unique_ips']}")
        print(f"Locations: {', '.join(data['aggregated_info']['locations'])}")
        print("-"*70)

    def run_etl_pipeline(self):
        """
        Execute the complete ETL pipeline
        Extract → Transform → Load
        """
        print("\n" + "="*70)
        print("CLOUDFLARE ETL PIPELINE - STARTING")
        print("="*70)
        print(f"Student: Rithika S (3122225001705)")
        print(f"Assignment: ETL2 - Cloudflare Trace")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            # EXTRACT
            raw_data = self.extract_all_endpoints()
            
            if not raw_data:
                print("\n✗ Extraction failed - No data retrieved")
                return False
            
            # TRANSFORM
            transformed_data = self.transform_data(raw_data)
            
            if not transformed_data:
                print("\n✗ Transformation failed")
                return False
            
            # LOAD
            success = self.load_to_mongodb(transformed_data)
            
            if success:
                print("\n" + "="*70)
                print("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
                print("="*70)
                return True
            else:
                print("\n✗ ETL Pipeline failed at Load phase")
                return False
                
        except Exception as e:
            print(f"\n✗ ETL Pipeline failed: {str(e)}")
            return False
        finally:
            self.close_connection()

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("\n✓ MongoDB connection closed")

    def validate_data(self):
        """
        Validate the data in MongoDB collection
        """
        print("\n" + "="*70)
        print("DATA VALIDATION")
        print("="*70)
        
        try:
            # Count documents
            count = self.collection.count_documents({})
            print(f"\nTotal documents in collection: {count}")
            
            # Show latest document
            if count > 0:
                latest = self.collection.find_one(
                    sort=[('ingestion_timestamp', -1)]
                )
                print(f"\nLatest document details:")
                print(f"  ID: {latest['_id']}")
                print(f"  Timestamp: {latest['ingestion_timestamp']}")
                print(f"  Endpoints: {list(latest['endpoints_data'].keys())}")
                print(f"  Unique IPs: {latest['aggregated_info']['unique_ips']}")
            
            return True
            
        except Exception as e:
            print(f"✗ Validation error: {str(e)}")
            return False


def main():
    """Main execution function"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           CLOUDFLARE ETL DATA CONNECTOR                             ║
║                                                                     ║
║           Student: Rithika S (3122225001705)                        ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize and run ETL
    connector = CloudflareETLConnector()
    
    # Run the pipeline
    success = connector.run_etl_pipeline()
    
    # Validate if successful
    if success:
        connector.validate_data()
    
    # Exit with appropriate status
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

