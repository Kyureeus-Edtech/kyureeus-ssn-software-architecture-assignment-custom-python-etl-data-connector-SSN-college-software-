# Abuse.ch Threat Intelligence ETL Pipeline

**Software Architecture - Assignment 2**  
Rohan R – 3122225001108 – CSE B

## Overview

This project is a Python ETL (Extract, Transform, Load) pipeline that retrieves threat intelligence data from abuse.ch APIs (URLhaus and MalwareBazaar), transforms it into a standardized format, and stores it in MongoDB for analysis and monitoring.

## Features

* **Dual-Source Intelligence**: Fetches malicious URLs from URLhaus and malware samples from MalwareBazaar
* **Intelligent Transformation**: Standardizes data with threat classification and enrichment
* **Upsert Logic**: Prevents duplicate records using MongoDB's upsert functionality
* **Error Handling**: Graceful handling of API failures and connection issues
* **Comprehensive Testing**: Unit tests with mocked API responses for all ETL stages
* **Automated Classification**: Dynamic threat level and file class categorization
* **Flexible Date Parsing**: Handles both Unix timestamps and ISO format dates

## API Endpoint Details

### URLhaus API
* **Base URL**: `https://urlhaus-api.abuse.ch`
* **Endpoint**: `/v1/urls/recent/`
* **Method**: `GET`
* **Headers Required**: `{'Auth-Key': 'YOUR_API_KEY'}`

### MalwareBazaar API
* **Base URL**: `https://mb-api.abuse.ch`
* **Endpoint**: `/api/v1/`
* **Method**: `POST`
* **Headers Required**: `{'Auth-Key': 'YOUR_API_KEY'}`
* **POST Data**: `{'query': 'get_recent', 'selector': '100'}`

### Authentication
* A valid abuse.ch API key is required for both services
* Store the key in a `.env` file (never commit this to Git)
* Credentials are loaded using the `python-dotenv` package

## Project Structure
```
custom-python-etl-data-connector-rohanraja7/
├── connectors/
│   └── abusech_api.py           # API connector for abuse.ch services
├── transformations/
│   └── data_transformer.py      # Data transformation logic
├── database/
│   └── mongo_loader.py          # MongoDB loading operations
├── tests/
│   └── test_abusech_etl.py      # Comprehensive unit tests
├── main.py                       # Main ETL pipeline orchestrator
├── config.py                     # Configuration loader
├── .env                          # Environment variables (DO NOT COMMIT)
├── .env.template                 # Template for environment variables
├── .gitignore                    # Ignore sensitive files
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## Environment Variables (.env)
```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/

# Abuse.ch API Authentication
ABUSECH_API_KEY=your_api_key_here
```

## Installation & Setup

1. **Clone your branch from the main repository:**
```bash
git checkout main
git pull origin main
git checkout -b RohanR_3122225001108_B_Assign2
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up MongoDB:**
```bash
# Ensure MongoDB is running on localhost:27017
MONGO_URI=mongodb://localhost:27017/
```

4. **Create a `.env` file:**
```bash
# Copy the template and add your API key
cp .env.template .env
# Edit .env and add your abuse.ch API key
```

## Running the ETL Pipeline

### Standard Execution
```bash
python main.py
```

This will:
1. Extract recent URLs from URLhaus
2. Extract recent malware samples from MalwareBazaar
3. Transform both datasets into standardized formats
4. Load data into MongoDB collections

### Running Tests
```bash
# Run all unit tests
python -m unittest tests/test_abusech_etl.py

# Run with verbose output
python -m unittest tests/test_abusech_etl.py -v
```

## MongoDB Storage

### Database
* **Database Name**: `threat_intelligence`

### Collections
* **URLhaus Collection**: `urlhaus_iocs`
* **MalwareBazaar Collection**: `malwarebazaar_iocs`

### URLhaus Document Structure
```json
{
  "_id": "1",
  "source": "URLhaus",
  "ioc_type": "url",
  "ioc_value": "http://evil.com/payload.exe",
  "threat_type": "malware_download",
  "tags": ["exe", "trojan"],
  "threat_level": "high",
  "first_seen": "2025-10-16T10:00:00"
}
```

### MalwareBazaar Document Structure
```json
{
  "_id": "aaa123...",
  "source": "MalwareBazaar",
  "ioc_type": "hash_sha256",
  "ioc_value": "aaa123...",
  "signature": "evil_malware",
  "tags": ["rat"],
  "file_class": "executable",
  "first_seen": "2025-10-16T12:00:00"
}
```

## Data Transformation Logic

### URLhaus Threat Classification
* **High**: URLs containing executable file indicators (`exe` tag)
* **Medium**: All other malicious URLs

### MalwareBazaar File Classification
* **Document**: Files with types `docx`, `pdf`
* **Executable**: All other file types

### Date Handling
The pipeline intelligently handles multiple date formats:
* Unix timestamps (e.g., `1729084200`)
* ISO format strings (e.g., `2025-10-16 12:00:00`)

## Error Handling

The pipeline includes robust error handling for:
* **API Connection Failures**: Returns `None` and logs error
* **MongoDB Connection Issues**: Prevents crash with proper exception handling
* **Invalid Date Formats**: Logs warning and continues processing
* **Missing API Keys**: Validates before execution

## Testing Strategy

The test suite covers all three ETL stages:

### Extract Tests
* Successful data retrieval from both APIs
* Graceful handling of connection failures

### Transform Tests
* Correct threat level classification
* Proper file class categorization
* Multiple date format parsing

### Load Tests
* Successful upsert operations
* Database connection failure handling

## Dependencies
```txt
requests          # HTTP library for API calls
pymongo           # MongoDB driver
python-dotenv     # Environment variable management
```
## Security Best Practices

* API keys stored in `.env` (excluded from Git)
* `.env.template` provided for easy setup
* Sensitive credentials never hardcoded
* `.gitignore` configured to exclude sensitive files

## License

This project is created for educational purposes as part of Software Architecture coursework.
