"""
Setup Validation Script
Validates the pipeline configuration and dependencies
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def print_header(title):
    """Print section header"""
    print(f"\n{BLUE}{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}{NC}\n")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓{NC} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}⚠{NC} {message}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗{NC} {message}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python version too old: {version.major}.{version.minor}.{version.micro}")
        print_error("Python 3.8 or higher is required")
        return False


def check_dependencies():
    """Check required dependencies"""
    required = ['pymongo', 'feedparser', 'dotenv', 'dateutil']
    all_ok = True
    
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'dateutil':
                __import__('dateutil')
            else:
                __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            all_ok = False
    
    return all_ok


def check_directory_structure():
    """Check required directories"""
    required_dirs = ['data', 'logs', 'scripts', 'threat_intel_pipeline']
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_success(f"Directory exists: {dir_name}/")
        else:
            print_warning(f"Directory missing: {dir_name}/")
            if dir_name in ['data', 'logs']:
                print(f"  Creating {dir_name}/...")
                dir_path.mkdir(exist_ok=True)
            else:
                all_ok = False
    
    return all_ok


def check_env_file():
    """Check .env configuration"""
    if not Path('.env').exists():
        print_error(".env file not found")
        print("  Please copy .env.template to .env and configure it")
        return False
    
    print_success(".env file exists")
    
    load_dotenv()
    
    # Check required variables
    required_vars = ['MONGO_URI', 'DB_NAME']
    all_ok = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive info
            if var == 'MONGO_URI':
                display_value = value[:20] + '...' if len(value) > 20 else value
            else:
                display_value = value
            print_success(f"{var} = {display_value}")
        else:
            print_error(f"{var} not set in .env")
            all_ok = False
    
    return all_ok


def check_mongodb_connection():
    """Test MongoDB connection"""
    try:
        from pymongo import MongoClient
        load_dotenv()
        
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            print_error("MONGO_URI not configured")
            return False
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        client.close()
        
        print_success("MongoDB connection successful")
        return True
        
    except Exception as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        print("  Make sure MongoDB is running")
        print("  Start with: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        return False


def check_csv_files():
    """Check for CSV data files"""
    data_dir = Path('data')
    csv_files = [
        'certat_malware_infections.csv',
        'certat_vulnerable_systems.csv',
        'certat_brute_force_attacks.csv'
    ]
    
    found = 0
    for filename in csv_files:
        file_path = data_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print_success(f"{filename} ({size:,} bytes)")
            found += 1
        else:
            print_warning(f"{filename} not found")
    
    if found == 0:
        print("\n  Run this to generate sample data:")
        print("  python scripts/generate_sample_data.py")
        return False
    
    return found > 0


def check_pipeline_modules():
    """Check pipeline modules can be imported"""
    modules = [
        'threat_intel_pipeline.csv_feeds.extract',
        'threat_intel_pipeline.csv_feeds.transform',
        'threat_intel_pipeline.csv_feeds.load',
        'threat_intel_pipeline.rss_feeds.extract',
        'threat_intel_pipeline.rss_feeds.transform',
        'threat_intel_pipeline.rss_feeds.load',
        'threat_intel_pipeline.etl_orchestrator'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            module_name = module.split('.')[-1]
            print_success(f"{module_name} module")
        except Exception as e:
            print_error(f"Failed to import {module}: {str(e)}")
            all_ok = False
    
    return all_ok


def main():
    """Main validation function"""
    print(f"\n{BLUE}{'=' * 70}")
    print("  CERT.at Threat Intelligence Pipeline - Setup Validation")
    print(f"{'=' * 70}{NC}")
    
    results = {}
    
    # Python version
    print_header("Python Version")
    results['python'] = check_python_version()
    
    # Dependencies
    print_header("Python Dependencies")
    results['dependencies'] = check_dependencies()
    
    # Directory structure
    print_header("Directory Structure")
    results['directories'] = check_directory_structure()
    
    # Environment configuration
    print_header("Environment Configuration")
    results['env'] = check_env_file()
    
    # MongoDB connection
    print_header("MongoDB Connection")
    results['mongodb'] = check_mongodb_connection()
    
    # CSV data files
    print_header("CSV Data Files")
    results['csv_files'] = check_csv_files()
    
    # Pipeline modules
    print_header("Pipeline Modules")
    results['modules'] = check_pipeline_modules()
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}\n")
    
    if all(results.values()):
        print_success("All checks passed! ✓")
        print(f"\n{GREEN}The pipeline is ready to run!{NC}")
        print("\nRun the pipeline with:")
        print("  python threat_intel_pipeline/etl_orchestrator.py")
        print("  or")
        print("  ./run.sh")
        return 0
    else:
        print_error("Some checks failed")
        print(f"\n{YELLOW}Please fix the issues above before running the pipeline{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())