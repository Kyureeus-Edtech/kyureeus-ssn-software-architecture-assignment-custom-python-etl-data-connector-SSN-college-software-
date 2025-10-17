import os
import time
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()

BASE_URL = "https://api.ssllabs.com/api/v4"
EMAIL = os.getenv("EMAIL")  # registered email
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "ssl_labs"
COLLECTION_NAME = "ssl_raw"

# Domains to process
domains = [
    "google.com",
    "wikipedia.org",
    "stackoverflow.com",
    "github.com",
    "mozilla.org",
    "python.org",
    "linkedin.com",
    "amazon.com"
]

# MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Test connection
    client.server_info()
    print(" MongoDB connection established")
except PyMongoError as e:
    print(f"MongoDB connection failed: {e}")
    exit(1)


def validate_environment():
    """Validate required environment variables."""
    if not EMAIL:
        print("ERROR: EMAIL environment variable not set")
        print("    Please add EMAIL=your_email@organization.com to .env file")
        exit(1)
    
    if "@" not in EMAIL or "." not in EMAIL:
        print(f"ERROR: Invalid email format: {EMAIL}")
        exit(1)
    
    # Check for public email services
    public_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    email_domain = EMAIL.split("@")[1].lower()
    if email_domain in public_domains:
        print(f" WARNING: SSL Labs API does not accept {email_domain} addresses")
        print("    Please use an organization email")
    
    print(f" Using email: {EMAIL}")


