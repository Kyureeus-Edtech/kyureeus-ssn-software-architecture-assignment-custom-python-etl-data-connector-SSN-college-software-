# CIRCL Passive DNS ETL Data Connector

**Author:** Kavin (Roll Number: 302004)  
**Assignment:** Software Architecture - Custom Python ETL Data Connector  
**API Provider:** CIRCL Passive DNS  
**Date:** December 2024

## 📋 Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline for the CIRCL Passive DNS API. The connector extracts DNS records from the CIRCL Passive DNS service, transforms the data for MongoDB compatibility, and loads it into a MongoDB collection for analysis and storage.

## 🎯 Features

- **Secure Authentication**: Uses environment variables for API credentials
- **Robust Error Handling**: Implements retry logic and comprehensive error handling
- **Data Transformation**: Cleans and formats data for MongoDB compatibility
- **Batch Processing**: Efficiently processes large datasets
- **Structured Logging**: Comprehensive logging with structured JSON output
- **MongoDB Integration**: Seamless integration with MongoDB for data storage
- **Collection Statistics**: Built-in analytics and monitoring capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CIRCL API     │───▶│   ETL Pipeline  │───▶│   MongoDB       │
│   (Extract)     │    │   (Transform)    │    │   (Load)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### ETL Pipeline Components

1. **Extract**: Connects to CIRCL Passive DNS API and retrieves DNS records
2. **Transform**: Cleans, validates, and formats data for MongoDB
3. **Load**: Stores transformed data in MongoDB with proper indexing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or remote)
- CIRCL Passive DNS API credentials

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd custom-python-etl-data-connector-Kavin302004-1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual credentials
   ```

4. **Configure MongoDB:**
   - Ensure MongoDB is running on your system
   - Update `MONGODB_URI` in `.env` if using remote MongoDB

### Configuration

Create a `.env` file with the following variables:

```env
# CIRCL Passive DNS API Credentials
CIRCL_USERNAME=your_username_here
CIRCL_PASSWORD=your_password_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=etl_data
MONGODB_COLLECTION=circl_passivedns_raw

# API Configuration
CIRCL_BASE_URL=https://www.circl.lu
API_TIMEOUT=30
MAX_RETRIES=3
```

## 📖 API Documentation

### CIRCL Passive DNS API

**Base URL:** `https://www.circl.lu`  
**Authentication:** Basic Authentication (Username/Password)  
**Endpoint:** `/pdb/query`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | DNS query (domain name, IP address, etc.) |
| `limit` | integer | No | Maximum number of records to return (default: 100) |

#### Response Format

```json
[
  {
    "rrname": "example.com",
    "rrtype": "A",
    "rdata": "93.184.216.34",
    "time_first": "2024-01-01T00:00:00Z",
    "time_last": "2024-12-01T00:00:00Z",
    "count": 150,
    "bailiwick": "example.com"
  }
]
```

#### Rate Limits

- **Requests per minute:** 60
- **Daily limit:** 10,000 requests
- **Timeout:** 30 seconds per request

## 🔧 Usage

### Basic Usage

```python
from etl_connector import CIRCLPassiveDNSConnector

# Initialize connector
connector = CIRCLPassiveDNSConnector()

# Run ETL pipeline for a specific domain
success = connector.run_etl_pipeline("example.com", limit=100)

if success:
    print("ETL pipeline completed successfully")
else:
    print("ETL pipeline failed")
```

### Advanced Usage

```python
# Get collection statistics
stats = connector.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Unique domains: {stats['unique_domains']}")
print(f"Collection size: {stats['collection_size_mb']} MB")
```

### Command Line Usage

```bash
python etl_connector.py
```

## 📊 Data Schema

### MongoDB Collection Schema

The data is stored in the `circl_passivedns_raw` collection with the following schema:

