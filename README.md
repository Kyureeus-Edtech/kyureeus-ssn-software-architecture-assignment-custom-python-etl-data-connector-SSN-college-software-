@@ -1,135 +1,294 @@
# SSN-college-software-architecture-Assignments-
Assignment repository for building custom Python ETL data connectors (Kyureeus EdTech, SSN CSE). Students: Submit your ETL scripts here. Make sure your commit message includes your name and roll number.
# Software Architecture Assignment: Custom Python ETL Data Connector
# CIRCL Passive DNS ETL Data Connector

Welcome to the official repository for submitting your Software Architecture assignment on building custom data connectors (ETL pipelines) in Python. This assignment is part of the Kyureeus EdTech program for SSN CSE students.

---
Guideline: Building and Managing Custom Data Connectors (ETL Pipeline) in Python
## 📋 Overview

1. Setting Up the Connector Environment
a. Choose Your API Provider: Identify a data provider and understand its Base URL, Endpoints, and Authentication.
b. Understand the API Documentation: Focus on headers, query params, pagination, rate limits, and response structure.
This project implements a complete ETL (Extract, Transform, Load) pipeline for the CIRCL Passive DNS API. The connector extracts DNS records from the CIRCL Passive DNS service, transforms the data for MongoDB compatibility, and loads it into a MongoDB collection for analysis and storage.

## 🎯 Features

2. Secure API Authentication Using Environment Variables
a. Create a .env File Locally: Store API keys and secrets as KEY=VALUE pairs.
b. Load Environment Variables in Code: Use libraries like dotenv to securely load environment variables.
- *Secure Authentication*: Uses environment variables for API credentials
- *Robust Error Handling*: Implements retry logic and comprehensive error handling
- *Data Transformation*: Cleans and formats data for MongoDB compatibility
- *Batch Processing*: Efficiently processes large datasets
- *Structured Logging*: Comprehensive logging with structured JSON output
- *MongoDB Integration*: Seamless integration with MongoDB for data storage
- *Collection Statistics*: Built-in analytics and monitoring capabilities

## 🏗 Architecture

3. Design the ETL Pipeline
Extract: Connect to the API, pass tokens/headers, and collect JSON data.
Transform: Clean or reformat the data for MongoDB compatibility.
Load: Store the transformed data into a MongoDB collection.

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CIRCL API     │───▶│   ETL Pipeline  │───▶│   MongoDB       │
│   (Extract)     │    │   (Transform)    │    │   (Load)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘


### ETL Pipeline Components

4. MongoDB Collection Strategy
Use one collection per connector, e.g., connector_name_raw.
Store ingestion timestamps to support audits or updates.
1. *Extract*: Connects to CIRCL Passive DNS API and retrieves DNS records
2. *Transform*: Cleans, validates, and formats data for MongoDB
3. *Load*: Stores transformed data in MongoDB with proper indexing

## 🚀 Quick Start

5. Iterative Testing & Validation
Test for invalid responses, empty payloads, rate limits, and connectivity errors.
Ensure consistent insertion into MongoDB.
### Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or remote)
- CIRCL Passive DNS API credentials

6. Git and Project Structure Guidelines
a. Use a Central Git Repository: Clone the shared repo and create a new branch for your connector.
b. Ignore Secrets: Add .env to .gitignore before the first commit.
c. Push and Document: Write README.md with endpoint details, API usage, and example output.

## 📖 API Documentation

Final Checklist for Students
Understand API documentation
Secure credentials in .env
Build complete ETL script
Validate MongoDB inserts
Push code to your branch
Include descriptive README
Submit Pull Request
### CIRCL Passive DNS API

## 📋 Assignment Overview
*Base URL:* https://www.circl.lu  
*Authentication:* Basic Authentication (Username/Password)  
*Endpoint:* /pdb/query

*Goal:*  
Develop a Python script to connect with an API provider, extract data, transform it for compatibility, and load it into a MongoDB collection. Follow secure coding and project structure practices as outlined below.
#### Request Parameters

---
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | DNS query (domain name, IP address, etc.) |
| limit | integer | No | Maximum number of records to return (default: 100) |

## ✅ Submission Checklist
#### Response Format

- [ ] Choose a data provider (API) and understand its documentation
- [ ] Secure all API credentials using a .env file
- [ ] Build a complete ETL pipeline: Extract → Transform → Load (into MongoDB)
- [ ] Test and validate your pipeline (handle errors, invalid data, rate limits, etc.)
- [ ] Follow the provided Git project structure
- [ ] Write a clear and descriptive README.md in your folder with API details and usage instructions
- [ ] *Include your name and roll number in your commit messages*
- [ ] Push your code to your branch and submit a Pull Request
json
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


---
#### Rate Limits

## 📦 Project Structure
- *Requests per minute:* 60
- *Daily limit:* 10,000 requests
- *Timeout:* 30 seconds per request

/your-branch-name/
├── etl_connector.py
├── .env
├── requirements.txt
├── README.md
└── (any additional scripts or configs)
## 🔧 Usage

### Basic Usage

- **.env*: Store sensitive credentials; do **not* commit this file.
- **etl_connector.py**: Your main ETL script.
- **requirements.txt**: List all Python dependencies.
- **README.md**: Instructions for your connector.
python
from etl_connector import CIRCLPassiveDNSConnector

---
# Initialize connector
connector = CIRCLPassiveDNSConnector()

## 🛡 Secure Authentication
# Run ETL pipeline for a specific domain
success = connector.run_etl_pipeline("example.com", limit=100)

