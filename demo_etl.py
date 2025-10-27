#!/usr/bin/env python3
"""
Demo script for OSV ETL Connector without MongoDB dependency
This demonstrates the extract and transform phases only
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from etl_connector import OSVQueryConnector, OSVVulnerabilityConnector, OSVBatchQueryConnector

def demo_extract_and_transform():
    """Demo the extract and transform phases for all three connectors."""
    print("=" * 80)
    print("OSV ETL Demo - Extract & Transform Only")
    print("Author: Janeshvar S (3122225001047)")
    print("=" * 80)
    
    connectors = [
        (OSVQueryConnector(), "OSV Query API"),
        (OSVVulnerabilityConnector(), "OSV Vulnerability API"),
        (OSVBatchQueryConnector(), "OSV Batch Query API")
    ]
    
    for connector, api_name in connectors:
        print(f"\n🚀 Testing {api_name}...")
        print("-" * 50)
        
        try:
            # Extract data
            print("📥 Extracting data...")
            raw_data = connector.extract_data()
            print(f"✅ Extracted {len(raw_data)} records")
            
            if raw_data:
                # Transform data
                print("🔄 Transforming data...")
                transformed_data = connector.transform_data(raw_data)
                print(f"✅ Transformed {len(transformed_data)} records")
                
                # Show sample record
                if transformed_data:
                    sample = transformed_data[0]
                    print(f"\n📊 Sample Record Keys:")
                    keys = list(sample.keys())
                    for i, key in enumerate(keys[:10]):  # Show first 10 keys
                        print(f"   {i+1}. {key}")
                    if len(keys) > 10:
                        print(f"   ... and {len(keys) - 10} more keys")
                    
                    # Show ETL metadata
                    etl_keys = [k for k in keys if k.startswith('_etl_')]
                    print(f"\n🏷️  ETL Metadata Fields:")
                    for key in etl_keys:
                        print(f"   {key}: {sample[key]}")
            else:
                print("⚠️  No data extracted")
                
        except Exception as e:
            print(f"❌ Error in {api_name}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("🎉 OSV ETL Demo completed!")
    print("To run with MongoDB, ensure MongoDB is running and execute: python etl_connector.py")
    print("=" * 80)

if __name__ == "__main__":
    demo_extract_and_transform()