```json
{
  "_id": "ObjectId",
  "ingestion_timestamp": "2024-12-01T10:30:00Z",
  "source": "circl_passive_dns",
  "rrname": "example.com",
  "rrtype": "A",
  "rdata": "93.184.216.34",
  "time_first": "2024-01-01T00:00:00Z",
  "time_last": "2024-12-01T00:00:00Z",
  "count": 150,
  "bailiwick": "example.com",
  "raw_record": { /* Original API response */ }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ingestion_timestamp` | DateTime | When the record was ingested |
| `source` | String | Data source identifier |
| `rrname` | String | DNS record name |
| `rrtype` | String | DNS record type (A, AAAA, MX, etc.) |
| `rdata` | String | DNS record data |
| `time_first` | DateTime | First time this record was seen |
| `time_last` | DateTime | Last time this record was seen |
| `count` | Integer | Number of times this record was observed |
| `bailiwick` | String | DNS zone authority |
| `raw_record` | Object | Original API response for debugging |

## 🧪 Testing & Validation

### Test Queries

The connector includes built-in test queries:

```python
test_queries = [
    "example.com",
    "google.com", 
    "github.com"
]
```

### Error Handling

The connector handles various error scenarios:

- **Authentication failures**: Invalid credentials
- **Rate limiting**: Automatic retry with exponential backoff
- **Network timeouts**: Configurable timeout and retry logic
- **Invalid responses**: Graceful handling of malformed data
- **MongoDB connection issues**: Connection validation and error reporting

### Validation Checks

- ✅ API connectivity and authentication
- ✅ Data format validation
- ✅ MongoDB connection and insertion
- ✅ Duplicate record handling
- ✅ Batch processing efficiency

## 📈 Performance & Monitoring

### Logging

The connector uses structured logging with the following levels:

- **INFO**: Normal operation events
- **WARNING**: Non-critical issues (duplicates, rate limits)
- **ERROR**: Critical failures requiring attention

### Metrics

Built-in collection statistics:

- Total document count
- Unique domain count
- Collection size
- Latest ingestion timestamp

### Performance Optimization

- **Batch processing**: Inserts data in batches of 100 records
- **Indexing**: Automatic creation of performance indexes
- **Connection pooling**: Efficient MongoDB connection management
- **Retry logic**: Exponential backoff for failed requests

## 🔒 Security

### Credential Management

- All API credentials stored in `.env` file
- `.env` file excluded from version control
- Environment variables loaded securely using `python-dotenv`

### Data Privacy

- No sensitive data logged
- Raw API responses preserved for debugging
- Secure MongoDB connection with authentication

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```
   Error: Authentication failed. Check credentials.
   Solution: Verify CIRCL_USERNAME and CIRCL_PASSWORD in .env
   ```

2. **MongoDB Connection Failed**
   ```
   Error: Failed to connect to MongoDB
   Solution: Ensure MongoDB is running and MONGODB_URI is correct
   ```

3. **Rate Limit Exceeded**
   ```
   Warning: Rate limit exceeded, waiting
   Solution: Reduce query frequency or increase MAX_RETRIES
   ```

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Project Structure

```
custom-python-etl-data-connector-Kavin302004-1/
├── etl_connector.py          # Main ETL script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── .gitignore               # Git ignore rules
├── env_template.txt         # Environment template
└── README.md                # This documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

*: [CIRCL Passive DNS](https://www.circl.lu/services/passive-dns/)

## 🎓 Assignment Compliance

This implementation fulfills all assignment requirements:

- ✅ **API Integration**: Complete CIRCL Passive DNS API integration
- ✅ **Secure Authentication**: Environment variable-based credential management
- ✅ **ETL Pipeline**: Full Extract-Transform-Load implementation
- ✅ **MongoDB Integration**: Proper data storage with indexing
- ✅ **Error Handling**: Comprehensive error handling and retry logic
- ✅ **Documentation**: Complete README with usage instructions
- ✅ **Project Structure**: Proper Git structure with .gitignore
- ✅ **Testing**: Built-in validation and testing capabilities

---

**Author:** Kavin (Roll Number: 3122225001058)  
**Course:** Software Architecture  
**Institution:** SSN College of Engineering  
**Assignment:** Custom Python ETL Data Connector