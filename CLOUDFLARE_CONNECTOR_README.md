# Cloudflare Trace ETL Data Connector

**Student Name:** Rithika S  
**Roll Number:** 3122225001705  
**Assignment:** ETL2 - Custom Python ETL Data Connector  
**Branch:** RithikaS_3122225001705_A_ETL2  
**Data Source:** Cloudflare Trace API

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Endpoints Used](#api-endpoints-used)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [ETL Pipeline Details](#etl-pipeline-details)
9. [Data Schema](#data-schema)
10. [Error Handling](#error-handling)
11. [Testing](#testing)
12. [Project Structure](#project-structure)

---

## 🎯 Overview

This ETL (Extract, Transform, Load) data connector retrieves trace information from Cloudflare's public endpoints, transforms the data into a structured format, and stores it in MongoDB for analysis. The connector demonstrates secure API integration, data transformation best practices, and proper error handling.

### Key Features

✅ **Three distinct Cloudflare endpoints** for comprehensive data collection  
✅ **Secure credential management** using environment variables  
✅ **Data transformation** with type conversion and enrichment  
✅ **MongoDB integration** with proper indexing and timestamps  
✅ **Error handling** for network failures, rate limits, and data validation  
✅ **Detailed logging** for debugging and monitoring  
✅ **Data validation** to ensure data quality

---

## 🌐 API Endpoints Used

### 1. Cloudflare Trace (Primary)

- **URL:** `https://www.cloudflare.com/cdn-cgi/trace`
- **Method:** GET
- **Authentication:** None required (public endpoint)
- **Description:** Returns client IP address, location, TLS version, and connection metadata
- **Response Format:** Key-value pairs (text/plain)

**Sample Response:**

```
fl=361f75
h=www.cloudflare.com
ip=203.0.113.42
ts=1697721234.567
visit_scheme=https
uag=Mozilla/5.0
colo=BOM
sliver=none
http=http/2
loc=IN
tls=TLSv1.3
sni=plaintext
warp=off
gateway=off
rbi=off
kex=X25519
```

### 2. Cloudflare DNS Trace

- **URL:** `https://1.1.1.1/cdn-cgi/trace`
- **Method:** GET
- **Authentication:** None required (public endpoint)
- **Description:** Similar trace information via Cloudflare's 1.1.1.1 DNS resolver
- **Response Format:** Key-value pairs (text/plain)

### 3. Cloudflare IP Information

- **URL:** `https://cloudflare.com/cdn-cgi/trace`
- **Method:** GET
- **Authentication:** None required (public endpoint)
- **Description:** Detailed connection metadata and IP information
- **Response Format:** Key-value pairs (text/plain)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE FLOW                        │
└─────────────────────────────────────────────────────────────┘

1. EXTRACT PHASE
   ├── Endpoint 1: www.cloudflare.com/cdn-cgi/trace
   ├── Endpoint 2: 1.1.1.1/cdn-cgi/trace
   └── Endpoint 3: cloudflare.com/cdn-cgi/trace
           ↓
2. TRANSFORM PHASE
   ├── Parse key-value pairs
   ├── Type conversion (strings → integers where applicable)
   ├── Data enrichment (IP version, location description)
   ├── Aggregation (unique IPs, locations)
   └── Add metadata (timestamp, student info)
           ↓
3. LOAD PHASE
   ├── Connect to MongoDB
   ├── Insert transformed document
   ├── Add ingestion timestamp
   └── Validate insertion
           ↓
4. VALIDATION PHASE
   ├── Count documents
   ├── Verify latest entry
   └── Display summary
```

---

## 📦 Prerequisites

### Software Requirements

- **Python:** 3.8 or higher
- **MongoDB:** 4.4 or higher (local or cloud instance)
- **Internet Connection:** Required for API calls

### Python Libraries

All dependencies are listed in `requirements.txt`:

- `requests==2.31.0` - HTTP library for API calls
- `pymongo==4.6.1` - MongoDB driver for Python
- `python-dotenv==1.0.0` - Environment variable management
- `certifi==2023.11.17` - SSL certificate validation
- `urllib3==2.1.0` - HTTP client

---

## 🔧 Installation

### Step 1: Clone the Repository

```bash
cd /Users/rithikakalaimani/Documents/
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-Rithikakalaimani.git
cd custom-python-etl-data-connector-Rithikakalaimani
git checkout RithikaS_3122225001705_A_ETL2
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MongoDB

```bash
# If using local MongoDB, ensure it's running
# macOS:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod

# Windows:
# Start MongoDB service from Services app
```

---

## ⚙️ Configuration

### Create `.env` File

Create a `.env` file in the project root with the following configuration:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=cloudflare_etl_db

# Cloudflare API Configuration (Optional - only if using authenticated endpoints)
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ZONE_ID=your_zone_id_here
CLOUDFLARE_EMAIL=your_email_here

# Collection Name
COLLECTION_NAME=cloudflare_trace_raw
```

**Note:** For this project, the Cloudflare API credentials are optional since we're using public endpoints.

### MongoDB Cloud (MongoDB Atlas) Configuration

If using MongoDB Atlas instead of local MongoDB:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=cloudflare_etl_db
COLLECTION_NAME=cloudflare_trace_raw
```

---

## 🚀 Usage

### Run the ETL Pipeline

```bash
python etl_connector.py
```

### Expected Output

```
╔══════════════════════════════════════════════════════════════════════╗
║           CLOUDFLARE ETL DATA CONNECTOR                             ║
║                                                                     ║
║           Student: Rithika S (3122225001705)                        ║
╚══════════════════════════════════════════════════════════════════════╝

======================================================================
CLOUDFLARE ETL PIPELINE - STARTING
======================================================================
Student: Rithika S (3122225001705)
Assignment: ETL2 - Cloudflare Trace
======================================================================

✓ Successfully connected to MongoDB: cloudflare_etl_db

======================================================================
EXTRACTION PHASE - Fetching data from Cloudflare endpoints
======================================================================

→ Extracting data from trace...
  URL: https://www.cloudflare.com/cdn-cgi/trace
✓ Successfully extracted 15 fields from trace

→ Extracting data from trace_alternate...
  URL: https://1.1.1.1/cdn-cgi/trace
✓ Successfully extracted 15 fields from trace_alternate

→ Extracting data from ipinfo...
  URL: https://cloudflare.com/cdn-cgi/trace
✓ Successfully extracted 15 fields from ipinfo

✓ Extraction complete: 3/3 endpoints successful

======================================================================
TRANSFORMATION PHASE - Processing and cleaning data
======================================================================

→ Transforming data from trace...
✓ Transformed trace data

→ Transforming data from trace_alternate...
✓ Transformed trace_alternate data

→ Transforming data from ipinfo...
✓ Transformed ipinfo data

✓ Transformation complete: Document ready for MongoDB

======================================================================
LOAD PHASE - Inserting data into MongoDB
======================================================================

→ Inserting document into collection: cloudflare_trace_raw
✓ Successfully inserted document
  Document ID: 6531a8f2b3c4d5e6f7a8b9c0
  Collection: cloudflare_trace_raw
  Database: cloudflare_etl_db

----------------------------------------------------------------------
DATA SUMMARY
----------------------------------------------------------------------
Ingestion Time: 2025-10-19 15:30:52.123456
Total Endpoints: 3
Unique IPs: 1
Locations: BOM
----------------------------------------------------------------------

======================================================================
✓ ETL PIPELINE COMPLETED SUCCESSFULLY
======================================================================

✓ MongoDB connection closed

======================================================================
DATA VALIDATION
======================================================================

Total documents in collection: 1

Latest document details:
  ID: 6531a8f2b3c4d5e6f7a8b9c0
  Timestamp: 2025-10-19 15:30:52.123456
  Endpoints: ['trace', 'trace_alternate', 'ipinfo']
  Unique IPs: ['203.0.113.42']
```

---

## 🔄 ETL Pipeline Details

### 1. Extract Phase

The extraction phase retrieves data from three Cloudflare endpoints:

**Key Functions:**

- `extract_trace_endpoint()` - Fetches data from a single endpoint
- `extract_all_endpoints()` - Orchestrates extraction from all endpoints

**Features:**

- HTTP timeout: 10 seconds
- Custom User-Agent header
- Rate limiting (1 second between requests)
- Error handling for network failures
- Response validation

**Example Extracted Data:**

```python
{
    'trace': {
        'fl': '361f75',
        'h': 'www.cloudflare.com',
        'ip': '203.0.113.42',
        'ts': '1697721234.567',
        'visit_scheme': 'https',
        'uag': 'Mozilla/5.0',
        'colo': 'BOM',
        'http': 'http/2',
        'loc': 'IN',
        'tls': 'TLSv1.3'
    }
}
```

### 2. Transform Phase

The transformation phase processes raw data into a structured MongoDB document:

**Key Functions:**

- `transform_data()` - Main transformation orchestrator
- `_process_trace_data()` - Processes individual endpoint data
- `_aggregate_data()` - Aggregates data across endpoints

**Transformations Applied:**

1. **Type Conversion:** Convert numeric strings to integers
2. **Data Enrichment:** Add derived fields (IP version, location description)
3. **Aggregation:** Collect unique IPs and locations
4. **Metadata Addition:** Add timestamps, student information, source details
5. **Structure Normalization:** Create consistent document schema

**Example Transformed Data:**

```python
{
    'ingestion_timestamp': datetime(2025, 10, 19, 15, 30, 52),
    'ingestion_date': '2025-10-19',
    'source': 'Cloudflare API',
    'metadata': {
        'total_endpoints': 3,
        'connector_version': '1.0',
        'student_name': 'Rithika S',
        'roll_number': '3122225001705'
    },
    'endpoints_data': {
        'trace': {
            'endpoint_name': 'trace',
            'endpoint_url': 'https://www.cloudflare.com/cdn-cgi/trace',
            'raw_data': {...},
            'processed_data': {
                'ip': '203.0.113.42',
                'ip_version': 'IPv4',
                'loc': 'IN',
                'location_code': 'IN',
                'location_description': 'Data center location: IN',
                'http': 2,
                'tls': 'TLSv1.3'
            }
        }
    },
    'aggregated_info': {
        'unique_ips': ['203.0.113.42'],
        'locations': ['BOM'],
        'total_unique_ips': 1,
        'total_locations': 1
    }
}
```

### 3. Load Phase

The load phase inserts the transformed document into MongoDB:

**Key Functions:**

- `load_to_mongodb()` - Inserts document into collection
- `_display_summary()` - Displays insertion summary

**Features:**

- Atomic insertion
- Document ID tracking
- Error handling
- Success validation
- Summary display

### 4. Validation Phase

The validation phase ensures data integrity:

**Key Functions:**

- `validate_data()` - Validates inserted documents

**Checks:**

- Document count verification
- Latest document retrieval
- Field presence validation
- Data type verification

---

## 📊 Data Schema

### MongoDB Document Structure

```javascript
{
  "_id": ObjectId("..."),
  "ingestion_timestamp": ISODate("2025-10-19T15:30:52.123Z"),
  "ingestion_date": "2025-10-19",
  "source": "Cloudflare API",
  "metadata": {
    "total_endpoints": 3,
    "connector_version": "1.0",
    "student_name": "Rithika S",
    "roll_number": "3122225001705"
  },
  "endpoints_data": {
    "trace": {
      "endpoint_name": "trace",
      "endpoint_url": "https://www.cloudflare.com/cdn-cgi/trace",
      "raw_data": {
        "fl": "361f75",
        "h": "www.cloudflare.com",
        "ip": "203.0.113.42",
        "ts": "1697721234.567",
        "visit_scheme": "https",
        "uag": "Mozilla/5.0 ...",
        "colo": "BOM",
        "sliver": "none",
        "http": "http/2",
        "loc": "IN",
        "tls": "TLSv1.3",
        "sni": "plaintext",
        "warp": "off",
        "gateway": "off",
        "rbi": "off",
        "kex": "X25519"
      },
      "processed_data": {
        "fl": "361f75",
        "h": "www.cloudflare.com",
        "ip": "203.0.113.42",
        "client_ip": "203.0.113.42",
        "ip_version": "IPv4",
        "ts": "1697721234.567",
        "visit_scheme": 443,
        "uag": "Mozilla/5.0 ...",
        "colo": "BOM",
        "loc": "IN",
        "location_code": "IN",
        "location_description": "Data center location: IN",
        "http": 2,
        "tls": 1
      }
    },
    "trace_alternate": { ... },
    "ipinfo": { ... }
  },
  "aggregated_info": {
    "unique_ips": ["203.0.113.42"],
    "locations": ["BOM"],
    "total_unique_ips": 1,
    "total_locations": 1
  }
}
```

### Field Descriptions

| Field                 | Type     | Description                     |
| --------------------- | -------- | ------------------------------- |
| `_id`                 | ObjectId | MongoDB unique identifier       |
| `ingestion_timestamp` | DateTime | UTC timestamp of data ingestion |
| `ingestion_date`      | String   | Date of ingestion (YYYY-MM-DD)  |
| `source`              | String   | Data source identifier          |
| `metadata`            | Object   | Connector metadata              |
| `endpoints_data`      | Object   | Data from each endpoint         |
| `aggregated_info`     | Object   | Aggregated cross-endpoint data  |

---

## ⚠️ Error Handling

### Network Errors

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"✗ Network error: {str(e)}")
```

### MongoDB Connection Errors

```python
try:
    self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    self.client.server_info()
except Exception as e:
    print(f"✗ MongoDB connection error: {str(e)}")
    sys.exit(1)
```

### Data Validation Errors

- Empty response handling
- Invalid data format detection
- Missing field checks
- Type conversion error handling

### Rate Limiting

- 1 second delay between API calls
- Respects API best practices
- Prevents overwhelming the service

---

## 🧪 Testing

### Manual Testing Steps

1. **Test MongoDB Connection**

```bash
# Test local MongoDB
mongosh
> show dbs
> use cloudflare_etl_db
> show collections
```

2. **Test ETL Pipeline**

```bash
python etl_connector.py
```

3. **Verify Data in MongoDB**

```bash
mongosh
> use cloudflare_etl_db
> db.cloudflare_trace_raw.find().pretty()
> db.cloudflare_trace_raw.countDocuments()
```

4. **Test Error Handling**

```bash
# Stop MongoDB and run the connector
brew services stop mongodb-community
python etl_connector.py
# Should see connection error handling
```

### Expected Test Results

✅ **Success Criteria:**

- All 3 endpoints return data
- Data is properly transformed
- Document is inserted into MongoDB
- Validation passes
- No error messages

❌ **Failure Scenarios:**

- Network timeout → Graceful error message
- MongoDB down → Clear connection error
- Invalid data → Handled with error logging

---

## 📁 Project Structure

```
custom-python-etl-data-connector-Rithikakalaimani/
├── .gitignore                         # Git ignore file (excludes .env, __pycache__, etc.)
├── README.md                          # Original assignment instructions
├── CLOUDFLARE_CONNECTOR_README.md     # This file - Connector documentation
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables (NOT committed to Git)
├── etl_connector.py                   # Main ETL script
└── venv/                              # Virtual environment (NOT committed to Git)
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

- ✅ All credentials stored in `.env` file
- ✅ `.env` added to `.gitignore`
- ✅ Never hardcode credentials

### 2. API Security

- ✅ Use HTTPS endpoints only
- ✅ Implement request timeouts
- ✅ Respect rate limits
- ✅ Use appropriate User-Agent headers

### 3. MongoDB Security

- ✅ Use authentication in production
- ✅ Limit connection timeout
- ✅ Validate data before insertion
- ✅ Use connection URI from environment

---

## 📝 Git Workflow

### Commit Message Format

```
RithikaS_3122225001705: [Brief description]

Detailed description of changes made.
```

### Example Commits

```bash
git add .gitignore requirements.txt etl_connector.py CLOUDFLARE_CONNECTOR_README.md
git commit -m "RithikaS_3122225001705: Initial ETL connector implementation

- Added .gitignore to exclude sensitive files
- Created requirements.txt with dependencies
- Implemented etl_connector.py with 3 Cloudflare endpoints
- Added comprehensive documentation"

git push origin RithikaS_3122225001705_A_ETL2
```

### What NOT to Commit

❌ `.env` file (contains credentials)  
❌ `venv/` directory (virtual environment)  
❌ `__pycache__/` directories  
❌ `.DS_Store` files (macOS)  
❌ `*.pyc` files (compiled Python)  
❌ Database files

---

## 🐛 Troubleshooting

### Issue: MongoDB Connection Failed

**Solution:**

```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB if not running
brew services start mongodb-community

# Verify connection
mongosh --eval "db.version()"
```

### Issue: Package Installation Failed

**Solution:**

```bash
# Upgrade pip
pip install --upgrade pip

# Install packages one by one
pip install requests
pip install pymongo
pip install python-dotenv
```

### Issue: Import Error

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify packages are installed
pip list

# Reinstall if needed
pip install -r requirements.txt
```

### Issue: API Timeout

**Solution:**

- Check internet connection
- Verify firewall settings
- Try increasing timeout in code
- Check if Cloudflare is accessible

---

## 📈 Future Enhancements

### Potential Improvements

1. **Scheduling:** Add cron job or scheduler for periodic data collection
2. **Logging:** Implement file-based logging with rotation
3. **Metrics:** Add performance metrics and timing
4. **Visualization:** Create dashboard for data visualization
5. **Alerting:** Add email/SMS alerts for failures
6. **API Authentication:** Add support for authenticated Cloudflare APIs
7. **Data Analysis:** Add analytical queries and reporting
8. **Testing:** Add unit tests and integration tests

---

## 📚 References

### Cloudflare Documentation

- [Cloudflare Trace](https://www.cloudflare.com/cdn-cgi/trace)
- [Cloudflare API Documentation](https://developers.cloudflare.com/api/)

### Python Libraries

- [Requests Documentation](https://requests.readthedocs.io/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)

### MongoDB

- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [MongoDB Python Driver Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html)

---

## 👤 Author Information

**Name:** Rithika S  
**Roll Number:** 3122225001705  
**Institution:** SSN College of Engineering  
**Department:** Computer Science and Engineering  
**Program:** Kyureeus EdTech  
**Assignment:** ETL2 - Custom Python ETL Data Connector  
**Date:** October 2025

---

## 📄 License

This project is created for educational purposes as part of the Software Architecture course at SSN College of Engineering under the Kyureeus EdTech program.

---

## ✅ Submission Checklist

- [x] Choose a data provider (Cloudflare Trace API)
- [x] Understand API documentation
- [x] Secure credentials in `.env` file
- [x] Build complete ETL script
- [x] Use 3 distinct endpoints
- [x] Implement proper error handling
- [x] Validate MongoDB inserts
- [x] Push code to branch
- [x] Include descriptive README
- [x] Add .gitignore file
- [x] Include name and roll number in commits
- [x] Ready to submit Pull Request

---

**Happy Coding! 🚀**
