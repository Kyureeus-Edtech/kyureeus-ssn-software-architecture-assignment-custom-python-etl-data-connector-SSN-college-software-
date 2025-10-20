import requests
import os
import time
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime, timedelta
import argparse

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# NVD API Configuration
NVD_API_KEY = os.getenv('NVD_API_KEY')
if not NVD_API_KEY:
    raise ValueError("NVD_API_KEY not found. Please add it to your .env file.")

NVD_BASE_URL = os.getenv('BASE_URL')
API_HEADERS = {'apiKey': NVD_API_KEY}

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_CONNECTION_URL')
MONGO_DB_NAME = os.getenv('DB_NAME')

# --- 1. EXTRACT ---

def fetch_nvd_data(endpoint: str, params: dict) -> list:
    """
    Fetches all results for a given NVD endpoint, handling pagination.
    """
    all_results = []
    start_index = 0
    results_per_page = 2000  # NVD max is 2000
    
    # Adjust resultsPerPage for cpematch, which has a lower limit
    if endpoint.startswith('/cpematch'):
        results_per_page = 500 # Max for cpematch is 500

    print(f"[Extract] Fetching data from: {endpoint}")

    while True:
        # Add pagination parameters to the request
        params['startIndex'] = start_index
        params['resultsPerPage'] = results_per_page
        
        try:
            response = requests.get(
                f"{NVD_BASE_URL}{endpoint}", 
                headers=API_HEADERS, 
                params=params,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            data = response.json()
            total_results = data.get('totalResults', 0)

            # Extract the correct data list based on the endpoint
            if endpoint.startswith('/cves'):
                results = data.get('vulnerabilities', [])
            elif endpoint.startswith('/cpes'):
                results = data.get('products', [])
            elif endpoint.startswith('/cpematch'):
                results = data.get('matchStrings', [])
            else:
                results = []

            if not results:
                print("[Extract] No results found or data format unrecognized.")
                break

            all_results.extend(results)
            
            print(f"[Extract] ... Fetched {len(all_results)} / {total_results} records")
            
            # Check if we have fetched all results
            start_index += len(results)
            if start_index >= total_results:
                break
            
            # Be polite to the API: wait between paged requests
            time.sleep(1) # Public APIs without a key are 6s, with a key is faster
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            break
            
    print(f"[Extract] Finished. Total records fetched: {len(all_results)}")
    return all_results

# --- 2. TRANSFORM ---

def transform_cve(cve_data: dict) -> dict:
    """
    Transforms a single CVE item for MongoDB storage.
    - Sets the CVE ID as the MongoDB '_id'
    - Converts date strings to native datetime objects
    """
    cve = cve_data.get('cve', {})
    
    # Set the MongoDB document ID to the CVE ID
    cve['_id'] = cve.get('id')
    
    # Convert date strings to datetime objects for better querying
    try:
        if 'published' in cve:
            cve['published'] = datetime.fromisoformat(cve['published'])
        if 'lastModified' in cve:
            cve['lastModified'] = datetime.fromisoformat(cve['lastModified'])
    except (ValueError, TypeError):
        print(f"Warning: Could not parse date for CVE {cve.get('id')}")
        
    return cve

def transform_cpe(cpe_data: dict) -> dict:
    """
    Transforms a single CPE item for MongoDB storage.
    - Sets the cpeNameId as the MongoDB '_id'
    - Converts date strings to native datetime objects
    """
    cpe = cpe_data.get('cpe', {})
    
    # Set the MongoDB document ID to the unique cpeNameId
    cpe['_id'] = cpe.get('cpeNameId')
    
    try:
        if 'created' in cpe:
            cpe['created'] = datetime.fromisoformat(cpe['created'])
        if 'lastModified' in cpe:
            cpe['lastModified'] = datetime.fromisoformat(cpe['lastModified'])
    except (ValueError, TypeError):
        print(f"Warning: Could not parse date for CPE {cpe.get('cpeNameId')}")
        
    return cpe

def transform_cpematch(match_data: dict) -> dict:
    """
    Transforms a single CPE Match item for MongoDB storage.
    - Sets the matchCriteriaId as the MongoDB '_id'
    - Converts date strings to native datetime objects
    """
    match = match_data.get('matchString', {})
    
    # Set the MongoDB document ID to the unique matchCriteriaId
    match['_id'] = match.get('matchCriteriaId')
    
    try:
        if 'created' in match:
            match['created'] = datetime.fromisoformat(match['created'])
        if 'lastModified' in match:
            match['lastModified'] = datetime.fromisoformat(match['lastModified'])
    except (ValueError, TypeError):
        print(f"Warning: Could not parse date for Match {match.get('matchCriteriaId')}")

    return match

# --- 3. LOAD ---

def load_to_mongo(data: list, collection_name: str, client: MongoClient):
    """
    Loads a list of transformed documents into a MongoDB collection.
    Uses 'replace_one' with 'upsert=True' to ensure idempotency:
    - If a document with the _id exists, it's updated.
    - If not, it's inserted.
    """
    if not data:
        print(f"[Load] No data to load for collection '{collection_name}'")
        return

    db = client[MONGO_DB_NAME]
    collection = db[collection_name]
    
    print(f"[Load] Loading {len(data)} records into '{collection_name}' collection...")
    
    upsert_count = 0
    modified_count = 0
    
    for doc in data:
        if '_id' not in doc:
            print(f"[Load] Skipping document without '_id': {doc}")
            continue
            
        try:
            result = collection.replace_one(
                {'_id': doc['_id']},  # The filter to find the document
                doc,                  # The new document to replace it with
                upsert=True           # Insert if it doesn't exist
            )
            if result.upserted_id:
                upsert_count += 1
            elif result.modified_count > 0:
                modified_count += 1
                
        except errors.PyMongoError as e:
            print(f"Error loading document {doc.get('_id')}: {e}")
            
    print(f"[Load] Complete. New records: {upsert_count}, Updated records: {modified_count}")

# --- MAIN EXECUTION ---

def main():
    """
    Main ETL process function.
    """
    # 1. --- Define Command-Line Arguments ---
    parser = argparse.ArgumentParser(description="ETL Connector for NVD API to MongoDB.")
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=7, 
        help="Number of days back to search for modified CVEs. Default: 7"
    )
    parser.add_argument(
        '--cpe-keyword', 
        type=str, 
        default='microsoft', 
        help="Keyword to search for in the CPE database (e.g., 'apache', 'google'). Default: microsoft"
    )
    parser.add_argument(
        '--cpe-no-exact',
        dest='cpe_exact_match',
        action='store_false',
        help="Add this flag to disable exact match for the CPE keyword (default is exact match)."
    )
    parser.add_argument(
        '--cve-id', 
        type=str, 
        default='CVE-2024-3094', 
        help="Specific CVE ID to find CPE match criteria for. Default: CVE-2024-3094 (xz backdoor)"
    )
    
    # 2. --- Parse the arguments ---
    args = parser.parse_args()

    print("--- Starting NVD ETL Connector ---")
    print(f"Running with parameters: Days={args.days}, CPE Keyword='{args.cpe_keyword}', Exact Match={args.cpe_exact_match}, Match CVE-ID='{args.cve_id}'")
    
    try:
        # Establish MongoDB connection
        mongo_client = MongoClient(MONGO_URI)
        mongo_client.server_info() # Test connection
        print(f"Successfully connected to MongoDB at {MONGO_URI}")
    except errors.ServerSelectionTimeoutError as e:
        print(f"FATAL: Could not connect to MongoDB. Is it running? Error: {e}")
        return

    # --- Process 1: CVEs ---
    print(f"\n--- Processing Endpoint 1: /cves/2.0 (Last {args.days} days) ---")
    end_date = datetime.utcnow()
    # Use the 'args.days' variable instead of the hardcoded 7
    start_date = end_date - timedelta(days=args.days) 
    
    cve_params = {
        'lastModStartDate': start_date.isoformat(),
        'lastModEndDate': end_date.isoformat()
    }
    raw_cves = fetch_nvd_data('/cves/2.0', cve_params)
    transformed_cves = [transform_cve(item) for item in raw_cves]
    load_to_mongo(transformed_cves, 'vulnerabilities', mongo_client)

    # --- Process 2: CPEs ---
    print(f"\n--- Processing Endpoint 2: /cpes/2.0 (Keyword: '{args.cpe_keyword}') ---")
    
    # Build params dictionary dynamically
    cpe_params = {
        'keywordSearch': args.cpe_keyword,
    }

    if args.cpe_exact_match:
        cpe_params['keywordExactMatch'] = None 
        
    raw_cpes = fetch_nvd_data('/cpes/2.0', cpe_params)
    transformed_cpes = [transform_cpe(item) for item in raw_cpes]
    load_to_mongo(transformed_cpes, 'products', mongo_client)

    # --- Process 3: CPE Match ---
    print(f"\n--- Processing Endpoint 3: /cpematch/2.0 (CVE ID: '{args.cve_id}') ---")
    cpematch_params = {
        # Use the 'args.cve_id' variable
        'cveId': args.cve_id
    }
    raw_matches = fetch_nvd_data('/cpematch/2.0', cpematch_params)
    transformed_matches = [transform_cpematch(item) for item in raw_matches]
    load_to_mongo(transformed_matches, 'matches', mongo_client)

    # --- Cleanup ---
    mongo_client.close()
    print("\n--- NVD ETL Process Finished Successfully ---")

if __name__ == "__main__":
    main()