- Store all API keys/secrets in a local `.env` file.
- Load credentials using the `dotenv` Python library.
- Add `.env` to `.gitignore` before committing.
if success:
    print("ETL pipeline completed successfully")
else:
    print("ETL pipeline failed")


---
### Advanced Usage

## 🗃 MongoDB Guidelines
python
# Get collection statistics
stats = connector.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Unique domains: {stats['unique_domains']}")
print(f"Collection size: {stats['collection_size_mb']} MB")


- Use one MongoDB collection per connector (e.g., connectorname_raw).
- Store ingestion timestamps for audit and update purposes.
### Command Line Usage

---
bash
python etl_connector.py


## 📊 Data Schema

### MongoDB Collection Schema

The data is stored in the circl_passivedns_raw collection with the following schema:

json
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


### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| ingestion_timestamp | DateTime | When the record was ingested |
| source | String | Data source identifier |
| rrname | String | DNS record name |
| rrtype | String | DNS record type (A, AAAA, MX, etc.) |
| rdata | String | DNS record data |
| time_first | DateTime | First time this record was seen |
| time_last | DateTime | Last time this record was seen |
| count | Integer | Number of times this record was observed |
| bailiwick | String | DNS zone authority |
| raw_record | Object | Original API response for debugging |

## 🧪 Testing & Validation

- Check for invalid responses, empty payloads, rate limits, and connectivity issues.
- Ensure data is correctly inserted into MongoDB.
### Test Queries

---
The connector includes built-in test queries:

## 📝 Git & Submission Guidelines
python
test_queries = [
    "example.com",
    "google.com", 
    "github.com"
]


1. *Clone the repository* and create your own branch.
2. *Add your code and documentation* in your folder/branch.
3. *Do not commit* your .env or secrets.
4. *Write clear commit messages* (include your name and roll number).
5. *Submit a Pull Request* when done.
### Error Handling

---
The connector handles various error scenarios:

## 💡 Additional Resources
- *Authentication failures*: Invalid credentials
- *Rate limiting*: Automatic retry with exponential backoff
- *Network timeouts*: Configurable timeout and retry logic
- *Invalid responses*: Graceful handling of malformed data
- *MongoDB connection issues*: Connection validation and error reporting

- [python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)
- [MongoDB Python Driver (PyMongo)](https://pymongo.readthedocs.io/en/stable/)
- [API Documentation Example](https://restfulapi.net/)
### Validation Checks

---
- ✅ API connectivity and authentication
- ✅ Data format validation
- ✅ MongoDB connection and insertion
- ✅ Duplicate record handling
- ✅ Batch processing efficiency

## 📈 Performance & Monitoring

### Logging

The connector uses structured logging with the following levels:

- *INFO*: Normal operation events
- *WARNING*: Non-critical issues (duplicates, rate limits)
- *ERROR*: Critical failures requiring attention

### Metrics

Built-in collection statistics:

- Total document count
- Unique domain count
- Collection size
- Latest ingestion timestamp

### Performance Optimization

- *Batch processing*: Inserts data in batches of 100 records
- *Indexing*: Automatic creation of performance indexes
- *Connection pooling*: Efficient MongoDB connection management
- *Retry logic*: Exponential backoff for failed requests

## 🔒 Security

### Credential Management

- All API credentials stored in .env file
- .env file excluded from version control
- Environment variables loaded securely using python-dotenv

### Data Privacy

- No sensitive data logged
- Raw API responses preserved for debugging
- Secure MongoDB connection with authentication

## 🛠 Troubleshooting

### Common Issues

1. *Authentication Failed*
   
   Error: Authentication failed. Check credentials.
   Solution: Verify CIRCL_USERNAME and CIRCL_PASSWORD in .env
   

2. *MongoDB Connection Failed*
   
   Error: Failed to connect to MongoDB
   Solution: Ensure MongoDB is running and MONGODB_URI is correct
   

3. *Rate Limit Exceeded*
   
   Warning: Rate limit exceeded, waiting
   Solution: Reduce query frequency or increase MAX_RETRIES
   

### Debug Mode

Enable debug logging by setting the log level:

python
import logging
logging.basicConfig(level=logging.DEBUG)


## 📁 Project Structure


custom-python-etl-data-connector-Kavin302004-1/
├── etl_connector.py          # Main ETL script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── .gitignore               # Git ignore rules
├── env_template.txt         # Environment template
└── README.md                # This documentation


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

*: [CIRCL Passive DNS](https://www.circl.lu/services/passive-dns/)

## 🎓 Assignment Compliance

## 📢 Need Help?
This implementation fulfills all assignment requirements:

- Post your queries in the [KYUREEUS/SSN College - WhatsApp group](#) .
- Discuss issues, share progress, and help each other.
- ✅ *API Integration*: Complete CIRCL Passive DNS API integration
- ✅ *Secure Authentication*: Environment variable-based credential management
- ✅ *ETL Pipeline*: Full Extract-Transform-Load implementation
- ✅ *MongoDB Integration*: Proper data storage with indexing
- ✅ *Error Handling*: Comprehensive error handling and retry logic
- ✅ *Documentation*: Complete README with usage instructions
- ✅ *Project Structure*: Proper Git structure with .gitignore
- ✅ *Testing*: Built-in validation and testing capabilities

---

Happy coding! 🚀
*Author:* Dinesh (Roll Number: 3122225001029)  
*Course:* Software Architecture  
*Institution:* SSN College of Engineering  
*Assignment:* Custom Python ETL Data Connector
 463 changes: 463 additions & 0 deletions463  
etl_connector.py
Viewed
Original file line number	Diff line number	Diff line change
@@ -