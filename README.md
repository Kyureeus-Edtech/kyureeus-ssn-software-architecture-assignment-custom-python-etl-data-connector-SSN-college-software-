# Custom Python ETL Data Connector

**File**: README.md  
**Author**: Rohith Arumugam S - 3122225001110  
**Assignment**: Software Architecture - Custom Python ETL Data Connector  
**Institution**: Kyureeus EdTech, SSN CSE  
**Data Source**: NetworkCalc API (Entry #8 from provided connector list)

## Overview

This project implements a robust ETL (Extract, Transform, Load) pipeline that connects to the **NetworkCalc API**, processes network infrastructure and security data, and stores it in a MongoDB database. The connector handles multiple endpoint types including subnet calculations, binary conversions, and SSL certificate security information with comprehensive data validation and pretty-printed output.

## Features

- Secure API configuration using environment variables
- Robust error handling and logging
- Multiple queries per endpoint for comprehensive data collection
- Network data transformation with structured summaries
- MongoDB integration with proper indexing
- Pretty-printed MongoDB content for debugging and validation
- Comprehensive data visualization during transformation
- Real network infrastructure and security intelligence processing

## API Details

**Provider**: NetworkCalc  
**Source**: Entry #8 from provided connector list  
**Base URL**: https://networkcalc.com/api  
**Endpoints**: 
- `/ip/{cidr}` - Subnet calculations
- `/binary/{value}?from={base}&to={base}` - Number base conversions
- `/security/certificate/{domain}` - SSL certificate information

**Method**: GET  
**Authentication**: None required (public API)  
**Response Format**: JSON with comprehensive network and security data

### API Response Structures

#### Subnet Endpoint Response
```json
{
  "address": {
    "assignable_hosts": 254,
    "broadcast_address": "192.168.1.255",
    "cidr_notation": "192.168.1.1/24",
    "first_assignable_host": "192.168.1.1",
    "last_assignable_host": "192.168.1.254",
    "network_address": "192.168.1.0",
    "subnet_bits": 24,
    "subnet_mask": "255.255.255.0",
    "wildcard_mask": "0.0.0.255"
  },
  "status": "OK"
}
```

#### Binary Endpoint Response
```json
{
  "converted": "11111111",
  "from": "10",
  "original": "255",
  "status": "OK",
  "to": "2"
}
```

#### Security Endpoint Response
```json
{
  "certificate": {
    "alternate_names": ["DNS:*.example.com", "DNS:example.com"],
    "fingerprint": "31:0D:B7:AF:...",
    "hostname": "example.com",
    "issued_by": "DigiCert Global G3 TLS ECC SHA384 2020 CA1",
    "issued_to": "*.example.com",
    "serial_number": "0AD893BAFA68B0B7FB7A404F06ECAF9A",
    "valid_from": "2025-01-15T00:00:00.000Z",
    "valid_to": "2026-01-15T23:59:59.000Z"
  },
  "status": "OK"
}
```

## Project Structure

```
/networkcalc-etl-connector/
├── networkcalc_etl.py        # Main ETL script
├── .env                      # Environment variables (NOT COMMITTED)
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
├── .gitignore               # Git ignore rules
├── networkcalc_etl.log      # ETL execution logs
└── ENV_TEMPLATE             # Environment variables template
```

## Prerequisites

- Python 3.7 or higher
- MongoDB server (local or remote)
- Internet connection for API access

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
git checkout -b your-branch-name
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP library for API calls
- `pymongo` - MongoDB Python driver
- `python-dotenv` - Environment variable management

### 4. Configure Environment Variables
Create a `.env` file in the project root and configure the following variables:

```bash
# Copy the example and modify as needed
cp ENV_TEMPLATE .env
```

Required environment variables:
- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/)
- `MONGO_DATABASE`: Database name (default: etl_database)
- `MONGO_COLLECTION`: Collection name (default: networkcalc_raw)

### 5. Start MongoDB
Ensure MongoDB is running on your system:
```bash
# For local MongoDB installation
mongod

# Or use MongoDB Atlas cloud service
```

## Usage

### Run the ETL Pipeline
```bash
python networkcalc_etl.py
```

### Query Configuration

The connector processes multiple queries per endpoint for comprehensive data collection:

```python
self.queries = {
    "subnet": ["192.168.1.1/24", "10.0.0.1/16"],
    "binary": [
        {"value": 255, "from": 10, "to": 2}, 
        {"value": 128, "from": 10, "to": 2}
    ],
    "security": ["example.com", "google.com"]
}
```

### Expected Output

