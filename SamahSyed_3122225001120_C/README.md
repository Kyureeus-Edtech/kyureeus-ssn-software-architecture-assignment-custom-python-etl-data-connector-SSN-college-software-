# Custom Python ETL Data Connector — NetworkCalc API

## Overview

This project is part of the Software Architecture Assignment for the Kyureeus EdTech program at SSN CSE.  
The goal is to build a custom Python ETL (Extract, Transform, Load) pipeline that connects to an external data provider, processes the data, and loads it into a MongoDB collection following secure coding and project structure best practices.

For this submission, the chosen data provider is **NetworkCalc API** — a publicly available REST API providing network calculations, binary conversions, and SSL certificate security information.

## API Details 
- **Source**: https://networkcalc.com/api
- **Endpoints Used**:
  - `/api/ip/{cidr}` - Subnet calculations
  - `/api/binary/{value}?from={base}&to={base}` - Binary/base conversions
  - `/api/security/certificate/{domain}` - SSL certificate information
- **Format**: JSON
- **Auth**: None

## Features Implemented

### Extract
- Fetches data from multiple NetworkCalc API endpoints with different query parameters
- Queries include:
  - **Subnet calculations**: `192.168.1.1/24`, `10.0.0.1/16`
  - **Binary conversions**: 255 and 128 from base 10 to base 2
  - **Security certificates**: example.com and google.com
- Handles connection errors and request timeouts gracefully with 20-second timeout
- Uses session management for efficient HTTP requests
- Logs each API call with endpoint and query details

### Transform
- **Enhanced Data Enrichment**: Adds comprehensive derived fields based on endpoint type
- **Subnet Transformation**:
  - Extracts network, broadcast, mask, and host count
  - Calculates subnet bits from host count
- **Binary Transformation**:
  - Preserves input/output values and base conversions
  - Calculates parity (even/odd) of binary output
- **Security Transformation**:
  - Parses certificate subject and issuer information
  - Extracts validity dates (valid_from, valid_to)
  - Calculates certificate validity duration in days
  - Preserves serial numbers for audit trails
- **Data Structure**: Creates summary objects alongside original data
- **Timestamp Addition**: Adds ingestion timestamp (`ingestion_time`) for auditing
- **Pretty Printing**: Displays MongoDB content before transformation and transformed records preview

### Load
- Inserts transformed records into MongoDB collection
- Creates indexes on `endpoint` and `ingestion_time` for efficient querying
- Handles MongoDB connection errors and write failures
- Pretty prints the latest 5 records after successful insertion
- Provides detailed logging at each stage

## Secure Credential Handling
- All database connection details are stored in a local `.env` file (not committed to Git)
- Environment variables are loaded using the `python-dotenv` library
- `.gitignore` is configured to exclude `.env` and other sensitive files

## Project Structure

```bash
SamahSyed_3122225001120_C
├── networkcalc_etl.py: Main ETL pipeline script
├── .env: Environment variables (excluded from Git)
├── requirements.txt: Python dependencies
├── networkcalc_etl.log: ETL execution logs
└── README.md: Documentation (this file)
.gitignore: Ignore sensitive & unnecessary files such as .env, __pycache__, venv, *.log
```

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repo_url>
cd <repo_folder>
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
Create a `.env` file in the project root with the following variables:

```bash
MONGO_URI=your_mongo_uri
MONGO_DATABASE=etl_database
MONGO_COLLECTION=networkcalc_raw
```

## Running the ETL Pipeline
```bash
python networkcalc_etl.py
```

## MongoDB Collection Design
Each document in MongoDB follows this structure:

### Subnet Endpoint Document
```json
{
  "_id": ObjectId("..."),
  "endpoint": "subnet",
  "query": "192.168.1.1/24",
  "ingestion_time": "2025-10-21T06:22:10.059690+00:00",
  "original_data": {
    "address": {
      "network_address": "192.168.1.0",
      "broadcast_address": "192.168.1.255",
      "subnet_mask": "255.255.255.0",
      "assignable_hosts": 254,
      "subnet_bits": 24
    },
    "status": "OK"
  },
  "summary": {
    "network": "192.168.1.0",
    "broadcast": "192.168.1.255",
    "mask": "255.255.255.0",
    "host_count": 254,
    "subnet_bits": 8
  }
}
```

