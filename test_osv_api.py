#!/usr/bin/env python3
"""
Test script for OSV API connectivity
"""

import requests
import json

def test_osv_api():
    print("Testing OSV API connectivity...")
    
    # Test 1: Query API
    print("\n1. Testing OSV Query API...")
    query_data = {
        "package": {
            "name": "numpy",
            "ecosystem": "PyPI"
        }
    }
    
    try:
        response = requests.post('https://api.osv.dev/v1/query', json=query_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            vulns = result.get('vulns', [])
            print(f"Found {len(vulns)} vulnerabilities for numpy")
            if vulns:
                print(f"Sample vulnerability ID: {vulns[0].get('id', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Query API test failed: {e}")
    
    # Test 2: Get a real vulnerability
    print("\n2. Testing OSV Vulnerability API...")
    try:
        # First get a real vulnerability ID from numpy query
        response = requests.post('https://api.osv.dev/v1/query', json=query_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            vulns = result.get('vulns', [])
            if vulns:
                vuln_id = vulns[0].get('id')
                print(f"Testing with vulnerability ID: {vuln_id}")
                
                # Now get details for this vulnerability
                vuln_response = requests.get(f'https://api.osv.dev/v1/vulns/{vuln_id}', timeout=10)
                print(f"Vulnerability details status: {vuln_response.status_code}")
                if vuln_response.status_code == 200:
                    vuln_details = vuln_response.json()
                    print(f"Vulnerability summary: {vuln_details.get('summary', 'N/A')[:100]}...")
    except Exception as e:
        print(f"Vulnerability API test failed: {e}")
    
    # Test 3: Batch query
    print("\n3. Testing OSV Batch Query API...")
    batch_data = {
        "queries": [
            {"package": {"name": "numpy", "ecosystem": "PyPI"}},
            {"package": {"name": "requests", "ecosystem": "PyPI"}}
        ]
    }
    
    try:
        response = requests.post('https://api.osv.dev/v1/querybatch', json=batch_data, timeout=10)
        print(f"Batch query status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            batch_results = result.get('results', [])
            print(f"Batch query returned {len(batch_results)} result sets")
            total_vulns = sum(len(r.get('vulns', [])) for r in batch_results)
            print(f"Total vulnerabilities found: {total_vulns}")
    except Exception as e:
        print(f"Batch API test failed: {e}")

if __name__ == "__main__":
    test_osv_api()