The script will:
1. Connect to MongoDB
2. Extract data from NetworkCalc API (6 queries across 3 endpoints)
3. Display MongoDB content BEFORE transformation (first 5 records)
4. Transform and validate the network data with pretty-printed preview
5. Load data into MongoDB with proper indexing
6. Display latest 5 records with full formatting

### Example Log Output

```
2025-10-21 10:51:38,110 - INFO - Starting NetworkCalc ETL pipeline
2025-10-21 10:51:38,153 - INFO - Connected to MongoDB: etl_database.networkcalc
2025-10-21 10:51:38,154 - INFO - Fetching subnet data for query 192.168.1.1/24
2025-10-21 10:51:41,924 - INFO - Fetching subnet data for query 10.0.0.1/16
2025-10-21 10:51:42,181 - INFO - Fetching binary data for query {'value': 255, 'from': 10, 'to': 2}
2025-10-21 10:51:42,441 - INFO - Fetching binary data for query {'value': 128, 'from': 10, 'to': 2}
2025-10-21 10:51:42,704 - INFO - Fetching security data for query example.com
2025-10-21 10:51:43,061 - INFO - Fetching security data for query google.com
2025-10-21 10:51:43,340 - INFO - Extracted data from 6 queries
2025-10-21 10:51:43,341 - INFO - MongoDB content BEFORE transformation (first 5 records):
{pretty-printed existing data...}
2025-10-21 10:51:43,370 - INFO - Transformed records (preview of first 5):
{pretty-printed transformed data...}
2025-10-21 10:51:43,398 - INFO - Transformed 6 records
2025-10-21 10:51:43,402 - INFO - Data loaded into MongoDB successfully. Latest 5 records:
{pretty-printed latest records...}
2025-10-21 10:51:43,444 - INFO - ETL pipeline completed successfully
```

## Data Schema

### Transformed Document Structure

#### Subnet Query Document
```json
{
  "_id": "ObjectId",
  "endpoint": "subnet",
  "query": "192.168.1.1/24",
  "ingestion_time": "2025-10-21T05:21:41.924706Z",
  "original_data": {
    "address": {
      "assignable_hosts": 254,
      "broadcast_address": "192.168.1.255",
      "cidr_notation": "192.168.1.1/24",
      "network_address": "192.168.1.0",
      "subnet_mask": "255.255.255.0"
    }
  },
  "summary": {
    "network": "192.168.1.0",
    "broadcast": "192.168.1.255",
    "host_count": 254,
    "mask": "255.255.255.0"
  }
}
```

#### Binary Query Document
```json
{
  "_id": "ObjectId",
  "endpoint": "binary",
  "query": {"value": 255, "from": 10, "to": 2},
  "ingestion_time": "2025-10-21T05:21:42.441710Z",
  "original_data": {
    "converted": "11111111",
    "from": "10",
    "original": "255",
    "to": "2"
  },
  "summary": {
    "input": "255",
    "from_base": "10",
    "to_base": "2",
    "output": "11111111"
  }
}
```

#### Security Query Document
```json
{
  "_id": "ObjectId",
  "endpoint": "security",
  "query": "example.com",
  "ingestion_time": "2025-10-21T05:21:43.061235Z",
  "original_data": {
    "certificate": {
      "hostname": "example.com",
      "issued_by": "DigiCert Global G3 TLS ECC SHA384 2020 CA1",
      "serial_number": "0AD893BAFA68B0B7FB7A404F06ECAF9A",
      "valid_from": "2025-01-15T00:00:00.000Z",
      "valid_to": "2026-01-15T23:59:59.000Z"
    }
  },
  "summary": {
    "subject": {},
    "issuer": {},
    "serial_number": "0AD893BAFA68B0B7FB7A404F06ECAF9A",
    "valid_from": "2025-01-15T00:00:00.000Z",
    "valid_to": "2026-01-15T23:59:59.000Z"
  }
}
```

### MongoDB Indexes
- `endpoint`: For filtering by endpoint type
- `ingestion_time`: For time-based queries and sorting

## Key Features

### Multiple Queries Per Endpoint
The connector processes multiple queries for each endpoint type, enabling:
- Comprehensive subnet analysis across different network ranges
- Multiple binary conversions in a single run
- Security certificate checks for multiple domains

### Pretty-Printed Output
Uses Python's `pprint` module to display:
- MongoDB content BEFORE transformation (debugging)
- Transformed records preview (validation)
- Latest loaded records (verification)

### Structured Summaries
Each endpoint type has a tailored summary extraction:
- **Subnet**: Network address, broadcast, host count, subnet mask
- **Binary**: Input/output values and base conversions
- **Security**: Certificate issuer, subject, serial number, validity dates

