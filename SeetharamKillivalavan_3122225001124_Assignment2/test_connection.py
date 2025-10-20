"""
Connection Testing Utility for RIPEstat ETL Pipeline
Student: Seetharam Killivalavan
Roll Number: 3122225001124

This script tests:
1. MongoDB connection
2. RIPEstat API connectivity
3. Environment variables configuration
4. Required Python packages

Run this BEFORE executing the main ETL pipeline to ensure everything is configured correctly.
"""

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def test_python_version():
    """Test if Python version is adequate."""
    print_info("Testing Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version: {version_str} (OK)")
        return True
    else:
        print_error(f"Python version: {version_str} (Required: 3.8+)")
        return False

def test_required_packages():
    """Test if required Python packages are installed."""
    print_info("Testing required packages...")
    
    required_packages = {
        'pymongo': 'MongoDB driver',
        'requests': 'HTTP library',
        'dotenv': 'Environment variables'
    }
    
    all_installed = True
    
    for package, description in required_packages.items():
        try:
            __import__(package if package != 'dotenv' else 'dotenv')
            print_success(f"{package}: Installed ({description})")
        except ImportError:
            print_error(f"{package}: NOT installed ({description})")
            all_installed = False
    
    if not all_installed:
        print_warning("\nInstall missing packages with: pip install -r requirements.txt")
    
    return all_installed

def test_env_file():
    """Test if .env file exists and has required variables."""
    print_info("Testing environment configuration...")
    
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print_warning("Create .env file from ENV_TEMPLATE")
        return False
    
    print_success(".env file exists")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = {
        'MONGODB_URI': 'MongoDB connection string',
        'DATABASE_NAME': 'Database name',
        'RATE_LIMIT_DELAY': 'API rate limit delay'
    }
    
    all_vars_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'URI' in var and '@' in value:
                masked = value.split('@')[0].split('://')[0] + '://***@' + value.split('@')[1]
                print_success(f"{var}: {masked}")
            else:
                print_success(f"{var}: {value}")
        else:
            print_error(f"{var}: NOT SET ({description})")
            all_vars_present = False
    
    return all_vars_present

def test_mongodb_connection():
    """Test MongoDB connection."""
    print_info("Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
        
        load_dotenv()
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        database_name = os.getenv('DATABASE_NAME', 'etl_database')
        
        print_info(f"Connecting to MongoDB...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print_success("MongoDB connection successful")
        
        # Get server info
        server_info = client.server_info()
        print_success(f"MongoDB version: {server_info.get('version', 'Unknown')}")
        
        # Test database access
        db = client[database_name]
        print_success(f"Database '{database_name}' accessible")
        
        # List existing collections
        collections = db.list_collection_names()
        if collections:
            print_info(f"Existing collections: {', '.join(collections)}")
        else:
            print_info("No collections found (expected for first run)")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print_error("MongoDB connection timeout - Is MongoDB running?")
        print_warning("Start MongoDB with: mongod")
        return False
    except ConfigurationError as e:
        print_error(f"MongoDB configuration error: {e}")
        return False
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return False

def test_ripestat_api():
    """Test RIPEstat API connectivity."""
    print_info("Testing RIPEstat API connectivity...")
    
    base_url = "https://stat.ripe.net/data"
    
    # Test endpoints
    test_cases = [
        {
            'name': 'ASN Overview',
            'endpoint': 'as-overview',
            'params': {'resource': 'AS3333'},
            'expected_field': 'holder'
        },
        {
            'name': 'Network Info',
            'endpoint': 'network-info',
            'params': {'resource': '193.0.0.0/21'},
            'expected_field': 'asns'
        },
        {
            'name': 'Geolocation',
            'endpoint': 'geoloc',
            'params': {'resource': '8.8.8.8'},
            'expected_field': 'locations'
        }
    ]
    
    all_tests_passed = True
    
    for test in test_cases:
        try:
            url = f"{base_url}/{test['endpoint']}/data.json"
            print_info(f"Testing {test['name']} endpoint...")
            
            response = requests.get(url, params=test['params'], timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                if test['expected_field'] in data.get('data', {}):
                    print_success(f"{test['name']}: API responding correctly")
                else:
                    print_warning(f"{test['name']}: Unexpected response structure")
            else:
                print_error(f"{test['name']}: API returned status '{data.get('status')}'")
                all_tests_passed = False
            
            # Small delay between requests
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            print_error(f"{test['name']}: Request timeout")
            all_tests_passed = False
        except requests.exceptions.RequestException as e:
            print_error(f"{test['name']}: Request failed - {e}")
            all_tests_passed = False
        except Exception as e:
            print_error(f"{test['name']}: Unexpected error - {e}")
            all_tests_passed = False
    
    return all_tests_passed

def test_disk_space():
    """Check if there's enough disk space for data storage."""
    print_info("Checking disk space...")
    
    try:
        import shutil
        
        total, used, free = shutil.disk_usage("/")
        
        free_gb = free // (2**30)  # Convert to GB
        
        if free_gb > 1:
            print_success(f"Free disk space: {free_gb} GB (OK)")
            return True
        else:
            print_warning(f"Free disk space: {free_gb} GB (Low)")
            return True
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
        return True

def run_all_tests():
    """Run all connection and configuration tests."""
    print_header("RIPEstat ETL Pipeline - Connection Test")
    print(f"Student: Seetharam Killivalavan | Roll: 3122225001124")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'Python Version': test_python_version(),
        'Required Packages': test_required_packages(),
        'Environment File': test_env_file(),
        'MongoDB Connection': test_mongodb_connection(),
        'RIPEstat API': test_ripestat_api(),
        'Disk Space': test_disk_space()
    }
    
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name:<25} {status}")
    
    print(f"\n{Colors.BOLD}Tests Passed: {passed}/{total}{Colors.END}\n")
    
    if passed == total:
        print_success("All tests passed! ✓ Ready to run ETL pipeline")
        print_info("Run: python etl_connector.py")
        return True
    else:
        print_error("Some tests failed. Please fix the issues above before running the ETL pipeline.")
        return False

def main():
    """Main entry point."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()