def register_email(first_name, last_name, org_name):
    """Register email with SSL Labs API (only once)."""
    register_url = f"{BASE_URL}/register"
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "email": EMAIL,
        "organization": org_name
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(register_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            print(" Email registered successfully")
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print(f" Using registered email: {EMAIL}")
        elif response.status_code == 441:
            print(f"Unauthorized: Email not registered properly")
            print(f"    Response: {response.text}")
        else:
            print(f"Registration failed ({response.status_code}): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f" Registration connection error: {e}")


def get_info():
    """Get SSL Labs server info."""
    try:
        response = requests.get(f"{BASE_URL}/info", timeout=15)
        
        if response.status_code == 200:
            info = response.json()
            print(f" SSL Labs engine: {info.get('engineVersion')}")
            print(f" Max concurrent assessments: {info.get('maxAssessments')}")
            print(f" Current assessments: {info.get('currentAssessments')}")
            return info
        else:
            print(f" Failed to fetch info ({response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f" Connection error while fetching info: {e}")
        return None


def handle_rate_limit(status_code, domain):
    """Handle rate limiting and service unavailability."""
    if status_code == 429:
        print(f" Rate limit exceeded for {domain}")
        print("    Too many concurrent assessments or requests too fast")
        print("    Waiting 60 seconds before retry...")
        time.sleep(60)
        return True
    elif status_code == 529:
        print(f" Service overloaded for {domain}")
        print("    Waiting 15 minutes (900s) before retry...")
        time.sleep(900)
        return True
    elif status_code == 503:
        print(f" Service unavailable for {domain}")
        print("    May be down for maintenance")
        print("    Waiting 15 minutes (900s) before retry...")
        time.sleep(900)
        return True
    elif status_code == 441:
        print(f"Unauthorized for {domain} - Email not registered")
        return False
    
    return False


def analyze_domain(domain, max_retries=3):
    """Analyze domain until ready, return JSON data."""
    analyze_url = f"{BASE_URL}/analyze"
    headers = {"email": EMAIL}
    params = {"host": domain, "startNew": "on", "all": "done"}
    first_call = True
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(analyze_url, headers=headers, params=params, timeout=30)
            
            # Handle rate limiting and service issues
            if handle_rate_limit(response.status_code, domain):
                retry_count += 1
                continue
            
            if response.status_code != 200:
                print(f"Failed to analyze {domain} ({response.status_code}): {response.text}")
                return None
            
            data = response.json()
            
            # Validate response structure
            if not isinstance(data, dict):
                print(f"Invalid response format for {domain}")
                return None
            
            status = data.get("status", "")
            
            if status in ["READY", "ERROR"]:
                if status == "ERROR":
                    error_msg = data.get("statusMessage", "Unknown error")
                    print(f"Analysis error for {domain}: {error_msg}")
                    return None
                
                # Validate that we have endpoints
                if "endpoints" not in data or not data["endpoints"]:
                    print(f" Warning: No endpoints found for {domain}")
                
                return data
            
            print(f"→ {domain}: status = {status}, waiting 10s...")
            time.sleep(10)
            
            if first_call:
                params.pop("startNew", None)
                first_call = False
        
        except requests.exceptions.Timeout:
            print(f" Timeout error for {domain}, retrying...")
            retry_count += 1
            time.sleep(5)
            
        except requests.exceptions.RequestException as e:
            print(f" Connection error for {domain}: {e}")
            retry_count += 1
            time.sleep(10)
        
        except ValueError as e:
            print(f" JSON parsing error for {domain}: {e}")
            return None
    
    print(f"Max retries ({max_retries}) reached for {domain}")
    return None


def fetch_endpoint_data(domain, endpoints):
    """Fetch detailed endpoint info for each IP."""
    if not endpoints:
        print(f" No endpoints to fetch for {domain}")
        return []
    
    headers = {"email": EMAIL}
    detailed = []
    
    for ep in endpoints:
        ip = ep.get("ipAddress")
        if not ip:
            print(f" Endpoint missing IP address for {domain}")
            continue
        
        try:
            resp = requests.get(
                f"{BASE_URL}/getEndpointData",
                headers=headers,
                params={"host": domain, "s": ip},
                timeout=20
            )
            
            if resp.status_code == 200:
                endpoint_data = resp.json()
                if isinstance(endpoint_data, dict):
                    detailed.append(endpoint_data)
                else:
                    print(f" Invalid endpoint data format for {ip}")
            else:
                print(f" Failed to fetch endpoint {ip} ({resp.status_code}): {resp.text}")
                
        except requests.exceptions.RequestException as e:
            print(f" Connection error for endpoint {ip}: {e}")
        except ValueError as e:
            print(f" JSON parsing error for endpoint {ip}: {e}")
    
    return detailed


def transform_and_load(domain, data):
    """Transform and insert into MongoDB."""
    if not data:
        print(f" No data to insert for {domain}")
        return False
    
    # Validate essential fields exist
    if "status" not in data:
        print(f" Invalid data structure for {domain} - missing status field")
        return False
    
    if "endpoints" not in data:
        print(f" Invalid data structure for {domain} - missing endpoints field")
        return False
    
    # Create record with metadata
    record = {
        "domain": domain,
        "status": data.get("status"),
        "data": data,
        "ingestion_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ingestion_timestamp": int(time.time())
    }
    
    try:
        result = collection.insert_one(record)
        print(f" Data inserted for {domain} (ID: {result.inserted_id})")
        
        # Human-readable summary
        print(f"\nSUMMARY {domain}")
        endpoints = data.get("endpoints", [])
        
        if not endpoints:
            print("No endpoints available")
        else:
            for ep in endpoints:
                ip = ep.get("ipAddress", "N/A")
                grade = ep.get("grade", "N/A")
                status = ep.get("statusMessage", "N/A")
                print(f"IP: {ip} | Grade: {grade} | Status: {status}")
        
        print("------------------------\n")
        return True
        
    except PyMongoError as e:
        print(f"MongoDB insertion failed for {domain}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during insertion for {domain}: {e}")
        return False


def print_statistics(successful, failed, total):
    """Print final statistics."""
    print("\n" + "="*50)
    print("=== ETL Pipeline Completed ===")
    print("="*50)
    print(f"Total domains processed: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"MongoDB collection: {DB_NAME}.{COLLECTION_NAME}")
    print(f"Total documents in collection: {collection.count_documents({})}")
    print("="*50 + "\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("SSL Labs API - ETL Pipeline")
    print("="*50 + "\n")
    
    # Validate environment
    validate_environment()
    
    # Register email
    register_email("Niranjana", "A", "SSN")
    
    # Get API info
    get_info()
    
    print("\n" + "="*50)
    print("Starting domain analysis...")
    print("="*50 + "\n")
    
    successful = 0
    failed = 0
    
    for domain in domains:
        print(f"\n=== Processing {domain} ===")
        
        # Extract
        result = analyze_domain(domain)
        
        if result:
            # Fetch detailed endpoint data
            endpoints_data = fetch_endpoint_data(domain, result.get("endpoints", []))
            result["endpoints_detailed"] = endpoints_data
            
            # Transform and Load
            if transform_and_load(domain, result):
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # Polite delay between domains
        if domain != domains[-1]:  # Don't wait after last domain
            print(f" Waiting 5 seconds before next domain...")
            time.sleep(5)
    
    # Print statistics
    print_statistics(successful, failed, len(domains))
    
    # Close MongoDB connection
    client.close()
    print(" MongoDB connection closed")