### Binary Endpoint Document
```json
{
  "_id": ObjectId("..."),
  "endpoint": "binary",
  "query": {"value": 255, "from": 10, "to": 2},
  "ingestion_time": "2025-10-21T06:22:10.683187+00:00",
  "original_data": {
    "original": "255",
    "converted": "11111111",
    "from": "10",
    "to": "2",
    "status": "OK"
  },
  "summary": {
    "input": "255",
    "output": "11111111",
    "from_base": "10",
    "to_base": "2",
    "parity": "even"
  }
}
```

### Security Endpoint Document
```json
{
  "_id": ObjectId("..."),
  "endpoint": "security",
  "query": "example.com",
  "ingestion_time": "2025-10-21T06:22:11.492490+00:00",
  "original_data": {
    "certificate": {
      "hostname": "example.com",
      "issued_to": "*.example.com",
      "issued_by": "DigiCert Global G3 TLS ECC SHA384 2020 CA1",
      "valid_from": "2025-01-15T00:00:00.000Z",
      "valid_to": "2026-01-15T23:59:59.000Z",
      "serial_number": "0AD893BAFA68B0B7FB7A404F06ECAF9A",
      "fingerprint": "31:0D:B7:AF:4B:2B:C9:04:0C:83:44:70:1A:CA:08:D0:C6:93:81:E3"
    },
    "status": "OK"
  },
  "summary": {
    "subject": {},
    "issuer": {},
    "valid_from": "2025-01-15T00:00:00+00:00",
    "valid_to": "2026-01-15T23:59:59+00:00",
    "validity_days": 365,
    "serial_number": "0AD893BAFA68B0B7FB7A404F06ECAF9A"
  }
}
```

## Key Features

### Data Enrichment & Transformation Logic
- **Subnet Calculations**: Automatically calculates subnet bits from host count
- **Binary Analysis**: Determines parity (even/odd) of binary strings
- **Certificate Analysis**: Calculates certificate validity duration in days
- **Dual Storage**: Maintains both original API response and enriched summary data

### Error Handling & Logging
- Comprehensive logging to both file (`networkcalc_etl.log`) and console
- Request timeout handling (20 seconds per API call)
- MongoDB connection failure detection
- Graceful handling of API failures - continues processing remaining endpoints

### MongoDB Integration
- Automatic index creation on `endpoint` and `ingestion_time`
- Connection validation with ping command
- Bulk insert operations for efficiency
- Pretty-printed output for debugging and verification

## Sample ETL Execution Output

```bash
2025-10-21 11:52:08,957 - INFO - Starting NetworkCalc ETL pipeline
2025-10-21 11:52:09,015 - INFO - Connected to MongoDB: etl_database.networkcalc_raw
2025-10-21 11:52:09,015 - INFO - Fetching subnet data for query: 192.168.1.1/24
2025-10-21 11:52:10,059 - INFO - Fetching subnet data for query: 10.0.0.1/16
2025-10-21 11:52:10,368 - INFO - Fetching binary data for query: {'value': 255, 'from': 10, 'to': 2}
2025-10-21 11:52:10,683 - INFO - Fetching binary data for query: {'value': 128, 'from': 10, 'to': 2}
2025-10-21 11:52:10,994 - INFO - Fetching security data for query: example.com
2025-10-21 11:52:11,492 - INFO - Fetching security data for query: google.com
2025-10-21 11:52:11,805 - INFO - Extracted data from 6 queries
2025-10-21 11:52:11,807 - INFO - MongoDB content BEFORE transformation (first 5 records):
2025-10-21 11:52:11,810 - INFO - Transformed records (preview of first 5):
[Preview of transformed data with summaries...]
2025-10-21 11:52:11,885 - INFO - Transformed 6 records
2025-10-21 11:52:11,951 - INFO - Data loaded into MongoDB successfully. Latest 5 records:
[Pretty-printed MongoDB documents...]
2025-10-21 11:52:12,021 - INFO - ETL pipeline completed successfully
```

## Assignment Requirements Covered
- **Data Provider**: NetworkCalc REST API with multiple endpoints
- **Secure Credentials**: Stored in `.env`
- **ETL Pipeline**: Extract → Transform → Load with data enrichment
- **MongoDB Storage**: Single collection with indexed fields
- **Multiple Queries**: 6 different queries across 3 endpoints
- **Data Transformation**: Custom logic per endpoint type with calculated fields
- **Validation & Error Handling**: Implemented in all stages
- **Git Hygiene**: `.env` and log files ignored, descriptive README included
- **Extra Enhancements**: 
  - Data enrichment with derived calculations
  - Pretty printing for debugging
  - Dual storage (original + summary)
  - Comprehensive logging
  - Session-based HTTP requests
  - Index creation for query optimization

---

**Author:** Samah Syed (Roll No: 3122225001120)