## Error Handling

The connector handles various error scenarios:
- Network connectivity issues
- Invalid API responses
- MongoDB connection failures
- Individual query processing failures
- JSON parsing errors
- Timeout handling (20-second request timeout)

## Security Features

- Environment variables for sensitive configuration
- .env file excluded from version control
- Secure MongoDB connection handling
- Proper session management with headers
- Input validation and sanitization

## Testing and Validation

### Manual Testing
```bash
# Test MongoDB connection
python -c "from networkcalc_etl import NetworkCalcETLConnector; NetworkCalcETLConnector().connect_to_mongodb()"

# Test API connectivity
curl https://networkcalc.com/api/ip/192.168.1.1/24
curl "https://networkcalc.com/api/binary/255?from=10&to=2"
curl https://networkcalc.com/api/security/certificate/example.com
```

### Data Validation
The pipeline includes automatic validation for:
- Endpoint type consistency
- Query parameter presence
- Timestamp accuracy
- Original data preservation
- Summary field population
- MongoDB insertion success

## Monitoring and Logging

- Comprehensive logging to both file (`networkcalc_etl.log`) and console
- Query-level tracking with timestamps
- Pretty-printed data inspection at key pipeline stages
- Extraction, transformation, and load statistics
- Error tracking and reporting

## Troubleshooting

### Common Issues

**MongoDB Connection Error**
- Ensure MongoDB is running
- Check connection string in .env
- Verify network connectivity

**API Request Failures**
- Check internet connectivity
- Verify NetworkCalc API endpoint URLs
- Review timeout settings (default: 20 seconds)

**Empty Summaries in Transformed Data**
- Check API response structure matches expected format
- Verify field names in transformation logic
- Review original_data content for available fields

**Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.7+)
- Activate virtual environment

### Debug Mode
Review the log file for detailed execution traces:
```bash
tail -f networkcalc_etl.log
```

## Performance Considerations

- Efficient MongoDB operations with proper indexing
- Session reuse for API requests
- Memory-efficient data processing
- Timeout protection (20-second request timeout)
- Batch processing of multiple queries

## NetworkCalc Data Insights

This connector processes critical network infrastructure and security data:

- **Subnet Analysis**: IP address planning, network segmentation, and capacity calculations
- **Binary Conversions**: Number base transformations for network engineering
- **Certificate Intelligence**: SSL/TLS certificate validation and expiry tracking
- **Multi-Query Support**: Comprehensive data collection across different network ranges and domains

## What Your Pipeline Successfully Does

1. **Extract**: 
   - Connects to NetworkCalc API with proper session management
   - Processes 6 queries across 3 different endpoints
   - Handles multiple query types (strings, dictionaries)
   - Includes timestamps for all extractions

2. **Transform**: 
   - Displays existing MongoDB data before transformation
   - Creates endpoint-specific summaries
   - Preserves original API response data
   - Pretty-prints transformation results for validation
   - Adds ingestion timestamps and metadata

3. **Load**: 
   - Stores data in MongoDB with comprehensive indexing
   - Creates indexes on endpoint and ingestion_time
   - Displays latest loaded records with full formatting
   - Maintains audit trails with timestamps

## Future Enhancements

- Additional NetworkCalc endpoints (DNS lookup, port scanning, WHOIS)
- Automated certificate expiry alerts
- Historical trend analysis for network changes
- Integration with network monitoring tools
- Advanced subnet optimization recommendations
- Batch processing for large-scale network audits
- Real-time monitoring dashboard

## Dependencies

- `requests`: HTTP library for API calls
- `pymongo`: MongoDB Python driver
- `python-dotenv`: Environment variable management
- `pprint`: Pretty-printing for debugging and validation

## Contributing

1. Create a feature branch from main
2. Implement changes with proper testing
3. Update documentation as needed
4. Submit pull request with descriptive commit message

## License

This project is created for educational purposes as part of the Software Architecture course at SSN CSE through Kyureeus EdTech.

---

**Submission Details**  
Student: Rohith Arumugam S  
Roll Number: 3122225001110  
Branch: RohithArumugamS_3122225001110_CSE_B  
Submission Date: October 21, 2025  
Data Source: NetworkCalc API (Entry #8)

## Script Details

**Main Script**: `networkcalc_etl.py`  
**Log File**: `networkcalc_etl.log`  
**Collection**: `networkcalc` (in `etl_database`)  
**Endpoints Processed**: 3 (subnet, binary, security)  
**Queries Per Run**: 6 (2 subnet, 2 binary, 2 security)